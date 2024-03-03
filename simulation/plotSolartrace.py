import file_handler as fh
import matplotlib.pyplot as plt
import numpy as np


trace = fh.file("summer", 31).brightnessDF
trace2 = fh.file("autumn", 31).brightnessDF
trace3 = fh.file("winter", 31).brightnessDF

x = []
x2 = []
x3 = []
for _, irr in trace.itertuples():
    x.append(irr)

for _, irr in trace2.itertuples():
    x2.append(irr)

for _, irr in trace3.itertuples():
    x3.append(irr)

time = np.linspace(start=0.5, stop=31.5, num=len(x))


plt.plot(time, x)
plt.plot(time, x2)
plt.plot(time, x3)
plt.xticks(np.arange(1, 32, step=1))
plt.show()