import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta
import time
#import scipy.interpolate as sc
from scipy.signal import savgol_filter


resultFile = 'emulationResults/Test_interval_240_2_2.7_200.tsv'

VoltageDF = pd.read_csv(resultFile, sep='\t', usecols = ['STORAGE_OUT'],  dtype = np.float32)
irrDF = pd.read_csv(resultFile, sep='\t', usecols = ['irrValue'],  dtype = np.float32)
currDF = pd.read_csv(resultFile, sep='\t', usecols = ['CSA_STORAGE_IN'],  dtype = np.float32)
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
timeS = []
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
    timeS.append(timeCurr)

for _, v in VoltageDF.itertuples():
    voltage.append(v)

for i, s in irrDF.itertuples():
    irr.append(s)
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


#iterator = [[irr[i],curr[i]*voltage[i]] for i in range(5000, 77000, 1)]
timeS = np.array(timeS) - timedelta(hours=2, minutes=30) #20:55 to 03:18, 09:15 to 06:51
#for e in range(len(timeS)):
#    timeS[e] = timeS[e].strftime("%H%M%S")
#    timeS[e] = datetime.strptime(timeS[e], "%H%M%S")

#x = np.array([((i/10000 * 0.93 * 3/1000)/y) for i, y in iterator])
#x = np.array([y for _, y in iterator])
#irr = np.array([(i/10000 * 0.93 * 3/1000) for i, _ in iterator])

#xx = savgol_filter(x, 1001, 2)

#dif = irr / xx


dcdccurr = [dcdccsa[i] * dcdcbuf[i] for i in range(len(dcdccsa))]
timeS = np.array(timeS)
#print(np.mean(x))
plt.figure(figsize=(8,3))
plt.plot(timeS, voltage, label='Measured')
#plt.plot(voltageExp, label='Expected')
#plt.plot(irr)
plt.plot(timeS, dcdccurr)
#plt.plot(en)
#plt.plot(x)
#plt.axhline(np.mean(x), color='r')
#print(np.mean(dif))
#plt.plot(timeS, x, label='Unfiltered')
#plt.plot(timeS, xx, label='Filtered')
#plt.plot(timeS, irr, label='Expected', color='r')
#plt.ylim(top=2.8)
plt.ylabel('Voltage [V]')
plt.xlabel('Time of day')
xformatter = mdates.DateFormatter('%H:%M')
plt.gcf().axes[0].xaxis.set_major_formatter(xformatter)
plt.legend(loc='upper right')
plt.tight_layout()
#plt.plot(dif)

#plt.axhline(26, color='orange')
plt.show()