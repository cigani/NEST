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
from AEC_Dummy import *
from Filter_Rect_LinSpaced import *
from Filter_Rect_LogSpaced import *
import matplotlib.pyplot as plt
import Tools
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

myExp.addTrainingSetTrace(V,V_units,I,I_units,25018, FILETYPE='Array')
#myExp.trainingset_traces[0].setROI([70000,250188])

myExp.addTestSetTrace(V[175000:], V_units, I[175000:], I_units,25000-17500,
                      FILETYPE='Array')

####################################################
#AEC
####################################################


myAEC=AEC_Dummy()
myExp.setAEC(myAEC)
myExp.performAEC()

for tr in myExp.trainingset_traces:
        tr.plot()
plt.show()
myGIF_rect=GIF(0.1)
myGIF_rect.Tref=4.0
myGIF_rect.eta.setMetaParameters(length=5000.0, binsize_lb=2.0,
                                 binsize_ub=1000.0, slope=4.5)
myGIF_rect.fit(myExp, DT_beforeSpike=5.0)


