
from multiprocessing import Process, Event, Value, Array, Manager
import threading

from modules.Peripherals import Peri, ADC, DAC, LED, System_States
from modules.Aux import Emulator, Bluetooth

import RPi.GPIO as GPIO
import modules.pinOut_BCM as pinOut
from modules.file_handler import file
import parameters as pm

import pandas as pd
import time
from datetime import datetime
import socket

# Create events
exit_event = Event()
end_voltage_reached_event = Event()
start_voltage_reached_event = Event()
env_dataset_done = Event()


# Create shared variables
shared_V_th = Value('d', 0.0)
shared_V_hyst = Value('d', 0.0)
Dynamic_Banks = Value('i',0)
performance_log = Array('i', [0, 0, 0, 0]) # Checkpoint, Recover, Sampling, Communication


Peri()
dac_instance = DAC()


def main():

    print("Starting main")

    # Define if static or dynamic energy storage banks
    Dynamic_Banks.value = 0

    # Define Irradiance Dataset
    #dataset = "winter_28days_start_cut.tsv"
    #dataset = "autumn_17days_start_cut.tsv"
    #dataset = "summer_31days_start_cut.tsv"
    #dataset = "3_winter_3_autumn_2_summer_start_cut.tsv"
    #dataset = "Test_500W.tsv"
    #dataset = "Test_700W-300W_Mix_Long.tsv"
    #dataset = "Test_200W-700W-changes.tsv"
    #dataset = "summer7low.tsv"
    #dataset = "summer10high.tsv"
    dataset = "summer2smooth.tsv"
    #dataset = "winter11low.tsv"
    #dataset = "winter20high.tsv"
    #dataset = "winter3smooth.tsv"

    if Dynamic_Banks.value:
        print("Dynamic Banks ACTIVATED!")
    else:
        print("Dynamic Banks DEACTIVATED!")
    time.sleep(2)

    sys_states = init_sys_states()

    manager = Manager()
    data_log, adc_channels = init_data_log(manager)


    system_states_instance = System_States(sys_states)
    adc_instance = ADC(system_states_instance, end_voltage_reached_event, start_voltage_reached_event, shared_V_th, shared_V_hyst, Dynamic_Banks)
    emulator_instance = Emulator(dac_instance)
    led_instance = LED(data_log)
    bluetooth_instance = Bluetooth()

    # Attaching Data_Ready Callback
    GPIO.add_event_detect(pinOut.ADC1_DRDY, GPIO.FALLING, callback=adc_instance.data_ready_callback)

    time.sleep(1)

    #Exp_Runtime1(adc_instance, adc_channels, led_instance, system_states_instance, sys_states, dataset, data_log)

    #Exp_Runtime2(adc_instance, adc_channels, led_instance, system_states_instance, sys_states, dataset, data_log)

    Exp_Runtime3(adc_instance, adc_channels, led_instance, system_states_instance, emulator_instance, bluetooth_instance, sys_states, dataset, data_log, performance_log)

    #Exp_LEDCalib(adc_instance, adc_channels, led_instance, sys_states, dataset, data_log)





def init_sys_states():
    # sys_states array: (B1, B2, B3, B4, B5, MPPT, DCDC)
    # Components will be deactivated in System_States init
    sys_states = Array('i', (1, 1, 1, 1, 1, 1, 1))
    return sys_states


