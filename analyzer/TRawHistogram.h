#pragma once

#include <string>
#include "THistogramArrayBase.h"
#include "TSimpleHistogramCanvas.hxx"

class TRawHistogram : public THistogramArrayBase {

public:
   TRawHistogram();

   void UpdateHistograms(TDataContainer& dataContainer);  

   void CreateHistograms();
};
