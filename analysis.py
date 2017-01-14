
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from string import Template

colors = {"S11":"red",
          "S21":"green",
          "S12": "orange",
          "S22": "blue"}
          
sparams = ["S11", "S21","S12","S22"]
data_dir = "data"
tables_dir = "tables"
latex_dir = "report/data"
plots_dir = "report/images"
channels = range(1, 8) + range(9, 16)
freqs = [2.998000000, 5.997250000, 8.996500000]
freq_locs = dict(zip(freqs, [888, 2210, 3554]))

def load_sparams(fname):
    names = ["Freq"] + sparams
    fname = data_dir + "/" + fname
    s = pd.read_table(fname, names = names, skiprows = 5, header = None,
                      usecols = [0, 1, 3, 5, 7], delim_whitespace = True)
    s.Freq *= 10**-9
    s[sparams] *= -1 # turn them positive
    return s
    
def complete_plot(title = ""):
    plt.xlabel("Freq (GHz)")
    plt.ylabel("Att (dB)")
    plt.title(title)
    plt.legend()    
    [plt.axvline(f, color = 'grey') for f in freqs]  
    
def print_all_params(params, title = ""):
    plt.figure()
    for p in sparams:
        plt.plot(params.Freq, params[p], color = colors[p], label = p)
    complete_plot(title)
    
def sparams_tolatex(params, fname):
    df = pd.DataFrame({"Attenuation": [params[p][freq_locs[f]] for p in sparams]},
                       index = sparams)
    df.index.name = "Parameter"
    df.to_latex(fname, index_names = True)
        
## Load all the data into 3 dataframes for each
## output of each one of the 14 channels
#data = {}
#for c in channels:
#    data[c]= {}
#    for o in (1, 2, 3):
#        data[c][o] = load_sparams("canal%iout%i.s2p" % (c, o))
#        
#
## Organize the data by S-parameter and frequency
#        
#atts = {}
#for p in sparams: # for each s-parameter
#    atts[p] = {}
#    for f in freqs: # for each frequency
#        atts[p][f] = pd.DataFrame({#"Ch":channels,
#                                   "Out1 (dB)":0,
#                                   "Out2 (dB)":0,
#                                   "Out3 (dB)":0}, index = channels)
#        atts[p][f].index.name = "Ch" #unnecessary when I improve the latex                   
#        for c in channels: # for each channel
#        # Create a dataframe with 3 entries for each channel
#            for o in (1, 2, 3): # for each output
#                # Get the attenuation 
#                a = data[c][o].loc[freq_locs[f], p]
#                # and put it where it belongs
#                atts[p][f].loc[c, "Out%i (dB)" % o] = a
#        # Write them as tables
#        atts[p][f].to_csv("%s/%s_%iHz.csv" % (tables_dir, p, f), index_label = "Ch")
#        atts[p][f].to_latex("%s/%s_%iHz.tex" % (latex_dir, p, f), index_names = True)
#
##Plot things
#
## For each s-parameter and frequency, plot the atenuation at each channel
#for p in sparams:
#    for f in freqs:
#        plt.figure()
#        for o in (1, 2, 3):
#           plt.plot(channels, atts[p][f]["Out%i (dB)" % o], "o")
#        plt.xlabel("Canal")
#        plt.ylabel("Attenuation (dB)")
#        plt.title("Attenuation of %s at %i Hz" % (p, f))
#        plt.xticks(channels)
#        #plt.legend()
#        plt.savefig(plots_dir + "/" + p + "_%iHz.png" % f)
        
# Cable measures
        
cable = load_sparams("cable.s2p")
print_all_params(cable, "Cable S-parameters")
plt.savefig("{}/cable.png".format(plots_dir))

table_data = sum([[cable[p][f] for p in ("S11", "S21", "S22")] for f in freq_locs.values()], [])

latex_table = """
\\begin{{figure}}[ht]
  \\begin{{minipage}}{{0.4\\linewidth}}
    \\includegraphics[scale=0.4]{{images/cable.png}}
  \\end{{minipage}}
  \\begin{{minipage}}{{0.4\\linewidth}}
%    \\begin{{table}}[ht]
      \\centering
      \\begin{{tabular}}{{rrrr}}
        \\toprule
        Freq (GHz) &  S11 (dB) & S21 (dB) &  S22 (dB)  \\\\
        \\midrule
          $ {freqs[0]:3.5f} $ & {:2.2f} & {:2.2f}  & {:2.2f} \\\\
          $ {freqs[1]:3.5f} $ & {:2.2f} & {:2.2f}  & {:2.2f} \\\\
          $ {freqs[2]:3.5f} $ & {:2.2f} & {:2.2f}  & {:2.2f} \\\\
        \\bottomrule
      \\end{{tabular}}
      \\label{{Comparison}}  
%    \\end{{table}}
  \\end{{minipage}}
\\end{{figure}}
""".format(*table_data, freqs=freqs)      

