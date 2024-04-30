import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

resultFile = 'emulationResults/firstTest.tsv'

VoltageDF = pd.read_csv(resultFile, sep='\t', usecols = ['CSA_STORAGE_IN_+'],  dtype = np.float32)
irrDF = pd.read_csv(resultFile, sep='\t', usecols = ['irrValue'],  dtype = np.float32)
currDF = pd.read_csv(resultFile, sep='\t', usecols = ['CSA_STORAGE_IN'],  dtype = np.float32)

voltage = []
irr = []
curr = []

for _, v in VoltageDF.itertuples():
    voltage.append(v)

for _, s in irrDF.itertuples():
    irr.append(s)

for _, i in currDF.itertuples():
    curr.append(i)

iterator = [[irr[i],curr[i]*voltage[i]] for i in range(35000, 49000, 1)]

x = np.array([((i/10000 * 0.93 * 4/1000 * 18.2)/y) for i, y in iterator])

print(np.mean(x)*18.2)
#plt.plot(voltage)
#plt.plot(irr)
plt.plot(x*18.2)
plt.show()