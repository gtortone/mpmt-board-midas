
registers = {}

default_settings = {
   "Enable ADC sampling": [False] * 19,
   "Power enable": [False] * 19,
   "Overcurrent": [False] * 19,
   "Clock A OK" : False,
   "Clock A lost": False,
   "Clock A found": False,
   "Clock B OK" : False,
   "Clock B lost": False,
   "Clock B found": False,
   "Clock A-B auto select": 0,
   "Reference clock A-B select": 0,
   "Reference clock mux status": 0,
   "Clock int-ext auto select": 0,
   "Clock int-ext select": 0,
   "Clock int-ext mux status": 0,
   "PLL locked": False,
   "PLL reset": False,
   "Clock fail": False,
   "PPS OK": False,
   "Unix timestamp aligned": False,
   "PPS counter": 0,
   "Unix timestamp": 0,
   "Enable PPS event": False,
   "Enable ADC calibration": False,
   "Peak delay": 0,
   "Dark delay": 0,
   "Pulser period": 0,
   "Dead time": 0,
   "Channel ratemeter": [0] * 19,
}

def configRegisters(basepath):

   registers[f'{basepath}/Enable ADC sampling'] = {
      "mode": "RW",
      "memaddr": 0,
      "datatype": "boolset",
      "count": 19,
   }
   registers[f'{basepath}/Power enable'] = {
      "mode": "RW",
      "memaddr": 1,
      "datatype": "boolset",
      "count": 19,
   }
   registers[f'{basepath}/Overcurrent'] = {
      "mode": "R",
      "memaddr": 2,
      "datatype": "boolset",
      "count": 19,
   }
   registers[f'{basepath}/Clock A OK'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 0,
      "count": 1,
   }
   registers[f'{basepath}/Clock A lost'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 1,
      "count": 1,
   }
   registers[f'{basepath}/Clock A found'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 2,
      "count": 1,
   }
   registers[f'{basepath}/Clock B OK'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 3,
      "count": 1,
   }
   registers[f'{basepath}/Clock B lost'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 4,
      "count": 1,
   }
   registers[f'{basepath}/Clock B found'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 5,
      "count": 1,
   }
   registers[f'{basepath}/Clock A-B auto select'] = {
      "mode": "RW",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 6,
      "count": 1,
   }
   registers[f'{basepath}/Reference clock A-B select'] = {
      "mode": "RW",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 7,
      "count": 1,
   }
   registers[f'{basepath}/Reference clock mux status'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 8,
      "count": 1,
   }
   registers[f'{basepath}/Clock int-ext auto select'] = {
      "mode": "RW",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 9,
      "count": 1,
   }
   registers[f'{basepath}/Clock int-ext select'] = {
      "mode": "RW",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 10,
      "count": 1,
   }
   registers[f'{basepath}/Clock int-ext mux status'] = {
      "mode": "RW",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 11,
      "count": 1,
   }
   registers[f'{basepath}/PLL locked'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 12,
      "count": 1,
   }
   registers[f'{basepath}/PLL reset'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 13,
      "count": 1,
   }
   registers[f'{basepath}/Clock fail'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 14,
      "count": 1,
   }
   registers[f'{basepath}/PPS OK'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 15,
      "count": 1,
   }
   registers[f'{basepath}/Unix timestamp aligned'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 16,
      "count": 1,
   }
   registers[f'{basepath}/PPS counter'] = {
      "mode": "R",
      "memaddr": 4,
      "datatype": "int",
   }
   registers[f'{basepath}/Unix timestamp'] = {
      "mode": "RW",
      "memaddr": 5,
      "datatype": "int",
   }
   registers[f'{basepath}/Enable PPS event'] = {
      "mode": "RW",
      "memaddr": 6,
      "datatype": "bitset",
      "startBit": 0,
      "count": 1,
   }
   registers[f'{basepath}/Enable ADC calibration'] = {
      "mode": "RW",
      "memaddr": 6,
      "datatype": "bitset",
      "startBit": 1,
      "count": 1,
   }
   registers[f'{basepath}/Peak delay'] = {
      "mode": "RW",
      "memaddr": 10,
      "datatype": "int",
   }
   registers[f'{basepath}/Dark delay'] = {
      "mode": "RW",
      "memaddr": 11,
      "datatype": "int",
   }
   registers[f'{basepath}/Pulser period'] = {
      "mode": "RW",
      "memaddr": 12,
      "datatype": "int",
   }
   registers[f'{basepath}/Dead time'] = {
      "mode": "R",
      "memaddr": 13,
      "datatype": "int",
   }
   registers[f'{basepath}/Channel ratemeter'] = {
      "mode": "R",
      "memaddr": 20,
      "datatype": "intset",
      "count": 19,
   }

