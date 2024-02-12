# take in solar trace
# feed solar trace to simulated energy storage
# do work (measure, communicate, sleep) in state machine

def get_solar_trace():
    # use file_handler
    pass

class energyStorage:
    # C = (ε0 * A) / d
    # E = (Q ⋅ V) / 2
    def __init__(self, capacitance, maxVolt):
        self.maxEnergy = 1/2 * capacitance * maxVolt

    def addEnergy(self, irr):
        pass

    def useEnergy(self, energy):
        pass

class stateMachine:
    self.measureEnergyUse = 
    self.communicateEnergyUse = 
    self.sleepEnergyUse = 
    def __init__(self, measTime, comTime, sleepTime):
        self.measTime   = measTime
        self.comTime    = comTime
        self.sleepTime  = sleepTime

    def measure(self):
        energyUsage = self.measureEnergyUse * self.measTime
        return energyUsage
        
    def communicate(self):
        energyUsage = self.measureEnergyUse * self.measTime
        return energyUsage

    def sleep(self):
        energyUsage = self.measureEnergyUse * self.measTime
        return energyUsage
