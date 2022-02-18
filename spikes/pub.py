#!/usr/bin/env python3

import zmq
from time import sleep

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://0.0.0.0:4444")

topic = "control"
payload = "stop"

while(True):

   socket.send_string(topic, flags=zmq.SNDMORE)
   socket.send_string(payload)
   sleep(2)
