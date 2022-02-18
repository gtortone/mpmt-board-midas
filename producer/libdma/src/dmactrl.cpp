#include <iostream>
#include <string>
#include <thread>
#include <fcntl.h>
#include <unistd.h>  // usleep
#include <stdexcept>
#include <sys/mman.h>
#include <fmt/core.h>

#include "dmactrl.h"

//#define DEBUG

DMACtrl::DMACtrl(unsigned int baseaddr) {

   dh = open("/dev/mem", O_RDWR | O_SYNC);
   // check return value

   mem = (unsigned int *) mmap(NULL, AXI_DMA_DEPTH, PROT_READ | PROT_WRITE, MAP_SHARED, dh, baseaddr);
   // check return value

   minLoop = 5;
   maxLoop = 10;

   minWait = 100;    // 100 us
   maxWait = 10000;  //  10 ms
   curWait = (maxWait - minWait) / 2;

   bdStartIndex = 0;
   bdStopIndex = 0;

   initsg = false;
   blockTransfer = false;
   bufferTransfer = false;
}

DMACtrl::~DMACtrl(void) {
   munmap((unsigned int *) mem, AXI_DMA_DEPTH);
}

void DMACtrl::setChannel(DMACtrl::Channel ch) {

   channel = ch;
   if(channel == MM2S)
      regs = mm2sRegs;
   else if(channel == S2MM)
      regs = s2mmRegs;
}

void DMACtrl::setRegister(int offset, unsigned int value) {
   mem[offset>>2] = value;
}

unsigned int DMACtrl::getRegister(int offset) {
   return (mem[offset>>2]);
}

void DMACtrl::halt(void) {

   if(channel == UNKNOWN)
      throw std::runtime_error(std::string(__func__) + ": DMA channel not set");

   setRegister(regs["DMACR"], 0);
}

void DMACtrl::reset(void) {

   if(channel == UNKNOWN)
      throw std::runtime_error(std::string(__func__) + ": DMA channel not set");

   setRegister(regs["DMACR"], 4);
}

void DMACtrl::run(void) {

   if(isSG()) runSG();
   else runDirect();
}

bool DMACtrl::isIdle(void) {

   if(channel == UNKNOWN)
      throw std::runtime_error(std::string(__func__) + ": DMA channel not set");

   return( getRegister(regs["DMASR"]) & 0x0002 );
}

bool DMACtrl::isRunning(void) {

   if(channel == UNKNOWN)
      throw std::runtime_error(std::string(__func__) + ": DMA channel not set");

   return( ~(getRegister(regs["DMASR"]) & 0x0001) );
}

bool DMACtrl::isSG(void) {

   if(channel == UNKNOWN)
      throw std::runtime_error(std::string(__func__) + ": DMA channel not set");

   return( getRegister(regs["DMASR"]) & 0x0008 );
}

void DMACtrl::setMem(volatile unsigned int *mem_address, int offset, unsigned int value) {
   mem_address[offset>>2] = value;
}

unsigned int DMACtrl::getMem(volatile unsigned int *mem_address, int offset) {
   return(mem_address[offset>>2]);
}

void DMACtrl::getStatus(void) {

   if(channel == UNKNOWN)
      throw std::runtime_error(std::string(__func__) + ": DMA channel not set");

   unsigned int status = getRegister(regs["DMASR"]);

   if(channel == S2MM)
      fmt::print("Stream to memory-mapped status (0x{:08x}@0x{:02x}): ", status, regs["DMACR"]);
   else if(channel == MM2S)
      fmt::print("Memory-mapped to stream status (0x{:08x}@0x{:02x}): ", status, regs["DMACR"]);

   if (status & 0x00000001) std::cout << " halted"; else std::cout << " running";
   if (status & 0x00000002) std::cout << " idle";
   if (status & 0x00000008) std::cout << " SGIncld";
   if (status & 0x00000010) std::cout << " DMAIntErr";
   if (status & 0x00000020) std::cout << " DMASlvErr";
   if (status & 0x00000040) std::cout << " DMADecErr";
   if (status & 0x00000100) std::cout << " SGIntErr";
   if (status & 0x00000200) std::cout << " SGSlvErr";
   if (status & 0x00000400) std::cout << " SGDecErr";
   if (status & 0x00001000) std::cout << " IOC_Irq";
   if (status & 0x00002000) std::cout << " Dly_Irq";
   if (status & 0x00004000) std::cout << " Err_Irq";
   int nirq = (status & 0x00FF0000) >> 16;
   std::cout << " IRQThresholdSts: " << nirq;

   std::cout << std::endl;
}

