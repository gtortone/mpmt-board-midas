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

### Notes

- Submodule checkout

```
git submodule update --init
```
