## MPMT events frontend

MPMT events frontend runs on multiprocessor/multicore host. Data sent by event producer is received from ZMQ proxy (router / pull) and fetched by configurable number of threads that extract events from buffer, parse and store them on disk. 

An additional thread is used to synchronize MIDAS run control with remote producers.

| data | port | direction | ZMQ socket |
|------|------|-----------|------------|
|event buffer| 5555 (default) | in/out | proxy(router/push) |
|run control | 4444 | out | publisher |

### ODB settings

| key | type | description | 
|------|------|-----------|
|/Equipment/MPMT/Settings/Number of MPMT boards|int|number of MPMT boards collected by MIDAS frontend|

### Event data

#### Event header
`Event id`: 1\
`Mask`: MPMT id\
`Bank name`: `BPMT`, `BPPS`

#### Bank format

A single MPMT producer includes 19 channels (0...18).

Events collected contain `BPMT` or `BPPS` bank.

- Events with `BPMT` bank are organized as follow:

`CH`:  MPMT channel\
`UX`:  UNIX timestamp (16 bit)\
`TCH`: TDC coarse H (@5ns)\
`TCL`: TDC coarse L (@5ns)\
`TF`:  TDC fine\
`TWC`: Time width coarse\
`TWF`: Time width fine\
`ADC`: ADC value

```
Bank:BPMT
   1-> 0x0006 0x3320 0x0180 0x9112 0x0006 0x0008 0x0005 0x0221
       (CH)   (UX)   (TCH)  (TCL)  (TF)   (TWC)  (TWF)   (ADC)
```

- Events with `BPPS` bank are organized as follow:

`TSH`: Unix timestamp H\
`TSL`: Unix timestamp L\
`DIA`: Diagnostic info (tbd)\
`RMH`: Rate meter H (sum of rate of each channel)\
`RML`: Rate meter L (sum of rate of each channel)\
`DT `: Dead time (%) 


```
Bank:BPPS
   1-> 0x0037 0x0000 0x0100 0x0001 0x0000 0x0064
       (TSH)  (TSL)  (DIA)  (RMH)  (RML)  (DT)
```
