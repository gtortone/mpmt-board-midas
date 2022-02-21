#pragma once

#include <vector>
#include <string>
#include <cstdint>

#define SOE          0xBAAB         // start of event
#define EOE          0xFEEF         // end of event

#define MAX_CHANNEL     18                // channels 0...18
#define EVENT_BYTELEN   16                // 16 bytes
#define EVENT_WORDLEN   EVENT_BYTELEN/2   // 8 word

class MpmtEvent {

private:
   std::vector<uint16_t> event;

public:
   void load(uint8_t *data);

   uint16_t head(void) { return event[0]; };
   uint16_t tail(void) { return event[EVENT_WORDLEN - 1]; };

   std::string sanityCheck(void);
   uint16_t CRC(void);
   void print(void);

   uint16_t getChannel(void);
   uint16_t getUnixtime(void);
   uint32_t getTDCCoarse(void);
   uint16_t getTDCFine(void);
   uint16_t getTimeWidthCoarse(void);
   uint16_t getTimeWidthFine(void);
   uint16_t getADC(void);
   uint16_t getCRC(void);

   uint32_t getPPSUnixtime(void);
   uint16_t getPPSDiagnostic(void);
   uint16_t getPPSDeadtime(void);
   uint32_t getPPSRatemeter(void);
};
