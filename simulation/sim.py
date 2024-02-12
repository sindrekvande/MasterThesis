import file_handler as fh
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
        self.voltage = 0
        self.energy = 0

    def addEnergy(self, irr):
        self.energy += irr * 60

    def useEnergy(self, energy):
        if self.energy < energy:
            self.energy = 0
        else:
            self.energy -= energy
        return self.energy

class states:
    self.measureCurrent       = 8 * 10 ** -3
    self.communicateCurrent   = 9 * 10 ** -3
    self.sleepCurrent         = 1.9 * 10 ** -6
    def __init__(self, measTime, comTime, sleepTime, capacitor: energyStorage):
        self.measTime   = measTime
        self.comTime    = comTime
        self.sleepTime  = sleepTime

    def measure(self):
        capacitor.useEnergy(self.measureCurrent * self.measTime)
        
    def communicate(self):
        capacitor.useEnergy(self.communicationCurrent * self.comTime)

    def sleep(self):
        capacitor.useEnergy(self.sleepCurrent * self.sleepTime)

class checkpoint:
    # 58 μA/MHz running from flash memory
    self.energyUse = 58 * 10 ** -6 * 64
    def __init__(self, capacitor: energyStorage):
        pass

    def save(timeToSave):
        capacitor.useEnergy(self.energyUse * timeToSave)

    def recover(timeToRecover):
        capacitor.useEnergy(self.energyUse * timeToRecover)

def main():
    trace = fh.file("summer").brightnessDF
    capacitor = energyStorage()
    states = states(0.01, 0.01, 50)
    JITsvs = checkpoint()
    JITadc = checkpoint()
    interval = checkpoint()

    for key, irrValue in trace.intertuples():
        capacitor.addEnergy(irrValue)
        counter = 60
        nextstate = "measure"
        while counter > 0:
            match nextstate:
                case "measure":
                    counter -= states.measure()
                    nextstate = "communicate"
                case "communicate":
                    counter -= states.communicate()
                    nextstate = "sleep"
                case "sleep":
                    counter -= states.sleep()
                    nextstate = "measure"
            if capacitor.energy = 0:
                break
