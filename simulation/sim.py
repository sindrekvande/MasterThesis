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
    energyUse = 58 * 10 ** -6 * 64
    def __init__(self, timeStep):
        self.timeStep = timeStep

    def save(self, capacitor: energyStorage):
        capacitor.useEnergy(self.energyUse * self.timeStep)

    def recover(self, capacitor: energyStorage):
        capacitor.useEnergy(self.energyUse * self.timeStep)

def main():
    start = time.now()
    ############## Parameters ###############
    timeStep        = 1*10**-3  # millisecond
    adcSamples      = 10        # 10 samples
    btSize          = 1024      # 1kb data (should be atleast more than adcSamples*12)
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
    #stateTrace = [[0,0,0,0,0]]
    #currentSate = [0,0,0,0,0]
    #stateTrace.append(currentSate)
    # SVS
    nextstate = "measure"
    measureCounter = adcSamples/200/timeStep
    comCounter = btSize/1000/timeStep
    sleepCounter = sleepTime/timeStep

    for key, irrValue in trace.itertuples():
        #print(irrValue)
        counter = 60/timeStep
        #counterstart = counter
        irrTrace.append(irrValue/1000)
        while counter > 0:
            capacitor.addEnergy(irrValue)
            match nextstate:
                case "recover":
                    #currentSate = [1,0,0,0,0]
                    nextstate = prevstate
                    #counterstart = counter
                case "measure":
                    #currentSate = [0,1,0,0,0]
                    state.measure(capacitor)
                    measureCounter -= 1
                    if capacitor.voltage < thresholdStop:
                        nextstate = "sleep"
                        prevstate = "measure"
                        #counterstart = counter
                        sleepCounter = sleepTime/timeStep
                    elif measureCounter <= 0:
                        nextstate = "communicate"
                        #counterstart = counter
                        comCounter = btSize/1000/timeStep
                case "communicate":
                    #currentSate = [0,0,1,0,0]
                    state.communicate(capacitor)
                    comCounter -= 1
                    if capacitor.voltage < thresholdStop:
                        nextstate = "sleep"
                        prevstate = "communicate"
                        #counterstart = counter
                        sleepCounter = sleepTime/timeStep
                    elif comCounter <= 0:
                        nextstate = "sleep"
                        #counterstart = counter
                        sleepCounter = sleepTime/timeStep
                case "sleep":
                    #currentSate = [0,0,0,1,0]
                    state.sleep(capacitor)
                    sleepCounter -= 1
                    if capacitor.voltage < 1.7:
                        nextstate = "dead"
                        prevstate = "sleep"
                        #counterstart = counter
                    elif (capacitor.voltage > thresholdStart) and (sleepCounter <= 0):
                        nextstate = "measure"
                        #counterstart = counter
                        adcSamples/200/timeStep
                case "dead":
                    #currentSate = [0,0,0,0,1]
                    if capacitor.voltage > thresholdStart:
                        nextstate = "recover"
                        #counterstart = counter
            counter -= 1
            voltage.append(capacitor.voltage)
            irrTrace.append(irrValue/1000)
            #stateTrace.append(currentSate)
    
    print("Code execution time: ", time.now() - start)
    
    plt.plot(voltage)
    plt.plot(irrTrace)
    #plt.plot(stateTrace)
    plt.show()

main()