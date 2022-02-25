
registers = {}

scratch_ro_settings = {
   "Status": [0] * 19,
   "V": [0.0] * 19,
   "I": [0.0] * 19,
   "T": [0.0] * 19,
   "Alarm": [0] * 19
}

scratch_rw_settings = {
   "Power command": ["none"] * 19,
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
   "Port device": "/dev/ttyPS1",
   "Online": [False] * 19,
   "Power command": ["none"] * 19,
   "Status": [0] * 19,
   "Vset": [0.0] * 19,
   "V": [0.0] * 19,
   "I": [0.0] * 19,
   "T": [0.0] * 19,
   "Rate up": [0] * 19,
   "Rate down": [0] * 19,
   "Limit V": [0] * 19,
   "Limit I": [0] * 19,
   "Limit T": [0] * 19,
   "Trip time": [0] * 19,
   "Trigger threshold": [0] * 19,
   "Alarm": [0] * 19
}

def configRegisters(basepath):

   # read only
   registers[f'{basepath}/Status'] = {
      "mode": "R",
   }
   registers[f'{basepath}/V'] = {
      "mode": "R",
   }
   registers[f'{basepath}/I'] = {
      "mode": "R",
   }
   registers[f'{basepath}/T'] = {
      "mode": "R",
   }
   registers[f'{basepath}/Alarm'] = {
      "mode": "R",
   }
   
   # read write
   registers[f'{basepath}/Power command'] = {
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
