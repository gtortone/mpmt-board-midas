#!/usr/bin/env python3

import sys
import mmap
import copy
import midas
import midas.frontend
import midas.event
sys.path.append('/opt/mpmt-board-cli/highvoltage')
from hvmodbus import HVModbus
import conf

class HighVoltage(midas.frontend.EquipmentBase):

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

      # main hv modbus object
      self.hv = HVModbus()
 
      self.port = self.settings["Port device"]
      # set online HV modules
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

      self.updateODB(update_rw_settings=True)

      self.set_status("Initialized")

   def watchPowerCommand(self, client, path, idx, cmd):
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
      l = [False] * 19
      for addr in range(1,20):
         found = self.hv.probe(self.port, addr)
         if found:
            l[addr-1] = True
      self.client.odb_set(f'{self.odb_settings_dir}/Online', l)

   #
   # update ODB keys from HV Modbus registers
   #
   def updateODB(self, update_rw_settings=False):
      settings = copy.deepcopy(conf.scratch_ro_settings)
      if update_rw_settings is True:    # update read-only and read-write settings
        settings.update(copy.deepcopy(conf.scratch_rw_settings))
      # avoid using of self.settings here due to inconsistency first invocation after init
      hvOnline = self.client.odb_get(f'{self.odb_settings_dir}/Online')
      for addr in range(1,20):
         if hvOnline[addr-1]:
            try:
               monData = self.hv.readMonRegisters(addr)
            except:
               if self.settings["Report Modbus errors"] == True:
                  self.client.msg(f"HV Modbus communication error on address {addr}", is_error=True)
            else:
               settings["Status"][addr-1] = monData['status']
               settings["V"][addr-1] = monData['V']
               settings["I"][addr-1] = monData['I']
               settings["T"][addr-1] = monData['T']
               settings["Alarm"][addr-1] = monData['alarm']
               if update_rw_settings is True: # include read-write settings also
                  settings["Vset"][addr-1] = monData['Vset']
                  settings["Rate up"][addr-1] = monData['rateUP']
                  settings["Rate down"][addr-1] = monData['rateDN']
                  settings["Limit V"][addr-1] = monData['limitV']
                  settings["Limit I"][addr-1] = monData['limitI']
                  settings["Limit T"][addr-1] = monData['limitT']
                  settings["Trip time"][addr-1] = monData['limitTRIP']
                  settings["Trigger threshold"][addr-1] = monData['threshold']

      self.client.odb_set(f'{self.odb_settings_dir}', settings, remove_unspecified_keys=False)

   #
   # update Modbus registers from ODB keys changed by user
   #
   def detailed_settings_changed_func(self, path, idx, new_value):
      if path == f'{self.odb_settings_dir}/Port device':
         return
      if path == f'{self.odb_settings_dir}/Report Modbus errors':
         return
      if path == f'{self.odb_settings_dir}/Power command':
         return
      if path == f'{self.odb_settings_dir}/Online':
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
      hvOnline = self.settings['Online']
      for idx in range(0,19):
         if hvOnline[idx]:
            data = []
            data.append(midas.frontend.frontend_index)
            data.append(idx+1)         # modbus address
            data.append(int(self.settings["Status"][idx]))
            data.append(int(self.settings["V"][idx] * 1000))     # mV)
            data.append(int(self.settings["I"][idx] * 1000))     # nA
            data.append(int(self.settings["T"][idx]))
            data.append(int(self.settings["Alarm"][idx]))
            data.append(int(self.settings["Vset"][idx]))
            data.append(int(self.settings["Rate up"][idx]))
            data.append(int(self.settings["Rate down"][idx]))
            data.append(int(self.settings["Limit V"][idx]))
            data.append(int(self.settings["Limit I"][idx]))
            data.append(int(self.settings["Limit T"][idx]))
            data.append(int(self.settings["Trip time"][idx]))
            data.append(int(self.settings["Trigger threshold"][idx]))
            
            event.create_bank(f"HV{str(idx).zfill(2)}", midas.TID_INT, data)
      
      return event

class MyFrontend(midas.frontend.FrontendBase):

   def __init__(self):
      midas.frontend.FrontendBase.__init__(self, "hvfe")
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