bool DMACtrl::IRQioc(void) {

   if(channel == UNKNOWN)
      throw std::runtime_error(std::string(__func__) + ": DMA channel not set");

   return( getRegister(regs["DMASR"]) & (1<<12) );
}

void DMACtrl::clearIRQioc(void) {

   if(channel == UNKNOWN)
      throw std::runtime_error(std::string(__func__) + ": DMA channel not set");

   unsigned int status = getRegister(regs["DMASR"]);
   setRegister(regs["DMASR"], status & ~(1<<12));
}

long int DMACtrl::getBufferAddress(int desc) {
   return ( getMem(bdmem, BUFFER_ADDRESS + (DESC_SIZE * desc)) );
}

void DMACtrl::initDirect(unsigned int blocksize, unsigned int addr) {

   if(channel == UNKNOWN)
      throw std::runtime_error(std::string(__func__) + ": DMA channel not set");

   if(isSG())
      throw std::runtime_error(std::string(__func__) + ": DMA channel not configured for Direct mode");

   if(channel == S2MM)
      setRegister(regs["DESTINATION_ADDRESS"], addr);
   else if(channel == MM2S)
      setRegister(regs["START_ADDRESS"], addr);
   else throw std::runtime_error(std::string(__func__) + ": DMA channel not set");

   size = blocksize;

   // DMACR[0]  = 1 : run dma
   // DMACR[12] = 1 : enable Interrupt on Complete
   // DMACR[13] = 1 : enable Delay Interrupt
   // DMACR[14] = 1 : enable Error Interrupt
   // DMACR[15] = 1 : [reserved] - no effect
   setRegister(regs["DMACR"], 0xF001);
}

void DMACtrl::runDirect(void) {

   if(channel == UNKNOWN)
      throw std::runtime_error(std::string(__func__) + ": DMA channel not set");

   if(isSG())
      throw std::runtime_error(std::string(__func__) + ": DMA channel not configured for Direct mode");

   setRegister(regs["LENGTH"], size);
}

void DMACtrl::initSG(unsigned int baseaddr, int n, unsigned int blocksize, unsigned int tgtaddr) {

   if(channel == UNKNOWN)
      throw std::runtime_error(std::string(__func__) + ": DMA channel not set");

   if(!isSG())
      throw std::runtime_error(std::string(__func__) + ": DMA channel not configured for Scatter-Gather mode");

   bdmem = (unsigned int *) mmap(NULL, n * DESC_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, dh, baseaddr);
   descaddr = baseaddr;
   targetaddr = tgtaddr;
   size = blocksize;
   ndesc = n;

   initSGDescriptors();
}

void DMACtrl::runSG(void) {

   if(!initsg)
      throw std::runtime_error(std::string(__func__) + ": Scatter-Gather not initialized");

   // start channel with complete interrupt and cyclic mode
   setRegister(regs["DMACR"], (ndesc << 16) + 0x1011);
   setRegister(regs["TAILDESC"], descaddr + (DESC_SIZE * (ndesc-1)));

   // reset BD indexes
   blockOffset = 0;
   blockSize = 0;
   bdStartIndex = 0;
   bdStopIndex = 0;
   lastIrqThreshold = ndesc;

   // reset transfer state
   blockTransfer = false;
   bufferTransfer = false;
}

void DMACtrl::initSGDescriptors(void) {

   unsigned int i;

   // Initialization of Descriptors Array
   for(i=0; i < (DESC_SIZE * ndesc); i++)
      setMem(bdmem, i, 0);

   // Write descriptors arrays
   for(i=0; i<ndesc; i++) {
      setMem(bdmem, NXTDESC + (DESC_SIZE * i), descaddr + NXTDESC + (DESC_SIZE * (i+1)));
      setMem(bdmem, BUFFER_ADDRESS + (DESC_SIZE * i), targetaddr + (size * i));
      setMem(bdmem, CONTROL + (DESC_SIZE * i), size);
   }

   setMem(bdmem, NXTDESC + (DESC_SIZE * (ndesc-1)), 0);

   setRegister(regs["CURDESC"], descaddr);

   initsg = true;
}

