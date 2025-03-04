## RunControl frontend

This MIDAS frontend provides data from Run Control registers.

### ODB settings

| key | type | description | 
|------|------|-----------|
|```Board startup mode```|string[19]|Set board startup mode (fw, bl)|
|```Enable ADC sampling	```|int|Enable ADC acquisition for channel index|
|```Power enable```|int|Power channel index|
|```Overcurrent```|int|Overcurrent on channel index|
|```Clock A OK```|bool|Reference clock A status ok|
|```Clock A lost```|bool|Reference clock A lost|
|```Clock A found```|bool|Reference clock A found|
|```Clock B OK```|bool|Reference clock B status ok|
|```Clock B lost```|bool|Reference clock B lost|
|```Clock B found```|bool|Reference clock B found|
|```Clock A-B auto select```|int|Automatic selection of reference clock|
|```Reference clock A-B select```|int|Manual selection of reference clock (0=A, 1=B)|
|```Reference clock A-B select```|int|Reference clock multiplexer status (0=A, 1=B)|
|```Clock int-ext auto select```|int|Automatic selection of int/ext reference clock|
|```Clock int-ext select```|int|Manual selection of int/ext reference clock (0=int, 1=ext)|
|```Clock int-ext mux status```|int|Int/ext clock multiplexer status (0=int, 1=ext)|
|```PLL locked```|bool|200 MHz PLL locked|
|```PLL reset```|bool|Reset flag for PLL not locked|
|```Clock fail```|bool|Clock failure|
|```PPS OK```|bool|PPS received on reference clock line|
|```Unix timestamp aligned```|bool|Unix timestamp and PPS counter aligned|
|```PPS counter```|int|PPS counter|
|```Unix timestamp```|int|Unix timestamp|
|```Enable PPS event```|bool|Enable generation of PPS event|
|```Enable ADC calibration```|bool|Start ADC calibration|
|```Peak delay```|int|Peak delay|
|```Dark delay```|int|Dark delay|
|```Pulser period```|int|Pulser period|
|```Dead time```|int|Dead time (0=100%, 48828=0%)|
|```Channel ratemeter```|int[19]|Events rate for channel index|


### Event data

#### Event header

`Event id`: 2\
`Mask`: MPMT id\
`Bank name`: `RCCH`, `RCGL`

#### Bank format

- Events within `RCCH` bank are organized as follow:

`ADC`: ADC sampling mask\
`POW`: Power status mask\
`OC`: Overcurrent flags mask\
`RM0` - `RM18`: Channel ratemeter channel 0...18
```
Bank:RCCH
   1->    0        1        1    65535   ...       0
      (ADC)    (POW)     (OC)    (RM0)        (RM18)
```

- Events within `RCGL` bank are organized as follow:

`CLK`: Clock diagnostic bits (register 0xC)\
`PPS`: PPS counter\
`UX`: Unix timestamp\
`EPE`: PPS event enabled\
`ACE`: ADC calibration enabled\
`PDL`: Peak delay\
`DDL`: Dark delay\
`PP`: Pulser period\
`DT`: Dead time

```
Bank:RCGL
   1->     7602    21095     1234        1        0       24      240       10
          (CLK)    (PPS)     (UX)    (EPE)    (ACE)    (PDL)    (DDL)     (PP)
   9->        0
           (DT)
```

