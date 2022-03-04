## Sensors frontend

This MIDAS frontend provides data from environmental sensors installed on MPMT board.

### ODB settings

| key | type | description | 
|------|------|-----------|
|```Voltage 5V```|double|Monitored 5V voltage (V)|
|```Voltage 3.3V```|double|Monitored 3.3V voltage (V)|
|```Current POE channel A```|double|Current on POE channel A (A)|
|```Current POE channel B```|double|Current on POE channel B (A)|
|```Power POE channel A```|double|Power on POE channel A (W)|
|```Power POE channel B```|double|Power on POE channel B (W)|
|```On-board temperature```|double|PCB temperature (degC)|
|```On-board pressure```|double|PCB pressure (hPa)|
|```On-board humidity```|double|PCB humidity (%Rh)|
|```External temperature```|double|External temperature (degC)|
|```External pressure```|double|External pressure (hPa)|

### Event data

### Event header

`Event id`: 4\
`Mask`: MPMT id\
`Bank name`: `SENS`

### Bank format

- Events within `SENS` bank are organized as follow:

`V5`: Monitored 5V voltage (V)\
`V33`: Monitored 3.3V voltage (V)\
`IA`: Current on POE channel A (A)\
`IB`: Current on POE channel B (A)\
`PA`: Power on POE channel A (W)\
`PB`: Power on POE channel B (W)\
`BT`: On-board temperature (degC)\
`BP`: On-board pressure (hPa)\
`BU`: On-board humidity (%Rh)\
`ET`: External temperature (degC)\
`EP`: External pressure (hPa)

```
Bank:SENS - Mask:0001
  1-> 4.878e+00 3.252e+00 0.000e+00 6.440e-01 0.000e+00 2.094e+00 2.602e+01 9.977e+02
           (V5)     (V33)      (IA)      (IB)      (PA)      (PB)      (BT)      (BP)
  9-> 2.330e+01 2.306e+01 9.984e+02
           (BU)      (ET)      (EP)
```
