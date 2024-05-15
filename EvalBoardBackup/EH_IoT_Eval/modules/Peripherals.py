
import spidev
import numpy as np
import RPi.GPIO as GPIO
import pigpio
import modules.pinOut_BCM as pinOut
import modules.Aux as Aux
#import messages as msg
import time
import timeit
from multiprocessing import Value, Array, Event
import parameters as pm
from modules.file_handler import file
import ctypes


class Peri:

    def __init__(self):

        print("Class Peri Init")

        self.setup_gpio()


    def setup_gpio(self):
        """Setup GPIO pins."""
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(pinOut.ADC12_RESET, GPIO.OUT)
        GPIO.setup(pinOut.ADC1_DRDY, GPIO.IN)

        # Bank 2 Switch
        GPIO.setup(pinOut.RPI_GPIO_22, GPIO.OUT)
        GPIO.output(pinOut.RPI_GPIO_22, GPIO.LOW)
        print("Bank 2 inactive")
        # GPIO.output(pinOut.RPI_GPIO_22, GPIO.HIGH)
        # print("Bank 2 active")

        # Bank 3 Switch
        GPIO.setup(pinOut.I2C_SCI, GPIO.OUT)
        GPIO.output(pinOut.I2C_SCI, GPIO.LOW)
        print("Bank 3 inactive")
        # GPIO.output(pinOut.I2C_SCI, GPIO.HIGH)
        # print("Bank 3 active")

        # MPPT / Bypass Switch
        GPIO.setup(pinOut.UART_TXD, GPIO.OUT)
        GPIO.output(pinOut.UART_TXD, GPIO.LOW)
        # GPIO.setup(pinOut.SPI_1_CS_ADC1, GPIO.OUT)
        # GPIO.setup(pinOut.SPI_1_CS_ADC2, GPIO.OUT)

        # Emulated DCDC EN Signal
        GPIO.setup(pinOut.UART_RXD, GPIO.OUT)
        GPIO.output(pinOut.UART_RXD, GPIO.LOW)

        # Board LED for Debugging
        GPIO.setup(pinOut.BOARD_LED, GPIO.OUT)
        GPIO.output(pinOut.BOARD_LED, GPIO.LOW)

        # Temp Debug!! (EH Connect Test)
        GPIO.setup(pinOut.I2C_SDA, GPIO.OUT)
        GPIO.output(pinOut.I2C_SDA, GPIO.HIGH)


