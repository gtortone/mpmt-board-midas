#!/usr/bin/env python3

import sys
import copy
import time
import json
import mmap
import midas
import midas.frontend
import midas.event
sys.path.append('/opt/mpmt-board-cli/highvoltage')
from hvmodbus import HVModbus
import conf
import threading

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

      # HV status
      self.online_channels = [False] * 19
      self.prev_online_channels = [False] * 19
      self.enabled_channels = [False] * 19
      self.adc_channels = [False] * 19

      # threads
      self.mutex = threading.Lock()
      # monitor thread to run updateODB()
      self.mthread = threading.Thread(target=self.monitor, args=(self,))
      # communication thread to spin the wheel of client.communicate()
      self.cthread = threading.Thread(target=self.communicate, args=(self,))
 
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

      self.updateODB(update_rw_settings=True)

      self.set_status("Initialized")

      self.mthread.start()
      self.cthread.start()

      # Register our function.
      client.register_jrpc_callback(self.rpc_handler, True)

   def readRegister(self, offset):
      return self.regs[offset]

   def writeRegister(self, offset, value):
      self.regs[offset] = value

   def monitor(self, this):
      while True:
         this.updateODB()
         time.sleep(2)

   def communicate(self, this):
      while True:
         this.client.communicate(10)

   #
   # update ODB keys from HV Modbus registers
   #
   def updateODB(self, update_rw_settings=False):
      readback = copy.deepcopy(conf.scratch_ro_settings)
      settings = {}

      hv_adc_channels = self.readRegister(0)
      hv_enabled_channels = self.readRegister(1)
      for addr in range(1,20):

         adc = (hv_adc_channels & (1<<(addr-1)) > 0)
         status = (hv_enabled_channels & (1<<(addr-1)) > 0)
         self.adc_channels[addr-1] = adc
         self.enabled_channels[addr-1] = status

         # check if HV channel is online or just powered
         if self.online_channels[addr-1] or status == True:
            comerr = False

            if self.param.mode == "rtu":
               self.mutex.acquire()

            try:
               monData = self.hv.readMonRegisters(addr)
            except:
               comerr = True
               # channel is online and has errors
               if self.online_channels[addr-1] and self.settings["Report Modbus errors"] == True:
                  self.client.msg(f"HV Modbus communication error on channel {addr}", is_error=True)

            if self.param.mode == "rtu":
               self.mutex.release()

            if monData is None or comerr == True:  # skip this update - channel is offline
               self.online_channels[addr-1] = False 
               continue

            self.online_channels[addr-1] = True

            readback["V"][addr-1] = monData['V']
            readback["I"][addr-1] = monData['I']
            readback["T"][addr-1] = monData['T']
            readback["Status"][addr-1] = monData['status']
            readback["Alarm"][addr-1] = monData['alarm']

            new_channel = self.online_channels[addr-1] == True and self.prev_online_channels[addr-1] == False
            if new_channel or update_rw_settings:
               if len(settings.items()) == 0:
                  settings = copy.deepcopy(self.settings)
               settings["Vset"][addr-1] = monData['Vset']
               settings["Rate up"][addr-1] = monData['rateUP']
               settings["Rate down"][addr-1] = monData['rateDN']
               settings["Limit V"][addr-1] = monData['limitV']
               settings["Limit I"][addr-1] = monData['limitI']
               settings["Limit T"][addr-1] = monData['limitT']
               settings["Trip time"][addr-1] = monData['limitTRIP']
               settings["Trigger threshold"][addr-1] = monData['threshold']

      self.prev_online_channels = copy.deepcopy(self.online_channels)
      if len(settings.items()) == 0:
         self.client.odb_set(f'{self.odb_settings_dir}', settings, remove_unspecified_keys=False)
      self.client.odb_set(f'{self.odb_settings_dir.replace("Settings", "Readback")}', readback, remove_unspecified_keys=False)
      self.client.odb_set(f'{self.odb_settings_dir.replace("Settings", "Readback")}/Online', self.online_channels)

   #
   # update Modbus registers from ODB keys changed by user
   #
   def detailed_settings_changed_func(self, path, idx, new_value):
      if path == f'{self.odb_settings_dir}/RTU mode':
         return
      if path == f'{self.odb_settings_dir}/Port device':
         return
      if path == f'{self.odb_settings_dir}/Report Modbus errors':
         return
      if path == f'{self.odb_settings_dir}/Grid display':
         return
 
      if idx == -1 or self.regMap[path]["mode"] != "RW":     # whole array assigned to ODB key or read-only register
         return
      addr = idx+1
      if idx is not None:  # array element is changed
         if not self.online_channels[idx]:
            self.client.msg(f"HV channel {addr} is offline", is_error=True)
            return
         # channel is online and register is read-write, update register value
         #print(f'{path} {idx} {new_value}')
         self.mutex.acquire()
         try:
            self.regMap[path]["func"](int(new_value), addr)
            #print(path, new_value, addr)
         except Exception as e:
            self.client.msg(f"Error writing to HV channel {addr}", is_error=True)
         self.mutex.release()

   def readout_func(self):
      # add parameter to skip event buildint
      event = midas.event.Event()
      event.header.trigger_mask = midas.frontend.frontend_index
      readback = self.client.odb_get(f'{self.odb_settings_dir.replace("Settings", "Readback")}')

      for idx in range(0,19):
         # check if HV channel is probed and powered
         if self.online_channels[idx]:
            data = []
            data.append(readback["Status"][idx])
            data.append(readback["V"][idx])
            data.append(readback["I"][idx])
            data.append(readback["T"][idx])
            data.append(readback["Alarm"][idx])
            data.append(self.settings["Vset"][idx])
            data.append(self.settings["Rate up"][idx])
            data.append(self.settings["Rate down"][idx])
            data.append(self.settings["Limit V"][idx])
            data.append(self.settings["Limit I"][idx])
            data.append(self.settings["Limit T"][idx])
            data.append(self.settings["Trip time"][idx])
            data.append(self.settings["Trigger threshold"][idx])
            
            event.create_bank(f"HV{str(idx+1).zfill(2)}", midas.TID_FLOAT, data)

      return event

   # RPC functions
   # HV channels number: [1...19]

   def rpc_handler(self,client, cmd, args, max_len):
      ret_int = midas.status_codes["SUCCESS"]
      ret_str = ""
       
      if cmd == "set_enable_bit":
         jargs = json.loads(args)
         ch = jargs.get("channel")
         value = jargs.get("value")
         if (not self.channel_is_valid(ch)):
            ret_int = midas.status_codes["FE_ERR_DRIVER"]
            ret_str = json.dumps({"result": f'channel {ch} not valid'})
         else:
            self.set_enable_bit(ch, value)
            ret_int = midas.status_codes["SUCCESS"]
            ret_str = json.dumps({"result": f'ok'})

      elif cmd == "set_adc_bit":
         jargs = json.loads(args)
         ch = jargs.get("channel")
         value = jargs.get("value")
         if (not self.channel_is_valid(ch)):
            ret_int = midas.status_codes["FE_ERR_DRIVER"]
            ret_str = json.dumps({"result": f'channel {ch} not valid'})
         else:
            self.set_adc_bit(ch, value)
            ret_int = midas.status_codes["SUCCESS"]
            ret_str = json.dumps({"result": f'ok'})

      elif cmd == "set_enable_all":
         jargs = json.loads(args)
         value = jargs.get("value")
         for ch in range(1,20):
            self.set_enable_bit(ch, value)
            time.sleep(0.1)
         ret_int = midas.status_codes["SUCCESS"]
         ret_str = json.dumps({"result": f'ok'})

      elif cmd == "set_adc_all":
         jargs = json.loads(args)
         value = jargs.get("value")
         for ch in range(1,20):
            self.set_adc_bit(ch, value)
         ret_int = midas.status_codes["SUCCESS"]
         ret_str = json.dumps({"result": f'ok'})

      elif cmd == "set_enable_adc_all":
         for ch in range(1,20):
            self.set_enable_bit(ch, 1)
            time.sleep(0.1)
            self.set_adc_bit(ch, 1)
         ret_int = midas.status_codes["SUCCESS"]
         ret_str = json.dumps({"result": f'ok'})

      elif cmd == "control":
         jargs = json.loads(args)
         ch = jargs.get("channel")
         command = jargs.get("command").lower()
         if (not self.channel_is_valid(ch)):
            ret_int = midas.status_codes["FE_ERR_DRIVER"]
            ret_str = json.dumps({"result": f'channel {ch} not valid'})
         elif command not in ["on", "off", "reset"]:
            ret_int = midas.status_codes["FE_ERR_DRIVER"]
            ret_str = json.dumps({"result": f'command {command} not valid'})
         else:
            #print(ch, command)
            success = False
            if self.param.mode == "rtu":
               self.mutex.acquire()
            if command == "on":
               success = self.hv.powerOn(ch)
            elif command == "off":
               success = self.hv.powerOff(ch)
            elif command == "reset":
               success = self.hv.reset(ch)
            if self.param.mode == "rtu":
               self.mutex.release()
         
         if success:
            ret_int = midas.status_codes["SUCCESS"]
            ret_str = json.dumps({"result": f'ok'})
         else:
            ret_int = midas.status_codes["FE_ERR_DRIVER"]
            ret_str = json.dumps({"result": f'command failure'})

      elif cmd == "get_channels_status":
         ret_int = midas.status_codes["SUCCESS"]
         ret_str = json.dumps({
            "online": self.online_channels, 
            "power": self.enabled_channels,
            "adc": self.adc_channels,
            "result": f'ok'
         })

      else:
         ret_int = midas.status_codes["FE_ERR_DRIVER"]
         ret_str = json.dumps({"result": f'unknown command {cmd}'})
           
      return (ret_int, ret_str)

   def channel_is_valid(self, ch):
      return (ch >= 1 and ch <= 19)

   def set_adc_bit(self, ch, value):
      b = ch - 1
      mask = (1 << b)
      if value == 1:
         en = self.readRegister(0) | mask
      elif value == 0:
         en = self.readRegister(0) & ~mask
      self.writeRegister(0, en)

   def set_enable_bit(self, ch, value, safe=True):
      b = ch - 1
      mask = (1 << b)
      if value == 1:
         if(safe):      # safe mode prevent to enable channel with adc true (= bootloader)
            self.set_adc_bit(ch, 0)
         en = self.readRegister(1) | mask
      elif value == 0:
         en = self.readRegister(1) & ~mask
      self.writeRegister(1, en)

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
