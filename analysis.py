
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

colors = {"S11":"red",
          "S21":"green",
          "S12": "orange",
          "S22": "blue"}
          
sparams = ["S11", "S21","S12","S22"]
data_dir = "data"
tables_dir = "tables"
latex_dir = "report/data"
plots_dir = "report/images"
channels = list(range(1, 8)) + list(range(9, 16))
freqs = [2.998000000, 5.997250000, 8.996500000]
freq_locs = dict(zip(freqs, [888, 2210, 3554]))
error = 0.01 # dB

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
    #plt.title(title)
    plt.legend()    
    [plt.axvline(f, color = 'grey') for f in freqs]  
#    
#def print_all_params(params, title = ""):
#    plt.figure()
#    for p in sparams:
#        plt.plot(params.Freq, params[p], color = colors[p], label = p)
#    complete_plot(title)
    
def sparams_tolatex(params, fname):
    df = pd.DataFrame({"Attenuation": [params[p][freq_locs[f]] for p in sparams]},
                       index = sparams)
    df.index.name = "Parameter"
    df.to_latex(fname, index_names = True)
    
# TODO: interpolate instead of getting the closest freqs
# TODO: find a better way to do the templates
        
## Load all the data into 3 dataframes for each
## output of each one of the 14 channels
        
data = {}
for c in channels:
    data[c]= {}
    for o in (1, 2, 3):
        data[c][o] = load_sparams("canal{}out{}.s2p".format(c, o))
        

# Organize the data by S-parameter and frequency
        
atts = {}
for p in sparams: # for each s-parameter
    atts[p] = {}
    for f in freqs: # for each frequency
        atts[p][f] = pd.DataFrame({#"Ch":channels,
                                   "Out1 (dB)":0,
                                   "Out2 (dB)":0,
                                   "Out3 (dB)":0}, index = channels)
        atts[p][f].index.name = "Ch" #unnecessary when I improve the latex                   
        for c in channels: # for each channel
        # Create a dataframe with 3 entries for each channel
            for o in (1, 2, 3): # for each output
                # Get the attenuation 
                a = data[c][o].loc[freq_locs[f], p]
                # and put it where it belongs
                atts[p][f].loc[c, "Out{} (dB)".format(o)] = a
        # Write them as tables
                
        latex_table = r"""
  \begin{{figure}}[ht]
    \begin{{minipage}}{{0.5\linewidth}}
      \includegraphics[scale=0.5]{{images/channels{p}_{f:0.0f}GHz.png}}
      \caption{{Attenuation of parameter {p} at {f:2.2f} GHz. The horizontal 
      line indicates attenuation for this parameter and frequency.}}
      \label{{channels{p}_{f:0.0f}GHz}}  
    \end{{minipage}}
    \begin{{minipage}}{{0.3\linewidth}}
    \end{{minipage}}
    \begin{{minipage}}{{0.45\linewidth}}
      \centering
      \begin{{tabular}}{{rrrr}}
        \toprule
        Ch &  Out1 (dB) & Out2 (dB) &  Out3 (dB)  \\
        \midrule""".format(p=p, f=f)
        for c in channels:
            latex_table += r"""
            $ {} $ & {:2.2f} $\pm$ 0.01 & {:2.2f} $\pm$ 0.01 & {:2.2f} $\pm$ 0.01 \\
            """.format(c, *atts[p][f].loc[c])
        latex_table += r"""
        \bottomrule
      \end{{tabular}}
    \end{{minipage}}
  \end{{figure}}
      """.format(p=p, f=f)
# TODO :I can probably do better than having a loop in the middel of the template
        fname = "{}/channels{}_{:0.0f}GHz.tex".format(latex_dir, p, f)
        f = open(fname, "w")
        f.write(latex_table)

# Get average attenuation for every frequency and parameter

means = pd.DataFrame({"S11":0.0,
                      "S21":0.0,
                      "S12":0.0,
                      "S22":0.0}, index = freqs)
for p in sparams:
    for f in freqs:
        means[p][f] = np.mean(atts[p][f].values)
        stds[p][f] = np.std(atts[p][f].values)

#means.to_latex(latex_dir + "/attmeans.tex")

# Averages table