void DMACtrl::incSGDescTable(int index) {

   if(!initsg)
      throw std::runtime_error(std::string(__func__) + ": Scatter-Gather not initialized");

   for(unsigned int i=0; i<ndesc; i++)
      setMem(bdmem, BUFFER_ADDRESS + (DESC_SIZE * i), targetaddr + (size * (ndesc * index + i)));
}

void DMACtrl::dumpSGDescTable(void) {

   if(!initsg)
      throw std::runtime_error(std::string(__func__) + ": Scatter-Gather not initialized");

   for(unsigned int i=0; i<ndesc; i++) {
      unsigned int bdaddr = descaddr + (DESC_SIZE * i);
      unsigned int nxtdesc = getMem(bdmem, NXTDESC + (DESC_SIZE * i));
      unsigned int buffer_address = getMem(bdmem, BUFFER_ADDRESS + (DESC_SIZE * i));
      unsigned int control =  getMem(bdmem, CONTROL + (DESC_SIZE * i));
      unsigned int status = getMem(bdmem, STATUS + (DESC_SIZE * i));
      fmt::print("BD{}: addr {:04X} NXTDESC {:04X}, BUFFER_ADDRESS {:04X}, CONTROL {:04X}, STATUS {:04X}\n", \
         i, bdaddr, nxtdesc, buffer_address, control, status);
   }
}

void DMACtrl::dumpSGDescAllStatus(void) {

   if(!initsg)
      throw std::runtime_error(std::string(__func__) + ": Scatter-Gather not initialized");

   for(unsigned int i=0; i<ndesc; i++) {
      unsigned int status = getMem(bdmem, STATUS + (DESC_SIZE * i));
      fmt::print("BD{}: STATUS {:04X}\n", i, status);
   }
}

void DMACtrl::clearSGDescAllStatus(void) {
   
   if(!initsg)
      throw std::runtime_error(std::string(__func__) + ": Scatter-Gather not initialized");

   for(unsigned int i=0; i<ndesc; i++)
      setMem(bdmem, STATUS + (DESC_SIZE * i), 0);
}

long int DMACtrl::getSGDescBufferAddress(int desc) {

   if(!initsg)
      throw std::runtime_error(std::string(__func__) + ": Scatter-Gather not initialized");

   return ( getMem(bdmem, BUFFER_ADDRESS + (DESC_SIZE * desc)) );
}

unsigned int DMACtrl::getBlockOffset(void) {
   return(blockOffset);
}

unsigned int DMACtrl::getBlockSize(void) {
   return(blockSize);
}

void DMACtrl::calibrateWaitTime(unsigned int count) {

   if(count > maxLoop) {
      curWait *= 2;
      if(curWait > maxWait) curWait = maxWait;
   } else if(count < minLoop) {
      curWait /= 2;
      if(curWait < minWait) curWait = minWait;
   }
}

bool DMACtrl::rx(unsigned int timeout) {

   // check if DMA mode is scatter-gather or direct
   if(!isSG()) return(directRx(timeout));

   // check if block or buffer transfer is in progress
   if(blockTransfer) return(blockRx(timeout));
   if(bufferTransfer) return(bufferRx(timeout));

   if(curWait == maxWait) {
      // in case of low rate send ready BDs and don't wait all BDs
      return(blockRx(timeout));
   } else return(bufferRx(timeout));
}

