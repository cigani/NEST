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

####################################################
# Import Data. Create Arrays
####################################################

myExp=Experiment('Experiment 1', 0.1)
dataPath='soma_voltage_25s.dat'
def expLoad(dataPath=dataPath, cols=1):
    expFile=np.loadtxt(dataPath, usecols=[cols])
    expData=np.array([
        expFile,
        np.append(
            np.zeros(7000),
            np.ones(np.size(expFile)-7000)*0.6)])
    return expData
dataArray=expLoad()
V=dataArray[0]
I=dataArray[1]
V_units=10**-3
I_units=10**-9

####################################################
#Load Training Set
####################################################

myExp.addTrainingSetTrace(V,V_units,I,I_units,250188, FILETYPE='Array')
myExp.trainingset_traces[0].setROI([0,75000])

myExp.addTestSetTrace(V[75000:], V_units, I[75000:], I_units,250188-75000,
                      FILETYPE='Array')


