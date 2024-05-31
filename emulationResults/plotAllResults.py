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
    resultFiles = np.array(f.read().splitlines())

for i in range(0, len(resultFiles), 3):
    VoltageDF0 = pd.read_csv(resultFiles[i], sep='\t', usecols = ['STORAGE_OUT'],  dtype = np.float32)
    VoltageDF1 = pd.read_csv(resultFiles[i+1], sep='\t', usecols = ['STORAGE_OUT'],  dtype = np.float32)
    VoltageDF2 = pd.read_csv(resultFiles[i+2], sep='\t', usecols = ['STORAGE_OUT'],  dtype = np.float32)

    voltage0 = np.array([])
    voltage1 = np.array([])
    voltage2 = np.array([])

    for _, v in VoltageDF0.itertuples():
        voltage0.append(v)

    for _, v1 in VoltageDF1.itertuples():
        voltage1.append(v1)

    for _, v2 in VoltageDF2.itertuples():
        voltage2.append(v2)

    timeDF = pd.read_csv(resultFiles[np.argmax(np.array([len(voltage0),len(voltage1),len(voltage2)]))], sep='\t', usecols = ['datetime'])

    timeS = np.array([])
    for _, t in timeDF:
        try:
            timeCurr = datetime.strptime(t+'0000', datetime_strT)
        except:
            timeCurr = datetime.strptime(t+'0000', datetime_str)
        timeS.append(timeCurr)

    voltages = np.array([voltage0, voltage1, voltage2])
    labels = np.array(['Interval', 'ADC', 'LPCOMP'])
    
    fig = plt.figure(figsize=(6,6))
    gs = fig.add_gridspec(4, hspace=0)
    ax = gs.subplots(sharex=True, sharey=False)
    for i in range(3):
        ax[i].plot(timeS, voltages[i], label=labels[i])
        ax[i].set(ylabel='Voltage [V]')
        ax[i].legend(loc="upper right")
        ax[i].margins(x=0)
        ax[i].axhline(3.0, color='grey', ls='--')
        ax[i].axhline(2.7, color='green', ls='--')
        if i != 0:
            ax[i].axhline(1.9, color='orange', ls='--')
        ax[i].axhline(1.7, color='red', ls='--')
    ax[3].plot(timeS, voltages, label='LED', color='gold')
    ax[3].axhline(0.5, color='grey', ls='--')
    ax[3].set(xlabel='Time of day', ylabel='Brightness [%]')
    ax[3].legend(loc="upper right")
    ax[3].margins(x=0)
    plt.legend()
    xformatter = mdates.DateFormatter('%H:%M')
    plt.gcf().axes[0].xaxis.set_major_formatter(xformatter)
    #loc = ticker.MultipleLocator(base=1/12)
    #plt.gcf().axes[0].xaxis.set_major_locator(loc)
    fig.tight_layout()
    plt.savefig('emulationResults/allPlots/'+resultFiles[-15:-4]+'.pdf', format='pdf', bbox_inches="tight")