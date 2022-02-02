#include <iostream>
#include <chrono>
#include <thread>
#include <fmt/core.h>
#include <zmq_addon.hpp>

#include "libudmabuf.h"
#include "argparse.hpp"

using namespace std::literals::chrono_literals;

unsigned int rxsize = 256;
unsigned int wroff = 0;
unsigned int rdoff = 0;
unsigned int bufsize = 0;

// command line arguments
bool debug = false;
bool verbose = false;
std::string host;
int port;

zmq::context_t ctx;

void myfree (void *data, void *hint) {
   // we are working with CMA memory, so we don't need
   // to free buffers here...
   return;
}

auto writer = [](std::string thread_id, Udmabuf ub) {

   bool sleeping = false;

   while(true) {

      // wait if ring buffer is full
      while(wroff == ((rdoff - rxsize) % bufsize)) {
         if(debug) {
            if(!sleeping)
               fmt::print("W: S\n");
            sleeping = true;
            fmt::print(".");
         }
         std::this_thread::sleep_for(100us);
      }

      sleeping = false;

      // S2MM_DA = addr : set destination address for DMA transfer
      ub.setRegister(S2MM_DESTINATION_ADDRESS, ub.getPhysicalAddress() + wroff);

      // S2MM_LENGTH = set buffer size for DMA transfer
      ub.setRegister(S2MM_LENGTH, rxsize);

      // wait for data ready
      ub.sync(S2MM_ENDPOINT, 500us);

      wroff = (wroff + rxsize) % bufsize;

      if(debug)
         fmt::print("W: offset={:d}\n", wroff);

      if(verbose)
         ub.getStatus(S2MM_ENDPOINT);
   }
};

auto reader = [](std::string thread_id, unsigned char *buffer) {

   bool sleeping = false;
   zmq::socket_t sock(ctx, zmq::socket_type::pair);
   const std::string url = fmt::format("tcp://{}:{}", host, port);
   sock.connect(url);

   while(true) {

      // wait if ring buffer is empty
      while(rdoff == wroff) {
         if(debug) {
            if(!sleeping)
               fmt::print("R: S");
            sleeping = true;
            fmt::print(".");
         }
         std::this_thread::sleep_for(100us);
      }

      sleeping = false;

      unsigned short int *bufusint;
      bufusint = reinterpret_cast<unsigned short int*>(buffer + rdoff);

      if(verbose) {
         for(unsigned int i=0; i<rxsize/2; i++)
            fmt::print("{:04X} ", bufusint[i]);
         fmt::print("\n");
      }

      // send event
      zmq::message_t z_out(bufusint, rxsize/2, myfree);
      sock.send(z_out, zmq::send_flags::dontwait);

      rdoff = (rdoff + rxsize) % bufsize;
   
      if(debug)
         fmt::print("R: offset={:d}\n", rdoff);
   }
};

int main(int argc, const char **argv) {

   Udmabuf ub;

   argparse::ArgumentParser program("evproducer");

   program.add_argument("--debug")
    .help("enable debug")
    .default_value(false)
    .implicit_value(true);

   program.add_argument("--verbose")
    .help("print events on stdout")
    .default_value(false)
    .implicit_value(true);

   program.add_argument("--host")
    .help("receiver hostname")
    .default_value(std::string(""))
    .required();
   
   program.add_argument("--port")
    .help("receiver port")
    .default_value(5555)
    .required();

    try {
      program.parse_args(argc, argv);
   } catch (const std::runtime_error& err) {
      std::cerr << err.what() << std::endl;
      std::cerr << program;
      return EXIT_FAILURE;
   }

   debug = program.get<bool>("--debug");
   verbose = program.get<bool>("--verbose");
   host = program.get<std::string>("--host");
   port = program.get<int>("--port");

   if(verbose)
      fmt::print("I: verbose ON\n");

   if(!ub.openUIO("dma")) {
      std::cout << "E: UIO error" << std::endl;
      return EXIT_FAILURE;
   }

   // use CPU cache without O_SYNC flag
   if(!ub.openDMABuffer("udmabuf0", true)) {
      std::cout << "E: udmabuf error" << std::endl;
      return EXIT_FAILURE;
   }

   // set DMA coherency mode
   if(!ub.setSyncMode(7)) {
      std::cout << "E: udmabuf sync mode error" << std::endl;
      return EXIT_FAILURE;
   }

   fmt::print("I: initialization done\n");

   if(verbose) {
      ub.getStatus(S2MM_ENDPOINT);
      fmt::print("S2MM.DMACR = 0x{:8X}\n", ub.getRegister(S2MM_CONTROL_REGISTER));    
   }

   bufsize = ub.getBufferSize();

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

   std::thread th0 = std::thread(writer, "writer", std::move(ub));
   std::thread th1 = std::thread(reader, "reader", ub.getBuffer());

   th0.join();
   th1.join();

   ub.closeDMABuffer();

   return EXIT_SUCCESS;
}
