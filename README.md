# MPMT FrontEnd for MIDAS DAQ

## Index
[Zynq-ARM event producer](#arm-event-producer)\
[MIDAS Frontend](#midas-frontend)\
[MIDAS Event data format](#midas-data-format)

## Introduction

This MIDAS frontend collects events from multiple MPMT then through MIDAS flow data are stored in MIDAS event files or analyzed with MIDAS analyzer.

MPMT DAQ software is composed by two parts:

- Zynq-ARM event producer
- Midas frontend

## Zynq-ARM event producer

Event producer runs on embedded ARM on Zynq FPGA. It uses udmabuf (https://github.com/ikwzm/udmabuf) to transfer data from FPGA to RAM and ZMQ (https://github.com/zeromq) to send data through network.

Due to limited performance of Zynq-ARM data is not parsed and transferred directly to MIDAS frontend. Two threads provide decoupling of data fetching loop from RAM and network data sending and a separate thread receives run control commands (start/stop) through a ZMQ socket from MIDAS frontend.

Data sent to MIDAS frontend is composed by id of MPMT followed by fixed size buffer configured on FPGA.

| data | port | direction | ZMQ socket |
|------|------|-----------|------------|
|event buffer| 5555 (default) | out | dealer |
|run control | 4444 | in | subscriber |

### Usage of event producer
