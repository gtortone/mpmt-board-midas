#pragma once

#include <string>
#include "THistogramArrayBase.h"
#include "TSimpleHistogramCanvas.hxx"

class TTotHistogram : public THistogramArrayBase {

public:
   TTotHistogram();

   void UpdateHistograms(TDataContainer& dataContainer);  

   void CreateHistograms();
};