def init_data_log(manager):

    data_log = manager.dict()

    timeStamp = "datetime"
    irrValue = "irrValue"
    ledPercent = "ledPercent"

    btConnect = "btConnectedFlag"
    # btDisconnect    = "btDisconnectFlag"
    btPackets = "btPackets"

    adc1ch0 = "EH_IN_+_BUF"
    adc1ch1 = "CSA_STORAGE_IN_+"
    adc1ch2 = "V_BANK1"
    adc1ch3 = "V_BANK2"
    adc1ch4 = "V_BANK3"
    adc1ch5 = "V_BANK4"
    adc1ch6 = "V_BANK5"
    adc1ch7 = "STORAGE_OUT"

    adc2ch0 = "DCDC_OUT_BUF"
    adc2ch1 = "EXT_AN_IN_1"
    adc2ch2 = "EXT_AN_IN_2"
    adc2ch3 = "EXT_CSA"
    adc2ch4 = "CSA_EH_IN"
    adc2ch5 = "CSA_STORAGE_IN"
    adc2ch6 = "CSA_STORAGE_OUT"
    adc2ch7 = "CSA_DCDC_OUT"

    MPPT_EN = "MPPT_EN"
    DCDC_EN = "DCDC_EN"
    BANK1_EN = "BANK1_EN"
    BANK2_EN = "BANK2_EN"
    BANK3_EN = "BANK3_EN"
    BANK4_EN = "BANK4_EN"
    BANK5_EN = "BANK5_EN"

    adc_channels = [adc1ch0, adc1ch1, adc1ch2, adc1ch3, adc1ch4, adc1ch5, adc1ch6, adc1ch7, adc2ch0, adc2ch1, adc2ch2, adc2ch3, adc2ch4, adc2ch5, adc2ch6, adc2ch7]

    data_log.update({timeStamp: 0,
                irrValue: 0,
                ledPercent: 0,
                btConnect: 0,
                # btDisconnect:   0,
                btPackets: 0,

                adc1ch0: 0,
                adc1ch1: 0,
                adc1ch2: 0,
                adc1ch3: 0,
                adc1ch4: 0,
                adc1ch5: 0,
                adc1ch6: 0,
                adc1ch7: 0,

                adc2ch0: 0,
                adc2ch1: 0,
                adc2ch2: 0,
                adc2ch3: 0,
                adc2ch4: 0,
                adc2ch5: 0,
                adc2ch6: 0,
                adc2ch7: 0,
                MPPT_EN: 0,
                DCDC_EN: 0,
                BANK1_EN: 1,
                BANK2_EN: 0,
                BANK3_EN: 0,
                BANK4_EN: 0,
                BANK5_EN: 0,
                })

    return data_log, adc_channels


def drain_energy_storage():
    print("Starting Energy Drain")
    start_voltage_reached_event.clear()
    dac_instance.current_sink(100)
    while not start_voltage_reached_event.is_set():
        time.sleep(0.1)
    dac_instance.current_sink(0)
    print("Draining Stage 1 finished")
    time.sleep(3)
    start_voltage_reached_event.clear()

    dac_instance.current_sink(2)
    while not start_voltage_reached_event.is_set():
        time.sleep(0.1)
    dac_instance.current_sink(0)
    print("Draining Stage 2 finished")
    time.sleep(1)
    start_voltage_reached_event.clear()




