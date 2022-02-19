#pragma once

#include <string>

/*
 * Implementation based on udmabuf (https://github.com/ikwzm/udmabuf)
 */

#define  CPU_OWNER               0x01
#define  DEVICE_OWNER            0x02

class DMABuffer {

private:
   std::string    name;
   std::string    sys_class_path;
   int            fd;
   unsigned int   buf_size;
   unsigned long  phys_addr;
   unsigned long  sync_mode;
   bool           cache_on;

public:
   DMABuffer(void);
   ~DMABuffer(void);

   unsigned char* buf;

   bool open(std::string bufname, bool cache_on);
   bool close(void);
   unsigned int size(void) { return buf_size; };
   unsigned long getPhysicalAddress(void) { return phys_addr; };
   unsigned int getBufferSize(void) { return buf_size; };
   bool setSyncArea(unsigned int offset, unsigned int size, unsigned int direction);
   bool setBufferOwner(unsigned int owner);
   bool setSyncMode(unsigned int mode);
};

