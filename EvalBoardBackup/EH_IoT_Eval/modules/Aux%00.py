import time
import parameters as pm
import modules.pinOut_BCM as pinOut
import RPi.GPIO as GPIO
from bleak import BleakClient
import asyncio


class ThresholdHandler:
    def __init__(self):
        print("Class ThresholdHandler Init")
        self.ov_count = 0
        self.uv_count = 0

    def above_threshold(self, value, threshold, action, *args):
        if value > threshold:
            self.ov_count += 1
            if self.ov_count > 50:
                #print("Last value: " + str(value))
                #print("Threshold: " + str(threshold))
                #print("Upper Threshold reached")
                #print(action)
                action(*args)
                return 1
        else:
            self.ov_count = 0
            return 0

    def below_threshold(self, value, threshold, action, *args):
        if value < threshold:
            self.uv_count += 1
            if self.uv_count > 10:
                action(*args)
                return 1
        else:
            self.uv_count = 0
            return 0


class Emulator:

    DCDC_Out_V = 3.3

    Idle_pwr_mW = 0.02

    Sampling_pwr_mW = 50   #33
    Sampling_time_s = 0.01 #0.005

    Communication_pwr_mW = 1
    Communication_time_s = 2

    Sampling_period_s = 5
    Communication_incidence = 10

    SoC_power_off = 1           # Flag for emulating initial power consumption after power-on
    Check_time_s = 0.5          # Time between event and registering a successful event (if DCDC converter is still on)

    Sampling_frequency_Hz = 1/20
    Energy_Surplus_Integrator_V = 0

    # For Analytical_Frequency_Control
    t_old = 0 
    VoC_Sampling_time = 0
    EH_Open_Circuit_V = 0
    State_of_Charge_V_old = 0
    Diode_Drop_V = 0.1



    def __init__(self, dac_instance):
        print("Class SoC Emulator Init")
        self.dac_instance = dac_instance



    def PI_Controller(self, data_log, EH_Open_Circuit_V):

        # Refine sampling frequency
        State_of_Charge_V = data_log['V_BANK1'] # Bank 1 voltage

        print("Sampling frequency old: " + str(self.Sampling_frequency_Hz))
        print("Sampling period old: " + str(1/self.Sampling_frequency_Hz))

        Energy_Surplus_V = State_of_Charge_V - 0.8*EH_Open_Circuit_V
        self.Energy_Surplus_Integrator_V = self.Energy_Surplus_Integrator_V + Energy_Surplus_V/self.Sampling_frequency_Hz
        PI_Controller_Out = 0.4*Energy_Surplus_V + 0.002*self.Energy_Surplus_Integrator_V
        self.Sampling_frequency_Hz = self.Sampling_frequency_Hz + self.Sampling_frequency_Hz*PI_Controller_Out
        
        if 1/self.Sampling_frequency_Hz <= self.Communication_time_s+self.Sampling_time_s+self.Check_time_s:
            print("Sampling period adjusted from: " + str(1/self.Sampling_frequency_Hz))    
            self.Sampling_frequency_Hz = 0.8*(self.Communication_time_s+self.Sampling_time_s+self.Check_time_s)
            print("Sampling period adjusted to: " + str(1/self.Sampling_frequency_Hz))  


        print("Sampling frequency new: " + str(self.Sampling_frequency_Hz))
        print("Sampling period new: " + str(1/self.Sampling_frequency_Hz))
        print("State of Charge: " + str(State_of_Charge_V))
        print("Target Voltage: " + str(0.8*EH_Open_Circuit_V))
        print("Energy Surplus: " + str(Energy_Surplus_V))
        print("Energy Surplus Integrator: " + str(self.Energy_Surplus_Integrator_V))
        print("PI Out: " + str(PI_Controller_Out))


    def Analytical_Frequency_Control(self, data_log):

        t_new = time.time()
        State_of_Charge_V_new = data_log['V_BANK1'] # Bank 1 voltage

        # Measure EH's open-circuit voltage every >=180 seconds
        if t_new - self.VoC_Sampling_time >= 180:
            GPIO.output(pinOut.I2C_SDA, GPIO.LOW)
            time.sleep(1)
            self.EH_Open_Circuit_V = data_log['EH_IN_+_BUF'] # EH voltage
            GPIO.output(pinOut.I2C_SDA, GPIO.HIGH)
            self.VoC_Sampling_time = time.time()

        # Calculate optimum sampling frequency
        
        print("Sampling frequency old: " + str(self.Sampling_frequency_Hz))
        print("Sampling period old: " + str(1/self.Sampling_frequency_Hz))

        if not self.t_old == 0:

            Average_Power_Consumed_Ws = self.Sampling_frequency_Hz * (self.Sampling_pwr_mW/1000 * self.Sampling_time_s + self.Communication_pwr_mW/1000*self.Communication_time_s/self.Communication_incidence) + self.Idle_pwr_mW/1000
            Average_Power_In_Ws = (1/2 * 0.020 * (pow(State_of_Charge_V_new,2) - pow(self.State_of_Charge_V_old,2)))/(t_new-self.t_old) + Average_Power_Consumed_Ws
            Energy_Neutral_fs = (Average_Power_In_Ws - self.Idle_pwr_mW/1000)/(self.Sampling_pwr_mW/1000 * self.Sampling_time_s + self.Communication_pwr_mW/1000*self.Communication_time_s/self.Communication_incidence)
            
            print("State of Charge new: " + str(State_of_Charge_V_new))
            print("State of Charge old: " + str(self.State_of_Charge_V_old))
            print("delta t: " + str(t_new-self.t_old))
            print("Power Consumed: " + str(Average_Power_Consumed_Ws))
            print("Power In: " + str(Average_Power_In_Ws))
            

            print("Energy Neutral fs: " + str(Energy_Neutral_fs))
            print("Energy Neutral period: " + str(1/Energy_Neutral_fs))

            self.Sampling_frequency_Hz = (1+1.0*((State_of_Charge_V_new+self.Diode_Drop_V)-0.8*self.EH_Open_Circuit_V)) * Energy_Neutral_fs
            #self.Sampling_frequency_Hz = Energy_Neutral_fs
            
            if self.Sampling_frequency_Hz < 0:
                print("Manually adjusting to minimum sampling frequency")
                self.Sampling_frequency_Hz = 1/60

            if 0.8*self.EH_Open_Circuit_V < 1.0:
                print("Open Circuit Voltage too low.")
                #self.Sampling_frequency_Hz = 1/20

            if 1/self.Sampling_frequency_Hz <= self.Communication_time_s+self.Sampling_time_s+self.Check_time_s:
                print("Sampling period adjusted from: " + str(1/self.Sampling_frequency_Hz))    
                self.Sampling_frequency_Hz = 0.8/(self.Communication_time_s+self.Sampling_time_s+self.Check_time_s)
                print("Sampling period adjusted to: " + str(0.8/(self.Communication_time_s+self.Sampling_time_s+self.Check_time_s))  )

            print("Sampling frequency new: " + str(self.Sampling_frequency_Hz))
            print("Sampling period new: " + str(1/self.Sampling_frequency_Hz))

            print("State of Charge: " + str(State_of_Charge_V_new))
            print("Target Voltage: " + str(0.8*self.EH_Open_Circuit_V))
            print("Energy Neutral fs: " + str(Energy_Neutral_fs))


        self.State_of_Charge_V_old = State_of_Charge_V_new
        self.t_old = t_new


    def Energy_Neutral_Op(self, data_log):

        # Fixed target voltage for energy neutral operation
        Target_Voltage_V = 2.5

        t_new = time.time()
        State_of_Charge_V_new = data_log['V_BANK1'] # Bank 1 voltage

        # Calculate optimum sampling frequency
        
        print("Sampling frequency old: " + str(self.Sampling_frequency_Hz))
        print("Sampling period old: " + str(1/self.Sampling_frequency_Hz))

        if not self.t_old == 0:

            Average_Power_Consumed_Ws = self.Sampling_frequency_Hz * (self.Sampling_pwr_mW/1000 * self.Sampling_time_s + self.Communication_pwr_mW/1000*self.Communication_time_s/self.Communication_incidence) + self.Idle_pwr_mW/1000
            Average_Power_In_Ws = (1/2 * 0.020 * (pow(State_of_Charge_V_new,2) - pow(self.State_of_Charge_V_old,2)))/(t_new-self.t_old) + Average_Power_Consumed_Ws
            Energy_Neutral_fs = (Average_Power_In_Ws - self.Idle_pwr_mW/1000)/(self.Sampling_pwr_mW/1000 * self.Sampling_time_s + self.Communication_pwr_mW/1000*self.Communication_time_s/self.Communication_incidence)
            
            print("State of Charge new: " + str(State_of_Charge_V_new))
            print("State of Charge old: " + str(self.State_of_Charge_V_old))
            print("delta t: " + str(t_new-self.t_old))
            print("Power Consumed: " + str(Average_Power_Consumed_Ws))
            print("Power In: " + str(Average_Power_In_Ws))
            

            print("Energy Neutral fs: " + str(Energy_Neutral_fs))
            print("Energy Neutral period: " + str(1/Energy_Neutral_fs))

            self.Sampling_frequency_Hz = (1+1.0*((State_of_Charge_V_new+self.Diode_Drop_V)-Target_Voltage_V)) * Energy_Neutral_fs
            #self.Sampling_frequency_Hz = Energy_Neutral_fs
            
            if self.Sampling_frequency_Hz < 1/60:
                print("Manually adjusting to minimum sampling frequency")
                self.Sampling_frequency_Hz = 1/60

            if 1/self.Sampling_frequency_Hz <= self.Communication_time_s+self.Sampling_time_s+self.Check_time_s:
                print("Sampling period adjusted from: " + str(1/self.Sampling_frequency_Hz))    
                self.Sampling_frequency_Hz = 0.8/(self.Communication_time_s+self.Sampling_time_s+self.Check_time_s)
                print("Sampling period adjusted to: " + str(0.8/(self.Communication_time_s+self.Sampling_time_s+self.Check_time_s))  )

            print("Sampling frequency new: " + str(self.Sampling_frequency_Hz))
            print("Sampling period new: " + str(1/self.Sampling_frequency_Hz))

            print("State of Charge: " + str(State_of_Charge_V_new))
            print("Target Voltage: " + str(Target_Voltage_V))
            print("Energy Neutral fs: " + str(Energy_Neutral_fs))


        self.State_of_Charge_V_old = State_of_Charge_V_new
        self.t_old = t_new


    def SoC_Emulator(self, exit_event, sys_states, performance_log, data_log):

        while not exit_event.is_set():
            while not exit_event.is_set() and sys_states[6] == 1:
                if self.SoC_power_off == 1:
                    print("SoC booting")
                    time.sleep(0.25) # Delay to make sure that the converter's ouput voltage is stable
                    # SoC Boot Phase 1
                    self.dac_instance.current_sink_curr_mA(18/self.DCDC_Out_V)
                    time.sleep(3.5/1000)
                    # SoC Boot Phase 2
                    self.dac_instance.current_sink_curr_mA(0.005/self.DCDC_Out_V)
                    time.sleep(0.38)
                    # SoC Boot Phase 3
                    self.dac_instance.current_sink_curr_mA(23/self.DCDC_Out_V)
                    time.sleep(43/1000)
                    self.SoC_power_off = 0

                    # Measure EH's open-circuit voltage
                    GPIO.output(pinOut.I2C_SDA, GPIO.LOW)
                    time.sleep(0.5)
                    EH_Open_Circuit_V = data_log['EH_IN_+_BUF'] # EH voltage
                    GPIO.output(pinOut.I2C_SDA, GPIO.HIGH)

                    self.Energy_Surplus_Integrator_V = 0 # Reset intergral part of PI controller

                    t_comm_end = 0 # not executed communication before


                if time.time()-t_comm_end < 10: # ESR
                    print("Waiting for additional "+str(time.time()-t_comm_end) + " s")
                    time.sleep(10-(time.time()-t_comm_end))

                self.Analytical_Frequency_Control(data_log)

                for i in range(self.Communication_incidence):

                    #self.PI_Controller(data_log, EH_Open_Circuit_V)

                    print("SoC sampling #"+ str(i))
                    self.dac_instance.current_sink_curr_mA(self.Sampling_pwr_mW/self.DCDC_Out_V)
                    time.sleep(self.Sampling_time_s)
                    self.dac_instance.current_sink_curr_mA(self.Idle_pwr_mW/self.DCDC_Out_V)
                    time.sleep(self.Check_time_s)
                    if sys_states[6] == 1:
                        performance_log[0] = performance_log[0] + 1     # Register sampling event
                    if i < self.Communication_incidence-1:
                        time.sleep(1/self.Sampling_frequency_Hz-self.Sampling_time_s-self.Check_time_s)

                print("SoC communicating")
                self.dac_instance.current_sink_curr_mA(self.Communication_pwr_mW / self.DCDC_Out_V)
                time.sleep(self.Communication_time_s)
                self.dac_instance.current_sink_curr_mA(self.Idle_pwr_mW/self.DCDC_Out_V)
                time.sleep(self.Check_time_s)
                if sys_states[6] == 1:
                    performance_log[1] = performance_log[1] + 1     # Register communication event
                t_comm_end = time.time()

                time.sleep(1/self.Sampling_frequency_Hz-self.Communication_time_s-self.Sampling_time_s-self.Check_time_s)


            else:
                time.sleep(0.1)
                self.SoC_power_off = 1   # Emulate initial power consumption next time the DCDC converter turns on





    """
        def SoC_Emulator(self, exit_event, sys_states, performance_log):

        while not exit_event.is_set():
            while not exit_event.is_set() and sys_states[6] == 1:
                if SoC_power_off == 1:
                    print("SoC booting")
                    time.sleep(0.25) # Delay to make sure that the converter's ouput voltage is stable
                    # SoC Boot Phase 1
                    self.dac_instance.current_sink_curr_mA(18/self.DCDC_Out_V)
                    time.sleep(3.5/1000)
                    # SoC Boot Phase 2
                    self.dac_instance.current_sink_curr_mA(0.005/self.DCDC_Out_V)
                    time.sleep(0.38)
                    # SoC Boot Phase 3
                    self.dac_instance.current_sink_curr_mA(23/self.DCDC_Out_V)
                    time.sleep(43/1000)
                    SoC_power_off = 0

                for i in range(self.Communication_incidence):
                    print("SoC sampling")
                    self.dac_instance.current_sink_curr_mA(self.Sampling_pwr_mW/self.DCDC_Out_V)
                    time.sleep(self.Sampling_time_s)
                    self.dac_instance.current_sink_curr_mA(self.Idle_pwr_mW/self.DCDC_Out_V)
                    time.sleep(self.Check_time_s)
                    if sys_states[6] == 1:
                        performance_log[0] = performance_log[0] + 1     # Register sampling event
                    if i < self.Communication_incidence-1:
                        time.sleep(self.Sampling_period_s-self.Sampling_time_s-self.Check_time_s)

                print("SoC communicating")
                self.dac_instance.current_sink_curr_mA(self.Communication_pwr_mW / self.DCDC_Out_V)
                time.sleep(self.Communication_time_s)
                self.dac_instance.current_sink_curr_mA(self.Idle_pwr_mW/self.DCDC_Out_V)
                time.sleep(self.Check_time_s)
                if sys_states[6] == 1:
                    performance_log[1] = performance_log[1] + 1     # Register communication event
                time.sleep(self.Sampling_period_s-self.Communication_time_s-self.Sampling_time_s-self.Check_time_s)
            else:
                time.sleep(0.1)
                SoC_power_off = 1   # Emulate initial power consumption next time the DCDC converter turns on
    """


    def Env_Emulator(self, file_instance, led_instance, data_log, env_dataset_done):

        NumSteps = 2* pm.IrrDatasetTimeStep / pm.EvalSpeedUp   # Number of steps for 0.5s change interval
        for key, irrValue in file_instance.brightnessDF.itertuples():
            if key < len(file_instance.brightnessDF)-1:
                nextValue = file_instance.single_value(key+1)
                for i in range(0, int(NumSteps), 1):
                    tempValue = irrValue + ((nextValue - irrValue) * i) / NumSteps
                    led_instance.set_brightness(tempValue)
                    data_log.update({"irrValue": tempValue})
                    time.sleep(0.5)
        env_dataset_done.set()