# Drain, turn on LED for fixed period, measure time for single DCDC=On period, stop when DCDC off
def Exp_Runtime1(adc_instance, adc_channels, led_instance, system_states_instance, sys_states, dataset, data_log):
    filename_time_logger = "DCDC_Runtime_Log.csv"

    # Create an empty DataFrame with one row and column names
    df = pd.DataFrame(columns=['Brightness', 'V_th', 'V_hyst', 'time'])
    df.to_csv(pm.outputFilePath + filename_time_logger, index=False, sep="\t")  # Write the column names to the CSV file

    # Eval loop through bank threshold and hysteresis voltages. Discharge, enable LED for xx s and measure on-time of DCDC
    # for bri in range(400, 1600, 400):
    for bri in [15]:# range(2, 25, 3):
        for V_th in range(20, 29, 2):  # 20,27,1
            shared_V_th.value = V_th / 10
            for V_hyst in range(1, 10, 1):  # 1, 10, 2
                shared_V_hyst.value = V_hyst / 10

                print("Bri: " + str(bri))
                print("V_th: " + str(shared_V_th.value))
                print("V_hyst: " + str(shared_V_hyst.value))

                # Drain the energy storage
                drain_energy_storage()

                print("Energy storage is drained.")

                # Parameters for LED time
                LED_time = 800  # LED on-time in s
                Sleep_stepsize = 0.01  # time in s
                Timer_started = 0  # Flag
                start_time = 0  # Will be set below

                # OPEN NEW FILE
                filename = f"output_Bri_{bri}_NoScaler_V_th_{shared_V_th.value}_V_hyst_{shared_V_hyst.value}_LED_{LED_time}s.csv"  # Create a unique filename
                # filename = f"output_Bri_{bri}_Bank2_static.csv"  # Create a unique filename
                file_instance = file(dataset, filename)
                file_instance.create_output_file(data_log)  # Create the output file
                print("Output File Created")
                adc_instance.filename.value = filename.encode('utf-8')

                # Start Processes
                processes = []
                p_Proc_A = Process(target=adc_instance.Data_Processing_A, args=(exit_event, dataset, data_log, adc_channels, sys_states))
                p_Proc_B = Process(target=adc_instance.Data_Processing_B, args=(exit_event, dataset, data_log, adc_channels, sys_states))
                processes.append(p_Proc_A)
                processes.append(p_Proc_B)
                p_Proc_A.start()
                p_Proc_B.start()

                print("Turning on LED.")

                # Turn on LED
                # ! Bypassing the Irradiance Scaler !
                led_instance.set_brightness(bri/pm.IrradianceScaler)

                # LED on. Waiting for time to elapse
                for i in range(int(LED_time / Sleep_stepsize)):
                    time.sleep(Sleep_stepsize)
                    if sys_states[6] == 1 and Timer_started == 0:
                        # Record the start time
                        start_time = time.time()
                        Timer_started = 1
                        print("DCDC converter turned on -> Timer started")

                print("Turning off LED. Waiting for DCDC converter to turn off.")
                # Turn off LED
                led_instance.set_brightness(0)

                while sys_states[6] == 1:
                    time.sleep(0.01)

                # Record the end time
                end_time = time.time()
                # Calculate the elapsed time
                elapsed_time = end_time - start_time

                df.loc[0, 'Brightness'] = bri
                df.loc[0, 'V_th'] = shared_V_th.value
                df.loc[0, 'V_hyst'] = shared_V_hyst.value
                df.loc[0, 'time'] = elapsed_time

                df.to_csv(pm.outputFilePath + filename_time_logger, mode='a', header=False, index=False,
                          sep="\t")  # Append data without writing column names

                print("DCDC Converter off. Going to next iteration.")

                exit_event.set()  # Set the event to signal the child process to exit
                # completing process
                for p in processes:
                    p.join()
                exit_event.clear()


# Drain, turn on LED for fixed period, measure time for total DCDC=On periods, stop when DCDC off
def Exp_Runtime2(adc_instance, adc_channels, led_instance, system_states_instance, sys_states, dataset, data_log):
    filename_time_logger = "DCDC_Runtime_Log.csv"

    # Create an empty DataFrame with one row and column names
    df = pd.DataFrame(columns=['Brightness', 'V_th', 'V_hyst', 'time'])
    df.to_csv(pm.outputFilePath + filename_time_logger, index=False, sep="\t")  # Write the column names to the CSV file

    # Eval loop through bank threshold and hysteresis voltages. Discharge, enable LED for xx s and measure on-time of DCDC
    # for bri in range(400, 1600, 400):
    for bri in [12]:# range(30, 220, 5):
        for V_th in [28]:# range(20, 29, 2):  # 20,27,1
            shared_V_th.value = V_th / 10
            for V_hyst in [5]:# range(1, 10, 1):  # 1, 10, 2
                shared_V_hyst.value = V_hyst / 10

                print("Bri: " + str(bri))
                print("V_th: " + str(shared_V_th.value))
                print("V_hyst: " + str(shared_V_hyst.value))

                # Drain the energy storage
                drain_energy_storage()

                print("Energy storage is drained.")

                # Parameters for LED time
                LED_time = 600  # LED on-time in s
                Sleep_stepsize = 0.01  # time in s
                #Timer_started = 0  # Flag
                On_time = 0     # Measured time of DCDC converter == on

                # OPEN NEW FILE
                filename = f"output_Bri_{bri}_NoScaler_V_th_{shared_V_th.value}_V_hyst_{shared_V_hyst.value}_LED_{LED_time}s.csv"  # Create a unique filename
                # filename = f"output_Bri_{bri}_Bank2_static.csv"  # Create a unique filename
                file_instance = file(dataset, filename)
                file_instance.create_output_file(data_log)  # Create the output file
                print("Output File Created")
                adc_instance.filename.value = filename.encode('utf-8')

                # Start Processes
                processes = []
                p_Proc_A = Process(target=adc_instance.Data_Processing_A, args=(exit_event, dataset, data_log, adc_channels, sys_states))
                p_Proc_B = Process(target=adc_instance.Data_Processing_B, args=(exit_event, dataset, data_log, adc_channels, sys_states))
                processes.append(p_Proc_A)
                processes.append(p_Proc_B)
                p_Proc_A.start()
                p_Proc_B.start()

                print("Turning on LED.")
                # Turn on LED
                # ! Bypassing the Irradiance Scaler !
                led_instance.set_brightness(bri/pm.IrradianceScaler)

                # LED on. Waiting for time to elapse
                for i in range(int(LED_time / Sleep_stepsize)):
                    time.sleep(Sleep_stepsize)
                    if sys_states[6] == 1: 
                        On_time += Sleep_stepsize

                print("Turning off LED. Waiting for DCDC converter to turn off.")
                # Turn off LED
                led_instance.set_brightness(0)

                while sys_states[6] == 1:
                    On_time += Sleep_stepsize
                    time.sleep(Sleep_stepsize)

                df.loc[0, 'Brightness'] = bri
                df.loc[0, 'V_th'] = shared_V_th.value
                df.loc[0, 'V_hyst'] = shared_V_hyst.value
                df.loc[0, 'time'] = On_time

                df.to_csv(pm.outputFilePath + filename_time_logger, mode='a', header=False, index=False,
                          sep="\t")  # Append data without writing column names

                print("DCDC Converter off. Going to next iteration.")

                exit_event.set()  # Set the event to signal the child process to exit
                # completing process
                for p in processes:
                    p.join()
                exit_event.clear()


