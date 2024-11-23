#!/usr/bin/env python3

import sys
import copy
import mmap
import time
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

      # regMap contains settings/readback values from FPGA 
      conf.configRegisters(self.odb_settings_dir)
      self.regMap = conf.registers

      self.odb_readback_dir = self.odb_settings_dir.replace("Settings", "Readback")
      self.client.odb_set(self.odb_readback_dir, conf.default_settings)

      self.set_status("Initializing...", "yellowLight")

      self.command_in_progress = False
      self.scanRegisters(init=True)

      client.odb_watch(f"{self.odb_settings_dir}/Board startup mode", self.watchBoardCommand, pass_changed_value_only=True)
  
      self.set_status("Initialized")

   def readRegister(self, offset):
      return self.regs[offset]

   def writeRegister(self, offset, value):
      self.regs[offset] = value

   #
   # update ODB keys from FPGA registers
   #
   def scanRegisters(self, init=False):

      if self.command_in_progress:
         return

      settings = copy.deepcopy(self.settings)
      readback = conf.default_settings
      for k,v in self.regMap.items():

         regval = self.readRegister(v["memaddr"])
         basekey = k.split('/')[-1]
         #print(f"basekey: {basekey} : regval: {regval}")

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

         if init:
            if v["datatype"] == "boolset" or v["datatype"] == "intset":
               for i in range(0, v["count"]):
                  self.client.odb_set(f'{k}[{i}]', v["value"][i])
                  self.client.odb_set(k.replace("Settings", "Readback"), v["value"][i])
            else:
               self.client.odb_set(k, v["value"])
               self.client.odb_set(k.replace("Settings", "Readback"), v["value"])
         else:
            if v["datatype"] == "boolset" or v["datatype"] == "intset":
               for i in range(0, v["count"]):
                  #if v["value"][i] != readback[basekey][i]:
                  self.client.odb_set(f'{k.replace("Settings", "Readback")}[{i}]', v["value"][i])
                  #print(f"scanRegister: set {k}[{i}] to {v['value'][i]}")
            else:
               #if v["value"] != readback[basekey]: 
               self.client.odb_set(k.replace("Settings", "Readback"), v["value"])

   def readout_func(self):
      self.scanRegisters()
      event = midas.event.Event()
      event.header.trigger_mask = midas.frontend.frontend_index

      data = []
      data.append(int(self.settings['Enable ADC sampling']))
      data.append(int(self.settings['Power enable']))
      data.append(int(self.settings['Overcurrent']))
      for idx in range(0,19):
         data.append(int(self.settings['Channel ratemeter'][idx]))

      event.create_bank("RCCH", midas.TID_INT, data)

      data = []
      #data.append(int(self.readRegister(3)))          # clock diagnostic bits
      data.append(int(self.settings['PPS counter']))
      data.append(int(self.settings['Unix timestamp']))
      data.append(int(self.settings['Enable PPS event']))
      data.append(int(self.settings['Enable ADC calibration']))
      data.append(int(self.settings['Pulser period']))
      data.append(int(self.settings['Dead time']))
      
      event.create_bank("RCGL", midas.TID_INT, data)

      return event   

   #
   # watch callback for board startup mode
   #
   def watchBoardCommand(self, client, path, idx, cmd):
      cmd = str.lower(cmd)
      if cmd == 'none' or idx == -1:
         return
      adc = self.readRegister(0)
      power = self.readRegister(1)
      if cmd == "bootloader" or cmd == "bl":
         self.command_in_progress = True
         adc = (1<<idx) | adc
         self.writeRegister(0, adc)
         power = ~(1<<idx) & power
         self.writeRegister(1, power)
         time.sleep(0.5)
         power = (1<<idx) | power
         self.writeRegister(1, power)
         self.command_in_progress = False
      elif cmd == "firmware" or cmd == "fw":
         self.command_in_progress = True
         power = ~(1<<idx) & power
         self.writeRegister(1, power)
         adc = ~(1<<idx) & adc
         self.writeRegister(0, adc)
         time.sleep(0.5)
         power = (1<<idx) | power
         self.writeRegister(1, power)
         self.command_in_progress = False
      # reset board command
      self.client.odb_set(f'{path}[{idx}]', 'none')

   #
   # update FPGA registers from ODB keys changed by user
   #
   def detailed_settings_changed_func(self, path, idx, new_value):
      #print(f'ODB callback: {path}[{idx}] - new value {new_value}')
      if self.command_in_progress:
         return
      if path == f"{self.odb_settings_dir}/Board startup mode":
         return
      # if 'Power enable' register is changed power off changed bits on 'Enable ADC sampling' register
      if path == f"{self.odb_settings_dir}/Power enable":
         prev_adc = self.readRegister(0)
         prev_power = self.readRegister(1)
         self.writeRegister(0, prev_adc & ~(prev_power ^ new_value))
         self.writeRegister(1, new_value)
         return
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
      midas.frontend.parse_args()
      midas.frontend.FrontendBase.__init__(self, "rcfe" + str(midas.frontend.frontend_index).zfill(2))
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
