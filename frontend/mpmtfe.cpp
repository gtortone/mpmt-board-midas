#include <stdio.h>
#include <zmq.hpp>
#include <iostream>
#include <valarray>
#include <exception>
#include <map>
#include <fmt/core.h>
#include <zmq_addon.hpp>

#include "midas.h"
#include "odbxx.h"
#include "msystem.h"
#include "mfe.h"
#include "mpmtevent.h"
#include "socketmonitor.h"

/*-- Globals -------------------------------------------------------*/

/* The frontend name (client name) as seen by other MIDAS clients   */
const char *frontend_name = "MPMT-fe";
/* The frontend file name, don't change it */
const char *frontend_file_name = __FILE__;

/* frontend_loop is called periodically if this variable is TRUE    */
BOOL frontend_call_loop = FALSE;

/* a frontend status page is displayed with this frequency in ms */
INT display_period = 0;

/* maximum event size produced by this frontend */
INT max_event_size = 100000;

/* maximum event size for fragmented events (EQ_FRAGMENTED) */
INT max_event_size_frag = 5 * 1024 * 1024;

/* buffer size to hold events */
INT event_buffer_size = 100 * 1000000;    // 100 MB

#define NUM_THREADS	2

MUTEX_T *odbmutex = NULL;

struct _pdata {
   int index;
};

struct _pdata pdata[NUM_THREADS];

zmq::context_t context;

// ODB for data
midas::odb od;

/*-- Function declarations -----------------------------------------*/

INT proxy_thread(void *);
INT monitor_thread(void *);
INT trigger_thread(void *);
void equip_data_init(void);

/*-- Equipment list ------------------------------------------------*/

BOOL equipment_common_overwrite = TRUE;

EQUIPMENT equipment[] = {
      {"MPMT%02d-data",  /* equipment name */
      {  
         1, 0,                   /* event ID, trigger mask */
         "SYSTEM",               /* event buffer */
         EQ_USER,                /* equipment type */
         0,                      /* event source (not used) */
         "MIDAS",                /* format */
         TRUE,                   /* enabled */
         RO_RUNNING,             /* read only when running */
         500,                    /* poll for 500ms */
         0,                      /* stop run after this event limit */
         0,                      /* number of sub events */
         0,                      /* don't log history */
         "", "", "",},
         NULL,                   /* readout routine */
      },
    {""}
};

/* ZMQ proxy thread: frontend(ROUTER) - backend(PUSH) */

INT proxy_thread(void *param) {

   zmq::socket_t frontend(context, zmq::socket_type::router);
   frontend.bind("tcp://0.0.0.0:5555");

   zmq::socket_t backend(context, zmq::socket_type::push);
   backend.bind("inproc://events");

   while (!readout_enabled())
      ss_sleep(1000);
   printf("ZMQ proxy start...\n");

   zmq::proxy(frontend, backend, zmq::socket_ref());

   return 0;
}

INT monitor_thread(void *param) {

   zmq::socket_t control(context, zmq::socket_type::pub);
   socketMonitor mon;
   INT cur_state = run_state;
   std::string cmd;

   /* create ZMQ control socket */
   control.bind("tcp://0.0.0.0:4444");

   /* initialize ZMQ monitor to handle join of new nodes */
   mon.init(control, "inproc://conmon");

   while(true) {

      if(mon.check_event(100)) {

         if(mon.eventID == ZMQ_EVENT_ACCEPTED) {
            ss_sleep(1000);      // wait for endpoint initialization
            cmd = (run_state == STATE_RUNNING)?"start":"stop";
            zmq::message_t topic(std::string("control"));
            control.send(topic, zmq::send_flags::sndmore);
            zmq::message_t payload(cmd);
            control.send(payload, zmq::send_flags::none);
            mon.eventID = 0;
         }
      }

      if(run_state != cur_state) {

         cmd = (run_state == STATE_RUNNING)?"start":"stop";
         zmq::message_t topic(std::string("control"));
         control.send(topic, zmq::send_flags::sndmore);
         zmq::message_t payload(cmd);
         control.send(payload, zmq::send_flags::none);
         cur_state = run_state;
      }
   }
}

/* DATA equipment init */

void equip_data_init(void) {

   std::string odb_base = std::string("/Equipment/") + std::string(equipment[0].name);

   /* create ZMQ proxy thread */
   printf("Create ZMQ proxy thread...\n");
   ss_thread_create(proxy_thread, NULL);

   /* create ZMQ monitor thread */
   printf("Create ZMQ monitor thread...\n");
   ss_thread_create(monitor_thread, NULL);

   od.connect(odb_base);

   ss_mutex_create(&odbmutex, false);

   for (int i=0; i<NUM_THREADS; i++) {
      
      pdata[i].index = i;

      /* create a ring buffer for each thread */
      create_event_rb(i);

      /* create readout thread */
      ss_thread_create(trigger_thread, &pdata[i]);
   }
}

/*-- Frontend Init -------------------------------------------------*/

INT frontend_init() {
   
   int feIndex = get_frontend_index();
   if(feIndex < 0){
      cm_msg(MERROR,"Init", "Must specify the frontend index (ie use -i <n> command line option)");
      return FE_ERR_HW;
   }

   set_equipment_status(equipment[0].name, "Initialized", "#ffff00");

   equip_data_init();

   if(run_state == STATE_RUNNING) 
      set_equipment_status(equipment[0].name, "Started run", "#00ff00");

   return SUCCESS;
}

