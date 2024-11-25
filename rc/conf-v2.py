

default_settings = {
   "Board startup mode": ["none"] * 19,
   "Enable ADC sampling": 0,
   "Power enable": 0,
   "Overcurrent": 0,
   "FIFO half full": False,
   "FIFO reset": False,
   "PLL locked": False,
   "Clock B found": False,
   "Clock B lost": False,
   "Clock B OK": False,
   "Clock A found": False,
   "Clock A lost": False,
   "Clock A OK": False,
   "Clock int-ext select": False,
   "Reference clock A-B select": False,
   "Reference clock A-B status": False,
   "Clock int-ext mux status": False,
   "PPS not aligned": False,
   "PPS not received": False,
   "Unix timestamp not aligned": False,
   "Enable PPS event": False,
   "ACQ reset": False,
   "Enable ADC calibration": False,
   "Channel read timeout": 0,
   "PPS counter": 0,
   "Unix timestamp": 0,
   "Pulser period": 0,
   "Channel ratemeter": [0] * 19,
   "Dead time": 0,
   "Time to peak CH0": 0,
   "Time to peak CH1": 0,
   "Time to peak CH2": 0,
   "Time to peak CH3": 0,
   "Time to peak CH4": 0,
   "Time to peak CH5": 0,
   "Time to peak CH6": 0,
   "Time to peak CH7": 0,
   "Time to peak CH8": 0,
   "Time to peak CH9": 0,
   "Time to peak CH10": 0,
   "Time to peak CH11": 0,
   "Time to peak CH12": 0,
   "Time to peak CH13": 0,
   "Time to peak CH14": 0,
   "Time to peak CH15": 0,
   "Time to peak CH16": 0,
   "Time to peak CH17": 0,
   "Time to peak CH18": 0,
   "TDC delay CH0": 0,
   "TDC delay CH1": 0,
   "TDC delay CH2": 0,
   "TDC delay CH3": 0,
   "TDC delay CH4": 0,
   "TDC delay CH5": 0,
   "TDC delay CH6": 0,
   "TDC delay CH7": 0,
   "TDC delay CH8": 0,
   "TDC delay CH9": 0,
   "TDC delay CH10": 0,
   "TDC delay CH11": 0,
   "TDC delay CH12": 0,
   "TDC delay CH13": 0,
   "TDC delay CH14": 0,
   "TDC delay CH15": 0,
   "TDC delay CH16": 0,
   "TDC delay CH17": 0,
   "TDC delay CH18": 0,
}

