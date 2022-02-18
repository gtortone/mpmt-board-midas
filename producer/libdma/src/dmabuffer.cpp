#include <iostream>
#include <vector>
#include <fcntl.h>      // open
#include <unistd.h>     // close
#include <filesystem>
#include <fstream>
#include <fmt/core.h>
#include <sys/mman.h>

#include "dmabuffer.h"

DMABuffer::DMABuffer(void) {
   fd = -1;
}

DMABuffer::~DMABuffer(void) {
   if(fd != -1)
      close();
}

bool DMABuffer::open(std::string bufname, bool cache_on) {

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
   if((fd = ::open(filename.data(), O_RDWR | ((cache_on == 0)? O_SYNC : 0))) == -1) {
      std::cout << "E: can not open " << filename << std::endl;
      return false;
   }

   buf = (unsigned char *) mmap(NULL, buf_size, PROT_READ|PROT_WRITE, MAP_SHARED, fd, 0);
   sync_mode = 1;

   return true;
}

bool DMABuffer::close(void) {

   if(fd < 0)
      return false;

   ::close(fd);
   fd = -1;
   return true;
}

bool DMABuffer::setSyncArea(unsigned int offset, unsigned int size, unsigned int direction) {

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

bool DMABuffer::setBufferOwner(unsigned int owner) {

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

bool DMABuffer::setSyncMode(unsigned int mode) {
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
