#!/usr/bin/env python3

import midas.file_reader

# Open our file
mfile = midas.file_reader.MidasFile("run00410sub0000.mid.lz4")

# We can simply iterate over all events in the file
evnum = 0
for event in mfile:
   if event.header.is_midas_internal_event():
       print("Saw a special event")
       continue
   
   event.dump()

   print(f"+++ Event: evid {event.header.event_id}  mask {event.header.trigger_mask}") 

   for name, content in event.banks.items():
      print(f'BANK: {name} DATA: {content.data}')

   # stop events dump at 20 events
   if evnum == 20:
         break

   evnum += 1

print("New loop...")

# We can iterate on all events and lookup for a specific bank name
mfile.jump_to_start()
for event in mfile:
   bank_sens = event.get_bank("BPMT")
   if bank_sens is not None:
      print(f'data: {bank_sens.data}')

