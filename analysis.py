
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

colors = {"S11":"red",
          "S21":"green",
          "S12": "orange",
          "S22": "blue"}
          
sparams = ["S11", "S21","S12","S22"]
data_dir = "data"
channels = range(1, 8) + range(9, 16)
freqs = [2998000000, 5997250000, 8996500000]
freq_locs = dict(zip(freqs, [888, 2210, 3554]))

def load_sparams(fname):
    names = ["Freq"] + sparams
    fname = data_dir + "/" + fname
    s = pd.read_table(fname, names = names, skiprows = 5, header = None,
                      usecols = [0, 1, 3, 5, 7], delim_whitespace = True)
    return s
    
def print_params(params, title = ""):
    plt.figure()
    for p in sparams:
        plt.plot(params.Freq, params[p], color = colors[p])
    plt.xlabel("Freq (Hz)")
    plt.ylabel("Att (dB)")
    plt.title(title)
    
# Load all the data into 3 dataframes for each
# output of each one of the 14 channels
data = {}
for c in channels:
    data[c]= {}
    for o in (1, 2, 3):
        data[c][o] = load_sparams("canal%iout%i.s2p" % (c, o))
        

# Organize the data by S-parameter and frequency
        
atts = {}
for p in sparams: # for each s-parameter
    atts[p] = {}
    for f in freqs: # for each frequency
        atts[p][f] = pd.DataFrame({"Out1 (dB)":0,
                               "Out2 (dB)":0,
                               "Out3 (dB)":0}, index = channels)
        for c in channels: # for each channel
        # Create a dataframe with 3 entries for each channel
            for o in (1, 2, 3): # for each output
                # Get the attenuation 
                a = data[c][o].loc[freq_locs[f], p]
                # and put it where it belongs
                atts[p][f].loc[c, "Out%i (dB)" % o] = a

# Write them as tables

