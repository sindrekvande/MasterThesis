
column = 'Gg_pyr'
BTmac = 'DA:B0:BB:56:98:73' #Nordic: 'E0:21:78:85:2A:FB'
BTname = 'SoC BLE'
BTservice = '180d'
BTserviceUUID = '0x180D'
BTinterval = 1.0

MaxLedWatt = 1000 # Max W/m^2 output of LED
IrradianceScaler = 0.003#0.0009 # Simulated Irradiance = Actual Irradiance x IrrandianceScaler

LoggingTimeStep = 0.2 # Time in s between datapoints written to the csv file = time between LED updates
IrrDatasetTimeStep = 60 # Time in s between samples in Irradiance dataset
EvalSpeedUp = 1    # Speedup factor - impacts evaluation time and LED output scaling

inputFilePath = "datasets/"
outputFilePath = "measurements/"
