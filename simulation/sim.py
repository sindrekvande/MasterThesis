import file_handler as fh
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime as time
import pandas as pd
import gc
import os
#import openpyxl as xl

import xl_handler as xl
# take in solar trace
# feed solar trace to simulated energy storage
# do work (measure, communicate, sleep) in state machine

def get_solar_trace():
    # use file_handler
    pass

class energyStorage:
    # C = (ε0 * A) / d
    # E = (Q * V) / 2 = C*V**2 / 2
    # V = sqrt(2*E/C)
    def __init__(self, timeStep, capacitance, maxVolt, solarCellSize):
        self.maxEnergy = 1/2 * capacitance * maxVolt**2
        self.voltage = 0
        self.energy = 0
        self.capacitance = capacitance
        self.timeStep = timeStep
        self.solarCellSize = solarCellSize

    def addEnergy(self, irr):
        self.energy += irr * self.timeStep / 10000 * self.solarCellSize
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

class states:
    measurePower       = 8 * 10 ** -3 * 3
    communicatePower   = 9 * 10 ** -3 * 3
    sleepPower         = 1.9 * 10 ** -6 * 3
    def __init__(self, timeStep, capacitor: energyStorage):
        self.timeStep = timeStep

    def measure(self, capacitor: energyStorage):
        capacitor.useEnergy(self.measurePower * self.timeStep)
        
    def communicate(self, capacitor: energyStorage):
        capacitor.useEnergy(self.communicatePower * self.timeStep)

    def sleep(self, capacitor: energyStorage):
        capacitor.useEnergy(self.sleepPower * self.timeStep)

class checkpoint:
    # 58 μA/MHz running from flash memory
    powerUse = 58 * 10 ** -6 * 64 * 3.3
    def __init__(self, timeStep):
        self.timeStep = timeStep

    def save(self, capacitor: energyStorage):
        capacitor.useEnergy(self.powerUse * self.timeStep)

    def recover(self, capacitor: energyStorage):
        capacitor.useEnergy(self.powerUse * self.timeStep)

