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
   
   uint16_t *buf = reinterpret_cast<uint16_t *>(data);
   event.clear();
   event.shrink_to_fit();
   event = std::vector<uint16_t>(buf, buf + EVENT_WORDLEN);
}

std::string MpmtEvent::sanityCheck() {

   if(head() != SOE)
      return "Start of Event error";
   else if(tail() != EOE)
      return "End of Event error";
   else if(CRC() != getCRC())
      return fmt::format("CRC error: exp({:02X}) calc({:02X}) ev({:04X} {:04X} {:04X} {:04X} {:04X} {:04X} {:04X} {:04X})", \
         getCRC(), CRC(), event[0], event[1], event[2], event[3], event[4], event[5], event[6], event[7]);
   return "";
}

uint16_t MpmtEvent::CRC(void) {

   uint8_t *buf = reinterpret_cast<uint8_t *>(event.data());
   unsigned short int crc = buf[2];

   for(int i=3; i<EVENT_BYTELEN - 2; i++) {
      if(i == EVENT_BYTELEN - 4)
         continue;
      crc ^= buf[i];
   }

   return(crc);
}

uint16_t MpmtEvent::getChannel(void) {
   return( (event[1] >> 8) & 0x003F );
}

/* PMT event */

uint16_t MpmtEvent::getUnixtime(void) {
   return( ((event[1] << 8) & 0xFF00) + ((event[2] >> 8) & 0x00FF) );
}

uint32_t MpmtEvent::getTDCCoarse(void) {
   return( (((event [2] & 0x00FF) << 20) & 0x0FFFFFFF) + (event[3] << 1) + (event[4] >> 11) );   
}

uint16_t MpmtEvent::getTDCFine(void) {
   return( (event[5] >> 4) & 0x001F );
}

uint16_t MpmtEvent::getTimeWidthCoarse(void) {
   return( (event[4] >> 5) & 0x0003F ); 
}

uint16_t MpmtEvent::getTimeWidthFine(void) {
   return( event[4] & 0x001F );
}

uint16_t MpmtEvent::getADC(void) {
   return( ((event[5] << 8) & 0x0F00) + ((event[6] >> 8) & 0x00FF) );
}

uint16_t MpmtEvent::getCRC(void) {
   return( event[6] & 0x00FF );
}

/* PPS event */

uint32_t MpmtEvent::getPPSUnixtime(void) {
   return( (event[2] << 8) + (event[3] >> 23) );   
}

uint16_t MpmtEvent::getPPSDiagnostic(void) {
   // [7:6] CLK
   // [5:0] Diagnostic
   return ( (((event[3] >> 5) & 0x0003) << 7) + ( (event[5] >> 8) & 0x003F) );
}

uint16_t MpmtEvent::getPPSDeadtime(void) {
   uint16_t dt = ( ((event[5] & 0x00FF) << 8) + (event[6] >> 8) );
   return (100 - (dt/48829 * 100));
}

uint32_t MpmtEvent::getPPSRatemeter(void) {
   return ( ( (event[3] & 0x001F) << 11 ) + event[4] );
}

void MpmtEvent::print(void) {

   for(auto &el : event)
       fmt::print("{:04X} ", el);

   fmt::print("\n");
};


