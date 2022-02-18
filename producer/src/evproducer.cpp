#include <iostream>
#include <thread>
#include <unistd.h>  // usleep
#include <fmt/core.h>
#include <zmq_addon.hpp>

#include "dmactrl.h"
#include "dmabuffer.h"
#include "argparse.hpp"

#define AXI_DMA_BASEADDR      0x40400000
#define DESC_BASEADDR         0x40000000
#define NDESC                 8              // only for SG mode
#define UDMABUF_NAME          "udmabuf0"

// command line arguments
bool debug = false;
bool verbose = false;
bool local = false;
std::string host;
int port;
int mpmtid;
int size;
std::string mode;

zmq::context_t ctx;
std::string run_state;

auto control = [](std::string thread_id) {

   zmq::socket_t sock(ctx, zmq::socket_type::sub);
   const std::string url = fmt::format("tcp://{}:4444", host);
   sock.connect(url);
   sock.set(zmq::sockopt::subscribe, "control");

   fmt::print("I: control thread subscribed to {}\n", url);

   while(true) {

      zmq::message_t topic;
      zmq::message_t payload;

      sock.recv(topic);
      sock.recv(payload);

      if(payload.to_string_view() == "start")
         run_state = "running";
      else if(payload.to_string_view() == "stop")
         run_state = "stopped";

      fmt::print("I: {}\n", payload.to_string_view());

      usleep(500000);
   }
};

int main(int argc, const char **argv) {

   argparse::ArgumentParser program("evproducer-mt");

   // START parsing command line options

   program.add_argument("--local")
    .default_value(false)
    .implicit_value(true)
    .help("local mode");

   program.add_argument("--debug")
    .default_value(false)
    .implicit_value(true)
    .help("enable debug");

   program.add_argument("--verbose")
    .default_value(false)
    .implicit_value(true)
    .help("print events on stdout");

   program.add_argument("--host")
    .help("receiver hostname");

   program.add_argument("--port")
    .default_value(5555)
    .help("receiver port");

   program.add_argument("--id")
    .help("MPMT id")
    .default_value(1)
    .scan<'d', int>();

   program.add_argument("--size")
    .help("DMA block size")
    .default_value(32768)
    .scan<'d', int>();

   try {
      program.parse_args(argc, argv);
   } catch (const std::runtime_error& err) {
      std::cerr << err.what() << std::endl;
      std::cerr << program;
      return EXIT_FAILURE;
   }

   if(program.get<bool>("--local")) {
      mode = "local";
   } else if(program.present("--host")) {
      host = program.get<std::string>("--host");
      port = program.get<int>("--port");
      mpmtid = program.get<int>("--id");
      mode = "remote";
   } else {
      std::cerr << "E: specify local or host/id options" << std::endl;
      return EXIT_FAILURE;
   }

   size = program.get<int>("--size");
   debug = program.get<bool>("--debug");
   verbose = program.get<bool>("--verbose");

   if(verbose)
      fmt::print("I: verbose ON\n");

   // END parsing command line options

   DMACtrl dmac(AXI_DMA_BASEADDR);
   DMABuffer dbuf;

   zmq::socket_t sock(ctx, zmq::socket_type::dealer);
   unsigned short int *bufusint;

   // ZMQ socket
   if(mode == "remote") {
      const std::string url = fmt::format("tcp://{}:{}", host, port);
      sock.set(zmq::sockopt::routing_id, std::to_string(mpmtid));
      /* queue messages only to completed connections */
      sock.set(zmq::sockopt::immediate, 1);
      /* set linger period for socket shutdown - 0 no linger period */
      sock.set(zmq::sockopt::linger, 0);
      sock.connect(url);
   }

   // open and initialize udmabuf
   if(!dbuf.open(UDMABUF_NAME, true)) {
      fmt::print("E: error opening /dev/{}\n", UDMABUF_NAME);
      return EXIT_FAILURE;
   }
   memset(dbuf.buf, 0, dbuf.size());

   // local buffer pointer
   bufusint = reinterpret_cast<unsigned short int*>(dbuf.buf);

   // set DMA coherency mode
   if(!dbuf.setSyncMode(7)) {
      std::cout << "E: udmabuf sync mode error" << std::endl;
      return EXIT_FAILURE;
   }

   fmt::print("I: initialization done\n");

   // set DMA channel RX (S2MM)
   dmac.setChannel(DMACtrl::Channel::S2MM);

   dmac.reset();
   dmac.halt();

   if(dmac.isSG()) {
      dmac.initSG(DESC_BASEADDR, NDESC, size, dbuf.getPhysicalAddress());
      if(debug)
         dmac.dumpSGDescTable();
   } else {
      dmac.initDirect(size, dbuf.getPhysicalAddress()); 
   }

   if(verbose) 
      dmac.getStatus();

   std::thread th0;
   if(mode == "remote") {
      th0 = std::thread(control, "control");
   } else run_state = "running";

   // main loop

   while(true) {

      if(run_state == "running") {

         dmac.run();
            
         while(!dmac.isIdle()) {

            if(dmac.rx()) {      // no timeout

               if(verbose) {
                  for(int i=0; i<size/2; i++)
                     fmt::print("{:04X} ", bufusint[i]);
                  fmt::print("\n");
               }

               // transfer BD with message copy
               zmq::const_buffer buf = zmq::buffer(bufusint + dmac.getBlockOffset()/2, dmac.getBlockSize());
               zmq::send_result_t rc = sock.send(buf, zmq::send_flags::dontwait);

               if(rc) {
                  // send successfull
               } 

               if(debug) {
                  fmt::print("DMA transfer completed - offset: 0x{:04X}  size: 0x{:04X}\n", \
                     dmac.getBlockOffset(), dmac.getBlockSize());
               }
            }
         }

         if(debug) {
            fmt::print("+++ Transfer completed\n");
            dmac.getStatus();
         }

      } else usleep(50000);
   }

   if(mode == "remote")
      th0.join();

   dbuf.close();

   return EXIT_SUCCESS;
}