def main(
    ############## Parameters ###############
    timeStep            = 1*10**-3,  # millisecond
    adcSamples          = 3000,      # 200 samples per second
    btSize              = None,      # should be atleast adcSamples*122
    sleepTime           = 60*10,     # in seconds
    numDays             = 11,        # which day of the month
    capacitorSize       = 476*10**-3, # in Farad
    solarCellSize       = 1,         # in cm^2
    maxVoltageOut       = 3.3,
    timeToSave          = 0.1,       # should reflect 64kB RAM to flash write at 64MHz
    timeToRecover       = 0.1,
    thresholdStart      = 3.2,       # nRF: 1.7 V–3.6 V supply voltage range
    thresholdStop       = 2.2,
    thresholdDead       = 1.7,
    season              = 'winter',
    timeLoc             = None):
    if btSize is None:
        btSize = adcSamples*12
    if timeLoc is None:
        timeLoc = 'simulation/results/autosim_time_'+str(season)+str(numDays)+'_'+str(int(capacitorSize*1000))+'mF'+'_adc'+str(adcSamples)+'_sleep'+str(sleepTime)+'_start'+str(thresholdStart)+'_stop'+str(thresholdStop)+'.png' 
    thresholdStartINT   = thresholdStart
    #testToDo            = "all"     # svs, adc, int or all
    ########################################
    start = time.now()
    trace = fh.file(season, numDays).brightnessDF
    capacitorSVS = energyStorage(timeStep, capacitorSize, maxVoltageOut, solarCellSize)
    capacitorADC = energyStorage(timeStep, capacitorSize, maxVoltageOut, solarCellSize)
    capacitorINT = energyStorage(timeStep, capacitorSize, maxVoltageOut, solarCellSize)
    stateSVS = states(timeStep, capacitorSVS)
    stateADC = states(timeStep, capacitorADC)
    stateINT = states(timeStep, capacitorINT)
    JITsvs = checkpoint(timeStep)
    JITadc = checkpoint(timeStep)
    interval = checkpoint(timeStep)
    
    voltageSVS = []
    voltageADC = []
    voltageINT = []
    irrTrace = []
    # SVS
    nextstateSVS = "dead"
    measureCounterSVS = adcSamples/200/timeStep
    comCounterSVS = btSize/1000000/timeStep
    sleepCounterSVS = sleepTime/timeStep
    checkpointedSVS = 0
    timeSavedSVS = 0
    timesRecoveredSVS = 0
    prevstateSVS = "measure"
    supplyCurrentSVS = 0.8 * 10 ** -6
    timeCheckpointedSVS = 0
    timesMeasuredSVS = 0
    timesCommunicatedSVS = 0

    nextstateADC = "dead"
    measureCounterADC = adcSamples/200/timeStep
    comCounterADC = btSize/1000000/timeStep
    sleepCounterADC = sleepTime/timeStep
    checkpointedADC = 0
    timeSavedADC = 0
    timesRecoveredADC = 0
    prevstateADC = "measure"
    timeCheckpointedADC = 0
    timesMeasuredADC = 0
    timesCommunicatedADC = 0

    nextstateINT = "dead"
    measureCounterINT = adcSamples/200/timeStep
    comCounterINT = btSize/1000000/timeStep
    sleepCounterINT = sleepTime/timeStep
    checkpointedINT = 0
    timeSavedINT = 0
    timesRecoveredINT = 0
    prevstateINT = "measure"
    timeCheckpointedINT = 0
    timesMeasuredINT = 0
    timesCommunicatedINT = 0
    

    saveCounterSVS = timeToSave/timeStep
    recoverCounterSVS = timeToRecover/timeStep

    saveCounterADC = timeToSave/timeStep
    recoverCounterADC = timeToRecover/timeStep

    saveCounterINT = timeToSave/timeStep
    recoverCounterINT = timeToRecover/timeStep

    for _, irrValue in trace.itertuples():
        counter = 60/timeStep
        while counter > 0:
            capacitorSVS.addEnergy(irrValue)
            capacitorADC.addEnergy(irrValue)
            capacitorINT.addEnergy(irrValue)
            if capacitorSVS.voltage > thresholdDead:
                capacitorSVS.useEnergy(supplyCurrentSVS*timeStep*2.2)
            match nextstateSVS:
                case "recover":
                    recoverCounterSVS -= 1
                    JITsvs.recover(capacitorSVS)
                    if recoverCounterSVS <= 0:
                        timesRecoveredSVS += 1
                        timeSavedSVS += (adcSamples/200/timeStep + btSize/1000000/timeStep - comCounterSVS if comCounterSVS > 0 else 0) + (adcSamples/200/timeStep - measureCounterSVS if measureCounterSVS > 0 else 0)
                        nextstateSVS = prevstateSVS
                        recoverCounterSVS = timeToRecover/timeStep
                        comCounterSVS = btSize/1000000/timeStep
                case "save":
                    saveCounterSVS -= 1
                    JITsvs.save(capacitorSVS)
                    if saveCounterSVS <= 0:
                        nextstateSVS = "sleep"
                        checkpointedSVS = 1
                        sleepCounterSVS = sleepTime/timeStep
                        saveCounterSVS = timeToSave/timeStep
                        timeCheckpointedSVS += 1
                case "measure":
                    stateSVS.measure(capacitorSVS)
                    measureCounterSVS -= 1
                    if capacitorSVS.voltage < thresholdStop:
                        nextstateSVS = "save"
                        prevstateSVS = "measure"
                    elif measureCounterSVS <= 0:
                        timesMeasuredSVS += 1
                        nextstateSVS = "communicate"
                        comCounterSVS = btSize/1000000/timeStep
                case "communicate":
                    stateSVS.communicate(capacitorSVS)
                    comCounterSVS -= 1
                    if capacitorSVS.voltage < thresholdStop:
                        nextstateSVS = "sleep"
                        prevstateSVS = "communicate"
                        #sleepCounterSVS = sleepTime/timeStep
                        checkpointedSVS = 1
                    elif comCounterSVS <= 0:
                        timesCommunicatedSVS += 1
                        nextstateSVS = "sleep"
                        sleepCounterSVS = sleepTime/timeStep
                case "sleep":
                    stateSVS.sleep(capacitorSVS)
                    sleepCounterSVS -= 1
                    if capacitorSVS.voltage < thresholdDead:
                        nextstateSVS = "dead"
                    elif capacitorSVS.voltage > thresholdStart and checkpointedSVS:
                        nextstateSVS = "recover"
                        checkpointedSVS = 0
                    elif (sleepCounterSVS <= 0) and (capacitorSVS.voltage > thresholdStart):
                        nextstateSVS = "measure"
                        measureCounterSVS = adcSamples/200/timeStep
                case "dead":
                    if capacitorSVS.voltage > thresholdStart:
                        nextstateSVS = "recover"
            
            match nextstateADC:
                case "recover":
                    recoverCounterADC -= 1
                    JITadc.recover(capacitorADC)
                    if recoverCounterADC <= 0:
                        timesRecoveredADC += 1
                        timeSavedADC += (adcSamples/200/timeStep if comCounterADC > 0 else 0)
                        nextstateADC = prevstateADC
                        recoverCounterADC = timeToRecover/timeStep
                        comCounterADC = btSize/1000000/timeStep
                        measureCounterADC = adcSamples/200/timeStep
                case "save":
                    saveCounterADC -= 1
                    JITadc.save(capacitorADC)
                    if saveCounterADC <= 0:
                        saveCounterADC = timeToSave/timeStep
                        timeCheckpointedADC += 1
                        nextstateADC = "sleep"
                case "measure":
                    stateADC.measure(capacitorADC)
                    measureCounterADC -= 1
                    if capacitorADC.voltage < thresholdDead:
                        nextstateADC = "dead"
                    elif measureCounterADC <= -5: # Added measurements for input voltage
                        nextstateADC = "communicate"
                        comCounterADC = btSize/1000000/timeStep
                        timesMeasuredADC += 1
                        if capacitorADC.voltage < thresholdStop:
                            nextstateADC = "save"
                            prevstateADC = "communicate"
                            checkpointedADC = 1
                case "communicate":
                    if comCounterADC > 0:
                        stateADC.communicate(capacitorADC)
                    comCounterADC -= 1
                    if capacitorADC.voltage < thresholdDead:
                        nextstateADC = "dead"
                    elif comCounterADC <= 0:
                        stateADC.measure(capacitorADC)
                        if comCounterADC <= -5:
                            nextstateADC = "sleep"
                            sleepCounterADC = sleepTime/timeStep
                            timesCommunicatedADC += 1
                            if capacitorADC.voltage < thresholdStop:
                                nextstateADC = "save"
                                prevstateADC = "measure"
                case "sleep":
                    stateADC.sleep(capacitorADC)
                    sleepCounterADC -= 1
                    if capacitorADC.voltage < thresholdDead:
                        nextstateADC = "dead"
                        prevstateADC = "sleep"
                    elif capacitorADC.voltage > thresholdStart and checkpointedADC:
                        nextstateADC = "recover"
                        checkpointedADC = 0
                    elif (sleepCounterADC <= 0) and (capacitorADC.voltage > thresholdStart):
                        nextstateADC = "measure"
                        measureCounterADC = adcSamples/200/timeStep
                case "dead":
                    if capacitorADC.voltage > thresholdStart:
                        nextstateADC = "recover"

            match nextstateINT:
                case "recover":
                    recoverCounterINT -= 1
                    interval.recover(capacitorINT)
                    if recoverCounterINT <= 0:
                        timesRecoveredINT += 1
                        timeSavedINT += (adcSamples/200/timeStep if comCounterINT > 0 else 0)
                        nextstateINT = prevstateINT
                        recoverCounterINT = timeToRecover/timeStep
                        comCounterINT = btSize/1000000/timeStep
                        measureCounterINT = adcSamples/200/timeStep
                case "save":
                    saveCounterINT -= 1
                    interval.save(capacitorINT)
                    if saveCounterINT <= 0:
                        checkpointedINT = 1
                        timeCheckpointedINT += 1
                        saveCounterINT = timeToSave/timeStep
                        if prevstateINT == "measure":
                            nextstateINT = "communicate"
                            prevstateINT = "communicate"
                        else:
                            nextstateINT = "sleep"
                            prevstateINT = "measure"
                            sleepCounterINT = sleepTime/timeStep
                case "measure":
                    stateINT.measure(capacitorINT)
                    measureCounterINT -= 1
                    if capacitorINT.voltage < thresholdDead:
                        nextstateINT = "dead"
                    elif measureCounterINT <= 0:
                        nextstateINT = "save"
                        prevstateINT = "measure"
                        timesMeasuredINT += 1
                case "communicate":
                    stateINT.communicate(capacitorINT)
                    comCounterINT -= 1
                    if capacitorINT.voltage < thresholdDead:
                        nextstateINT = "dead"
                    elif comCounterINT <= 0:
                        nextstateINT = "save"
                        prevstateINT = "communicate"
                        timesCommunicatedINT += 1
                case "sleep":
                    stateINT.sleep(capacitorINT)
                    sleepCounterINT -= 1
                    if capacitorINT.voltage < thresholdDead:
                        nextstateINT = "dead"
                    elif (sleepCounterINT <= 0) and (capacitorINT.voltage > thresholdStartINT):
                        nextstateINT = "measure"
                        measureCounterINT = adcSamples/200/timeStep
                case "dead":
                    if capacitorINT.voltage > thresholdStartINT:
                        nextstateINT = "recover"
            
            counter -= 1
            voltageSVS.append(capacitorSVS.voltage)
            voltageADC.append(capacitorADC.voltage)
            voltageINT.append(capacitorINT.voltage)
            irrTrace.append(irrValue)
    del trace, capacitorINT, capacitorADC, capacitorSVS, stateINT, stateADC, stateSVS, interval, JITadc, JITsvs
    gc.collect()

    print("Code execution time: ", time.now() - start, "\n")
    print("SVS: ")
    print("Times checkpointed: ", timeCheckpointedSVS)
    print("Times recovered: ", timesRecoveredSVS)
    print("Times measured: ", timesMeasuredSVS)
    print("Times communicated: ", timesCommunicatedSVS)
    print("Potential time saved: ", timeSavedSVS*timeStep, "\n")
    resultSVS = ['SVS', timeCheckpointedSVS, timesRecoveredSVS, timesMeasuredSVS, timesCommunicatedSVS]

    print("ADC: ")
    print("Times checkpointed: ", timeCheckpointedADC)
    print("Times recovered: ", timesRecoveredADC)
    print("Times measured: ", timesMeasuredADC)
    print("Times communicated: ", timesCommunicatedADC)
    print("Potential time saved: ", timeSavedADC*timeStep, "\n")
    resultADC = ['ADC', timeCheckpointedADC, timesRecoveredADC, timesMeasuredADC, timesCommunicatedADC]

    print("INTERVAL: ")
    print("Times checkpointed: ", timeCheckpointedINT)
    print("Times recovered: ", timesRecoveredINT)
    print("Times measured: ", timesMeasuredINT)
    print("Times communicated: ", timesCommunicatedINT)
    print("Potential time saved: ", timeSavedINT*timeStep, "\n")
    resultINT = ['Interval', timeCheckpointedINT, timesRecoveredINT, timesMeasuredINT, timesCommunicatedINT]

    timeAxis = np.linspace(start=0, stop=24, num=len(voltageSVS))
    timeAxisTicks = np.arange(0, 24, step=1)
    
    voltageSVS = np.array(voltageSVS, dtype=np.float32)
    voltageADC = np.array(voltageADC, dtype=np.float32)
    voltageINT = np.array(voltageINT, dtype=np.float32)
    fig = plt.figure(figsize=(16,9))
    gs = fig.add_gridspec(4, hspace=0)
    ax = gs.subplots(sharex=True, sharey=False)
    ax[0].plot(timeAxis, voltageINT, label='Interval')
    #ax[0].set_title('Interval')
    ax[0].set(ylabel='Voltage [V]', xticks=timeAxisTicks)
    ax[0].legend(loc="upper right")
    ax[0].margins(x=0)
    ax[0].axhline(maxVoltageOut, color='grey', ls='--')
    ax[0].axhline(thresholdStart, color='green', ls='--')
    ax[0].axhline(thresholdStop, color='orange', ls='--')
    ax[0].axhline(thresholdDead, color='red', ls='--')
    ax[1].plot(timeAxis, voltageADC, label='ADC')
    #ax[1].set_title('ADC')
    ax[1].set(ylabel='Voltage [V]', xticks=timeAxisTicks)
    ax[1].legend(loc="upper right")
    ax[1].margins(x=0)
    ax[1].axhline(maxVoltageOut, color='grey', ls='--')
    ax[1].axhline(thresholdStart, color='green', ls='--')
    ax[1].axhline(thresholdStop, color='orange', ls='--')
    ax[1].axhline(thresholdDead, color='red', ls='--')
    ax[2].plot(timeAxis, voltageSVS, label='SVS')
    #ax[2].set_title('SVS')
    ax[2].set(ylabel='Voltage [V]', xticks=timeAxisTicks)
    ax[2].legend(loc="upper right")
    ax[2].margins(x=0)
    ax[2].axhline(maxVoltageOut, color='grey', ls='--')
    ax[2].axhline(thresholdStart, color='green', ls='--')
    ax[2].axhline(thresholdStop, color='orange', ls='--')
    ax[2].axhline(thresholdDead, color='red', ls='--')
    ax[3].plot(timeAxis, irrTrace, label='Solar trace', color=('#ffae49' if season=='summer' else '#44a5c2' if season =='autumn' else '#024b7a'))
    #ax[3].set_title('Solar trace')
    ax[3].set(xlabel='Time of day', ylabel='Solar irradiance [W/m$^2$]', xticks=timeAxisTicks, ylim=[-10,1300])
    ax[3].legend(loc="upper right")
    ax[3].margins(x=0)
    fig.tight_layout()
    #plt.legend(loc='best', bbox_to_anchor=(0.5, 0., 0.5, 0.5), ncols=2)
    #plt.plot(stateTrace)
    #timeLoc = 'simulation/results/autosim_time_'+str(season)+str(numDays)+'_'+str(int(capacitorSize*1000))+'mF'+'_adc'+str(adcSamples)+'_sleep'+str(sleepTime)+'_start'+str(thresholdStart)+'_stop'+str(thresholdStop)+'.png'
    print(timeLoc)
    #plt.show()
    plt.savefig(timeLoc, bbox_inches="tight")
    plt.cla()
    plt.close()
    del timeAxis, timeAxisTicks, voltageINT, voltageADC, voltageSVS, irrTrace 
    gc.collect()

    return timeLoc, resultINT, resultADC, resultSVS

