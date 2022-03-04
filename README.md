# MPMT FrontEnds for MIDAS DAQ

## Introduction

These MIDAS frontends collect events from multiple MPMT then through MIDAS flow data are stored in MIDAS event files or analyzed with MIDAS analyzer.

MPMT DAQ software is composed by two parts:

- Zynq-ARM event producer
- MPMT events frontend
- HighVoltage frontend
- RunControl frontend
- Sensors frontend


## MIDAS frontend

MIDAS frontend runs on multiprocessor/multicore host. Data sent by event producer is received from ZMQ proxy (router / pull) and fetched by configurable number of threads that extract events from buffer, parse and store them on disk. 

An additional thread is used to synchronize MIDAS run control with remote producers.

| data | port | direction | ZMQ socket |
|------|------|-----------|------------|
|event buffer| 5555 (default) | in/out | proxy(router/push) |
|run control | 4444 | out | publisher |

User can specify the number of MPMT boards collected by MIDAS frontend using this ODB key:

```
/Equipment/MPMT/Settings/Number of MPMT boards	
```

## MIDAS Event data format

A single MPMT producer includes 19 channels (0...18).

Raw events collected by MIDAS frontend are organized with MIDAS event format, each word is 16 bit:

- Event data start with event header:
```
Evid:0001- Mask:0000- Serial:639- Time:0x6200f2f6
```
`Evid`: event id - type of event\
`Mask`: trigger mask\
`Serial`: progressive number (provided by MIDAS)\
`Time`: UNIX timestamp (provided by MIDAS)

Events collected contains `PMT` or `PPS` bank.

- Events with `PMT` bank are organized as follow:

`ID`:  MPMT id\
`CH`:  MPMT channel\
`UX`:  UNIX timestamp (16 bit)\
`TCH`: TDC coarse H (@5ns)\
`TCL`: TDC coarse L (@5ns)\
`TF`:  TDC fine\
`TWC`: Time width coarse\
`TWF`: Time width fine\
`ADC`: ADC value

```
Bank:PMT
   1-> 0x0001 0x0006 0x3320 0x0180 0x9112 0x0006 0x0008 0x0005
       (ID)   (CH)   (UX)   (TCH)  (TCL)  (TF)   (TWC)  (TWF)
   9-> 0x0221
       (ADC)
```

- Events with `PPS` bank are organized as follow:

`ID`:  MPMT id\
`TSH`: Unix timestamp H\
`TSL`: Unix timestamp L\
`DIA`: Diagnostic info (tbd)\
`RMH`: Rate meter H (sum of rate of each channel)\
`RML`: Rate meter L (sum of rate of each channel)\
`DT `: Dead time (%) 


```
Bank:PPS
   1-> 0x0001 0x0037 0x0000 0x0100 0x0001 0x0000 0x0064
       (ID)   (TSH)  (TSL)  (DIA)  (RMH)  (RML)  (DT)
```

