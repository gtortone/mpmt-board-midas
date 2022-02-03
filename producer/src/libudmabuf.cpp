#include <iostream>
#include <string>
#include <filesystem>
#include <fstream>
#include <chrono>
#include <thread>
#include <fcntl.h>      // open
#include <unistd.h>     // close
#include <fmt/core.h>
#include <sys/mman.h>

#include "libudmabuf.h"

Udmabuf::Udmabuf(void) {
   dmafd = -1;
}

bool Udmabuf::openUIO(std::string name) {

   for (const auto &file : std::filesystem::recursive_directory_iterator("/sys/class/uio/")) {
      const std::string uioname = fmt::format("{}/name", file.path().string());
      std::fstream f(uioname, std::fstream::in);
      if(!f.is_open())
         return false;

      std::string label;
      std::getline(f, label);

      if(label == name) {
         std::string uiodev = fmt::format("/dev/{}", file.path().filename().string()); 
         uiofd = open(uiodev.data(), O_RDWR);
         uiomem = (volatile unsigned int*)mmap(NULL, 65535, PROT_READ|PROT_WRITE, MAP_SHARED, uiofd, 0);

         return true;
      }
   }

   return false;
}

bool Udmabuf::openDMABuffer(std::string bufname, bool cache_on) {

   std::vector<std::string> sys_class_path_list = {"/sys/class/u-dma-buf", "/sys/class/udmabuf"};

   bool found = false;
   for (auto& dir : sys_class_path_list) {
      
      std::string subdir = fmt::format("{0}/{1}", dir, bufname);
      std::filesystem::directory_entry entry(subdir.data());
      if(entry.is_directory()) {
         found = true;
         sys_class_path = subdir;
         name = bufname;
      }
   }

   if(!found) {
      std::cout << "E: sys class not found" << std::endl;
      return false;
   }

   std::string filename;
   std::fstream f;
   std::string line;

   filename = fmt::format("{}/phys_addr", sys_class_path);
   f.open(filename, std::fstream::in);
   if(!f.is_open()) {
      std::cout << "E: can not open " << filename << std::endl;
      return false;
   }
   std::getline(f, line);
   phys_addr = std::stoul(line, nullptr, 16);
   f.close();

   filename = fmt::format("{}/size", sys_class_path);
   f.open(filename, std::fstream::in);
   if(!f.is_open()) {
      std::cout << "E: can not open " << filename << std::endl;
      return false;
   }
   std::getline(f, line);
   buf_size = std::stoul(line);
   f.close();

   filename = fmt::format("/dev/{}", name);
   if((dmafd = open(filename.data(), O_RDWR | ((cache_on == 0)? O_SYNC : 0))) == -1) {
      std::cout << "E: can not open " << filename << std::endl;
      return false;
   }

   buf = (unsigned char *) mmap(NULL, buf_size, PROT_READ|PROT_WRITE, MAP_SHARED, dmafd, 0);
   debug_vma = 0;
   sync_mode = 1;

   return true;
} 

bool Udmabuf::closeDMABuffer(void) {
   if(dmafd < 0)
      return false;

   close(dmafd);
   dmafd = -1;
   return true;
}

void Udmabuf::setRegister(int addr, unsigned int value) {
   uiomem[addr>>2] = value;   
}

unsigned int Udmabuf::getRegister(int addr) {
   return uiomem[addr>>2];
}

void Udmabuf::getStatus(unsigned int ep) {
   
   unsigned int status;
   std::string msg;

   if(ep == S2MM_ENDPOINT) {
      status = getRegister(S2MM_STATUS_REGISTER);
      fmt::print("Stream to memory-mapped status (0x{:08x}@0x{:02x}): ", status, S2MM_STATUS_REGISTER);
   } else if(ep == MM2S_ENDPOINT) {
      status = getRegister(MM2S_STATUS_REGISTER);
      fmt::print("Memory-mapped to stream status (0x{:08x}@0x{:02x}): ", status, MM2S_STATUS_REGISTER);
   } else { 
      std::cout << "E: endpoint not valid" << std::endl;
      return;
   }

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
   std::cout << std::endl;
}