def plotBar(resultINT, resultADC, resultSVS, metrics, barLoc):
    barWidth = 0.2
    x = np.arange(len(metrics))
    fig = plt.figure(figsize=(10,6))

    plt.bar(x-barWidth, resultINT[1:], width=barWidth, label=resultINT[0], color='#0089B3')
    plt.bar(x         , resultADC[1:], width=barWidth, label=resultADC[0], color='#00556F')
    plt.bar(x+barWidth, resultSVS[1:], width=barWidth, label=resultSVS[0], color='#00C4FF')
    for i, v in enumerate(resultINT[1:]):
        plt.text(i-barWidth, v, str(v), color='#0089B3', horizontalalignment='center', verticalalignment='bottom')
    for i, v in enumerate(resultADC[1:]):
        plt.text(i, v, str(v), color='#00556F', horizontalalignment='center', verticalalignment='bottom')
    for i, v in enumerate(resultSVS[1:]):
        plt.text(i+barWidth, v, str(v), color='#00C4FF', horizontalalignment='center', verticalalignment='bottom')
    plt.xticks(x, metrics)
    #plt.ylim([0, max([max(resultINT[1:]), max(resultADC[1:]), max(resultSVS[1:])]) * 1.35])
    
    plt.ylabel('Number of times')
    plt.xlabel('Metric')
    plt.legend(loc='best')
    #plt.show()
    plt.savefig(barLoc, bbox_inches="tight")
    plt.cla()
    plt.close()
    del x
    gc.collect()
    

