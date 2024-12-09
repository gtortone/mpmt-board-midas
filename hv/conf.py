
registers = {}

scratch_ro_settings = {
   "Status": [1] * 19,     # 1: DOWN
   "V": [0.0] * 19,
   "I": [0.0] * 19,
   "T": [0.0] * 19,
   "Alarm": [0] * 19,
   "Online": [False] * 19,
}

scratch_rw_settings = {
   "Vset": [0.0] * 19,
   "Rate up": [0] * 19,
   "Rate down": [0] * 19,
   "Limit V": [0] * 19,
   "Limit I": [0] * 19,
   "Limit T": [0] * 19,
   "Trip time": [0] * 19,
   "Trigger threshold": [0] * 19,
}

default_settings = {
   "RTU mode": False,
   "Port device": "/dev/ttyPS2",
   "Report Modbus errors": False, 
   "Vset": [0.0] * 19,
   "Rate up": [0] * 19,
   "Rate down": [0] * 19,
   "Limit V": [0] * 19,
   "Limit I": [0] * 19,
   "Limit T": [0] * 19,
   "Trip time": [0] * 19,
   "Trigger threshold": [0] * 19,
   "Names": [ "Status", "V", "Power command", "T", "I", "Vset", "Rate up", "Rate down", "Limit V", "Limit I",
               "Limit T", "Trip time", "Trigger threshold", "Alarm"
            ],
}

def configRegisters(basepath):

   registers[f'{basepath}/Power command'] = {
      "mode": "RW",
   }
   registers[f'{basepath}/Power enable'] = {
      "mode": "RW",
   }
   registers[f'{basepath}/ADC enable'] = {
      "mode": "RW",
   }
   registers[f'{basepath}/Vset'] = {
      "mode": "RW",
   }
   registers[f'{basepath}/Rate up'] = {
      "mode": "RW",
   }
   registers[f'{basepath}/Rate down'] = {
      "mode": "RW",
   }
   registers[f'{basepath}/Limit V'] = {
      "mode": "RW",
   }
   registers[f'{basepath}/Limit I'] = {
      "mode": "RW",
   }
   registers[f'{basepath}/Limit T'] = {
      "mode": "RW",
   }
   registers[f'{basepath}/Trip time'] = {
      "mode": "RW",
   }
   registers[f'{basepath}/Trigger threshold'] = {
      "mode": "RW",
   }
