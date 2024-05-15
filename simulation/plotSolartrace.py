import file_handler as fh
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.ticker as ticker


trace = fh.file("summer", 7).brightnessDF #7,10,2
#trace2 = fh.file("autumn", 14).brightnessDF
#trace4 = fh.file("autumn", 3).brightnessDF
trace3 = fh.file("winter", 11).brightnessDF #11,20,3

x = []
#x2 = []
#x4 = []
x3 = []
for _, irr in trace.itertuples():
    x.append(irr)

#for _, irr in trace2.itertuples():
#    x2.append(irr)

#for _, irr in trace4.itertuples():
#    x4.append(irr)

for _, irr in trace3.itertuples():
    x3.append(irr)

startTime = pd.Timestamp('2022-07-02T00:00')
endTime = pd.Timestamp('2022-07-03T00:00')
timeAxis = np.linspace(start=startTime.value, stop=endTime.value, num=len(x))
timeAxis = pd.to_datetime(timeAxis)
fig = plt.figure(figsize=(8,3))

plt.plot(timeAxis, x, label='Summer', color='#ffae49')
#plt.plot(time, x2, label='AutumnLow', color='#44a5ff')
#plt.plot(time, x4, label='AutumnHigh', color='#44a5c2')
plt.plot(timeAxis, x3, label='Winter', color='#024b7a')
#plt.xticks(np.arange(0, 24, step=1))
plt.xlabel('Time of day')
plt.ylabel('Solar irradiance [W/m$^2$]')
plt.ylim(-10, 1300)
plt.legend()
plt.margins(x=0)
xformatter = mdates.DateFormatter('%H:%M')
plt.gcf().axes[0].xaxis.set_major_formatter(xformatter)
loc = ticker.MultipleLocator(base=1/12) # this locator puts ticks at regular intervals
plt.gcf().axes[0].xaxis.set_major_locator(loc)
fig.tight_layout()
plt.savefig('simulation/results/solarTraceLow.svg', bbox_inches="tight")
#plt.show()