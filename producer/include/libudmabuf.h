#ifndef LIBUDMABUF_H_
#define LIBUDMABUF_H_

#include <string>

#define MM2S_CONTROL_REGISTER    0x00
#define MM2S_STATUS_REGISTER     0x04
#define MM2S_START_ADDRESS       0x18
#define MM2S_LENGTH              0x28
#define MM2S_CURDESC             0x08    // must align 0x40 addresses
#define MM2S_CURDESC_MSB         0x0C    // unused with 32bit addresses
#define MM2S_TAILDESC            0x10    // must align 0x40 addresses
#define MM2S_TAILDESC_MSB        0x14    // unused with 32bit addresses

#define S2MM_CONTROL_REGISTER    0x30
#define S2MM_STATUS_REGISTER     0x34
#define S2MM_DESTINATION_ADDRESS 0x48
#define S2MM_LENGTH              0x58
#define S2MM_CURDESC             0x38    // must align 0x40 addresses
#define S2MM_CURDESC_MSB         0x3C    // unused with 32bit addresses
#define S2MM_TAILDESC            0x40    // must align 0x40 addresses
#define S2MM_TAILDESC_MSB        0x44    // unused with 32bit addresses

#define  HP0_DMA_BUFFER_MEM_ADDRESS         0x20000000
#define  DESCRIPTOR_REGISTERS_SIZE          0xFFFF
#define  SG_DMA_DESCRIPTORS_WIDTH           0xFFFF
#define  MEMBLOCK_WIDTH                     0x3FFFFFF    //size of mem used by s2mm and mm2s
#define  BUFFER_BLOCK_WIDTH                 0x20000   //size of memory block per descriptor in bytes  (131072)
#define  NUM_OF_DESCRIPTORS                 0x2    //number of descriptors for each direction

#define  HP0_MM2S_DMA_BASE_MEM_ADDRESS      (HP0_DMA_BUFFER_MEM_ADDRESS)
#define  HP0_MM2S_DMA_DESCRIPTORS_ADDRESS   (HP0_MM2S_DMA_BASE_MEM_ADDRESS)
#define  HP0_MM2S_SOURCE_MEM_ADDRESS        (HP0_MM2S_DMA_BASE_MEM_ADDRESS + SG_DMA_DESCRIPTORS_WIDTH + 1)

#define  HP0_S2MM_DMA_BASE_MEM_ADDRESS      (HP0_DMA_BUFFER_MEM_ADDRESS + MEMBLOCK_WIDTH + 1)
#define  HP0_S2MM_DMA_DESCRIPTORS_ADDRESS   (HP0_S2MM_DMA_BASE_MEM_ADDRESS)
#define  HP0_S2MM_TARGET_MEM_ADDRESS        (HP0_S2MM_DMA_BASE_MEM_ADDRESS + SG_DMA_DESCRIPTORS_WIDTH + 1)

#define  S2MM_ENDPOINT           0x10
#define  MM2S_ENDPOINT           0x20
#define  DMA_BIDIRECTIONAL       0x00
#define  DMA_TO_DEVICE           0x01
#define  DMA_FROM_DEVICE         0x02
#define  CPU_OWNER               0x01
#define  DEVICE_OWNER            0x02

class Udmabuf {

private:
   std::string    name;
   std::string    sys_class_path;
   int            uiofd;
   int            dmafd;
   unsigned char* buf;
   unsigned int   buf_size;
   unsigned long  phys_addr;
   unsigned long  debug_vma;
   unsigned long  sync_mode;
   bool           cache_on;
   volatile unsigned int*  uiomem;

public:

   Udmabuf(void);
   bool openUIO(std::string name);
   bool openDMABuffer(std::string bufname, bool cache_on);
   bool closeDMABuffer(void);
   void setRegister(int addr, unsigned int value); 
   unsigned int getRegister(int addr); 
   void getStatus(unsigned int ep);
   unsigned long getPhysicalAddress(void) { return phys_addr; };
   unsigned char * getBuffer(void) { return buf; };
   void sync(unsigned int ep);
   bool setSyncArea(unsigned int offset, unsigned int size, unsigned int direction);
   bool setBufferOwner(unsigned int owner);
};

#endif
