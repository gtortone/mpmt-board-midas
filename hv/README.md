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
|```Trip time```|int|trip time limit (ms)|
|```Trigger threshold```|int|trigger threshold|
|```Alarm```|int|alarm mask of bits|

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

