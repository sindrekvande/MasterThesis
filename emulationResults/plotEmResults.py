import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

resultFile = 'emulationResults/firstTest.tsv'

VoltageDF = pd.read_csv(resultFile, sep='\t', usecols = ['V_BANK5'],  dtype = np.float32)
irrDF = pd.read_csv(resultFile, sep='\t', usecols = ['irrValue'],  dtype = np.float32)

voltage = []
irr = []

for _, v in VoltageDF.itertuples():
    voltage.append(v)

for _, i in irrDF.itertuples():
    irr.append(i/333)

plt.plot(voltage)
plt.plot(irr)
plt.show()