latex_table = r"""
  \begin{figure}[ht]
      \centering
    \begin{tabular}{ccccc}
        \toprule
        Freq (GHz) &  S11 & S12 & S21 & S22  \\
        \midrule"""
for f in freqs: 
    latex_table += """\n $ {:2.2f} $ """.format(f)
    for p in sparams:
        latex_table += r"""& {:2.2f} $\pm$ 0.01 """.format(means[p][f])
    latex_table += r"""\\"""
latex_table += r"""
        \bottomrule
    \end{tabular}
      \caption{Mean attenuations}
      \label{means}
  \end{figure}"""


fname = latex_dir + "/attmeans.tex"
f = open(fname, "w")
f.write(latex_table)
       
# Standard deviation table
       
latex_table = r"""
  \begin{figure}[ht]
      \centering
    \begin{tabular}{ccccc}
        \toprule
        Freq (GHz) &  S11 & S12 & S21 & S22  \\
        \midrule"""
for f in freqs: 
    latex_table += """\n $ {:2.2f} $ """.format(f)
    for p in sparams:
        latex_table += r"""& {:2.2f} $\pm$ 0.01 """.format(means[p][f])
    latex_table += r"""\\"""
latex_table += r"""
        \bottomrule
    \end{tabular}
      \caption{Standard deviations}
      \label{stds}
  \end{figure}"""

fname = latex_dir + "/attstds.tex"
f = open(fname, "w")
f.write(latex_table)

#Plot things

# TODO : join this loop and the previous one

# For each s-parameter and frequency, plot the atenuation at each channel
for p in sparams:
    for f in freqs:
        plt.figure()
        for o in (1, 2, 3):
           plt.plot(channels, atts[p][f]["Out%i (dB)" % o], "o^s"[o-1])
           plt.errorbar(channels, atts[p][f]["Out%i (dB)" % o], error, 
                        fmt = "none", ecolor = "b")
        plt.xlabel("Canal")
        plt.ylabel("Attenuation (dB)")
        #plt.title("Attenuation of {} at {} GHz".format(p, f))
        plt.xticks(channels)
        plt.hlines(means[p][f], 0, 16, color="grey")
        plt.xlim(0, 16)
        # The best location for the legend for S22 and 5GHz is in the middle,
        # which looks awful. We change the y limits to avoid this.
        if p == "S22" and f == freqs[1]:
            plt.ylim(5, 18)
        plt.legend(loc="best", labels = ["Out%i (dB)" % o for o in (1,2,3)],
                    numpoints = 1)
        fname = "{}/channels{}_{:0.0f}GHz.png".format(plots_dir, p, f)
        plt.savefig(fname)
        
# Cable measures
        
cable = load_sparams("cable.s2p")
print_all_params(cable, "Cable S-parameters")
plt.savefig("{}/cable.png".format(plots_dir))

table_data = sum([[cable[p][f] for p in ("S11", "S21", "S22")] for f in freq_locs.values()], [])

latex_table = r"""
\begin{{figure}}[ht]
  \begin{{minipage}}{{0.4\linewidth}}
    \includegraphics[scale=0.4]{{images/cable.png}}
  \end{{minipage}}
  \begin{{minipage}}{{0.4\linewidth}}
      \centering
      \begin{{tabular}}{{rrrr}}
        \toprule
        Freq (GHz) &  S11 (dB) & S21 (dB) &  S22 (dB)  \\
        \midrule
          $ {freqs[0]:3.5f} $ & {:2.2f} $\pm$ 0.01 & {:2.2f} $\pm$ 0.01 & {:2.2f} $\pm$ 0.01 \\
          $ {freqs[1]:3.5f} $ & {:2.2f} $\pm$ 0.01 & {:2.2f} $\pm$ 0.01 & {:2.2f} $\pm$ 0.01 \\
          $ {freqs[2]:3.5f} $ & {:2.2f} $\pm$ 0.01 & {:2.2f} $\pm$ 0.01& {:2.2f} $\pm$ 0.01 \\
        \bottomrule
      \end{{tabular}}
      \caption{{Cable attenuations}}  
      \label{{cable}}  
  \end{{minipage}}
\end{{figure}}
""".format(*table_data, freqs=freqs)      

f = open(latex_dir + "/cable.tex", "w")                   
f.write(latex_table)

