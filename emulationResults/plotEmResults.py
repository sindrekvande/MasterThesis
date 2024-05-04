import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#import scipy.interpolate as sc


resultFile = 'emulationResults/Test182fix.tsv'

VoltageDF = pd.read_csv(resultFile, sep='\t', usecols = ['STORAGE_OUT'],  dtype = np.float32)
irrDF = pd.read_csv(resultFile, sep='\t', usecols = ['irrValue'],  dtype = np.float32)
currDF = pd.read_csv(resultFile, sep='\t', usecols = ['CSA_EH_IN'],  dtype = np.float32)
enDF = pd.read_csv(resultFile, sep='\t', usecols = ['DCDC_OUT_BUF'],  dtype = np.float32)
en1DF = pd.read_csv(resultFile, sep='\t', usecols = ['EXT_AN_IN_1'],  dtype = np.float32)
en2DF = pd.read_csv(resultFile, sep='\t', usecols = ['EXT_AN_IN_2'],  dtype = np.float32)

voltage = []
irr = []
curr = []
en = []
en1 = []
en2 = []

for _, v in VoltageDF.itertuples():
    voltage.append(v)

for _, s in irrDF.itertuples():
    irr.append(s)

for _, i in currDF.itertuples():
    curr.append(i)

for _, e in enDF.itertuples():
    en.append(e)

for _, e in en1DF.itertuples():
    en1.append(e)

for _, e in en2DF.itertuples():
    en2.append(e)

iterator = [[irr[i],curr[i]*voltage[i]] for i in range(21000, 40000, 1)]

x = np.array([(y/(i/10000 * 0.93 * 4/1000)) for i, y in iterator])

print(np.median(x))
#plt.plot(voltage)
#plt.plot(irr)
#plt.plot(en)
#plt.plot(en2)
plt.plot(x)
plt.axhline(np.median(x), color='r')
#plt.axhline(26, color='orange')
plt.show()