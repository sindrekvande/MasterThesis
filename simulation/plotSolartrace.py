import file_handler as fh
import matplotlib.pyplot as plt
import numpy as np


trace = fh.file("winter", 28).brightnessDF

x = []
for _, irr in trace.itertuples():
    x.append(irr)

plt.plot(x)
plt.show()