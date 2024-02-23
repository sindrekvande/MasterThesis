import file_handler as fh
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime as time
from decimal import *
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
    def __init__(self, timeStep, capacitance, maxVolt):
        self.maxEnergy = 1/2 * capacitance * maxVolt**2
        self.voltage = 0
        self.energy = 0
        self.capacitance = capacitance
        self.timeStep = timeStep

    def addEnergy(self, irr):
        self.energy += irr * self.timeStep / 10000 # For 1cm^2 soler cell
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

    def save(self, capacitor: energyStorage, timeToSave):
        capacitor.useEnergy(self.powerUse * timeToSave)

    def recover(self, capacitor: energyStorage, timeToRecover):
        capacitor.useEnergy(self.powerUse * timeToRecover)

def main():
    start = time.now()
    ############## Parameters ###############
    timeStep        = 1*10**-3  # millisecond
    adcSamples      = 10        # 10 samples
    btSize          = 1024      # 1kb data (should be atleast adcSamples*12)
    sleepTime       = 60*10     # in seconds
    numDays         = 1.5       # 
    capacitorSize   = 10*10**-3 # in Farad
    testToDo        = "all"     # svs, adc, int or all
    ########################################

    trace = fh.file("winter", numDays).brightnessDF
    capacitorSVS = energyStorage(timeStep, capacitorSize, 3.3)
    capacitorADC = energyStorage(timeStep, capacitorSize, 3.3)
    capacitorINT = energyStorage(timeStep, capacitorSize, 3.3)
    stateSVS = states(timeStep, capacitorSVS)
    stateADC = states(timeStep, capacitorADC)
    stateINT = states(timeStep, capacitorINT)
    JITsvs = checkpoint(timeStep)
    JITadc = checkpoint(timeStep)
    interval = checkpoint(timeStep)
    # nRF: 1.7 V–3.6 V supply voltage range
    thresholdStart = 2.5
    thresholdStop = 1.9
    thresholdDead = 1.7
    voltageSVS = []
    voltageADC = []
    voltageINT = []
    irrTrace = []
    # SVS
    nextstateSVS = "dead"
    measureCounterSVS = adcSamples/200/timeStep
    comCounterSVS = btSize/1000/timeStep
    sleepCounterSVS = sleepTime/timeStep
    checkpointedSVS = 0
    timeSavedSVS = 0
    timesRecoveredSVS = 0
    prevstateSVS = "measure"

    nextstateADC = "dead"
    measureCounterADC = adcSamples/200/timeStep
    comCounterADC = btSize/1000/timeStep
    sleepCounterADC = sleepTime/timeStep
    checkpointedADC = 0
    timeSavedADC = 0
    timesRecoveredADC = 0
    prevstateADC = "measure"

    nextstateINT = "dead"
    measureCounterINT = adcSamples/200/timeStep
    comCounterINT = btSize/1000/timeStep
    sleepCounterINT = sleepTime/timeStep
    checkpointedINT = 0
    timeSavedINT = 0
    timesRecoveredINT = 0
    prevstateINT = "measure"
    timeCheckpointedINT = 0
    thresholdStartINT = 3.3

    for key, irrValue in trace.itertuples():
        counter = 60/timeStep
        irrTrace.append(irrValue/1000)
        while counter > 0:
            capacitorSVS.addEnergy(irrValue)
            capacitorADC.addEnergy(irrValue)
            capacitorINT.addEnergy(irrValue)
            match nextstateSVS:
                case "recover":
                    timesRecoveredSVS += 1
                    timeSavedSVS += (adcSamples/200/timeStep + btSize/1000/timeStep - comCounterSVS if comCounterSVS > 0 else 0) + (adcSamples/200/timeStep - measureCounterSVS if measureCounterSVS > 0 else 0)
                    nextstateSVS = prevstateSVS
                    JITsvs.recover(capacitorSVS, 0.1)
                case "measure":
                    stateSVS.measure(capacitorSVS)
                    measureCounterSVS -= 1
                    if capacitorSVS.voltage < thresholdStop:
                        nextstateSVS = "sleep"
                        prevstateSVS = "measure"
                        JITsvs.save(capacitorSVS, 0.1)
                        checkpointedSVS = 1
                        sleepCounterSVS = sleepTime/timeStep
                    elif measureCounterSVS <= 0:
                        nextstateSVS = "communicate"
                        comCounterSVS = btSize/1000/timeStep
                        #########################
                        # For ADC/interval check voltage/take checkpoint here
                        #########################
                case "communicate":
                    stateSVS.communicate(capacitorSVS)
                    comCounterSVS -= 1
                    if capacitorSVS.voltage < thresholdStop:
                        nextstateSVS = "sleep"
                        prevstateSVS = "communicate"
                        sleepCounterSVS = sleepTime/timeStep
                    elif comCounterSVS <= 0:
                        nextstateSVS = "sleep"
                        sleepCounterSVS = sleepTime/timeStep
                case "sleep":
                    stateSVS.sleep(capacitorSVS)
                    sleepCounterSVS -= 1
                    if capacitorSVS.voltage < thresholdDead:
                        nextstateSVS = "dead"
                        #prevstate = "sleep"
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
                    timesRecoveredADC += 1
                    timeSavedADC += (adcSamples/200/timeStep)
                    nextstateADC = prevstateADC
                    JITadc.recover(capacitorADC, 0.1)
                case "measure":
                    stateADC.measure(capacitorADC)
                    measureCounterADC -= 1
                    if capacitorADC.voltage < thresholdDead:
                        nextstateADC = "dead"
                    elif measureCounterADC <= -5: # Added measurements for input voltage
                        nextstateADC = "communicate"
                        comCounterADC = btSize/1000/timeStep
                        if capacitorADC.voltage < thresholdStop:
                            nextstateADC = "sleep"
                            prevstateADC = "communicate"
                            JITadc.save(capacitorADC, 0.1)
                            checkpointedADC = 1
                            sleepCounterADC = sleepTime/timeStep
                case "communicate":
                    stateADC.communicate(capacitorADC)
                    comCounterADC -= 1
                    if capacitorADC.voltage < thresholdDead:
                        nextstateADC = "dead"
                    elif comCounterADC <= 0:
                        nextstateADC = "sleep"
                        sleepCounterADC = sleepTime/timeStep
                case "sleep":
                    stateADC.sleep(capacitorADC)
                    sleepCounterADC -= 1
                    if capacitorADC.voltage < thresholdDead:
                        nextstateADC = "dead"
                        #prevstate = "sleep"
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
                    timesRecoveredINT += 1
                    timeSavedINT += (adcSamples/200/timeStep)
                    nextstateINT = prevstateINT
                    interval.recover(capacitorINT, 0.1)
                case "measure":
                    stateINT.measure(capacitorINT)
                    measureCounterINT -= 1
                    if capacitorINT.voltage < thresholdDead:
                        nextstateINT = "dead"
                    elif measureCounterINT <= 0:
                        nextstateINT = "communicate"
                        comCounterINT = btSize/1000/timeStep
                        interval.save(capacitorINT, 0.1)
                        checkpointedINT = 1
                        timeCheckpointedINT += 1
                case "communicate":
                    stateINT.communicate(capacitorINT)
                    comCounterINT -= 1
                    if capacitorINT.voltage < thresholdDead:
                        nextstateINT = "dead"
                    elif comCounterINT <= 0:
                        nextstateINT = "sleep"
                        sleepCounterINT = sleepTime/timeStep
                case "sleep":
                    stateINT.sleep(capacitorINT)
                    sleepCounterINT -= 1
                    if capacitorINT.voltage < thresholdDead:
                        nextstateINT = "dead"
                    elif (sleepCounterINT <= 0) and (capacitorINT.voltage > thresholdStartINT):
                        nextstateINT = "measure"
                        measureCounterINT = adcSamples/200/timeStep
                case "dead":
                    if capacitorINT.voltage >= thresholdStartINT:
                        nextstateINT = "recover"
            
            counter -= 1
            voltageSVS.append(capacitorSVS.voltage)
            voltageADC.append(capacitorADC.voltage)
            voltageINT.append(capacitorINT.voltage)
            irrTrace.append(irrValue/1000)
    
    print("Code execution time: ", time.now() - start, "\n")
    print("SVS: ")
    print("Times recovered: ", timesRecoveredSVS)
    print("Potential time saved: ", timeSavedSVS*timeStep, "\n")

    print("ADC: ")
    print("Times recovered: ", timesRecoveredADC)
    print("Potential time saved: ", timeSavedADC*timeStep, "\n")

    print("INTERVAL: ")
    print("Times checkpointed: ", timeCheckpointedINT)
    print("Times recovered: ", timesRecoveredINT)
    print("Potetial time saved: ", timeSavedINT*timeStep, "\n")


    voltageSVS = np.array(voltageSVS, dtype=np.float16)
    voltageADC = np.array(voltageADC, dtype=np.float16)
    voltageINT = np.array(voltageINT, dtype=np.float16)
    plt.plot(voltageSVS)
    plt.plot(voltageADC)
    plt.plot(voltageINT)
    plt.plot(irrTrace)
    #plt.plot(stateTrace)
    plt.show()

main()