void Udmabuf::sync(unsigned int ep, const std::chrono::microseconds udelay) {
   
   unsigned int addr;
   unsigned int status;   

   if(ep == S2MM_ENDPOINT) {
      addr = S2MM_STATUS_REGISTER;
   } else if(ep == MM2S_ENDPOINT) {
      addr = S2MM_STATUS_REGISTER;
   } else {
      std::cout << "E: endpoint not valid" << std::endl;
      return;
   }

   status = getRegister(addr);
   while(!(status & 1<<12) || !(status & 1<<1)) {
      status = getRegister(addr);
      std::this_thread::sleep_for(udelay);
   }
}

bool Udmabuf::setSyncArea(unsigned int offset, unsigned int size, unsigned int direction) {
     
   std::string filename;
   std::fstream f;

   filename = fmt::format("{}/sync_offset", sys_class_path);
   f.open(filename, std::fstream::out);
   if(!f.is_open()) {
      std::cout << "E: can not open " << filename << std::endl;
      return false;
   }
   f << offset;
   f.close();

   filename = fmt::format("{}/sync_size", sys_class_path);
   f.open(filename, std::fstream::out);
   if(!f.is_open()) {
      std::cout << "E: can not open " << filename << std::endl;
      return false;
   }
   f << size;
   f.close();

   filename = fmt::format("{}/sync_direction", sys_class_path);
   f.open(filename, std::fstream::out);
   if(!f.is_open()) {
      std::cout << "E: can not open " << filename << std::endl;
      return false;
   }
   f << direction;
   f.close();
 
   return true;
}

bool Udmabuf::setBufferOwner(unsigned int owner) {

   std::string filename;
   std::fstream f;

   if(owner == CPU_OWNER) {
      filename = fmt::format("{}/sync_for_cpu", sys_class_path);
   } else if(owner == DEVICE_OWNER) {
      filename = fmt::format("{}/sync_for_device", sys_class_path);
   } else {
      std::cout << "E: owner not valid" << std::endl;
      return false;
   }

   f.open(filename, std::fstream::out);
   if(!f.is_open()) {
      std::cout << "E: can not open " << filename << std::endl;
      return false;
   }
   f << 1;
   f.close();

   return true;
}

/*
sync_mode=0: CPU cache is enabled regardless of the O_SYNC flag presense.
sync_mode=1: If O_SYNC is specified, CPU cache is disabled. If O_SYNC is not specified, CPU cache is enabled.
sync_mode=2: If O_SYNC is specified, CPU cache is disabled but CPU uses write-combine when writing data to DMA buffer 
             improves performance by combining multiple write accesses. If O_SYNC is not specified, CPU cache is enabled.
sync_mode=3: If O_SYNC is specified, DMA coherency mode is used. If O_SYNC is not specified, CPU cache is enabled.
sync_mode=4: CPU cache is enabled regardless of the O_SYNC flag presense.
sync_mode=5: CPU cache is disabled regardless of the O_SYNC flag presense.
sync_mode=6: CPU uses write-combine to write data to DMA buffer regardless of O_SYNC presence.
sync_mode=7: DMA coherency mode is used regardless of O_SYNC presence.
*/

bool Udmabuf::setSyncMode(unsigned int mode) {

   std::string filename;
   std::fstream f;

   if(mode < 0 || mode > 7)
      return false;

   filename = fmt::format("{}/sync_mode", sys_class_path);
   f.open(filename, std::fstream::out);
   if(!f.is_open()) {
      std::cout << "E: can not open " << filename << std::endl;
      return false;
   }
   f << mode;
   f.close();

   return true;
}

unsigned int Udmabuf::waitUIOInterrupt(void) {

   int count;
   unsigned int en = 1;
   
   // enable general uio interrupt
   write(uiofd, (void *)&en, sizeof(int));

   // blocking read till interrupt received and return interrupt count
   read(uiofd, (void *)&count, sizeof(int));

   return count;
}
