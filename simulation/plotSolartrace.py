import file_handler as fh
import matplotlib.pyplot as plt
import numpy as np


trace = fh.file("summer", 2).brightnessDF
#trace2 = fh.file("autumn", 14).brightnessDF
#trace4 = fh.file("autumn", 3).brightnessDF
trace3 = fh.file("winter", 3).brightnessDF

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

time = np.linspace(start=0, stop=24, num=len(x))

fig = plt.figure(figsize=(9,5))
plt.plot(time, x, label='Summer', color='#ffae49')
#plt.plot(time, x2, label='AutumnLow', color='#44a5ff')
#plt.plot(time, x4, label='AutumnHigh', color='#44a5c2')
plt.plot(time, x3, label='Winter', color='#024b7a')
plt.xticks(np.arange(0, 24, step=1))
plt.xlabel('Time of the day')
plt.ylabel('Solar irradiance [W/m$^2$]')
plt.ylim(-10, 1300)
plt.legend()
plt.margins(x=0)
fig.tight_layout()
plt.savefig('simulation/results/solarTraceSmooth.svg', bbox_inches="tight")
#plt.show()