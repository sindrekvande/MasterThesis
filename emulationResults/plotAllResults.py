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

    if len(voltage0) > len(voltage1) and len(voltage0) > len(voltage2):
        timeDF = pd.read_csv(resultFiles[i], sep='\t', usecols = ['datetime'])
    elif len(voltage1) > len(voltage0) and len(voltage1) > len(voltage2):
        timeDF = pd.read_csv(resultFiles[i+1], sep='\t', usecols = ['datetime'])
    else:
        timeDF = pd.read_csv(resultFiles[i+2], sep='\t', usecols = ['datetime'])

    timeS = np.array([])
    for _, t in timeDF:
        try:
            timeCurr = datetime.strptime(t+'0000', datetime_strT)
        except:
            timeCurr = datetime.strptime(t+'0000', datetime_str)
        timeS.append(timeCurr)

    
    fig = plt.figure(figsize=(6,2.25))


    plt.ylabel('Voltage [V]')
    plt.xlabel('Time of day')
    plt.legend()
    xformatter = mdates.DateFormatter('%H:%M')
    plt.gcf().axes[0].xaxis.set_major_formatter(xformatter)
    #loc = ticker.MultipleLocator(base=1/12)
    #plt.gcf().axes[0].xaxis.set_major_locator(loc)
    fig.tight_layout()
    plt.savefig('emulationResults/allPlots/'+resultFiles[-15:-4]+'.pdf', format='pdf', bbox_inches="tight")