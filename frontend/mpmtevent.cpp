#include "mpmtevent.h"
#include "fmt/core.h"

/*
   event[0]:                  HEAD(0xBAAB)
   event[1]:                  '11' CH[13.8] UNIXTIME[7.0] 
   event[2]:                  UNIXTIME[15.8] TDC_COARSE[7.0] 
   event[3]:                  '0' TDC_COARSE[14.0] 
   event[4]:                  TDC_COARSE[15.11] TWIDTH_COARSE[10.5] TWIDTH_FINE[4.0]
   event[5]:                  '1000000' TDC_FINE[8.4] ADC[3.0]
   event[6]:                  ADC[15.8] CRC[7.0]
   event[7]:                  TAIL(0xFEEF)
*/

void MpmtEvent::load(unsigned char *data) {
   
   unsigned short int *buf = reinterpret_cast<unsigned short int *>(data);
   event.clear();
   event.shrink_to_fit();
   event = std::vector<unsigned short int>(buf, buf + EVENT_WORDLEN);
}

std::string MpmtEvent::sanityCheck() {

   if(head() != SOE)
      return "Start of Event error";
   else if(tail() != EOE)
      return "End of Event error";
   else if(CRC() != getCRC())
      return "CRC error";

   return "";
}

unsigned char MpmtEvent::CRC(void) {

   unsigned char *buf = reinterpret_cast<unsigned char *>(event.data());
   unsigned short int crc = buf[2];

   for(int i=3; i<EVENT_BYTELEN - 3; i++) {
      if(i == EVENT_BYTELEN - 4)
         continue;
      crc ^= buf[i];
   }

   return(crc);
}

unsigned short int MpmtEvent::getChannel(void) {
   return( (event[1] >> 8) & 0x003F );
}

unsigned short int MpmtEvent::getUnixtime(void) {
   return( ((event[1] << 8) & 0xFF00) + ((event[2] >> 8) & 0x00FF) );
}

unsigned int MpmtEvent::getTDCCoarse(void) {
   return( (((event [2] & 0x00FF) << 20) & 0x0FFFFFFF) + (event[3] << 1) + (event[4] >> 11) );   
}

unsigned short int MpmtEvent::getTDCFine(void) {
   return( (event[5] >> 4) & 0x001F );
}

unsigned short int MpmtEvent::getTimeWidthCoarse(void) {
   return( (event[4] >> 5) & 0x0003F ); 
}

unsigned short int MpmtEvent::getTimeWidthFine(void) {
   return( event[4] & 0x001F );
}

unsigned short int MpmtEvent::getADC(void) {
   return( ((event[5] << 8) & 0x0F00) + ((event[6] >> 8) & 0x00FF) );
}

unsigned short int MpmtEvent::getCRC(void) {
   return( event[6] & 0x00FF );
}

void MpmtEvent::print(void) {

   for(auto &el : event)
       fmt::print("{:04X} ", el);

   fmt::print("\n");
};


