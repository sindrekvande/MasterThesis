import file_handler as fh
import matplotlib.pyplot as plt
import numpy as np


trace = fh.file("summer", 7).brightnessDF
trace2 = fh.file("summer", 10).brightnessDF
trace3 = fh.file("summer", 2).brightnessDF
trace4 = fh.file("winter", 11).brightnessDF
trace5 = fh.file("winter", 20).brightnessDF
trace6 = fh.file("winter", 3).brightnessDF

trace.to_csv("simulation\datasets\summer7low.tsv", index=False, sep="\t")
trace2.to_csv("simulation\datasets\summer10high.tsv", index=False, sep="\t")
trace3.to_csv("simulation\datasets\summer2smooth.tsv", index=False, sep="\t")
trace4.to_csv("simulation\datasets\winter11low.tsv", index=False, sep="\t")
trace5.to_csv("simulation\datasets\winter20high.tsv", index=False, sep="\t")
trace6.to_csv("simulation\datasets\winter3smooth.tsv", index=False, sep="\t")