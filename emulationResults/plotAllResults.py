import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib import rc
import numpy as np
from datetime import datetime, timedelta
import time
#import scipy.interpolate as sc
from scipy.signal import savgol_filter

fileNamesFile = "emulationResults/resultFilesLoc.txt"

datetime_strT = '%Y-%m-%dT%H:%M:%S.%f'
datetime_str = '%Y-%m-%d %H:%M:%S.%f'

rc('font',**{'family':'serif','serif':['Times New Roman']})

resultFiles = np.array([])
with open(fileNamesFile) as f:
    resultFiles = f.read().splitlines()
#print(resultFiles)
for i in range(0, len(resultFiles), 3):
    VoltageDF0 = pd.read_csv(resultFiles[i], sep='\t', usecols = ['STORAGE_OUT'],  dtype = np.float32)
    VoltageDF1 = pd.read_csv(resultFiles[i+1], sep='\t', usecols = ['STORAGE_OUT'],  dtype = np.float32)
    VoltageDF2 = pd.read_csv(resultFiles[i+2], sep='\t', usecols = ['STORAGE_OUT'],  dtype = np.float32)
    
    voltage0 = []
    voltage1 = []
    voltage2 = []

    for _, v in VoltageDF0.itertuples():
        voltage0.append(v)

    for _, v1 in VoltageDF1.itertuples():
        voltage1.append(v1)

    for _, v2 in VoltageDF2.itertuples():
        voltage2.append(v2)

    voltage0 = np.array(voltage0)
    voltage1 = np.array(voltage1)
    voltage2 = np.array(voltage2)

    timeDF = pd.read_csv(resultFiles[i+ np.argmax([len(voltage0),len(voltage1),len(voltage2)])], sep='\t', usecols = ['datetime'])
    ledDF = pd.read_csv(resultFiles[i+ np.argmax([len(voltage0),len(voltage1),len(voltage2)])], sep='\t', usecols = ['ledPercent'])

    timeS = []
    led = []

    for x, t in timeDF.itertuples():
        try:
            timeCurr = datetime.strptime(t+'0000', datetime_strT)
            if x == 0:
                start = t + '0000'
                start_str = datetime_strT
        except:
            timeCurr = datetime.strptime(t+'0000', datetime_str)
            if x == 0:
                start = t + '0000'
                start_str = datetime_str
        timeS.append(timeCurr)

    timeS = np.array(timeS)

    for _, l in ledDF.itertuples():
        led.append(l*100)

    print(resultFiles[i][-19:-13])
    if resultFiles[i][-19:-13] == '02_147':
        timeS = timeS - (timeS[0] - datetime.strptime(start[:-15]+'06:17'+start[-10:], start_str))
    elif resultFiles[i][-19:-13] == '02_200':
        timeS = timeS - (timeS[0] - datetime.strptime(start[:-15]+'06:38'+start[-10:], start_str))
    elif resultFiles[i][-19:-13] == '02_100':
        timeS = timeS - (timeS[0] - datetime.strptime(start[:-15]+'05:51'+start[-10:], start_str))
    elif resultFiles[i][-19:-13] == '02_294':
        timeS = timeS - (timeS[0] - datetime.strptime(start[:-15]+'07:11'+start[-10:], start_str))
    elif resultFiles[i][-19:-13] == '10_147':
        timeS = timeS - (timeS[0] - datetime.strptime(start[:-15]+'06:32'+start[-10:], start_str))

    voltages = [voltage0, voltage1, voltage2]
    #voltages = np.array(voltages)
    labels = np.array(['Interval', 'ADC', 'LPCOMP'])
    
    fig = plt.figure(figsize=(6,4.66))
    gs = fig.add_gridspec(4, hspace=0)
    ax = gs.subplots(sharex=True, sharey=False)
    for y in range(3):
        ax[y].plot(timeS[:len(voltages[y])], voltages[y], label=labels[y], color='#008585',zorder=20,linewidth=1)
        ax[y].set(ylabel='Voltage [V]')
        ax[y].legend(loc="lower right")
        ax[y].margins(x=0)
        ax[y].axhline(3.0, color='grey', ls='--',zorder=10, linewidth=1)
        ax[y].axhline(2.7, color='#74a892', ls='--',zorder=10, linewidth=1)
        if y != 0:
            ax[y].axhline(1.9, color='#d68a58', ls='--',zorder=10, linewidth=1)
        ax[y].axhline(1.7, color='#642915', ls='--',zorder=10, linewidth=1)
        ax[y].set(ylim=[-.1, 3.5], yticks=[0,1,2,3])
    ax[3].plot(timeS, led, label='LED', color='#d68a58', linewidth=1)
    ax[3].axhline(0.5, color='grey', ls='--', linewidth=1)
    ax[3].set(xlabel='Time of day', ylabel='Brightness [%]')
    ax[3].legend(loc="upper right")
    ax[3].margins(x=0)
    ax[3].legend(loc="upper right")
    ax[3].set(ylim=[-.1, 3.5],  yticks=[0,1,2,3])
    xformatter = mdates.DateFormatter('%H:%M')
    plt.gcf().axes[0].xaxis.set_major_formatter(xformatter)
    #loc = ticker.MultipleLocator(base=1/12)
    #plt.gcf().axes[0].xaxis.set_major_locator(loc)
    plt.xlim(right=datetime.strptime(start[:-15]+'18:00'+start[-10:], start_str))
    fig.tight_layout()
    plt.savefig('emulationResults/allPlots/'+resultFiles[i][-19:-4]+'.pdf', format='pdf', bbox_inches="tight")
    #plt.show()
    plt.cla()
    plt.close()