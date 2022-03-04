## RunControl frontend

This MIDAS frontend provides data from Run Control registers.

### ODB settings

| key | type | description | 
|------|------|-----------|
|```Enable ADC sampling	```|bool[19]|Enable ADC acquisition for channel index|
|```Power enable```|bool[19]|Power channel index|
|```Overcurrent```|bool[19]|Overcurrent on channel index|
|```Clock A OK```|book|Reference clock A status ok|
|```Clock A lost```|book|Reference clock A lost|
|```Clock A found```|book|Reference clock A found|
|```Clock B OK```|book|Reference clock B status ok|
|```Clock B lost```|book|Reference clock B lost|
|```Clock B found```|book|Reference clock B found|
|```Clock A-B auto select```|int|Automatic selection of reference clock|
|```Reference clock A-B select```|int|Manual selection of reference clock (0=A, 1=B)|
|```Reference clock A-B select```|int|Reference clock multiplexer status (0=A, 1=B)|
|```Clock int-ext auto select```|int|Automatic selection of int/ext reference clock|
|```Clock int-ext select```|int|Manual selection of int/ext reference clock (0=int, 1=ext)|
|```Clock int-ext mux status```|int|Int/ext clock multiplexer status (0=int, 1=ext)|
|```PLL locked```|bool|200 MHz PLL locked|
|```PLL reset```|bool|Reset flag for PLL not locked|
|```Clock fail```|bool|Clock failure|
|```PPS OK```|book|PPS received on reference clock line|
|```Unix timestamp aligned```|bool|Unix timestamp and PPS counter aligned|
|```Enable PPS event```|bool|Enable generation of PPS event|
|```Enable ADC calibration```|bool|Start ADC calibration|
|```Peak delay```|int|Peak delay|
|```Dark delay```|int|Dark delay|
|```Pulser period```|int|Pulser period|
|```Dead time```|int|Dead time (0=100%, 48828=0%)|
|```Channel ratemeter```|int[19]|Events rate for channel index|


### Event data

#### Event header

`Event id`: 4\
`Mask`: MPMT id\
`Bank name`: `SENS`
