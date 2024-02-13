import file_handler as fh
import matplotlib.pyplot as plt
import numpy as np
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
    def __init__(self, capacitance, maxVolt):
        self.maxEnergy = 1/2 * capacitance * maxVolt**2
        self.voltage = 0
        self.energy = 0
        self.capacitance = capacitance

    def addEnergy(self, irr):
        self.energy += irr * 60 / 10000
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
    measureCurrent       = 8 * 10 ** -3
    communicateCurrent   = 9 * 10 ** -3
    sleepCurrent         = 1.9 * 10 ** -6
    def __init__(self, measTime, comTime, sleepTime, capacitor: energyStorage):
        self.measTime   = measTime
        self.comTime    = comTime
        self.sleepTime  = sleepTime

    def measure(self, capacitor: energyStorage):
        capacitor.useEnergy(self.measureCurrent * self.measTime)
        return self.measTime
        
    def communicate(self, capacitor: energyStorage):
        capacitor.useEnergy(self.communicateCurrent * self.comTime)
        return self.comTime

    def sleep(self, capacitor: energyStorage):
        capacitor.useEnergy(self.sleepCurrent * self.sleepTime)
        return self.sleepTime

class checkpoint:
    # 58 μA/MHz running from flash memory
    energyUse = 58 * 10 ** -6 * 64
    def __init__(self):
        pass

    def save(self, timeToSave, capacitor: energyStorage):
        capacitor.useEnergy(self.energyUse * timeToSave)

    def recover(self, timeToRecover, capacitor: energyStorage):
        capacitor.useEnergy(self.energyUse * timeToRecover)

def main():
    trace = fh.file("winter").brightnessDF
    capacitor = energyStorage(47*10**-3, 3.3)
    state = states(0.01, 0.01, 59.98, capacitor)
    JITsvs = checkpoint()
    JITadc = checkpoint()
    interval = checkpoint()
    # nRF: 1.7 V–3.6 V supply voltage range
    thresholdStart = 2.5
    thersholdStop = 1.9
    voltage = []
    # SVS
    nextstate = "measure"
    for key, irrValue in trace.itertuples():
        capacitor.addEnergy(irrValue)
        counter = 60
        while counter > 0:
            match nextstate:
                case "recover":
                    nextstate = prevstate
                case "measure":
                    counter -= state.measure(capacitor)
                    if capacitor.voltage < thersholdStop:
                        nextstate = "sleep"
                        prevstate = "measure"
                    else:
                        nextstate = "communicate"
                case "communicate":
                    counter -= state.communicate(capacitor)
                    if capacitor.voltage < thersholdStop:
                        nextstate = "sleep"
                        prevstate = "communicate"
                    else:
                        nextstate = "sleep"
                case "sleep":
                    counter -= state.sleep(capacitor)
                    if capacitor.voltage < 1.7:
                        nextstate = "dead"
                        prevstate = "sleep"
                    else:
                        nextstate = "measure"
                case "dead":
                    if capacitor.voltage > thresholdStart:
                        nextstate = "recover"
                    else:
                        counter -= 1
        voltage.append(capacitor.voltage)

    plt.plot(voltage)
    plt.show()

main()
