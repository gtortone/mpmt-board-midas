#include <cstdint>

#include "TTotHistogram.h"
#include "TDirectory.h"
#include "TH2D.h"
#include "odbxx.h"

const int numberChannelPerModule = 19;

/// Reset the histograms for this canvas
TTotHistogram::TTotHistogram() {

  SetTabName("ToT");
  SetSubTabName("Channel ToT");
  SetNumberChannelsInGroup(numberChannelPerModule);
  CreateHistograms();
}

void TTotHistogram::CreateHistograms() {

   midas::odb od("/Equipment/MPMT/Settings");

   // read from ODB number of MPMTs
   int nboards = od["Number of MPMT boards"];
   
   // make histograms
   clear();
   
   for(int b=1; b<=nboards; b++) {

      for(int i=0; i<numberChannelPerModule; i++) { // loop over channels
         
         char name[100];
         char title[100];
         sprintf(name,"ToT_B%02i_CH%02i", b,i);
         TH1F *otmp = (TH1F*)gDirectory->Get(name);
         if (otmp) delete otmp;      
         
         sprintf(title,"Time over threshold histogram board %i channel %i" , b, i);	
         
         TH1F *tmp = new TH1F(name, title, 500, 0, 499);
         tmp->SetXTitle("ns");
         
         push_back(tmp);
      }
   }
}

void TTotHistogram::UpdateHistograms(TDataContainer& dataContainer) {

   std::string banks = dataContainer.GetMidasData().GetBankList();

   if(banks.find("PMT") != std::string::npos) {

      const uint16_t channel = dataContainer.GetEventData<TGenericData>("PMT")->GetData16()[1];
      const uint16_t board = dataContainer.GetEventData<TGenericData>("PMT")->GetData16()[0];
      const uint16_t twc = dataContainer.GetEventData<TGenericData>("PMT")->GetData16()[6];
      const uint16_t twf = dataContainer.GetEventData<TGenericData>("PMT")->GetData16()[7];
      const uint16_t tf = dataContainer.GetEventData<TGenericData>("PMT")->GetData16()[5];

      float tot = (5 * twc) - float(5/18 * twf) + float(5/18 * tf);

      GetHistogram(( (board-1) * numberChannelPerModule) + channel)->Fill(tot);
   }
}
