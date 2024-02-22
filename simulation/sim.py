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
    ########################################

    trace = fh.file("winter", numDays).brightnessDF
    capacitor = energyStorage(timeStep, capacitorSize, 3.3)
    state = states(timeStep, capacitor)
    JITsvs = checkpoint(timeStep)
    JITadc = checkpoint(timeStep)
    interval = checkpoint(timeStep)
    # nRF: 1.7 V–3.6 V supply voltage range
    thresholdStart = 2.5
    thresholdStop = 1.9
    voltage = []
    irrTrace = []
    # SVS
    nextstate = "measure"
    measureCounter = adcSamples/200/timeStep
    comCounter = btSize/1000/timeStep
    sleepCounter = sleepTime/timeStep
    checkpointed = 0
    timeSaved = 0
    timesRecovered = 0

    for key, irrValue in trace.itertuples():
        counter = 60/timeStep
        irrTrace.append(irrValue/1000)
        while counter > 0:
            capacitor.addEnergy(irrValue)
            match nextstate:
                case "recover":
                    timesRecovered += 1
                    timeSaved += (btSize/1000/timeStep - comCounter if comCounter > 0 else 0) + (adcSamples/200/timeStep - measureCounter if measureCounter > 0 else 0)
                    nextstate = prevstate
                    JITsvs.recover(capacitor, 1)
                case "measure":
                    state.measure(capacitor)
                    measureCounter -= 1
                    if capacitor.voltage < thresholdStop:
                        nextstate = "sleep"
                        prevstate = "measure"
                        JITsvs.save(capacitor, 1)
                        checkpointed = 1
                        sleepCounter = sleepTime/timeStep
                    elif measureCounter <= 0:
                        nextstate = "communicate"
                        comCounter = btSize/1000/timeStep
                        #########################
                        # For ADC/interval check voltage/take checkpoint here
                        #########################
                case "communicate":
                    state.communicate(capacitor)
                    comCounter -= 1
                    if capacitor.voltage < thresholdStop:
                        nextstate = "sleep"
                        prevstate = "communicate"
                        sleepCounter = sleepTime/timeStep
                    elif comCounter <= 0:
                        nextstate = "sleep"
                        sleepCounter = sleepTime/timeStep
                case "sleep":
                    state.sleep(capacitor)
                    sleepCounter -= 1
                    if capacitor.voltage < 1.7:
                        nextstate = "dead"
                        #prevstate = "sleep"
                    elif capacitor.voltage > thresholdStart and checkpointed:
                        nextstate = "recover"
                        checkpointed = 0
                    elif (sleepCounter <= 0) and (capacitor.voltage > thresholdStart):
                        nextstate = "measure"
                        measureCounter = adcSamples/200/timeStep
                case "dead":
                    if capacitor.voltage > thresholdStart:
                        nextstate = "recover"
            counter -= 1
            voltage.append(capacitor.voltage)
            irrTrace.append(irrValue/1000)
    
    print("Code execution time: ", time.now() - start)
    print("Times recovered: ", timesRecovered)
    print("Total time saved: ", timeSaved*timeStep)

    plt.plot(voltage)
    plt.plot(irrTrace)
    #plt.plot(stateTrace)
    plt.show()

main()