# Splitter measures
        
splitters = [load_sparams("splitter{}.s2p".format(s)) for s in (1, 2, 3)]

for c in (1, 2, 3):
    print_all_params(splitters[c-1], "Splitter Channel {} S-parameters".format(c))
    plt.savefig("{}/splitter{}.png".format(plots_dir, c))  
    
    table_data = sum([[splitters[c-1][p][f] for p in ("S11", "S21", "S22")] for f in freq_locs.values()], [])

    latex_table = r"""
\begin{{figure}}[ht]
  \begin{{minipage}}{{0.4\linewidth}}
    \includegraphics[scale=0.4]{{images/splitter{c}.png}}
  \end{{minipage}}
  \begin{{minipage}}{{0.4\linewidth}}
      \centering
      \begin{{tabular}}{{rrrr}}
        \toprule
        Freq (GHz) &  S11 (dB) & S21 (dB) &  S22 (dB)  \\
        \midrule
          $ {freqs[0]:3.5f} $ & {:2.2f} $\pm$ 0.01 & {:2.2f} $\pm$ 0.01 & {:2.2f} $\pm$ 0.01 \\
          $ {freqs[1]:3.5f} $ & {:2.2f} $\pm$ 0.01 & {:2.2f} $\pm$ 0.01 & {:2.2f} $\pm$ 0.01 \\
          $ {freqs[2]:3.5f} $ & {:2.2f} $\pm$ 0.01 & {:2.2f} $\pm$ 0.01 & {:2.2f} $\pm$ 0.01 \\
        \bottomrule
      \end{{tabular}}
      \caption{{Attenuations through channel {c} of a sample splitter}}  
      \label{{splitter{c}}}  
  \end{{minipage}}
\end{{figure}}
    """.format(*table_data, c=c, freqs=freqs)      

    f = open("{}/splitter{}.tex".format(latex_dir, c), "w")                   
    f.write(latex_table)

# Filter measures and comparison

filterVBF = load_sparams("filterVBF2900b.s2p")
filterVLP= load_sparams("filterVLP41.s2p")

# Make the latex template v2
latex_tmp = r"""
\begin{{figure}}[ht]
  \centering
  \includegraphics[scale=0.55]{{images/filter{p}comparison.png}}
\end{{figure}}
\begin{{table}}[ht]
  \centering
  \begin{{tabular}}{{ccc}}
    \toprule
    Freq (GHz) &  {p} of VBF2900 (dB) & {p} of VLP41 (dB) \\
    \midrule
      $ {freqs[0]:3.5f} $  & {:2.2f} $\pm$ 0.01 & {:2.2f} $\pm$ 0.01 \\
      $ {freqs[1]:3.5f} $  & {:2.2f} $\pm$ 0.01 & {:2.2f} $\pm$ 0.01 \\
      $ {freqs[2]:3.5f} $  & {:2.2f} $\pm$ 0.01 & {:2.2f} $\pm$ 0.01 \\
    \bottomrule
  \end{{tabular}}
  \caption{{Comparison of parameter {p} attenuation on the filters}}
  \label{{filter{p}comparison}}  
\end{{table}}
"""

for p in sparams:
    plt.figure()
    plt.plot(filterVBF.Freq, filterVBF[p], '-b', label = "VBF2900")
    plt.plot(filterVLP.Freq, filterVLP[p], ':r', label = "VLP41", )
#    plt.title("Filter {} parameter comparison".format(p))
    plt.xlabel("Freq (GHz)")
    plt.ylabel("Att (dB)")
    plt.legend()
#    bwc = float(filterVBF[filterVBF.Freq == freqs[0]][p])
    bwc = 4.96
    bw = filterVBF[filterVBF["S12"] < bwc].Freq.values[[0,-1]]
    plt.axvline(bw[0], color = "grey", linestyle = "dashed")
    plt.axvline(bw[1], color = "grey", linestyle = "dashed")
    [plt.axvline(f, color = 'grey') for f in freqs]
    11
    plt.savefig("{}/filter{}comparison.png".format(plots_dir, p))
    
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
    df.to_latex("{}/filtercomparison_{:0.0f}GHz.tex".format(latex_dir, f), index_names = True)
