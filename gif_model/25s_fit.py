import numpy as np
import h5py
import sys
sys.path.append('/Users/michaeljaquier/Documents/gewaltig/nest-/lib/python2.7/site-packages')
sys.path.append('/Users/michaeljaquier/Documents/gewaltig/fitting/GIFFittingToolbox/src')
import seaborn
import pylab
from Experiment import *
from GIF import *
from AEC_Badel import *
from Filter_Rect_LinSpaced import *
from Filter_Rect_LogSpaced import *
import matplotlib.pyplot as plt

myExp = Experiment('Experiment 1', 0.1)
dataPath = 'soma_voltage_25s.dat'
def expLoad(dataPath=dataPath, cols=1):
    expFile = np.loadtxt(dataPath, usecols=[cols])
    expData = np.array([expFile,np.append(np.zeros(7000),
                                   np.ones(np.size(expFile)-7000)*0.6)])
    return expData



a=expLoad(dataPath)

print a[0]
print a[1]
