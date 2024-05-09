import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import time
#import scipy.interpolate as sc


resultFile = 'emulationResults/Test8.tsv'

VoltageDF = pd.read_csv(resultFile, sep='\t', usecols = ['STORAGE_OUT'],  dtype = np.float32)
irrDF = pd.read_csv(resultFile, sep='\t', usecols = ['irrValue'],  dtype = np.float32)
currDF = pd.read_csv(resultFile, sep='\t', usecols = ['CSA_EH_IN'],  dtype = np.float32)
enDF = pd.read_csv(resultFile, sep='\t', usecols = ['DCDC_OUT_BUF'],  dtype = np.float32)
en1DF = pd.read_csv(resultFile, sep='\t', usecols = ['EXT_AN_IN_1'],  dtype = np.float32)
timeDF = pd.read_csv(resultFile, sep='\t', usecols = ['datetime'])
dcdccsaDF = pd.read_csv(resultFile, sep='\t', usecols = ['CSA_DCDC_OUT'],  dtype = np.float32)
dcdcbufDF = pd.read_csv(resultFile, sep='\t', usecols = ['DCDC_OUT_BUF'],  dtype = np.float32)

voltage = []
voltageExp = []
irr = []
curr = []
en = []
en1 = []
dcdccsa = []
dcdcbuf = []
dcdccurr = []
timeL = []
capacitance = 200 * 10 ** (-3)
#capacitance = 385 * 10 ** (-3)
energy = 0 #1.93 ** 2 * capacitance / 2
datetime_str = '%Y-%m-%d %H:%M:%S.%f'

for i, t in timeDF.itertuples():
    if i == 0:
        timeCurr = datetime.strptime(t+'0000', datetime_str)
    timePrev = timeCurr
    timeCurr = datetime.strptime(t+'0000', datetime_str)
    timeDiff = timeCurr - timePrev
    timeL.append(timeDiff.total_seconds())

for _, v in VoltageDF.itertuples():
    voltage.append(v)

for i, s in irrDF.itertuples():
    irr.append(s/333)
    energy += s/10000 * 0.93 * 3/1000 *timeL[i]
    volt = np.sqrt(2*energy/capacitance)
    if volt > 3.3:
        volt = 3.3
    voltageExp.append(volt)

for _, i in currDF.itertuples():
    curr.append(i)

for _, e in enDF.itertuples():
    en.append(e)

for _, e in en1DF.itertuples():
    en1.append(e)

for _, c in dcdccsaDF.itertuples():
    dcdccsa.append(c)

for _, b in dcdcbufDF.itertuples():
    dcdcbuf.append(b)


#iterator = [[irr[i],curr[i]*voltage[i]] for i in range(21000, 40000, 1)]

#x = np.array([(y/(i/10000 * 0.93 * 3/1000)) for i, y in iterator])

dcdccurr = [dcdccsa[i] * dcdcbuf[i] for i in range(len(dcdccsa))]

#print(np.median(x))
plt.plot(voltage)
plt.plot(voltageExp)
plt.plot(irr)
plt.plot(dcdccurr)
plt.plot(en)
#plt.plot(x)
#plt.axhline(np.median(x), color='r')
#plt.axhline(26, color='orange')
plt.show()