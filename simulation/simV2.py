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
        self.maxEnergy = 1/2 * capacitance * 2.95**2
        self.voltage = 0
        self.energy = 0
        self.capacitance = capacitance
        self.scale = scale

    def addEnergy(self, irr):
        self.energy += irr / 10000 * 0.93 * self.scale
        if self.energy > self.maxEnergy:
            self.energy = self.maxEnergy
        self.voltage = np.sqrt(2*self.energy/self.capacitance)
        return irr / 10000 * 0.93 * self.scale

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
    timeToSave      = 0.0617,    # should reflect 64kB RAM to flash write at 64MHz
    timeToRecover   = 0.00271,
    thresholdStart  = 3.2,      # nRF: 1.7 V–3.6 V supply voltage range
    thresholdStop   = 2.2,
    thresholdDead   = 1.7,
    season          = 'winter',
    scale           = 3/1000):

    btSize = sampleNum*sampleSize
    
    capacitorSize /= 1000

    measurePower        = 4 * 10 ** -3 * 3
    communicatePower    = 1.7 * 10 ** -3 * 3
    sleepPower          = 2.4 * 10 ** -6 * 3
    deepSleepPower      = 0.7 * 10 ** -6 * 3
    checkpointPower     = 3.0 * 10 ** -3 * 3
    recoverPower        = 3.7 * 10 ** -3 * 3
    measureTime         = sampleSize/200
    communicateTime     = 3.5 + (btSize//10 + (1 if btSize%10 else 0)) *0.009

    interval = 'Interval'
    adc = 'ADC'
    svs = 'SVS'
    schemes = [interval, adc, svs]
    trace = fh.file(season, day).brightnessDF
    measure, sleep, deepSleep, communicate, dead, checkpoint, recover = False, False, False, False, True, False, False
    #states = [measure, sleep, communicate, dead]
    nextState = measure
    irrTrace = ['Solar trace']
    timeResults = [[], [], [], []]
    barResults = []
    energyBar = []
    energies = {'checkpoint'    : (timeToSave*sampleNum*sampleSize/100) * checkpointPower,
                'recover'       : (timeToRecover*sampleNum*sampleSize/100) * recoverPower,
                'measure'       : measurePower*measureTime,
                'communicate'   : communicatePower*communicateTime,
                'sleep'         : sleepPower,
                'deepsleep'     : deepSleepPower,
                'svspower'      : 0.5 * 10 ** -6 * 3} #2.2 * 0.8 * 10 ** -6}
    for sCount, s in enumerate(schemes):
        capacitor = energyStorage(capacitorSize, scale)
        voltage = [s]
        timesMeasured = 0
        measureEnergy = 0
        measureEnergyUsed = 0
        measureEnergySaved = 0
        timesCommunicated = 0
        communicateEnergy = 0
        timesCheckpointed = 0
        checkpointEnergy = 0
        checkpointCheckEnergy = 0
        timesRecovered = -1
        recoverEnergy = 0
        sleepCount = sleepTime
        sleepEnergy = 0
        deepSleepEnergy = 0
        totalEnergy = 0
        measureCount = sampleNum
        totalEnergyIn = 0
        communicatedBool = False
        flag = 1
        
        for x, irrValue in trace.itertuples():
            for i in range(60):
                totalEnergyIn += capacitor.addEnergy(irrValue)
                energyUse = 0
                if capacitor.voltage >= 2.4 and flag:
                    print(x)
                    print(totalEnergyIn)
                    flag = 0
                if capacitor.voltage < thresholdDead:
                    dead = True
                if not dead:
                    if s == svs:
                        energyUse += energies['svspower']
                        checkpointCheckEnergy += energies['svspower']
                    if not deepSleep:
                        if not sleep:
                            if measureCount <= 0:
                                measureEnergyUsed += measureEnergy
                                measureEnergy = 0
                                energyUse += energies['communicate'] - energies['sleep'] * communicateTime
                                communicateEnergy += energies['communicate']
                                sleepEnergy -= energies['sleep'] * communicateTime
                                measureCount = sampleNum
                                timesCommunicated += 1
                                communicatedBool = True
                                if s == interval:
                                    energyUse += energies['checkpoint'] - energies['sleep'] * timeToSave
                                    timesCheckpointed += 1
                                    checkpointEnergy += energies['checkpoint']
                                    sleepEnergy -= energies['sleep'] * (timeToSave)
                                elif s == adc:
                                    energyUse += energies['measure'] / sampleSize
                                    checkpointCheckEnergy += energies['measure'] / sampleSize
                                    if (capacitor.voltage < thresholdStop):
                                        energyUse += energies['checkpoint'] - energies['sleep'] * (timeToSave)
                                        checkpointEnergy += energies['checkpoint']
                                        sleepEnergy -= energies['sleep'] * (timeToSave)
                                        timesCheckpointed += 1
                                        deepSleep = True
                            measureCount -= 1
                            energyUse += energies['measure'] + energies['sleep']* (1 - measureTime)
                            measureEnergy += energies['measure']
                            sleepEnergy += energies['sleep']* (1 - measureTime)
                            timesMeasured +=1
                            
                            if s == interval:
                                energyUse += energies['checkpoint'] - energies['sleep'] * timeToSave
                                timesCheckpointed += 1
                                checkpointEnergy += energies['checkpoint']
                                sleepEnergy -= energies['sleep'] * (timeToSave)
                            elif s == adc:
                                energyUse += energies['measure'] / sampleSize
                                checkpointCheckEnergy += energies['measure'] / sampleSize
                                if (capacitor.voltage < thresholdStop):
                                    energyUse += energies['checkpoint'] - energies['sleep'] * (timeToSave)
                                    checkpointEnergy += energies['checkpoint']
                                    sleepEnergy -= energies['sleep'] * (timeToSave)
                                    timesCheckpointed += 1
                                    deepSleep = True
                            if sleepTime > 1:
                                sleep = True
                                sleepCount = sleepTime - 1 + (4 if communicatedBool else 0)
                                if communicatedBool:
                                    communicatedBool = False
                        else:
                            energyUse += energies['sleep']
                            sleepEnergy += energies['sleep']
                            sleepCount -= 1
                            if sleepCount <= 0:
                                sleep = False
                                sleepCount = sleepTime
                        if (capacitor.voltage < thresholdStop) and (s == svs):
                                energyUse += energies['checkpoint'] - energies['sleep'] * (timeToSave)
                                checkpointEnergy += energies['checkpoint']
                                sleepEnergy -= energies['sleep'] * (timeToSave)
                                timesCheckpointed += 1
                                deepSleep = True
                        
                    else:
                        if capacitor.voltage > thresholdStart:
                            energyUse += energies['recover'] + energies['deepsleep']*(1-timeToRecover)
                            recoverEnergy += energies['recover']
                            deepSleepEnergy += energies['deepsleep']*(1-timeToRecover)
                            measureEnergySaved += measureEnergy
                            measureEnergy = 0
                            deepSleep = False
                            timesRecovered += 1
                        else:
                            energyUse += energies['deepsleep']
                            deepSleepEnergy += energies['deepsleep']
                else:
                    if capacitor.voltage > thresholdStart:
                        energyUse += energies['recover']
                        recoverEnergy += energies['recover']
                        measureEnergySaved += measureEnergy
                        measureEnergy = 0
                        timesRecovered += 1
                        dead = False
                        deepSleep = False
                totalEnergy += energyUse
                capacitor.useEnergy(energyUse)
                voltage.append(capacitor.voltage)
                if s == svs:
                    irrTrace.append(irrValue)

        print(totalEnergyIn)
        timeResults[sCount] = voltage
        if s == svs:
            timeResults[sCount + 1] = irrTrace
        barResults.append([s, timesCheckpointed, timesRecovered, timesMeasured, timesCommunicated])
        energyBar.append([s, measureEnergyUsed, measureEnergySaved, communicateEnergy, checkpointEnergy, checkpointCheckEnergy, recoverEnergy, sleepEnergy, deepSleepEnergy, totalEnergy])
    del voltage, irrTrace, capacitor, timesMeasured, timesCommunicated, timesCheckpointed, timesRecovered
    return timeResults, barResults, energyBar

def plotGraphs(barLoc, energyLoc, timeLoc, timeResults, barResults, energyBar, metrics, params):
    barWidth = 0.2
    x = np.arange(len(metrics))
    fig = plt.figure(figsize=(10,6))
    colors = ['#0089B3', '#00556F', '#00C4FF']

    for i in range(3):
        plt.bar(x+barWidth*(i-1), barResults[i][1:], width=barWidth, label=barResults[i][0], color=colors[i])
        for j, v in enumerate(barResults[i][1:]):
            plt.text(j+barWidth*(i-1), v, str(v), color=colors[i], horizontalalignment='center', verticalalignment='bottom')
    plt.xticks(x, metrics)
    plt.ylabel('Number of times')
    plt.xlabel('Metric')
    plt.legend(loc='best')
    plt.savefig(barLoc, bbox_inches="tight")
    plt.cla()
    plt.close()

    x = np.arange(3)
    fig = plt.figure(figsize=(6,6))
    energyBar = [list(l) for l in zip(*energyBar)]
    bot = [0]*len(energyBar[0])
    labels = ['measureUsed', 'measureSaved', 'communicate', 'checkpoint', 'checkpointCheck', 'recover', 'sleep', 'deepSleep']
    for i in range(1, len(energyBar)-1):
        plt.bar(x, energyBar[i], bottom=bot, width=.9, label=labels[i-1])
        bot = [a + b for a, b in zip(bot, energyBar[i])]
    #plt.bar(x + 0.25, energyBar[-1], width=0.5)
    plt.xticks(x, energyBar[0])
    plt.ylabel('Energy use [J]')
    plt.xlim(-1.5, 3.5)
    plt.legend(loc='best')
    plt.savefig(energyLoc, bbox_inches="tight")
    plt.cla()
    plt.close()

    timeAxis = np.linspace(start=0, stop=24, num=len(timeResults[0][1:]))
    timeAxisTicks = np.arange(0, 24, step=1)
    fig = plt.figure(figsize=(10,7))
    gs = fig.add_gridspec(4, hspace=0)
    ax = gs.subplots(sharex=True, sharey=False)
    for i in range(3):
        ax[i].plot(timeAxis, timeResults[i][1:], label=timeResults[i][0])
        ax[i].set(ylabel='Voltage [V]', xticks=timeAxisTicks)
        ax[i].legend(loc="upper right")
        ax[i].margins(x=0)
        ax[i].axhline(2.95, color='grey', ls='--')
        ax[i].axhline(params['start'], color='green', ls='--')
        if i != 0:
            ax[i].axhline(params['stop'], color='orange', ls='--')
        ax[i].axhline(1.7, color='red', ls='--')
    ax[3].plot(timeAxis, timeResults[3][1:], label=timeResults[3][0], color=('#ffae49' if params['season'] =='summer' else '#44a5c2' if params['season'] =='autumn' else '#024b7a'))
    ax[3].set(xlabel='Time of day', ylabel='Solar irradiance [W/m$^2$]', xticks=timeAxisTicks, ylim=[-10,1300])
    ax[3].legend(loc="upper right")
    ax[3].margins(x=0)
    
    fig.tight_layout()
    plt.savefig(timeLoc, bbox_inches="tight")
    plt.cla()
    plt.close()

def multiSim():
    headers = ['Season', 'Day', 'Capacitance [mF]', 'SampleNum', 'SampleSize', 'Sleep', 'Start', 'Stop', '', 'Resulting metrics', 'Energy Use', 'Time plot']
    metrics = ['Checkpointed', 'Recovered', 'Measured', 'Communicated']
    simSetFile = 'simSet9'
    #os.rmdir('simulation/results/'+simSetFile+'Results')
    os.makedirs('simulation/results/'+simSetFile+'Results')
    resultLoc = 'simulation/results/'+simSetFile+'Results/'+simSetFile+'.xlsx'

    simSet = pd.read_csv('simulation/'+simSetFile+'.tsv', sep='\t')

    xl.createExcel(resultLoc, headers)
    for i, row in simSet.iterrows():
        params = [row['season'], row['day'], row['capacitance'], row['sampleNum'], row['sampleSize'], row['sleep'], row['start'], row['stop']]
        print('Sim\t', str(i+1)+'/'+str(len(simSet))+':', params)
        timeLoc = 'simulation/results/'+simSetFile+'Results/'+simSetFile+'_time_'+str(row['season'])+str(row['day'])+'_'+str(int(row['capacitance']))+'mF'+'_sampleNum'+str(row['sampleNum'])+'_sampleSize'+str(row['sampleSize'])+'_sleep'+str(row['sleep'])+'_start'+str(row['start'])+'_stop'+str(row['stop'])+'.png'
        barLoc = 'simulation/results/'+simSetFile+'Results/'+simSetFile+'_bar_'+str(row['season'])+str(row['day'])+'_'+str(int(row['capacitance']))+'mF'+'_sampleNum'+str(row['sampleNum'])+'_sampleSize'+str(row['sampleSize'])+'_sleep'+str(row['sleep'])+'_start'+str(row['start'])+'_stop'+str(row['stop'])+'.png'
        energyLoc = 'simulation/results/'+simSetFile+'Results/'+simSetFile+'_energy_'+str(row['season'])+str(row['day'])+'_'+str(int(row['capacitance']))+'mF'+'_sampleNum'+str(row['sampleNum'])+'_sampleSize'+str(row['sampleSize'])+'_sleep'+str(row['sleep'])+'_start'+str(row['start'])+'_stop'+str(row['stop'])+'.png'
        
        timeResults, barResults, energyBar = singleSim(sampleNum       = row['sampleNum'],
                                                        sampleSize      = row['sampleSize'],
                                                        sleepTime       = row['sleep'],
                                                        day             = row['day'],
                                                        capacitorSize   = row['capacitance'],
                                                        thresholdStart  = row['start'],
                                                        thresholdStop   = row['stop'],
                                                        season          = row['season'],
                                                        scale           = 3/1000 * (8.618893646327617/6.3966938148805825 if row['day'] == 10 else 1))
        
        plotGraphs(barLoc, energyLoc, timeLoc, timeResults, barResults, energyBar, metrics, row)

        xl.writeExcel(resultLoc, params, barLoc, energyLoc, timeLoc)

multiSim()