class Bluetooth:

    def __init__(self):
        print("Class Bluetooth Init")
        self.device_mac_address = 'D8:D4:E7:9D:12:41' #Lukas: 'DA:B0:BB:56:98:73', DK: 'E0:21:78:85:2A:FB', Eval: 'D8:D4:E7:9D:12:41'
        self.service = "e9ea0001-e19b-482d-9293-c7907585fc48"
        self.characteristic = "e9ea0002-e19b-482d-9293-c7907585fc48"
        self.client = BleakClient(self.device_mac_address, disconnected_callback=self.on_disconnect)
        #self.serviceChar = '0x180D'
        self.bytes_received = 0

    def BT_Process(self, exit_event, performance_log, data_log, bt_recieved):
        self.bt_recieved = bt_recieved
        asyncio.run(self.connect_to_device(exit_event, performance_log, data_log))

    async def connect_to_device(self, exit_event, performance_log, data_log):
        self.performance_log = performance_log
        while not exit_event.is_set():
            try:
                if not self.client.is_connected:
                    # Set a timeout for the connection attempt
                    #connect_coro = self.client.connect()
                    try:
                        print("Trying to connect.")
                        await asyncio.wait_for(self.client.connect(), timeout=2)  # Adjust the timeout value as needed
                    except asyncio.TimeoutError:
                        print("Connection attempt timed out.")
                        continue  # Retry the connection loop
                else:
                    #msg.messages[msg.btConnect] = 1
                    data_log.update({"btConnectedFlag": 1})
                    print("Connected to the device!")
                    try:
                        print("Starting Notifications.")
                        # Subscribe to the Heart Rate Service (0x180D) for notifications
                        await self.client.start_notify(self.characteristic, self.notification_handler)
                        print("Starting Notifications successfull!")
                    except:
                        print("Starting Notifications failed.")
                        continue

                    #await asyncio.sleep(5)

                    await self.client.disconnect()
                    data_log.update({"btConnectedFlag": 0})

                    #msg.messages[msg.btConnect] = 0

            except Exception as e:
                print(f"Error: {e}")
                self.client = BleakClient(self.device_mac_address, disconnected_callback=self.on_disconnect)
                self.performance_log[4] = self.performance_log[4] + 1


    def notification_handler(self, sender, data):
        # Handle received notifications here
        numbers = []
        for i in range(0,len(data), 2):
            #print(data[i:i+2])
            number = int.from_bytes(data[i:i+2], byteorder='little')
            numbers.append(number)
        if numbers[0] == 65535:
            print('Recieved performance data')
            self.performance_log[0] = int(numbers[1])    # Checkpoint
            self.performance_log[1] = int(numbers[2])    # Recover
            self.performance_log[2] = int(numbers[3])    # Measure/sampling
            self.performance_log[3] = int(numbers[4])    # Communicate
            self.bt_recieved.value = 1
            print(numbers)

    def on_disconnect(self, client):
        #msg.messages[msg.btConnect] = 0
        print("Disconnected from the device")