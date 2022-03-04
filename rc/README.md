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
`Bank name`: `RCnn`, `RCGL`  (nn: number of channel [0...18])

#### Bank format

- Events within `RCxx` bank are organized as follow:

`ADC`: ADC sampling\
`POW`: Power status\
`OC`: Overcurrent flag\
`RM`: Channel ratemeter

```
Bank:RC15
   1->    0        1        1    65535
      (ADC)    (POW)     (OC)     (RM)
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