/*-- Frontend Exit -------------------------------------------------*/

INT frontend_exit() {

   stop_readout_threads();

   return SUCCESS;
}

/*-- Begin of Run --------------------------------------------------*/

INT begin_of_run(INT run_number, char *error) {

   set_equipment_status(equipment[0].name, "Started run", "#00ff00");

   return SUCCESS;
}

/*-- End of Run ----------------------------------------------------*/

INT end_of_run(INT run_number, char *error) {

   set_equipment_status(equipment[0].name, "Ended run", "#00ff00");

   return SUCCESS;
}

/*-- Pause Run -----------------------------------------------------*/

INT pause_run(INT run_number, char *error) {

   set_equipment_status(equipment[0].name, "Paused run", "#ffff00");

   return SUCCESS;
}

/*-- Resume Run ----------------------------------------------------*/

INT resume_run(INT run_number, char *error) {

   set_equipment_status(equipment[0].name, "Started run", "#00ff00");

   return SUCCESS;
}

/*-- Frontend Loop -------------------------------------------------*/

INT frontend_loop() {

   /* if frontend_call_loop is true, this routine gets called when
      the frontend is idle or once between every event */
   return SUCCESS;
}

/*-- Trigger event routines ----------------------------------------*/

INT poll_event(INT source, INT count, BOOL test) {

   /* Polling is not used */
   return 0;
}

/*-- Interrupt configuration ---------------------------------------*/

INT interrupt_configure(INT cmd, INT source, POINTER_T adr) {

   /* Interrupts are not used */
   return SUCCESS;
}

/*-- Event readout -------------------------------------------------*/

INT trigger_thread(void *param) {

   EVENT_HEADER *pevent;
   WORD *pbank, *pbody;
   int  index, status;
   INT rbh;
   MpmtEvent ev;

   struct _pdata *tdata = (struct _pdata *) param;

   zmq::socket_t sock(context, zmq::socket_type::pull);
   sock.connect("inproc://events");

   /* index of this thread */
   index = (int)tdata->index;

   /* tell framework that we are alive */
   signal_readout_thread_active(index, TRUE);
   
   /* Initialize hardware here ... */
   printf("Start readout thread %d\n", index);
   
   /* Obtain ring buffer for inter-thread data exchange */
   rbh = get_event_rbh(index);

   while (is_readout_thread_enabled()) {

      if (!readout_enabled()) {
         // do not produce events when run is stopped
         ss_sleep(10);
         continue;
      }

      std::vector<zmq::message_t> recv_msgs;
      auto res = zmq::recv_multipart(sock, std::back_inserter(recv_msgs));

      if (!res.has_value())
         continue;

      // check once more in case state changed during receive
      if (!is_readout_thread_enabled())
         break;

#ifdef DEBUG
      fmt::print("--- frame received: {} bytes\n", recv_msgs[1].size());
#endif

      size_t i = 0;
      while(i < recv_msgs[1].size()) {

         /* obtain buffer space */
         do {
            status = rb_get_wp(rbh, (void **) &pevent, 0);
            if (status == DB_TIMEOUT)
               ss_sleep(10);
         } while (status != DB_SUCCESS);

         ev.load((unsigned char *) recv_msgs[1].data() + i);
         i += EVENT_BYTELEN;

#ifdef DEBUG
         fmt::print("id: {} - ", recv_msgs[0].to_string());
         ev.print();
#endif

         std::string msg = ev.sanityCheck();
         if(msg != "") {
            cm_msg(MERROR, "fe", "%s", msg.data());
            continue;
         }

         bm_compose_event_threadsafe(pevent, 1, 0, 0, &equipment[0].serial_number);
         pbank = (WORD *)(pevent + 1);

         /* init bank structure */
         bk_init(pbank);

         /* init bank body */
         bk_create(pbank, "PMT", TID_WORD, (void **)&pbody);
         
         /* fill bank body */
         *pbody++ = std::stoi(recv_msgs[0].to_string());    // PMT id
         *pbody++ = ev.getChannel();                        // channel
         // handle channel 31 (0x1F)
         // ...
         *pbody++ = ev.getUnixtime();                       // UNIX time
         unsigned int tdccoarse = ev.getTDCCoarse();        // TDC coarse
         *pbody++ = (tdccoarse & 0xFFFF0000) >> 16;
         *pbody++ = (tdccoarse & 0x0000FFFF);
         *pbody++ = ev.getTDCFine();                        // TDC fine
         *pbody++ = ev.getTimeWidthCoarse();                // Time width coarse
         *pbody++ = ev.getTimeWidthFine();                  // Time width fine
         *pbody++ = ev.getADC();                            // ADC

         /* close bank */
         bk_close(pbank, pbody);

         pevent->data_size = bk_size(pbank);
         
         /* send event to ring buffer */
         rb_increment_wp(rbh, sizeof(EVENT_HEADER) + pevent->data_size);
      
      }  // end while on message.size()

   } // end while
   
   /* tell framework that we are finished */
   signal_readout_thread_active(index, FALSE);
   
   printf("Stop readout thread %d\n", index);

   return 0;
}
