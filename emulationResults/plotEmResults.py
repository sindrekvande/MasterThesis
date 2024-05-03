import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#import scipy.interpolate as sc


resultFile = 'emulationResults/firstTest.tsv'

VoltageDF = pd.read_csv(resultFile, sep='\t', usecols = ['STORAGE_OUT'],  dtype = np.float32)
irrDF = pd.read_csv(resultFile, sep='\t', usecols = ['irrValue'],  dtype = np.float32)
currDF = pd.read_csv(resultFile, sep='\t', usecols = ['CSA_EH_IN'],  dtype = np.float32)
enDF = pd.read_csv(resultFile, sep='\t', usecols = ['MPPT_EN'],  dtype = np.float32)

voltage = []
irr = []
curr = []
en = []

for _, v in VoltageDF.itertuples():
    voltage.append(v)

for _, s in irrDF.itertuples():
    irr.append(s/333)

for _, i in currDF.itertuples():
    curr.append(i)

for _, e in enDF.itertuples():
    en.append(e)

#iterator = [[irr[i],curr[i]*voltage[i]] for i in range(64000, 130000, 1)]

#x = np.array([(y/(i/10000 * 0.93 * 4/1000)) for i, y in iterator])

#print(np.median(x)*18.2)
plt.plot(voltage)
plt.plot(irr)
plt.plot(en)
#plt.plot(x*18.2)
#plt.axhline(np.median(x)*18.2, color='r')
#plt.axhline(26, color='orange')
plt.show()