bool DMACtrl::directRx(unsigned int timeout) {
   
   // timout: 0=infinite

   if(isSG())
      throw std::runtime_error(std::string(__func__) + ": DMA channel not configured for Direct mode");

   if(channel != S2MM)
      throw std::runtime_error(std::string(__func__) + ": DMA Scatter-Gather channel != S2MM");

   if(!isRunning())
      throw std::runtime_error(std::string(__func__) + ": DMA channel not running");

   int nloops = 0;
   unsigned int waitTime = 0;
   unsigned int step;

   if(timeout == 0)
      step = curWait;
   else
      step = minWait;

   do {

      if(isIdle()) {
         if(timeout == 0) 
            calibrateWaitTime(nloops);

         // send whole buffer
         blockOffset = 0;
         blockSize = size;

         return true;
      }

      // relax CPU
      usleep(step);

      waitTime += step;
      nloops++; 
         
   } while ( (waitTime < timeout) || (timeout == 0) );

   return false;
}

bool DMACtrl::blockRx(unsigned int timeout) {

   // timout: 0=infinite

   if(!initsg)
      throw std::runtime_error(std::string(__func__) + ": Scatter-Gather not initialized");

   if(channel != S2MM)
      throw std::runtime_error(std::string(__func__) + ": DMA Scatter-Gather channel != S2MM");

   if(!isRunning())
      throw std::runtime_error(std::string(__func__) + ": DMA channel not running");

   int nloops = 0;
   unsigned int waitTime = 0;
   unsigned int step;
   unsigned int status;
   unsigned int irqThreshold = 0;
   unsigned int readyBlocks = 0;

   if(timeout == 0)
      step = curWait;
   else
      step = minWait;

   blockTransfer = true;

   do {
      
      status = getRegister(regs["DMASR"]);

      readyBlocks = 0;

      if(isIdle()) {
         bdStopIndex = ndesc - 1;
         readyBlocks = bdStopIndex - bdStartIndex + 1;
         lastIrqThreshold = ndesc;
         blockTransfer = false;
      } else {
         irqThreshold = (status & 0x00FF0000) >> 16;
         if(irqThreshold < lastIrqThreshold) {      // there is an increment on ready BDs...
            readyBlocks = (ndesc - irqThreshold - bdStartIndex);
            lastIrqThreshold = irqThreshold;
         }
      }
      
      /*
      fmt::print("{}) irqThreshold: {}  lastIrqThreshold: {}  readyBlocks: {}  bdStartIndex: {}  bdStopIndex: {}\n", \
         nloops, irqThreshold, lastIrqThreshold, readyBlocks, bdStartIndex, bdStopIndex);
      */

      if(readyBlocks > 0) {

         bdStopIndex = bdStartIndex + readyBlocks - 1;

         if(timeout == 0)
            calibrateWaitTime(nloops);

         // SG mode: a subset of BDs are available 
         blockOffset = getBufferAddress(bdStartIndex) - targetaddr;
         blockSize = size * (bdStopIndex - bdStartIndex + 1);

#ifdef DEBUG
         fmt::print("BDs ready from BD{} to BD{} - offset: {} size: {}\n", \
            bdStartIndex, bdStopIndex, blockOffset, blockSize);
#endif

         if(bdStopIndex < (ndesc-1))
            bdStartIndex = bdStopIndex + 1;

         return true;
      }

      // relax CPU
      usleep(step);

      waitTime += step;
      nloops++; 
      
   } while ( (waitTime < timeout) || (timeout == 0) );

   return false;
}

bool DMACtrl::bufferRx(unsigned int timeout) {

   // timout: 0=infinite

   if(!initsg)
      throw std::runtime_error(std::string(__func__) + ": Scatter-Gather not initialized");

   if(channel != S2MM)
      throw std::runtime_error(std::string(__func__) + ": DMA Scatter-Gather channel != S2MM");

   if(!isRunning())
      throw std::runtime_error(std::string(__func__) + ": DMA channel not running");

   int nloops = 0;
   unsigned int waitTime = 0;
   unsigned int step;
   
   if(timeout == 0)
      step = curWait;
   else
      step = minWait;

   bufferTransfer = true;

   do {

      if(isIdle()) {
         if(timeout == 0) 
            calibrateWaitTime(nloops);

         // send whole buffer
         blockOffset = 0;
         blockSize = size * ndesc;

         bufferTransfer = false;

         return true;
      }

      // relax CPU
      usleep(step);

      waitTime += step;
      nloops++; 
 
   } while( (waitTime < timeout) || (timeout == 0) );

   return false;
}