#seasons = ['winter', 'summer']
#winterDays = [11, 20, 3]
#summerDays = [7, 10, 2]
headers = ['Season', 'Day', 'Capacitance [mF]', 'Samples', 'Sleep', 'Start', 'Stop', '', 'Resulting metrics', 'Time plot']
metrics = ['Checkpointed', 'Recovered', 'Measured', 'Communicated']
simSetFile = 'simSet1'
os.makedirs('simulation/results/'+simSetFile+'Results')
resultLoc = 'simulation/results/'+simSetFile+'Results/'+simSetFile+'.xlsx'

simSet = pd.read_csv('simulation/'+simSetFile+'.tsv', sep='\t')

xl.createExcel(resultLoc, headers)
del headers
gc.collect()
for i, row in simSet.iterrows():
    #for season in seasons:
    #    for day in (winterDays if season == seasons[0] else summerDays):
    params = [row['season'], row['day'], row['capacitance'], row['samples'], row['sleep'], row['start'], row['stop']]
    print('Sim\t', str(i+1)+'/'+str(len(simSet))+':', params)
    barLoc = 'simulation/results/'+simSetFile+'Results/'+simSetFile+'_bar_'+str(row['season'])+str(row['day'])+'_'+str(int(row['capacitance']))+'mF'+'_adc'+str(row['samples'])+'_sleep'+str(row['sleep'])+'_start'+str(row['start'])+'_stop'+str(row['stop'])+'.png'
    timeLoc= 'simulation/results/'+simSetFile+'Results/'+simSetFile+'_time_'+str(row['season'])+str(row['day'])+'_'+str(int(row['capacitance']))+'mF'+'_adc'+str(row['samples'])+'_sleep'+str(row['sleep'])+'_start'+str(row['start'])+'_stop'+str(row['stop'])+'.png' 
    timeLoc, resultINT, resultADC, resultSVS = main(adcSamples         = row['samples'],
                                                    sleepTime           = row['sleep'],
                                                    numDays             = row['day'],
                                                    capacitorSize       = row['capacitance']*10**-3,
                                                    thresholdStart      = row['start'],
                                                    thresholdStop       = row['stop'],
                                                    season              = row['season'],
                                                    timeLoc             = timeLoc)
    
    #resultINT, resultADC, resultSVS = ['Interval', 22, 1, 11, 11], ['ADC', 14, 3, 12, 12], ['SVS', 5, 5, 13, 13]
    plotBar(resultINT, resultADC, resultSVS, metrics, barLoc)
    del resultINT, resultADC, resultSVS
    gc.collect()

    xl.writeExcel(resultLoc, params, barLoc, timeLoc)
