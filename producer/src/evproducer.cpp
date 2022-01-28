#include <iostream>
#include <fmt/core.h>

#include "libudmabuf.h"
#include "argparse.h"

int main(void) {

   Udmabuf ub;
   unsigned int rxsize = 256;
   unsigned char *buf;

   if(!ub.openUIO("dma")) {
      std::cout << "E: UIO error" << std::endl;
      return EXIT_FAILURE;
   }

   if(!ub.openDMABuffer("udmabuf0", true)) {
      std::cout << "E: udmabuf error" << std::endl;
      return EXIT_FAILURE;
   }

   if(!ub.setSyncArea(0, rxsize, DMA_FROM_DEVICE)) {
      std::cout << "E: setSyncArea error" << std::endl;
      return EXIT_FAILURE;
   }

   if(!ub.setBufferOwner(CPU_OWNER)) {
      std::cout << "E: setBufferOwner error" << std::endl;
      return EXIT_FAILURE;
   }

   ub.getStatus(S2MM_ENDPOINT);

   fmt::print("S2MM.DMACR = 0x{:8X}\n", ub.getRegister(S2MM_CONTROL_REGISTER));    

   // S2MM_DMACR[2] = 1 : reset not in progress - normal operation
   ub.setRegister(S2MM_CONTROL_REGISTER, 4);

   // S2MM_DMACR[0] = 0 : halt dma
   ub.setRegister(S2MM_CONTROL_REGISTER, 0);

   // S2MM_DA = addr : set destination address for DMA transfer
   ub.setRegister(S2MM_DESTINATION_ADDRESS, ub.getPhysicalAddress());

   // S2MM_DMACR[0]  = 1 : run dma
   // S2MM_DMACR[12] = 1 : enable Interrupt on Complete
   // S2MM_DMACR[13] = 1 : enable Delay Interrupt
   // S2MM_DMACR[14] = 1 : enable Error Interrupt
   // S2MM_DMACR[15] = 1 : [reserved] - no effect
   ub.setRegister(S2MM_CONTROL_REGISTER, 0xf001);

   while(true) {

      ub.setRegister(S2MM_LENGTH, rxsize);

      ub.sync(S2MM_ENDPOINT);

      ub.getStatus(S2MM_ENDPOINT);      

      buf = ub.getBuffer();

      unsigned short int *bufusint;

	   bufusint = reinterpret_cast<unsigned short int*>(buf);

	   for(unsigned int i=0; i<rxsize/2; i++)
	      fmt::print("{:04X} ", bufusint[i]);

      fmt::print("\n");
   }

   ub.closeDMABuffer();

   return EXIT_SUCCESS;
}
