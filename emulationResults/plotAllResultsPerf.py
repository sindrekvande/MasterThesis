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

fileNamesFile = "emulationResults/resultFilesPerfLoc.txt"

rc('font',**{'family':'serif','serif':['Times New Roman']})

resultFiles = np.array([])
with open(fileNamesFile) as f:
    resultFiles = f.read().splitlines()
#print(resultFiles)
metrics = ['Checkpoint', 'Recover', 'Sample', 'Communicate']
fileMetrics = ['Checkpoint count', 'Recover count', 'Sampling count', 'Communication count']
labels = ['Interval', 'ADC', 'LPCOMP']
for i in range(0, len(resultFiles), 3):
    PerfDF0 = pd.read_csv(resultFiles[i], columns=fileMetrics, sep='\t', dtype=np.int16)
    PerfDF1 = pd.read_csv(resultFiles[i+1], columns=fileMetrics, sep='\t', dtype=np.int16)
    PerfDF2 = pd.read_csv(resultFiles[i+2], columns=fileMetrics, sep='\t', dtype=np.int16)
    

    barResults = []
    barResults[0] = [(PerfDF0.at[-1, 1] - PerfDF0.at[0, 1]), (PerfDF0.at[-1, 2] - PerfDF0.at[0, 2]), (PerfDF0.at[-1, 3] - PerfDF0.at[0, 3]), (PerfDF0.at[-1, 4] - PerfDF0.at[0, 4])]
    barResults[1] = [(PerfDF1.at[-1, 1] - PerfDF1.at[0, 1]), (PerfDF1.at[-1, 2] - PerfDF1.at[0, 2]), (PerfDF1.at[-1, 3] - PerfDF1.at[0, 3]), (PerfDF1.at[-1, 4] - PerfDF1.at[0, 4])]
    barResults[2] = [(PerfDF2.at[-1, 1] - PerfDF2.at[0, 1]), (PerfDF2.at[-1, 2] - PerfDF2.at[0, 2]), (PerfDF2.at[-1, 3] - PerfDF2.at[0, 3]), (PerfDF2.at[-1, 4] - PerfDF2.at[0, 4])]

    barWidth = 0.3
    x = np.arange(len(metrics))
    fig = plt.figure(figsize=(4.67,4))
    colors = ['#80c2c2', '#008585', '#74a892']#['#0089B3', '#00556F', '#00C4FF']

    for i in range(3):
        plt.bar(x+barWidth*(i-1), barResults[i], width=barWidth, label=labels[i], color=colors[i])
        for j, v in enumerate(barResults[i]):
            plt.text(j+barWidth*(i-1), v, str(v), color=colors[i], horizontalalignment='center', verticalalignment='bottom')
    plt.xticks(x, metrics)
    plt.ylabel('Number of times')
    plt.xlabel('Metric')
    plt.legend(loc='best')
    fig.tight_layout()
    plt.savefig('emulationResults/allPerfPlots/'+resultFiles[i][-19:-4]+'.pdf', format='pdf', bbox_inches="tight")
    #plt.show()
    plt.cla()
    plt.close()