#include <iostream>
#include <fmt/core.h>

#include "libudmabuf.h"
#include "argparse.hpp"

int main(int argc, const char **argv) {

   Udmabuf ub;
   unsigned int rxsize = 256;
   unsigned char *buf;
   unsigned short int *bufusint;
   bool verbose = false;

   argparse::ArgumentParser program("evproducer");

   program.add_argument("--verbose")
    .help("print events on stdout")
    .default_value(false)
    .implicit_value(true);
   
   try {
      program.parse_args(argc, argv);
   } catch (const std::runtime_error& err) {
      std::cerr << err.what() << std::endl;
      std::cerr << program;
      return EXIT_FAILURE;
   }

   verbose = program.get<bool>("--verbose");

   if(verbose)
      fmt::print("I: verbose ON\n");

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

   fmt::print("I: inizialization done\n");

   if(verbose) {
      ub.getStatus(S2MM_ENDPOINT);
      fmt::print("S2MM.DMACR = 0x{:8X}\n", ub.getRegister(S2MM_CONTROL_REGISTER));    
   }

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

   fmt::print("I: event producer started\n");
   while(true) {

      ub.setRegister(S2MM_LENGTH, rxsize);

      ub.sync(S2MM_ENDPOINT);

      if(verbose)
         ub.getStatus(S2MM_ENDPOINT);      

      buf = ub.getBuffer();

	   bufusint = reinterpret_cast<unsigned short int*>(buf);

      if(verbose) {
	      for(unsigned int i=0; i<rxsize/2; i++)
	         fmt::print("{:04X} ", bufusint[i]);

         fmt::print("\n");
      }
   }

   ub.closeDMABuffer();

   return EXIT_SUCCESS;
}
