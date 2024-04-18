import csv
import pandas as pd
#import import_main #LIGHT OFF
import parameters as pm
#import messages as msg
from datetime import datetime



class file:
    def __init__(self, dataset, filename):
        
        #self.inputFile = pm.inputFilePath + pm.season + ".tsv"
        self.inputFile = pm.inputFilePath + dataset

        #self.read_from_file()
        #self.filter_NaN_values()

        currentDatetime = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        strCurrentDatetime = str(currentDatetime)

        #self.outputFile = outputFilePath + pm.season + "_measurements_" + strCurrentDatetime + ".csv"
        self.outputFile = pm.outputFilePath + filename

        #self.create_output_file()
        
    def create_output_file(self, data_log):
        file = open(self.outputFile, "w")
        file.close()

        # Create an empty DataFrame with columns from messages dictionary
        df = pd.DataFrame(columns=data_log.keys())
        # Write the DataFrame to the CSV file
        df.to_csv(self.outputFile, index=False, sep="\t")

        #df = pd.DataFrame({ key:pd.Series(value) for key, value in msg.messages.items() })
        #df.to_csv(self.outputFile, index=False, sep="\t")

    def append_to_file(self, data_log, sys_states):#, df: pd.DataFrame):
        #with open(self.outputFile, "a") as file:
        #    csv.writer(file, delimiter='\t').writerow(list) 
        #    file.close()
        currentDatetime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]
        data_log["datetime"] = str(currentDatetime)
        data_log.update({"MPPT_EN": sys_states[5]})
        data_log.update({"DCDC_EN": sys_states[6]})
        data_log.update({"BANK2_EN": sys_states[1]})
        data_log.update({"BANK3_EN": sys_states[2]})
        data_log.update({"BANK4_EN": sys_states[3]})
        data_log.update({"BANK5_EN": sys_states[4]})
        df = pd.DataFrame({key: pd.Series(value) for key, value in data_log.items()})
        df.to_csv(self.outputFile, mode='a', index=False, header=False, sep="\t")
        #print(data_log)

    def read_from_file(self):
        self.brightnessDF= pd.read_csv(self.inputFile, sep='\t', usecols = [pm.column],  dtype = float) # header=0, index_col=False, nrows = (pm.numberOfDays*pm.IrrDatasetTimeStep*24)
        return self.brightnessDF

    def single_value(self, index):
        return self.brightnessDF.loc[index, pm.column]

    def filter_NaN_values(self):
        NaNCounter = 0
        #self.read_from_file(self.inputFile)

        for key, irrvalue in self.brightnessDF.itertuples():   
            if pd.isna(irrvalue) and NaNCounter == 0:
                previousValue = self.single_value(key - 1)
                #Check if next values are NaN
                for nextValueIndex in range(1, len(self.brightnessDF) - key):
                        NaNCounter += 1
                        nextValue = self.single_value(key + nextValueIndex)
                        if pd.notna(nextValue):
                            break
            if NaNCounter > 0:
                self.brightnessDF.loc[key, pm.column] = (previousValue + nextValue)/2
                NaNCounter -= 1
                    
        return self.brightnessDF