# MPMT FrontEnd for MIDAS DAQ

## Index
[Zynq-ARM event producer](#zynq-arm-event-producer)\
[MIDAS Frontend](#midas-frontend)\
[MIDAS Event data format](#midas-event-data-format)

## Introduction

This MIDAS frontend collects events from multiple MPMT then through MIDAS flow data are stored in MIDAS event files or analyzed with MIDAS analyzer.

MPMT DAQ software is composed by two parts:

- Zynq-ARM event producer
- MIDAS frontend

## Zynq-ARM event producer

Event producer runs on embedded ARM on Zynq FPGA. It uses udmabuf (https://github.com/ikwzm/udmabuf) to transfer data from FPGA to RAM and ZMQ (https://github.com/zeromq) to send data through network.

Due to limited performance of Zynq-ARM data is not parsed and transferred directly to MIDAS frontend. Two threads provide decoupling of data fetching loop from RAM and network data sending and a separate thread receives run control commands (start/stop) through a ZMQ socket from MIDAS frontend.

Data sent to MIDAS frontend is composed by id of MPMT followed by fixed size buffer configured on FPGA.

| data | port | direction | ZMQ socket |
|------|------|-----------|------------|
|event buffer| 5555 (default) | out | dealer |
|run control | 4444 | in | subscriber |

### Usage of event producer

Event producer can run in 'local' or 'remote' mode. In local mode no events will be sent to remote MIDAS frontend, while in remote mode `host`, `port` and `id` command line options will be used to setup ZMQ dealer. 

Options `verbose` and `debug` are useful to live dump of events and reader/writer threads status.

```
Usage: evproducer-mt [options] 

Optional arguments:
-h --help    	shows help message and exits [default: false]
-v --version 	prints version information and exits [default: false]
--local      	local mode [default: false]
--debug      	enable debug [default: false]
--verbose    	print events on stdout [default: false]
--host       	receiver hostname
--port       	receiver port [default: 5555]
--id         	MPMT id [default: 1]
```

## MIDAS frontend

MIDAS frontend runs on multiprocessor/multicore host. Data sent by event producer is received from ZMQ proxy (router / pull) and fetched by configurable number of threads that extract events from buffer, parse and store them on disk. 

An additional thread is used to synchronize MIDAS run control with remote producers.

| data | port | direction | ZMQ socket |
|------|------|-----------|------------|
|event buffer| 5555 (default) | in/out | proxy(router/push) |
|run control | 4444 | out | publisher |

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

- Each PMT event is included in `PMT` bank and inside a bank data are organized as follow:

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
