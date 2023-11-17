#!/usr/bin/env python3

import sys
import midas
import midas.frontend
import midas.event
import psutil
sys.path.append('/opt/mpmt-board-cli/sensors')
from tla2024 import TLA2024
from bme280 import BME280

class Sensors(midas.frontend.EquipmentBase):

   def __init__(self, client):

      if(midas.frontend.frontend_index == -1):
         client.msg("set frontend index with -i option", is_error=True)
         sys.exit(-1)

      equip_name = "MPMT-Sensors" + str(midas.frontend.frontend_index).zfill(2)

      default_common = midas.frontend.InitialEquipmentCommon()
      default_common.equip_type = midas.EQ_PERIODIC
      default_common.buffer_name = "SYSTEM"
      default_common.trigger_mask = 0
      default_common.event_id = 4
      default_common.period_ms = 5000
      default_common.read_when = midas.RO_ALWAYS
      default_common.log_history = 2 # history is enabled, data generated with period_ms frequency

      default_settings = {
         "Voltage 5V": 0.0, 
         "Voltage 3.3V": 0.0,
         "Current POE channel A": 0.0,
         "Current POE channel B": 0.0, 
         "Power POE channel A": 0.0,
         "Power POE channel B": 0.0,
         "On-board temperature": 0.0,
         "On-board pressure": 0.0,
         "On-board humidity": 0.0,
         "External temperature": 0.0,
         "External pressure": 0.0,
         "CPU used percentage": 0.0,
         "Memory used percentage": 0.0,
         "FPGA temperature": 0.0
      }

      midas.frontend.EquipmentBase.__init__(self, client, equip_name, default_common, default_settings)

      # BME280 on-board sensor
      self.bme = BME280(1, 0x76)

      # BME280 external sensor
      self.bmeExt = BME280(1, 0x77)

      # TLA ADC
      self.tla = TLA2024(1, 0x48)

      # FPGA temperature
      self.iiodir = "/sys/bus/iio/devices/iio:device0/"
      self.ftraw = open(f'{self.iiodir}/in_temp0_raw')
      self.ftoff = open(f'{self.iiodir}/in_temp0_offset')
      self.ftsca = open(f'{self.iiodir}/in_temp0_scale')
      
      self.set_status("Initialized")

   def updateODB(self):
      tlaData = self.tla.readAll()
      V1 = round(tlaData[0] * 3 / 1000, 3)
      V2 = round(tlaData[0] * 2 / 1000, 3)
      I1 = round(tlaData[1]/1000, 3)
      I2 = round(tlaData[3]/1000, 3)
      P1 = round(V1 * I1, 3)
      P2 = round(V1 * I2, 3)
      self.client.odb_set(f"{self.odb_settings_dir}/Voltage 5V", V1)
      self.client.odb_set(f"{self.odb_settings_dir}/Voltage 3.3V", V2)
      self.client.odb_set(f"{self.odb_settings_dir}/Current POE channel A", I1)
      self.client.odb_set(f"{self.odb_settings_dir}/Current POE channel B", I2)
      self.client.odb_set(f"{self.odb_settings_dir}/Power POE channel A", P1)
      self.client.odb_set(f"{self.odb_settings_dir}/Power POE channel B", P2)
      self.client.odb_set(f"{self.odb_settings_dir}/CPU used percentage", psutil.cpu_percent())
      self.client.odb_set(f"{self.odb_settings_dir}/Memory used percentage", psutil.virtual_memory().percent)

      self.ftraw.seek(0,0)
      self.ftoff.seek(0,0)
      self.ftsca.seek(0,0)
     
      traw = int(self.ftraw.read())
      toff = int(self.ftoff.read())
      tsca = float(self.ftsca.read())
      fpgat = (traw + toff) * tsca / 1000

      self.client.odb_set(f"{self.odb_settings_dir}/FPGA temperature", round(fpgat, 3))
      
      bmeData = self.bme.readAll()
      self.client.odb_set(f"{self.odb_settings_dir}/On-board temperature", round(bmeData[0], 3))
      self.client.odb_set(f"{self.odb_settings_dir}/On-board pressure", round(bmeData[1], 3))
      self.client.odb_set(f"{self.odb_settings_dir}/On-board humidity", round(bmeData[2], 3)) 

  
      try:
         bmeData = self.bmeExt.readAll()
      except:
         pass
      else:
         self.client.odb_set(f"{self.odb_settings_dir}/External temperature", round(bmeData[0], 3))
         self.client.odb_set(f"{self.odb_settings_dir}/External pressure", round(bmeData[1], 3))

   def readout_func(self):
      self.updateODB()
      event = midas.event.Event()
      event.header.trigger_mask = midas.frontend.frontend_index

      data = []
      data.append(self.settings['Voltage 5V']) 
      data.append(self.settings['Voltage 3.3V']) 
      data.append(self.settings['Current POE channel A'])
      data.append(self.settings['Current POE channel B'])
      data.append(self.settings['Power POE channel A'])
      data.append(self.settings['Power POE channel B'])
      data.append(self.settings['On-board temperature'])
      data.append(self.settings['On-board pressure'])
      data.append(self.settings['On-board humidity'])
      data.append(self.settings['External temperature'])
      data.append(self.settings['External pressure'])
      data.append(self.settings['CPU used percentage'])
      data.append(self.settings['Memory used percentage'])
      data.append(self.settings['FPGA temperature'])

      event.create_bank("SENS", midas.TID_FLOAT, data)

      return event

class MyFrontend(midas.frontend.FrontendBase):

   def __init__(self):
      midas.frontend.parse_args()
      midas.frontend.FrontendBase.__init__(self, "snfe" + str(midas.frontend.frontend_index).zfill(2))
      self.add_equipment(Sensors(self.client))

   def begin_of_run(self, run_number):
      self.set_all_equipment_status("MPMT-Sensors FE running", "greenLight")
      self.client.msg("Frontend has seen start of run number %d" % run_number)
      return midas.status_codes["SUCCESS"]

   def end_of_run(self, run_number):
      self.set_all_equipment_status("MPMT-Sensors FE finished", "greenLight")
      self.client.msg("Frontend has seen end of run number %d" % run_number)
      return midas.status_codes["SUCCESS"]

if __name__ == "__main__":
   my_fe = MyFrontend()
   my_fe.run()
