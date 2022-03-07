#!/usr/bin/env python3

import sys
import mmap
import midas
import midas.frontend
import midas.event
import conf

class RunControl(midas.frontend.EquipmentBase):

   def __init__(self, client):

      if(midas.frontend.frontend_index == -1):
         client.msg("set frontend index with -i option", is_error=True)
         sys.exit(-1)

      equip_name = "MPMT-RunControl" + str(midas.frontend.frontend_index).zfill(2)

      default_common = midas.frontend.InitialEquipmentCommon()
      default_common.equip_type = midas.EQ_PERIODIC
      default_common.buffer_name = "SYSTEM"
      default_common.trigger_mask = 0
      default_common.event_id = 2
      default_common.period_ms = 2000
      default_common.read_when = midas.RO_ALWAYS
      default_common.log_history = 2 # history is enabled, data generated with period_ms frequency

      # open memory mapped device
      try:
         self.fid = open('/dev/uio0', 'r+b', 0)
      except:
         client.msg("UIO device /dev/uio0 not found", is_error=True)
         sys.exit(-1)

      mem = mmap.mmap(self.fid.fileno(), 65536)
      mv = memoryview(mem)
      self.regs = mv.cast('I')

      midas.frontend.EquipmentBase.__init__(self, client, equip_name, default_common, conf.default_settings)

      # regMap contains readback values from FPGA 
      conf.configRegisters(self.odb_settings_dir)
      self.regMap = conf.registers

      self.scanRegisters()
      #print(self.regMap)
  
      self.set_status("Initialized")

   def readRegister(self, offset):
      return self.regs[offset]

   def writeRegister(self, offset, value):
      self.regs[offset] = value

   #
   # update ODB keys from FPGA registers
   #
   def scanRegisters(self):
      for k,v in self.regMap.items():

         regval = self.readRegister(v["memaddr"])

         if v["datatype"] == "bitset":       # bitset
            mask = (2 ** v["count"]) - 1
            mask = mask << v["startBit"]
            v["value"] = (regval & mask) >> v["startBit"]
         elif v["datatype"] == "boolset":    # boolset
            l = [False] * v["count"]
            for i in range(0, v["count"]):
               if regval & (1<<i):
                  l[i] = True
               else: l[i] = False
            v["value"] = l
         elif v["datatype"] == "intset":     # integer set
            l = [0] * v["count"]
            for i in range(0, v["count"]):
               regval = self.readRegister(v["memaddr"] + i)
               l[i] = regval
            v["value"] = l
         elif v["datatype"] == "int":        # integer
            v["value"] = regval

         if 'lastvalue' in v:
            # this check is needed for ODB arrays because overwriting elements with same value
            # triggers detailed_settings_changed_func and if there is a write in progress
            # array will be updated with old values
            if v["datatype"] == "boolset" or v["datatype"] == "intset":
               for i in range(0, v["count"]):
                  if v["value"][i] != v["lastvalue"][i]:
                     self.client.odb_set(f'{k}[{i}]', v["value"][i])
            else:
               if (v["value"] != v["lastvalue"]):
                  self.client.odb_set(k, v["value"])
         v["lastvalue"] = v["value"]

   def readout_func(self):
      self.scanRegisters()
      event = midas.event.Event()
      event.header.trigger_mask = midas.frontend.frontend_index

      for idx in range(0,19):
         data = []
         data.append(int(self.settings['Enable ADC sampling'][idx]))
         data.append(int(self.settings['Power enable'][idx]))
         data.append(int(self.settings['Overcurrent'][idx]))
         data.append(int(self.settings['Channel ratemeter'][idx]))

         event.create_bank(f"RC{str(idx).zfill(2)}", midas.TID_INT, data)

      data = []
      data.append(int(self.readRegister(3)))          # clock diagnostic bits
      data.append(int(self.settings['PPS counter']))
      data.append(int(self.settings['Unix timestamp']))
      data.append(int(self.settings['Enable PPS event']))
      data.append(int(self.settings['Enable ADC calibration']))
      data.append(int(self.settings['Peak delay']))
      data.append(int(self.settings['Dark delay']))
      data.append(int(self.settings['Pulser period']))
      data.append(int(self.settings['Dead time']))
      
      event.create_bank("RCGL", midas.TID_INT, data)

      return event

   #
   # update FPGA registers from ODB keys changed by user
   #
   def detailed_settings_changed_func(self, path, idx, new_value):
      if idx == -1 or self.regMap[path]["mode"] != "RW":     # whole array assigned to ODB key or read-only register
         return
      if idx is not None:  # array element is changed
         if self.regMap[path]["datatype"] == "boolset":
            regval = self.readRegister(self.regMap[path]["memaddr"])
            if(new_value == 0):
               regval = ~(1<<idx) & regval
            else:
               regval = (1<<idx) | regval
            self.writeRegister(self.regMap[path]["memaddr"], regval)
         if self.regMap[path]["datatype"] == "intset":
            memaddr = self.regMap[path]["memaddr"] + idx
            self.writeRegister(memaddr, new_value)
      else:                
         if self.regMap[path]["datatype"] == "int":
            self.writeRegister(self.regMap[path]["memaddr"], new_value)
         elif self.regMap[path]["datatype"] == "bitset":
            regval = self.readRegister(self.regMap[path]["memaddr"])
            mask = (2 ** self.regMap[path]["count"]) - 1
            mask = ~(mask << self.regMap[path]["startBit"]) 
            regval = regval & mask     # clear bitset
            regval = regval | (new_value << self.regMap[path]["startBit"])
            self.writeRegister(self.regMap[path]["memaddr"], regval)
            
class MyFrontend(midas.frontend.FrontendBase):

   def __init__(self):
      midas.frontend.FrontendBase.__init__(self, "rcfe")
      self.add_equipment(RunControl(self.client))

   def begin_of_run(self, run_number):
      self.set_all_equipment_status("MPMT-RunControl FE running", "greenLight")
      self.client.msg("Frontend has seen start of run number %d" % run_number)
      return midas.status_codes["SUCCESS"]

   def end_of_run(self, run_number):
      self.set_all_equipment_status("MPMT-RunControl FE finished", "greenLight")
      self.client.msg("Frontend has seen end of run number %d" % run_number)
      return midas.status_codes["SUCCESS"]

if __name__ == "__main__":
   my_fe = MyFrontend()
   my_fe.run()
