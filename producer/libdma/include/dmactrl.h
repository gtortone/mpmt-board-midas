#ifndef DMACTRL_H_
#define DMACTRL_H_

#include <map>
#include <string>

#define NXTDESC                  0x00      // NXTDESC
#define BUFFER_ADDRESS           0x08      // must align 0x40 addresses
#define CONTROL                  0x18      // must align 0x40 addresses
#define STATUS                   0x1C      // unused with 32bit addresses

#define AXI_DMA_DEPTH            0xFFFF
#define DESC_SIZE                64

class DMACtrl {
   
public:
   DMACtrl(unsigned int baseaddr);
   ~DMACtrl(void);

   enum Channel {
     MM2S,
     S2MM,
     UNKNOWN 
   };

   void setChannel(DMACtrl::Channel ch);
   void setRegister(int offset, unsigned int value);
   unsigned int getRegister(int offset);

   void halt(void);
   void reset(void);
   void run(void);

   bool isIdle(void);
   bool isRunning(void);
   bool isSG(void);

   void getStatus(void);
   bool IRQioc(void);
   void clearIRQioc(void);
   
   bool rx(unsigned int timeout = 0);

   /* Direct DMA methods */
   void initDirect(unsigned int blocksize, unsigned int addr);

   /* Scatter Gather DMA methods */
   void initSG(unsigned int baseaddr, int n, unsigned int blocksize, unsigned int tgtaddr);
   void incSGDescTable(int index);
   void dumpSGDescTable(void);
   void dumpSGDescAllStatus(void);
   void clearSGDescAllStatus(void);
   long int getSGDescBufferAddress(int desc);

   unsigned int getBlockOffset(void);
   unsigned int getBlockSize(void);

private:

   std::map<std::string, unsigned int> mm2sRegs = { 
      {"DMACR", 0x00}, 
      {"DMASR", 0x04},
      {"START_ADDRESS", 0x18},
      {"LENGTH", 0x28},
      {"CURDESC", 0x08},
      {"TAILDESC", 0x10} };

   std::map<std::string, unsigned int> s2mmRegs = { 
      {"DMACR", 0x30}, 
      {"DMASR", 0x34},
      {"DESTINATION_ADDRESS", 0x48},
      {"LENGTH", 0x58},
      {"CURDESC", 0x38},
      {"TAILDESC", 0x40} };

   std::map<std::string, unsigned int> regs;

   DMACtrl::Channel channel = DMACtrl::Channel::UNKNOWN;

   int dh;
   volatile unsigned int* mem;      // AXI-DMA controller
   volatile unsigned int* bdmem;    // block descriptors memory (SG)
   unsigned int size;
   unsigned int descaddr;
   unsigned int targetaddr;
   unsigned int ndesc;
   unsigned int blockOffset, blockSize;
   unsigned int bdStartIndex, bdStopIndex;
   unsigned int minWait, maxWait, curWait;
   unsigned int minLoop, maxLoop;
   unsigned int lastIrqThreshold;
   bool initsg;
   bool blockTransfer, bufferTransfer;

   void setMem(volatile unsigned int *mem_address, int offset, unsigned int value);
   unsigned int getMem(volatile unsigned int *mem_address, int offset);
   void initSGDescriptors(void);
   void calibrateWaitTime(unsigned int count);
   long int getBufferAddress(int desc);

   /* Direct DMA methods */
   void runDirect(void);
   bool directRx(unsigned int timeout);

   /* Scatter Gather DMA methods */
   void runSG(void);
   bool blockRx(unsigned int timeout = 0);
   bool bufferRx(unsigned int timeout = 0);
};

#endif