def configRegisters(basepath):

   registers = {}

   registers[f'{basepath}/Enable ADC sampling'] = {
      "mode": "RW",
      "memaddr": 0,
      "datatype": "int",
      "count": 1,
   }
   registers[f'{basepath}/Power enable'] = {
      "mode": "RW",
      "memaddr": 1,
      "datatype": "int",
      "count": 1,
   }
   registers[f'{basepath}/Overcurrent'] = {
      "mode": "R",
      "memaddr": 2,
      "datatype": "int",
      "count": 1,
   }
   registers[f'{basepath}/FIFO half full'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 0,
      "count": 1,
   }
   registers[f'{basepath}/FIFO reset'] = {
      "mode": "RW",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 1,
      "count": 1,
   }
   registers[f'{basepath}/PLL locked'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 2,
      "count": 1,
   }
   registers[f'{basepath}/Clock B found'] = {
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
   registers[f'{basepath}/Clock B OK'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 5,
      "count": 1,
   }
   registers[f'{basepath}/Clock A found'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 6,
      "count": 1,
   }
   registers[f'{basepath}/Clock A lost'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 7,
      "count": 1,
   }
   registers[f'{basepath}/Clock A OK'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 8,
      "count": 1,
   }
   registers[f'{basepath}/Clock int-ext select'] = {
      "mode": "RW",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 9,
      "count": 1,
   }
   registers[f'{basepath}/Reference clock A-B select'] = {
      "mode": "RW",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 10,
      "count": 1,
   }
   registers[f'{basepath}/Reference clock A-B status'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 11,
      "count": 1,
   }
   registers[f'{basepath}/Clock int-ext mux status'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 12,
      "count": 1,
   }
   registers[f'{basepath}/PPS not aligned'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 15,
      "count": 1,
   }
   registers[f'{basepath}/PPS not received'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 16,
      "count": 1,
   }
   registers[f'{basepath}/Unix timestamp not aligned'] = {
      "mode": "R",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 18,
      "count": 1,
   }
   registers[f'{basepath}/Enable PPS event'] = {
      "mode": "RW",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 20,
      "count": 1,
   }
   registers[f'{basepath}/ACQ reset'] = {
      "mode": "RW",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 21,
      "count": 1,
   }
   registers[f'{basepath}/Enable ADC calibration'] = {
      "mode": "RW",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 22,
      "count": 1,
   }
   registers[f'{basepath}/Channel read timeout'] = {
      "mode": "RW",
      "memaddr": 3,
      "datatype": "bitset",
      "startBit": 23,
      "count": 9,
   }
   registers[f'{basepath}/PPS counter'] = {
      "mode": "R",
      "memaddr": 4,
      "datatype": "int",
   }
   registers[f'{basepath}/Unix timestamp'] = {
      "mode": "R",
      "memaddr": 5,
      "datatype": "int",
   }
   registers[f'{basepath}/Pulser period'] = {
      "mode": "RW",
      "memaddr": 7,
      "datatype": "int",
   }
   registers[f'{basepath}/Channel ratemeter'] = {
      "mode": "R",
      "memaddr": 8,
      "datatype": "intset",
      "count": 19,
   }
   registers[f'{basepath}/Dead time'] = {
      "mode": "R",
      "memaddr": 27,
      "datatype": "int",
   }
   registers[f'{basepath}/Time to peak CH0'] = {
      "mode": "RW",
      "memaddr": 28,
      "datatype": "bitset",
      "startBit": 12,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH1'] = {
      "mode": "RW",
      "memaddr": 28,
      "datatype": "bitset",
      "startBit": 0,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH2'] = {
      "mode": "RW",
      "memaddr": 29,
      "datatype": "bitset",
      "startBit": 12,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH3'] = {
      "mode": "RW",
      "memaddr": 29,
      "datatype": "bitset",
      "startBit": 0,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH4'] = {
      "mode": "RW",
      "memaddr": 30,
      "datatype": "bitset",
      "startBit": 12,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH5'] = {
      "mode": "RW",
      "memaddr": 30,
      "datatype": "bitset",
      "startBit": 0,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH6'] = {
      "mode": "RW",
      "memaddr": 31,
      "datatype": "bitset",
      "startBit": 12,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH7'] = {
      "mode": "RW",
      "memaddr": 31,
      "datatype": "bitset",
      "startBit": 0,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH8'] = {
      "mode": "RW",
      "memaddr": 32,
      "datatype": "bitset",
      "startBit": 12,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH9'] = {
      "mode": "RW",
      "memaddr": 32,
      "datatype": "bitset",
      "startBit": 0,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH10'] = {
      "mode": "RW",
      "memaddr": 33,
      "datatype": "bitset",
      "startBit": 12,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH11'] = {
      "mode": "RW",
      "memaddr": 33,
      "datatype": "bitset",
      "startBit": 0,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH12'] = {
      "mode": "RW",
      "memaddr": 34,
      "datatype": "bitset",
      "startBit": 12,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH13'] = {
      "mode": "RW",
      "memaddr": 34,
      "datatype": "bitset",
      "startBit": 0,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH14'] = {
      "mode": "RW",
      "memaddr": 35,
      "datatype": "bitset",
      "startBit": 12,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH15'] = {
      "mode": "RW",
      "memaddr": 35,
      "datatype": "bitset",
      "startBit": 0,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH16'] = {
      "mode": "RW",
      "memaddr": 36,
      "datatype": "bitset",
      "startBit": 12,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH17'] = {
      "mode": "RW",
      "memaddr": 36,
      "datatype": "bitset",
      "startBit": 0,
      "count": 12
   }
   registers[f'{basepath}/Time to peak CH18'] = {
      "mode": "RW",
      "memaddr": 37,
      "datatype": "bitset",
      "startBit": 12,
      "count": 12
   }
   registers[f'{basepath}/TDC delay CH0'] = {
      "mode": "RW",
      "memaddr": 38,
      "datatype": "bitset",
      "startBit": 24,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH1'] = {
      "mode": "RW",
      "memaddr": 38,
      "datatype": "bitset",
      "startBit": 16,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH2'] = {
      "mode": "RW",
      "memaddr": 38,
      "datatype": "bitset",
      "startBit": 8,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH3'] = {
      "mode": "RW",
      "memaddr": 38,
      "datatype": "bitset",
      "startBit": 0,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH4'] = {
      "mode": "RW",
      "memaddr": 39,
      "datatype": "bitset",
      "startBit": 24,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH5'] = {
      "mode": "RW",
      "memaddr": 39,
      "datatype": "bitset",
      "startBit": 16,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH6'] = {
      "mode": "RW",
      "memaddr": 39,
      "datatype": "bitset",
      "startBit": 8,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH7'] = {
      "mode": "RW",
      "memaddr": 39,
      "datatype": "bitset",
      "startBit": 0,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH8'] = {
      "mode": "RW",
      "memaddr": 40,
      "datatype": "bitset",
      "startBit": 24,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH9'] = {
      "mode": "RW",
      "memaddr": 40,
      "datatype": "bitset",
      "startBit": 16,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH10'] = {
      "mode": "RW",
      "memaddr": 40,
      "datatype": "bitset",
      "startBit": 8,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH11'] = {
      "mode": "RW",
      "memaddr": 40,
      "datatype": "bitset",
      "startBit": 0,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH12'] = {
      "mode": "RW",
      "memaddr": 41,
      "datatype": "bitset",
      "startBit": 24,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH13'] = {
      "mode": "RW",
      "memaddr": 41,
      "datatype": "bitset",
      "startBit": 16,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH14'] = {
      "mode": "RW",
      "memaddr": 41,
      "datatype": "bitset",
      "startBit": 8,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH15'] = {
      "mode": "RW",
      "memaddr": 41,
      "datatype": "bitset",
      "startBit": 0,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH16'] = {
      "mode": "RW",
      "memaddr": 42,
      "datatype": "bitset",
      "startBit": 24,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH17'] = {
      "mode": "RW",
      "memaddr": 42,
      "datatype": "bitset",
      "startBit": 16,
      "count": 8
   }
   registers[f'{basepath}/TDC delay CH18'] = {
      "mode": "RW",
      "memaddr": 42,
      "datatype": "bitset",
      "startBit": 8,
      "count": 8
   }

   return registers
