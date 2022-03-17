#!/usr/bin/env python3

import sys
import mmap
import time

REG_PPS = 0x4  # PPS counter (R)
REG_UTS = 0x5  # Unix Timestamp (R/W)

# open memory mapped device
try:
   fid = open('/dev/uio0', 'r+b', 0)
except:
   print("UIO device /dev/uio0 not found")
   sys.exit(-1)

mem = mmap.mmap(fid.fileno(), 65536)
mv = memoryview(mem)
regs = mv.cast('I')

period = 10
timeout = int(time.time()) + 2.5

while True:

   ts = time.time()
   pps = regs[REG_PPS]

   if ts > timeout:

      if(pps != int(ts)):
         regs[REG_UTS] = int(ts)
         print(f"W: {int(ts)}")
         print(f'REG_PPS: {pps}  Unix timestamp: {ts}')

      timeout = ts + int(period)

   time.sleep(0.05)
