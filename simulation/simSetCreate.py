import pandas as pd

fileName = "simulation\simSet7.tsv"

header = ['season', 'day', 'capacitance', 'sampleNum', 'sampleSize', 'sleep', 'start', 'stop']

columns = {header[0] : [],
          header[1] : [],
          header[2] : [],
          header[3] : [],
          header[4] : [],
          header[5] : [],
          header[6] : [],
          header[7] : []
}

for season in ['summer']:
    for day in ([11, 3] if season == 'winter' else [7, 2]): # winter[11,20,3], summer[7, 10, 2]
        for capacitance in [147, 200]:
            for sampleNum in [10, 30]:
                for sampleSize in [10, 30]:
                    for sleep in [3, 5, 10]:
                        #for start in [2.7, 2.5, 2.3]:
                            #for stop in [2.2, 2.0, 1.8]:
                        for start, stop in [[2.7, 2.0]]:
                            columns[header[0]] += [season]
                            columns[header[1]] += [day]
                            columns[header[2]] += [capacitance]
                            columns[header[3]] += [sampleNum]
                            columns[header[4]] += [sampleSize]
                            columns[header[5]] += [sleep]
                            columns[header[6]] += [start]
                            columns[header[7]] += [stop]

df = pd.DataFrame(columns)
df.to_csv(fileName, index=False, sep="\t")