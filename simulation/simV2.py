import file_handler as fh
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime as time
import pandas as pd
import gc
import os
import xl_handler as xl

class energyStorage:
    # C = (ε0 * A) / d
    # E = (Q * V) / 2 = C*V**2 / 2
    # V = sqrt(2*E/C)
    def __init__(self, capacitance, scale):
        self.maxEnergy = 1/2 * capacitance * 3.3**2
        self.voltage = 0
        self.energy = 0
        self.capacitance = capacitance
        self.scale = scale

    def addEnergy(self, irr):
        self.energy += irr / 10000 * 0.93 * self.scale
        if self.energy > self.maxEnergy:
            self.energy = self.maxEnergy
        self.voltage = np.sqrt(2*self.energy/self.capacitance)

    def useEnergy(self, energy):
        if self.energy < energy:
            self.energy = 0
            self.voltage = 0
        else:
            self.energy -= energy
            self.voltage = np.sqrt(2*self.energy/self.capacitance)
        return self.energy

def singleSim(
    ############## Parameters ###############
    sampleNum       = 10,       # samples before com
    sampleSize      = 10,       # measurements in one sample
    sleepTime       = 10,       # in seconds
    day             = 11,       # which day of the month
    capacitorSize   = 476,      # in milliFarad
    timeToSave      = 0.1,      # should reflect 64kB RAM to flash write at 64MHz
    timeToRecover   = 0.1,
    thresholdStart  = 3.2,      # nRF: 1.7 V–3.6 V supply voltage range
    thresholdStop   = 2.2,
    thresholdDead   = 1.7,
    season          = 'winter',
    scale           = 3/1000):

    btSize = sampleNum*sampleSize*12
    
    capacitorSize /= 1000

    measurePower        = 8 * 10 ** -3 * 3
    communicatePower    = 9 * 10 ** -3 * 3
    sleepPower          = 1.9 * 10 ** -6 * 3
    measureTime         = sampleSize/200
    comunicateTime      = btSize/10**6

    interval = 'iterval'
    adc = 'adc'
    svs = 'svs'
    schemes = [interval, adc, svs]
    trace = fh.file(season, day).brightnessDF
    measure, sleep, deepSleep, communicate, dead, checkpoint, recover = False, False, False, False, True, False, False
    #states = [measure, sleep, communicate, dead]
    nextState = measure
    irrTrace = ['irradiance']
    timeResults = [[]]
    barResults = [[]]
    for s in schemes:
        capacitor = energyStorage(capacitorSize, scale)
        voltage = [s]
        timesMeasured = 0
        timesCommunicated = 0
        timesCheckpointed = 0
        timesRecovered = 0
        for _, irrValue in trace.itertuples():
            for i in range(60):
                capacitor.addEnergy(irrValue)
                if not dead:
                    if measure:

                        if communicate:
                            communicate = False
                    else:
                        sleep = True
                    if capacitor.voltage < thresholdDead:
                        dead = True
                else:
                    if capacitor.voltage > thresholdStart:
                        dead = False
                voltage.append(capacitor.voltage)
                if s == svs:
                    irrTrace.append(irrValue)

        timeResults.append(voltage)
        if s == svs:
            timeResults.append(irrValue)
        barResults.append([s, timesMeasured, timesCommunicated, timesCheckpointed, timesRecovered])
    del voltage, irrValue, capacitor, timesMeasured, timesCommunicated, timesCheckpointed, timesRecovered
    return timeResults, barResults

def plotGraphs(barLoc, timeLoc, timeResults, barResults):
    pass

def multiSim():
    headers = ['Season', 'Day', 'Capacitance [mF]', 'Samples', 'Sleep', 'Start', 'Stop', '', 'Resulting metrics', 'Time plot']
    metrics = ['Checkpointed', 'Recovered', 'Measured', 'Communicated']
    simSetFile = 'simSet1'
    os.makedirs('simulation/results/'+simSetFile+'Results')
    resultLoc = 'simulation/results/'+simSetFile+'Results/'+simSetFile+'.xlsx'

    simSet = pd.read_csv('simulation/'+simSetFile+'.tsv', sep='\t')

    xl.createExcel(resultLoc, headers)
    for i, row in simSet.iterrows():
        params = [row['season'], row['day'], row['capacitance'], row['samples'], row['sleep'], row['start'], row['stop']]
        print('Sim\t', str(i+1)+'/'+str(len(simSet))+':', params)
        timeLoc = 'simulation/results/autosim_time_'+str(row['season'])+str(row['day'])+'_'+str(int(row['capacitance']))+'mF'+'_adc'+str(row['samples'])+'_sleep'+str(row['sleep'])+'_start'+str(row['start'])+'_stop'+str(row['stop'])+'.png'
        barLoc = 'simulation/results/autosim_bar_'+str(row['season'])+str(row['day'])+'_'+str(int(row['capacitance']))+'mF'+'_adc'+str(row['samples'])+'_sleep'+str(row['sleep'])+'_start'+str(row['start'])+'_stop'+str(row['stop'])+'.png'
        
        timeResults, barResults = singleSim()

        plotGraphs(barLoc, timeLoc, timeResults, barResults)