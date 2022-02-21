#include <cstdint>

#include "TRawHistogram.h"
#include "TDirectory.h"
#include "TH2D.h"
#include "odbxx.h"

const int numberChannelPerModule = 19;

/// Reset the histograms for this canvas
TRawHistogram::TRawHistogram() {

  SetTabName("Raw");
  SetSubTabName("Channel Raw");
  SetNumberChannelsInGroup(numberChannelPerModule);
  CreateHistograms();
}

void TRawHistogram::CreateHistograms() {

   midas::odb od("/Equipment/MPMT/Settings");

   // read from ODB number of MPMTs
   int nboards = od["Number of MPMT boards"];
   
   // make histograms
   clear();
   
   for(int b=1; b<=nboards; b++) {

      for(int i=0; i<numberChannelPerModule; i++) { // loop over channels
         
         char name[100];
         char title[100];
         sprintf(name,"Raw_B%02i_CH%02i", b,i);
         TH1D *otmp = (TH1D*)gDirectory->Get(name);
         if (otmp) delete otmp;      
         
         sprintf(title,"Raw histogram board %i channel %i" , b, i);	
         
         TH1I *tmp = new TH1I(name, title, 4096, 0, 4095);
         tmp->SetXTitle("ADC value");
         
         push_back(tmp);
      }
   }
}

void TRawHistogram::UpdateHistograms(TDataContainer& dataContainer) {

   std::string banks = dataContainer.GetMidasData().GetBankList();

   if(banks.find("PMT") != std::string::npos) {

      const uint16_t channel = dataContainer.GetEventData<TGenericData>("PMT")->GetData16()[1];
      const uint16_t board = dataContainer.GetEventData<TGenericData>("PMT")->GetData16()[0];
      const uint16_t value = dataContainer.GetEventData<TGenericData>("PMT")->GetData16()[8];

      GetHistogram(( (board-1) * numberChannelPerModule) + channel)->Fill(value);
   }
}