# Read and "play" irradiance trace, emulate load, measure time for total DCDC=On periods. Requires manual drain!
def Exp_Runtime3(adc_instance, adc_channels, led_instance, system_states_instance, emulator_instance, bluetooth_instance, sys_states, dataset, data_log, performance_log):
        
    print("DRAIN ENERGY STORAGE MANUALLY!")
    time.sleep(5)

    currentDatetime = datetime.now().strftime("%Y-%m-%d_%H.%M")
    strCurrentDatetime = str(currentDatetime)

    filename_time_logger = socket.gethostname()+ "_Performance_Log_" + strCurrentDatetime + ".csv"

    # Create an empty DataFrame with one row and column names
    df = pd.DataFrame(columns=['Timestamp', 'Checkpointed', 'Recovered', 'Sampling count', 'Communication count', 'Idle time'])
    df.to_csv(pm.outputFilePath + filename_time_logger, index=False, sep="\t")  # Write the column names to the CSV file

    shared_V_th.value = 2.7
    shared_V_hyst.value = 1.7

    Sleep_stepsize = 1  # time in s
    #Timer_started = 0  # Flag
    On_time = 0     # Measured time of DCDC converter == on

    # OPEN NEW FILE
    filename = f"Trace_{socket.gethostname()}_Dyn_{Dynamic_Banks.value}_File_{dataset}_{strCurrentDatetime}.csv"  # Create a unique filename
    # filename = f"output_Bri_{bri}_Bank2_static.csv"  # Create a unique filename
    file_instance = file(dataset, filename)
    file_instance.create_output_file(data_log)  # Create the output file
    print("Output File Created")
    adc_instance.filename.value = filename.encode('utf-8')

    # Start Processes
    processes = []
    p_Proc_A = Process(target=adc_instance.Data_Processing_A, args=(exit_event, dataset, data_log, adc_channels, sys_states))
    p_Proc_B = Process(target=adc_instance.Data_Processing_B, args=(exit_event, dataset, data_log, adc_channels, sys_states))
    processes.append(p_Proc_A)
    processes.append(p_Proc_B)
    p_Proc_A.start()
    p_Proc_B.start()

    use_SoC_emulation = 0
    if use_SoC_emulation == 1:
        p_SoC_Proc = Process(target=emulator_instance.SoC_Emulator, args=(exit_event, sys_states, performance_log, data_log))
        processes.append(p_SoC_Proc)
        p_SoC_Proc.start()

    p_BT_Proc = Process(target=bluetooth_instance.BT_Process, args=(exit_event, performance_log, data_log))
    processes.append(p_BT_Proc)
    p_BT_Proc.start()

    print("Starting Trace")

    file_instance.read_from_file()
    file_instance.filter_NaN_values()

    env_dataset_done.clear()

    Env_Emulate = threading.Thread(target = emulator_instance.Env_Emulator, args=(file_instance, led_instance, data_log, env_dataset_done))
    
    Env_Emulate.start()


    # LED on. Waiting for time to elapse
    while not env_dataset_done.is_set():
        time.sleep(Sleep_stepsize)
        if sys_states[6] == 1: 
            On_time += Sleep_stepsize
            # Update and write performance log
            df.loc[0, 'Timestamp'] = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
            df.loc[0, 'Sampling count'] = performance_log[0]
            df.loc[0, 'Communication count'] = performance_log[1]
            df.loc[0, 'idle time'] = On_time
            df.to_csv(pm.outputFilePath + filename_time_logger, mode='a', header=False, index=False,
                sep="\t")  # Append data without writing column names

    print("Dataset finished. Waiting for DCDC converter to turn off")
    # Turn off LED
    led_instance.set_brightness(0)

    while sys_states[6] == 1:
        On_time += Sleep_stepsize
        # Update and write performance log
        df.loc[0, 'Timestamp'] = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        df.loc[0, 'Sampling count'] = performance_log[0]
        df.loc[0, 'Communication count'] = performance_log[1]
        df.loc[0, 'idle time'] = On_time
        df.to_csv(pm.outputFilePath + filename_time_logger, mode='a', header=False, index=False,
                sep="\t")  # Append data without writing column names
        
        time.sleep(Sleep_stepsize)



    print("DCDC Converter off. Going to next iteration.")

    exit_event.set()  # Set the event to signal the child process to exit
    # completing process
    for p in processes:
        p.join()
    exit_event.clear()
    Env_Emulate.join()

    # Disabling Data_Ready Callback
    GPIO.remove_event_detect(pinOut.ADC1_DRDY)
    time.sleep(1)
    print("Finishing Experiment 3")




