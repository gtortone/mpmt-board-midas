#!/usr/bin/env python3

import sys
import copy
import time
import mmap
import midas
import midas.frontend
import midas.event
sys.path.append('/opt/mpmt-board-cli/highvoltage')
from hvmodbus import HVModbus
import conf

class HighVoltage(midas.frontend.EquipmentBase):

   class HighVoltageParams():
      port: str
      host: str
      mode: str

   def __init__(self, client):

      if(midas.frontend.frontend_index == -1):
         client.msg("set frontend index with -i option", is_error=True)
         sys.exit(-1)

      equip_name = "MPMT-HighVoltage" + str(midas.frontend.frontend_index).zfill(2)

      default_common = midas.frontend.InitialEquipmentCommon()
      default_common.equip_type = midas.EQ_PERIODIC
      default_common.buffer_name = "SYSTEM"
      default_common.trigger_mask = 0
      default_common.event_id = 3
      default_common.period_ms = 2000
      default_common.read_when = midas.RO_ALWAYS
      default_common.log_history = 2      # history is enabled, data generated with period_ms frequency

      midas.frontend.EquipmentBase.__init__(self, client, equip_name, default_common, conf.default_settings)

      self.set_status("Initializing...", "yellowLight")

      # open memory mapped device for run control
      try:
         self.fid = open('/dev/uio0', 'r+b', 0)
      except:
         client.msg("UIO device /dev/uio0 not found", is_error=True)
         sys.exit(-1)  

      mem = mmap.mmap(self.fid.fileno(), 65536)
      mv = memoryview(mem)
      self.regs = mv.cast('I')

      self.param = self.HighVoltageParams()
      # by default HV frontend in TCP mode works only on localhost mbusd
      self.param.host = "localhost"
      self.param.port = self.settings["Port device"]
      if self.settings["RTU mode"] == False:
         self.param.mode = "tcp"
      else:
         self.param.mode = "rtu"

      # main hv modbus object
      self.hv = HVModbus(self.param)
 
      # set online HV modules
      self.probe_in_progress = False
      self.probeHV()

      # initialize registers map
      conf.configRegisters(self.odb_settings_dir)
      self.regMap = conf.registers

      # initialize set functions
      self.regMap[f'{self.odb_settings_dir}/Vset']["func"] = self.hv.setVoltageSet
      self.regMap[f'{self.odb_settings_dir}/Rate up']["func"] = self.hv.setRateRampup
      self.regMap[f'{self.odb_settings_dir}/Rate down']["func"] = self.hv.setRateRampdown
      self.regMap[f'{self.odb_settings_dir}/Limit V']["func"] = self.hv.setLimitVoltage
      self.regMap[f'{self.odb_settings_dir}/Limit I']["func"] = self.hv.setLimitCurrent
      self.regMap[f'{self.odb_settings_dir}/Limit T']["func"] = self.hv.setLimitTemperature
      self.regMap[f'{self.odb_settings_dir}/Trip time']["func"] = self.hv.setLimitTriptime
      self.regMap[f'{self.odb_settings_dir}/Trigger threshold']["func"] = self.hv.setThreshold

      # initialize ODB watchers
      client.odb_watch(f'{self.odb_settings_dir}/Power command', self.watchPowerCommand, pass_changed_value_only=True)
      client.odb_watch(f'{self.odb_settings_dir}/Probe modules', self.watchProbeCommand, pass_changed_value_only=True)

      self.updateODB(update_rw_settings=True)

      self.set_status("Initialized")

   def readRegister(self, offset):
      return self.regs[offset]

   def writeRegister(self, offset, value):
      self.regs[offset] = value

   def watchProbeCommand(self, client, path, idx, value):
      if self.probe_in_progress:
         return
      if value == True:
         self.client.msg(f'HV channel probing started')
         self.probeHV()
         self.client.msg(f'HV channel probing finished')
      self.client.odb_set(f'{self.odb_settings_dir}/Probe modules', False)

   def watchPowerCommand(self, client, path, idx, cmd):
      if self.probe_in_progress:
         return
      cmd = str.lower(cmd)
      addr = idx+1
      if cmd == 'none' or idx == -1:
         return
      if cmd == 'on':
         try:
            self.hv.powerOn(addr)
         except:
            self.client.msg(f'Error sending power on to HV module {addr}', is_error=True)
      elif cmd == 'off':
         try:
            self.hv.powerOff(addr)
         except:
            self.client.msg(f'Error sending power off to HV module {addr}', is_error=True)
      elif cmd == 'reset':
         try:
            self.hv.reset(addr)
         except:
            self.client.msg(f'Error sending reset to HV module {addr}', is_error=True)
      else: self.client.msg(f"Unknown command {cmd} for HV module {addr}", is_error=True)

      # reset power command
      self.client.odb_set(f'{self.odb_settings_dir}/Power command[{idx}]', 'none')

   def probeHV(self):
      self.probe_in_progress = True

      # power on all HV modules and turn off ADC enable to prevent bootloader
      self.writeRegister(0, 0)
      value = 1
      for i in range(0,19):
         self.writeRegister(1, value)
         value = value | (value << 1)
         time.sleep(0.1)

      l = [False] * 19
      mask = 0
      for addr in range(1,20):
         found = self.hv.probe(addr)
         if found:
            l[addr-1] = True
            mask += 2 ** (addr-1)
      self.client.odb_set(f'{self.odb_settings_dir}/Online', l)

      # apply online mask to Power Enable register
      value = 1
      for i in range(0,19):
         self.writeRegister(1, mask & value)
         value = value | (value << 1)
         time.sleep(0.1)

      self.probe_in_progress = False
   #
   # update ODB keys from HV Modbus registers
   #
   def updateODB(self, update_rw_settings=False):
      if self.probe_in_progress:
         return
      settings = copy.deepcopy(conf.scratch_ro_settings)
      if update_rw_settings is True:    # update read-only and read-write settings
        settings.update(copy.deepcopy(conf.scratch_rw_settings))
      hvOnline = self.settings['Online']
      #hvPower = self.client.odb_get(f'{self.odb_power_enable}')
      hvPower = self.readRegister(1)
      for addr in range(1,20):
         self.client.communicate(100)
         # check if HV module is probed and powered 
         if hvOnline[addr-1] and (hvPower & (1<<(addr-1)) > 0):
            comerr = False
            try:
               monData = self.hv.readMonRegisters(addr)
            except:
               comerr = True
               if self.settings["Report Modbus errors"] == True:
                  self.client.msg(f"HV Modbus communication error on address {addr}", is_error=True)
            
            self.client.communicate(100)
            settings["Status"][addr-1] = monData['status'] if not comerr else self.settings["Status"][addr-1]
            settings["V"][addr-1] = monData['V'] if not comerr else self.settings["V"][addr-1]
            settings["I"][addr-1] = monData['I'] if not comerr else self.settings["I"][addr-1]
            settings["T"][addr-1] = monData['T'] if not comerr else self.settings["T"][addr-1]
            settings["Alarm"][addr-1] = monData['alarm'] if not comerr else self.settings["Alarm"][addr-1]
            if update_rw_settings is True: # include read-write settings also
               settings["Vset"][addr-1] = monData['Vset'] if not comerr else self.settings["Vset"][addr-1]
               settings["Rate up"][addr-1] = monData['rateUP'] if not comerr else self.settings["Rate up"][addr-1]
               settings["Rate down"][addr-1] = monData['rateDN'] if not comerr else self.settings["Rate down"][addr-1]
               settings["Limit V"][addr-1] = monData['limitV'] if not comerr else self.settings["Limit V"][addr-1]
               settings["Limit I"][addr-1] = monData['limitI'] if not comerr else self.settings["Limit I"][addr-1]
               settings["Limit T"][addr-1] = monData['limitT'] if not comerr else self.settings["Limit T"][addr-1]
               settings["Trip time"][addr-1] = monData['limitTRIP'] if not comerr else self.settings["Trip time"][addr-1]
               settings["Trigger threshold"][addr-1] = monData['threshold'] if not comerr else self.settings["Trigger threshold"][addr-1]
            self.client.communicate(100)

      self.client.odb_set(f'{self.odb_settings_dir}', settings, remove_unspecified_keys=False)

   #
   # update Modbus registers from ODB keys changed by user
   #
   def detailed_settings_changed_func(self, path, idx, new_value):
      if self.probe_in_progress:
         return
      if path == f'{self.odb_settings_dir}/Port device':
         return
      if path == f'{self.odb_settings_dir}/Report Modbus errors':
         return
      if path == f'{self.odb_settings_dir}/Power command':
         return
      if path == f'{self.odb_settings_dir}/Online':
         return
      if path == f'{self.odb_settings_dir}/Probe modules':
         return
      if path == f'{self.odb_settings_dir}/Grid display':
         return
      if idx == -1 or self.regMap[path]["mode"] != "RW":     # whole array assigned to ODB key or read-only register
         return
      if idx is not None:  # array element is changed
         addr = idx+1
         if not self.settings["Online"][idx]:
            self.client.msg(f"HV module {addr} is offline", is_error=True)
            return
         # module is online and register is read-write, update register value
         #print(f'{path} {idx} {new_value}')
         try:
            self.regMap[path]["func"](new_value, addr)
         except:
            self.client.msg(f"Error writing to HV module {addr}", is_error=True)
            # request update of all registers to prevent stale values in ODB
            self.updateODB(update_rw_settings=True)

   def readout_func(self):
      self.updateODB()
      event = midas.event.Event()
      event.header.trigger_mask = midas.frontend.frontend_index

      hvOnline = self.settings['Online']
      hvPower = self.readRegister(1)
      for idx in range(0,19):
         # check if HV module is probed and powered
         if hvOnline[idx] and (hvPower & (1<<idx) > 0):
            data = []
            data.append(self.settings["Status"][idx])
            data.append(self.settings["V"][idx])
            data.append(self.settings["I"][idx])
            data.append(self.settings["T"][idx])
            data.append(self.settings["Alarm"][idx])
            data.append(self.settings["Vset"][idx])
            data.append(self.settings["Rate up"][idx])
            data.append(self.settings["Rate down"][idx])
            data.append(self.settings["Limit V"][idx])
            data.append(self.settings["Limit I"][idx])
            data.append(self.settings["Limit T"][idx])
            data.append(self.settings["Trip time"][idx])
            data.append(self.settings["Trigger threshold"][idx])
            
            event.create_bank(f"HV{str(idx).zfill(2)}", midas.TID_FLOAT, data)
      
      return event

class MyFrontend(midas.frontend.FrontendBase):

   def __init__(self):
      midas.frontend.parse_args()
      midas.frontend.FrontendBase.__init__(self, "hvfe" + str(midas.frontend.frontend_index).zfill(2))
      self.add_equipment(HighVoltage(self.client))

   def begin_of_run(self, run_number):
      self.set_all_equipment_status("MPMT-HighVoltage FE running", "greenLight")
      self.client.msg("Frontend has seen start of run number %d" % run_number)
      return midas.status_codes["SUCCESS"]

   def end_of_run(self, run_number):
      self.set_all_equipment_status("MPMT-HighVoltage FE finished", "greenLight")
      self.client.msg("Frontend has seen end of run number %d" % run_number)
      return midas.status_codes["SUCCESS"]

if __name__ == "__main__":
   my_fe = MyFrontend()
   my_fe.run()
