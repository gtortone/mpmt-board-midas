#!/usr/bin/env python3

import zmq
from time import sleep

context = zmq.Context()
client = context.socket(zmq.ROUTER)
#client.setsockopt(zmq.RCVHWM, 10000)
rh = client.getsockopt(zmq.RCVHWM)
print(f'recv high watermark: {rh}')
client.bind("tcp://*:5555")

i = 0
while True:
   identity = client.recv()
   msg = client.recv()

   print(identity)

   # simulate slow receiver - messages will pile-up on recv queue (1)
   # and after on send queue (2)
   #if i < 30:
   #   sleep(2)

   i += 1
