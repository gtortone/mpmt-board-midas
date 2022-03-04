## HighVoltage frontend

This MIDAS frontend provides data from HV modules installed on MPMT board. The communication is provided by Modbus protocol.

### ODB settings

ODB settings for 19 HV modules start from index 0 up to 18 while Modbus addresses start from index 1 up to 19 (address 0 is
broadcast address).

| key | type | description | 
|------|------|-----------|
|```Port device```|string|specify UART device to use for communication|
|```Report Modbus errors```|bool|redirect error messages to MIDAS messages|
|```Online```|bool[19]|each index reports if a module is online|
|```Power command```|string|send a power command (on,off,reset) to specified module|
|```Status```|int|status of module index (see status table)|
|```Vset```|double|voltage to reach (V)|
|```V```|double|monitored voltage (V)|
|```I```|double|monitored current (uA)|
|```T```|double|monitored temperature (degC)|
|```Rate up```|int|voltage ramp up rate (V/s)|
|```Rate down```|int|voltage ramp down rate (V/s)|
|```Limit V```|int|voltage margin limit (V)|
|```Limit I```|int|current limit (uA)|
|```Limit T```|int|temperature limit (degC)|
|```Trip time```|int|trip time limit (s)|
|```Trigger threshold```|int|trigger threshold|
|```Alarm```|int|alarm mask of bits (see alarm table)|

#### Status table

|code|description|
|----|-----------|
|```0```|UP|
|```1```|DOWN|
|```2```|RAMP UP|
|```3```|RAMP DOWN|
|```4```|TUNE UP|
|```5```|TUNE DOWN|
|```6```|TRIP|

#### Alarm table

|bit|description|
|----|-----------|
|```0```|NONE|
|```1```|OVER VOLTAGE|
|```2```|UNDER VOLTAGE|
|```4```|OVER CURRENT|
|```8```|OVER TEMPERATURE|

### Event data

### Event header

`Event id`: 3\
`Mask`: MPMT id\
`Bank name`: `HVnn` (nn: number of HV module [0...18])

### Bank format

- Events within `HVxx` bank are organized as follow:

`STA`: Status\
`V`: Monitored voltage (mV)\
`I`: Monitored current (nA)\
`T`: Monitored temperature (degC)\
`ALA`: Alarm code\
`VSE`: Voltage to reach (V)\
`RUP`: Ramp up rate (V/s)\
`RDN`: Ramp down rate (V/s)\
`LIV`: Voltage margin limit (V)\
`LII`: Current limit (uA)\
`LIT`: Temperature limit (degC)\
`TT`: Trip time (s)\
`THR`: Trigger threshold

```
Bank:HV00 - Mask:0001
  1-> 0.000e+00 2.998e+02 3.040e-01 2.800e+01 0.000e+00 3.000e+02 2.500e+01 2.500e+01
          (STA)       (V)       (I)       (T)     (ALA)     (VSE)     (RUP)     (RDN)
  9-> 1.500e+01 1.000e+01 5.000e+01 1.000e+03 1.320e+02 
          (LIV)     (LII)     (LIT)      (TT)     (THR)     
```