class ADC:

    sample_cnt = 0
    switcher = 0
    num_samples = 400
    channels = 16


    def __init__(self, system_states_instance, end_voltage_reached_event, start_voltage_reached_event, shared_V_th, shared_V_hyst, Dynamic_Banks):

        print("Class ADC Init")

        self.V1_Max_V_handler = Aux.ThresholdHandler()
        self.Initial_Discharge = Aux.ThresholdHandler()

        self.SPI_freq = 12500000

        self.ADC1 = spidev.SpiDev()
        self.ADC1.open(0, 0)
        self.ADC1.max_speed_hz = self.SPI_freq
        self.ADC1.mode = 0

        self.ADC2 = spidev.SpiDev()
        self.ADC2.open(0, 1)
        self.ADC2.max_speed_hz = self.SPI_freq
        self.ADC2.mode = 0

        self.reset_adc()

        self.write_adc_register(0x011, 0b01100100, self.ADC1)  # High Resolution Mode
        self.write_adc_register(0x011, 0b01100100, self.ADC2)  # High Resolution Mode

        self.write_adc_register(0x011, 0b00100010, self.ADC1)  # Divide MCLK by 2
        self.write_adc_register(0x011, 0b00100010, self.ADC2)  # Divide MCLK by 2

        self.write_adc_register(0x012, 0b00001000, self.ADC1)  # Synchronize ADCs
        self.write_adc_register(0x012, 0b00001001, self.ADC1)  # Synchronize ADCs

        self.write_adc_register(0x013, 0b10010000, self.ADC1)  # Set SD-output
        self.write_adc_register(0x013, 0b10010000, self.ADC2)  # Set SD-output

        # Use multiprocessing.Array for shared array
        self.ADC12_float_data_A = Array('d', [0.0] * (self.num_samples * self.channels))
        self.ADC12_float_data_B = Array('d', [0.0] * (self.num_samples * self.channels))

        self.ADC_mean =[0.0] * self.channels

        self.mean_compute_event_A = Event()
        self.mean_compute_event_B = Event()

        self.banks_full_checker = Aux.ThresholdHandler()
        self.MPPT_switcher = Aux.ThresholdHandler()
        self.DCDC_switcher = Aux.ThresholdHandler()
        self.V1_bank_supervisor = Aux.ThresholdHandler()
        self.V2_bank_supervisor = Aux.ThresholdHandler()
        self.banks_discharged_checker = Aux.ThresholdHandler()

        self.end_voltage_reached_event = end_voltage_reached_event
        self.start_voltage_reached_event = start_voltage_reached_event
        self.V_th = shared_V_th
        self.V_hyst = shared_V_hyst
        self.Dynamic_Banks = Dynamic_Banks

        self.filename = Value(ctypes.c_char_p, b'\0' * 256)

        self.system_states_instance = system_states_instance# = System_States()


    def reset_adc(self):
        """Reset the ADC."""
        GPIO.output(pinOut.ADC12_RESET, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(pinOut.ADC12_RESET, GPIO.HIGH)
        time.sleep(0.1)

    def data_ready_callback(self, channel):
        # Handle data ready interrupt.

        #GPIO.output(pinOut.I2C_SDA, GPIO.HIGH)

        self.response1 = self.ADC1.xfer2(
            [0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        #print(self.response1)
        self.response2 = self.ADC2.xfer2(
            [0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

        #GPIO.output(pinOut.I2C_SDA, GPIO.LOW)

        self.process_values(self.response1, self.response2)
        

    def read_adc_register(self, address, spi):
        """Read data from ADC register."""
        cmd = (1 << 7) | address
        resp = spi.xfer2([cmd, 0x00])
        if len(resp) < 2:
            print("Incomplete data received from ADC!")
            return None
        return [bin(resp[0]), bin(resp[1])]

    def write_adc_register(self, address, value, spi):
        """Write data to ADC register and verify."""
        cmd = [address, value]
        spi.xfer2(cmd)

        # Verification
        readValue = self.read_adc_register(address, spi)
        if readValue[1] != bin(value):
            print(
                f"Write mismatch! Expected {bin(value)} but got {readValue[1]} at address {hex(address)}. Header: {readValue[0]}")
        else:
            print(f"Write successful! {bin(value)} at address {hex(address)}.")



    #def process_values(self,ADC1_Hex_Data, ADC2_Hex_Data):
    def process_values(self, ADC1_Hex_Data, ADC2_Hex_Data):

        # Extract 24-bit data values from response
        ADC1_raw_data = [(ADC1_Hex_Data[i + 1] << 16) | (ADC1_Hex_Data[i + 2] << 8) | ADC1_Hex_Data[i + 3] for i in range(0, len(ADC1_Hex_Data), 4)]
        ADC2_raw_data = [(ADC2_Hex_Data[i + 1] << 16) | (ADC2_Hex_Data[i + 2] << 8) | ADC2_Hex_Data[i + 3] for i in range(0, len(ADC2_Hex_Data), 4)]

        # Convert to signed 32-bit integers
        ADC1_raw_data = [(val & 0xFFFFFF) - (0x800000 if val & 0x800000 else 0) for val in ADC1_raw_data]
        ADC2_raw_data = [(val & 0xFFFFFF) - (0x1000000 if val & 0x800000 else 0) for val in ADC2_raw_data]

        # Convert to float
        ADC1_float_data = [(raw_val / 0x7FFFFF) * 3.3 for raw_val in ADC1_raw_data]
        ADC2_float_data = [(raw_val / 0x7FFFFF) * 3.3 for raw_val in ADC2_raw_data]

        # Convert to float
        #ADC1_float_data = [(raw_val / 0x800000) * 3.3 for raw_val in ADC1_raw_data]
        #ADC2_float_data = [(raw_val / 0x800000) * 3.3 for raw_val in ADC2_raw_data]

        if self.switcher == 0:
            start_index = self.sample_cnt * self.channels
            self.ADC12_float_data_A[start_index:start_index + len(ADC1_float_data) * 2] = ADC1_float_data + ADC2_float_data
        else:
            start_index = self.sample_cnt * self.channels
            self.ADC12_float_data_B[start_index:start_index + len(ADC1_float_data) * 2] = ADC1_float_data + ADC2_float_data

        # Switch between input data buffers
        self.sample_cnt += 1
        if self.sample_cnt >= self.num_samples:
            if self.switcher == 0:
                self.mean_compute_event_A.set()
                self.switcher = 1
            else:
                self.mean_compute_event_B.set()
                self.switcher = 0
            self.sample_cnt = 0


        
        # Triggers based on monitored voltages / currents. CAUTION: Compensation for voltage dividers required here.
        if self.Dynamic_Banks.value:
            # Activate / Deactivate Bank 2 based on Bank 1 voltage
            self.V1_bank_supervisor.above_threshold(ADC1_float_data[2], self.V_th.value, self.system_states_instance.activate_bank,2)
            self.V1_bank_supervisor.below_threshold(ADC1_float_data[2], self.V_th.value - self.V_hyst.value, self.system_states_instance.deactivate_bank, 2)
            # Activate / Deactivate Bank 3 based on Bank 2 voltage
            self.V2_bank_supervisor.above_threshold(ADC1_float_data[3], self.V_th.value, self.system_states_instance.activate_bank,3)
            self.V2_bank_supervisor.below_threshold(ADC1_float_data[3], self.V_th.value - self.V_hyst.value, self.system_states_instance.deactivate_bank, 3)
            # Enable/Disable DC/DC converter based on Storage Out voltage
            self.DCDC_switcher.above_threshold(ADC1_float_data[7], 2.0, self.system_states_instance.DCDC_activate) #1.4 # self.V_th.value - 0.1
            self.DCDC_switcher.below_threshold(ADC1_float_data[7], 0.7, self.system_states_instance.DCDC_deactivate)
        else:
            # Statically activate all banks
            self.V1_bank_supervisor.above_threshold(ADC1_float_data[2], 0.1, self.system_states_instance.activate_bank,2)
            self.V1_bank_supervisor.above_threshold(ADC1_float_data[2], 0.1, self.system_states_instance.activate_bank,3)
            # Enable/Disable DC/DC converter based on Storage Out voltage
            self.DCDC_switcher.above_threshold(ADC1_float_data[7], self.V_th.value, self.system_states_instance.DCDC_activate) #1.4 # self.V_th.value - 0.1
            self.DCDC_switcher.below_threshold(ADC1_float_data[7], self.V_hyst.value, self.system_states_instance.DCDC_deactivate)
            
        # Enable/Disable MPPT based on Storage In voltage
        #self.MPPT_switcher.above_threshold(ADC1_float_data[1], 0.1, self.system_states_instance.MPPT_activate)  # -> Activate for no bypass
        self.MPPT_switcher.above_threshold(ADC1_float_data[1], 1.8, self.system_states_instance.MPPT_activate) # 1.8
        self.MPPT_switcher.below_threshold(ADC1_float_data[1], 1.6, self.system_states_instance.MPPT_deactivate) #1.6
        
        # Evaluation Start / Stop
        #self.banks_full_checker.above_threshold(ADC1_float_data[2], 2.8, self.end_voltage_reached_event.set)
        
        self.banks_discharged_checker.below_threshold(ADC1_float_data[2], 0.3, self.start_voltage_reached_event.set)
        

    def Data_Processing_A(self, exit_event, dataset, data_log, adc_channels, sys_states):

        DCDC_off_delay_cnt = 0

        while not exit_event.is_set():

            if self.mean_compute_event_A.is_set():

                # Convert the shared array to a NumPy array
                data_array = np.frombuffer(self.ADC12_float_data_A.get_obj(), dtype='d').reshape((self.num_samples, self.channels))

                # Calculate the mean values along axis 0 (columns)
                channel_means = np.mean(data_array, axis=0)

                for ch_num in [0,8]:
                    channel_means[ch_num] = channel_means[ch_num]*2     # Compensate for voltage divider
                for ch_num in [11, 12, 13]:
                    channel_means[ch_num] = channel_means[ch_num] / (4.02*25)  # Store corresponding current values
                for ch_num in [14, 15]:
                    channel_means[ch_num] = channel_means[ch_num] / (8.04*25)  # Store corresponding current values

                data_log.update({channel: mean_value for channel, mean_value in zip(adc_channels, channel_means)})

                filename = self.filename.value.decode('utf-8')
                file_instance = file(dataset, filename)
                file_instance.append_to_file(data_log, sys_states)

                # Prevent DC/DC deadlocks (if converter enabled but output voltage below threshold, turn off)
                if sys_states[6] == 1 and channel_means[8] < 1.7:
                    DCDC_off_delay_cnt = DCDC_off_delay_cnt + 1
                    if DCDC_off_delay_cnt >= 3:
                        self.system_states_instance.DCDC_deactivate()
                else:
                    DCDC_off_delay_cnt = 0

                #print(channel_means[1])

                self.mean_compute_event_A.clear()

    def Data_Processing_B(self, exit_event, dataset, data_log, adc_channels, sys_states):

        DCDC_off_delay_cnt = 0

        while not exit_event.is_set():

            if self.mean_compute_event_B.is_set():
                # Convert the shared array to a NumPy array
                data_array = np.frombuffer(self.ADC12_float_data_B.get_obj(), dtype='d').reshape((self.num_samples, self.channels))

                # Calculate the mean values along axis 0 (columns)
                channel_means = np.mean(data_array, axis=0)

                for ch_num in [0,8]:
                    channel_means[ch_num] = channel_means[ch_num]*2     # Compensate for voltage divider
                for ch_num in [11, 12, 13]:
                    channel_means[ch_num] = channel_means[ch_num] / (4.02*25)  # Store corresponding current values
                for ch_num in [14, 15]:
                    channel_means[ch_num] = channel_means[ch_num] / (8.04*25)  # Store corresponding current values

                data_log.update({channel: mean_value for channel, mean_value in zip(adc_channels, channel_means)})

                filename = self.filename.value.decode('utf-8')
                file_instance = file(dataset, filename)
                file_instance.append_to_file(data_log, sys_states)

                # Prevent DC/DC deadlocks (if converter enabled but output voltage below threshold, turn off)
                if sys_states[6] == 1 and channel_means[8] < 1.7:
                    DCDC_off_delay_cnt = DCDC_off_delay_cnt + 1
                    if DCDC_off_delay_cnt >= 3:
                        self.system_states_instance.DCDC_deactivate()
                else:
                    DCDC_off_delay_cnt = 0
                    
                #print(channel_means)

                self.mean_compute_event_B.clear()


class System_States:

    def __init__(self, sys_states):

        print("Class System_States Init")

        self.sys_states = sys_states

        for i in range (1,5):
            self.deactivate_bank(i)
        self.MPPT_deactivate()
        self.DCDC_deactivate()

    def activate_bank(self,number): # Bank number: 1...5

        if number == 0:
            print("Bank 0 does not exist.")
        elif number == 1:       # Bank 1 is always enabled
            print("Bank 1 can not be switched")
        #elif number == 2 and self.Bank_activated_state[number] == 0:
        elif number == 2 and self.sys_states[number-1] == 0:
            GPIO.output(pinOut.RPI_GPIO_22, GPIO.HIGH)
            self.sys_states[number-1] = 1
            print("Bank 2 activated")
        elif number == 3 and self.sys_states[number-1] == 0:
            GPIO.output(pinOut.I2C_SCI, GPIO.HIGH)
            self.sys_states[number-1] = 1
            print("Bank 3 activated")


    def deactivate_bank(self,number): # Bank number: 1...5
        if number == 0:
            print("Bank 0 does not exist.")
        if number == 1:     # Bank 1 is always enabled
            print("Bank 1 can not be switched")
        elif number == 2 and self.sys_states[number-1] == 1:
            GPIO.output(pinOut.RPI_GPIO_22, GPIO.LOW)
            self.sys_states[number-1] = 0
            print("Bank 2 deactivated")
        elif number == 3 and self.sys_states[number-1] == 1:
            GPIO.output(pinOut.I2C_SCI, GPIO.LOW)
            self.sys_states[number-1] = 0
            print("Bank 3 deactivated")

    def MPPT_activate(self):
        if self.sys_states[5] == 0:
            GPIO.output(pinOut.UART_TXD, GPIO.HIGH)
            self.sys_states[5] = 1
            GPIO.output(pinOut.BOARD_LED, GPIO.HIGH)
            print("MPPT activated")

    def MPPT_deactivate(self):
        if self.sys_states[5] == 1:
            GPIO.output(pinOut.UART_TXD, GPIO.LOW)
            self.sys_states[5] = 0
            GPIO.output(pinOut.BOARD_LED, GPIO.LOW)
            print("MPPT deactivated")

    def DCDC_activate(self):
        if self.sys_states[6] == 0:
            GPIO.output(pinOut.UART_RXD, GPIO.HIGH)
            self.sys_states[6] = 1
            print("DCDC activated")

    def DCDC_deactivate(self):
        if self.sys_states[6] == 1:
            GPIO.output(pinOut.UART_RXD, GPIO.LOW)
            self.sys_states[6] = 0
            print("DCDC deactivated")


class DAC:

    def __init__(self):

        print("Class DAC Init")

        self.DAC1 = spidev.SpiDev()
        self.DAC2 = spidev.SpiDev()

        # Current Sink
        # self.DAC2 = spidev.SpiDev()
        self.DAC2.open(1, 1)
        self.DAC2.max_speed_hz = 1000000  # 1 MHz
        self.DAC2.mode = 2

        # Initialize the current sink
        self.DAC2.writebytes2([0x05, 0x00, 0x0A])  # Soft Reset
        time.sleep(0.5)
        self.DAC2.writebytes2([0x03, 0x00, 0x00])  # DAC Power Up

        # Current Source
        # self.DAC1 = spidev.SpiDev()
        self.DAC1.open(1, 0)
        self.DAC1.max_speed_hz = 1000000  # 1 MHz
        self.DAC1.mode = 2

        # Initialize the current source
        self.DAC1.writebytes2([0x05, 0x00, 0x0A])  # Soft Reset
        time.sleep(0.5)
        self.DAC1.writebytes2([0x03, 0x00, 0x00])  # DAC Power Up
        self.DAC1.writebytes(self.DACpercent_to_hexlist(0))

    def current_sink(self, percentage: float):
        print("Setting current sink to " + str(percentage) + "%")
        self.DAC2.writebytes(self.DACpercent_to_hexlist(percentage))

    def current_sink_curr_mA(self, current_mA: float):
        print("Setting current sink to " + str(current_mA) + " mA")
        if current_mA > 16.5:
            print("Warning: Maximum current draw at 3.3 V is 16.5 mA!")
        self.DAC2.writebytes(self.DACpercent_to_hexlist(current_mA/25*100))


    def DACpercent_to_hexlist(self, percentage: float):
        DACCode = int(percentage / 100 * (pow(2, 16) - 1))
        hex_num = f"{DACCode:#0{6}x}"
        split_array = [hex_num[i:i + 2] for i in range(0, len(hex_num), 2)]
        str_array = ["0x" + split_array[i] for i in range(1, len(split_array))]
        byte_array = [int(str_array[i], 16) for i in range(0, len(split_array) - 1)]
        byte_array.insert(0, 0x08)
        return byte_array



class LED:
    freq = 250
    PWM_range = 40000
    duty = 0

    def __init__(self, data_log):
        # self.get_values_from_file(file)

        print("Class LED Init")

        self.pi = pigpio.pi()
        self.pi.set_mode(pinOut.LED_DRV_DIM, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(pinOut.LED_DRV_DIM, self.freq)
        self.pi.set_PWM_range(pinOut.LED_DRV_DIM, self.PWM_range)

        print("PWM Frequency:")
        print(self.pi.get_PWM_frequency(pinOut.LED_DRV_DIM))

        self.data_log = data_log

        # Open calibration file (Measured W/m^2 at 100% LED power (channel 2))
        f = open('/home/admin/LED_Calib.txt', 'r')
        self.LED_Irr_max = float(f.read())
        f.close()

        # Scaler for matching evaluation board energy input
        f = open('/home/admin/Board_Scaler.txt', 'r')
        self.Board_Scaler = float(f.read())
        f.close()

        self.set_brightness(0)

    def get_brightness_percent(self):
        return self.duty

    def set_brightness(self, watt):
        temp_duty = watt * pm.IrradianceScaler / self.LED_Irr_max # * self.Board_Scaler * pm.EvalSpeedUp
        if temp_duty >= 0 and temp_duty <= 1:
            self.pi.set_PWM_dutycycle(pinOut.LED_DRV_DIM, temp_duty * self.PWM_range)
            self.duty = temp_duty
            self.data_log.update({"ledPercent": temp_duty})
            print(temp_duty)

    # Mainly for testing LED linearity
    def set_dutycycle(self, dutycycle):
        if dutycycle >= 0 and dutycycle <= 1:
            self.pi.set_PWM_dutycycle(pinOut.LED_DRV_DIM, dutycycle * self.PWM_range)
            self.duty = dutycycle
            self.data_log.update({"ledPercent": dutycycle})
            print(dutycycle)


"""
async def LEDcoroutine(file_handler: file):
    # Initialize LED
    led_control = LED(file_handler.inputFile)

    timer = atimer.Timer(pm.LoggingTimeStep)
    timer.start()
    NumSteps = pm.IrrDatasetTimeStep / pm.EvalSpeedUp / pm.LoggingTimeStep
    for key, irrValue in file_handler.brightnessDF.itertuples():
        nextValue = file_handler.single_value(key)
        for i in range(0, int(NumSteps), 1):
            # print("Before await timer")
            tempValue = irrValue + ((nextValue - irrValue) * i) / NumSteps
            led_control.set_brightness(tempValue)
            msg.messages[msg.irrValue] = tempValue
            # await asyncio.sleep(pm.timeStep/pm.rampUpStep)

            await timer
            # print("After await timer")
            file_handler.append_to_file()
            msg.resetBTmessages()
            # print("Written to file")

        timer.close()

    # End the other corutines
    msg.testActive = False
"""