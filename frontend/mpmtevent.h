#ifndef MPMTEVENT_H_
#define MPMTEVENT_H_

#include <vector>
#include <string>

#define SOE          0xBAAB         // start of event
#define EOE          0xFEEF         // end of event

#define MAX_CHANNEL     18                // channels 0...18
#define EVENT_BYTELEN   16                // 16 bytes
#define EVENT_WORDLEN   EVENT_BYTELEN/2   // 8 word

class MpmtEvent {

private:
   std::vector<unsigned short int> event;

public:
   void load(unsigned char *data);

   unsigned short int head(void) { return event[0]; };
   unsigned short int tail(void) { return event[EVENT_WORDLEN - 1]; };

   std::string sanityCheck(void);
   unsigned char CRC(void);
   void print(void);

   unsigned short int getChannel(void);
   unsigned short int getUnixtime(void);
   unsigned int getTDCCoarse(void);
   unsigned short int getTDCFine(void);
   unsigned short int getTimeWidthCoarse(void);
   unsigned short int getTimeWidthFine(void);
   unsigned short int getADC(void);
   unsigned short int getCRC(void);
};

#endif