# Sweep LED from 0 to 100 % and record the ADC data, !Disconnect J26!
def Exp_LEDCalib(adc_instance, adc_channels, led_instance, sys_states, dataset, data_log):

    shared_V_th.value = 2.8
    shared_V_hyst.value = 0.6

    # OPEN NEW FILE
    filename = f"{socket.gethostname()}_LED_Linearity_Log.csv"  # Create a unique filename
    file_instance = file(dataset, filename)
    file_instance.create_output_file(data_log)  # Create the output file
    print("Output File Created")
    adc_instance.filename.value = filename.encode('utf-8')

    # Start Processes
    processes = []
    p_Proc_A = Process(target=adc_instance.Data_Processing_A, args=(exit_event, dataset, data_log, adc_channels, sys_states))
    p_Proc_B = Process(target=adc_instance.Data_Processing_B, args=(exit_event, dataset, data_log, adc_channels, sys_states))
    processes.append(p_Proc_A)
    processes.append(p_Proc_B)
    p_Proc_A.start()
    p_Proc_B.start()


    use_duty_cycle = 0

    # Use set_dutycycle without calibration factor for direct control
    if use_duty_cycle:
        led_instance.set_dutycycle(1)
        time.sleep(3)
        led_instance.set_dutycycle(0)
        time.sleep(10)
        
        for i in range(0,500, 1):
            led_instance.set_dutycycle(i/500)
            time.sleep(0.2)
        
        time.sleep(10)

        # Turn off LED
        led_instance.set_dutycycle(0)

    else:   # Use set_brightness with calibration factor (Check Irradiance_Scaler!)
        max_bri_W = 17
        led_instance.set_brightness(max_bri_W)
        time.sleep(3)
        led_instance.set_brightness(0)
        time.sleep(10)
        
        for i in range(0,1000, 1):
            led_instance.set_brightness(i/1000 * max_bri_W)
            time.sleep(0.25)
        led_instance.set_brightness(max_bri_W)
        time.sleep(10)

        # Turn off LED
        led_instance.set_brightness(0)


    exit_event.set()  # Set the event to signal the child process to exit
    # completing process
    for p in processes:
        p.join()
    exit_event.clear()

    # Disabling Data_Ready Callback
    GPIO.remove_event_detect(pinOut.ADC1_DRDY)
    time.sleep(1)
    print("Finishing Experiment 4")






if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit_event.set()  # Set the event to signal the child process to exit
        # completing process
        #led_instance.set_brightness(0)
        time.sleep(1)
        GPIO.cleanup()
        print("Exiting now.")