f = open(latex_dir + "/cable.tex", "w")                   
f.write(latex_table)

# Splitter measures
        
splitters = [load_sparams("splitter{}.s2p".format(s)) for s in (1, 2, 3)]

for c in (1, 2, 3):
    print_all_params(cable, "Splitter Channel {} S-parameters".format(c))
    plt.savefig("{}/splitter{}.png".format(plots_dir, c))  
    
    table_data = sum([[splitters[c-1][p][f] for p in ("S11", "S21", "S22")] for f in freq_locs.values()], [])

    latex_table = """
\\begin{{figure}}[ht]
  \\begin{{minipage}}{{0.4\\linewidth}}
    \\includegraphics[scale=0.4]{{images/splitter{c}.png}}
  \\end{{minipage}}
  \\begin{{minipage}}{{0.4\\linewidth}}
%    \\begin{{table}}[ht]
      \\centering
      \\begin{{tabular}}{{rrrr}}
        \\toprule
        Freq (GHz) &  S11 (dB) & S21 (dB) &  S22 (dB)  \\\\
        \\midrule
          $ {freqs[0]:3.5f} $ & {:2.2f} & {:2.2f}  & {:2.2f} \\\\
          $ {freqs[1]:3.5f} $ & {:2.2f} & {:2.2f}  & {:2.2f} \\\\
          $ {freqs[2]:3.5f} $ & {:2.2f} & {:2.2f}  & {:2.2f} \\\\
        \\bottomrule
      \\end{{tabular}}
      \\label{{Comparison}}  
%    \\end{{table}}
  \\end{{minipage}}
\\end{{figure}}
    """.format(*table_data, c=c, freqs=freqs)      

    f = open("{}/splitter{}.tex".format(latex_dir, c), "w")                   
    f.write(latex_table)

# Filter measures and comparison

filterVBF = load_sparams("filterVBF2900b.s2p")
filterVLP= load_sparams("filterVLP41.s2p")

# Make the latex template v2
latex_tmp = """
\\begin{{figure}}[ht]
  \\centering
  \\includegraphics[scale=0.55]{{images/filter{p}comparison.png}}
\\end{{figure}}
\\begin{{table}}[ht]
  \\centering
  \\begin{{tabular}}{{ccc}}
    \\toprule
    Freq (GHz) &  {p} of VBF2900 (dB) & {p} of VLP41 (dB) \\\\
    \\midrule
      $ {freqs[0]:3.5f} $  & {:2.2f} & {:2.2f} \\\\
      $ {freqs[1]:3.5f} $  & {:2.2f} & {:2.2f} \\\\
      $ {freqs[2]:3.5f} $  & {:2.2f} & {:2.2f} \\\\
    \\bottomrule
  \\end{{tabular}}
  \\label{{filter{p}comparison}}  
  \\caption{{Comparison of parameter {p} attenuation on the filters}}
\\end{{table}}
"""

for p in sparams:
    plt.figure()
    plt.plot(filterVBF.Freq, filterVBF[p], '-b', label = "VBF2900")
    plt.plot(filterVLP.Freq, filterVLP[p], '--r', label = "VLP41", )
    plt.title("Filter %s parameter comparison" % p)
    plt.xlabel("Freq (GHz)")
    plt.ylabel("Att (dB)")
    plt.legend()
    [plt.axvline(f, color = 'grey') for f in freqs]
    
    plt.savefig("%s/filter%scomparison.png" % (plots_dir, p))
    
    data = sum(zip([filterVBF[p][freq_locs[f]] for f in freqs],
                   [filterVLP[p][freq_locs[f]] for f in freqs]), ())
    latex_table = latex_tmp.format(*data, p=p, freqs=freqs)
    fname = "{}/filter{}comparison.tex".format(latex_dir, p)
    f = open(fname, "w")                
    f.write(latex_table)
    
for f in freqs:
    df = pd.DataFrame({"VBF2900":[filterVBF[p][freq_locs[f]] for p in sparams],
                       "VLP41":[filterVLP[p][freq_locs[f]] for p in sparams]},
                      index = sparams)
    df.index.name = "Parameter"
    df.to_latex("%s/filtercomparison_%iHz.tex" % (latex_dir, f), index_names = True)