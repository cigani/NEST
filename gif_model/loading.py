import numpy as np
import h5py
import glob

import sys
PATH_FLAT='/Users/michaeljaquier/Documents/gewaltig/'
sys.path.append(PATH_FLAT+'/nest-/lib/python2.7/site-packages')
sys.path.append(PATH_FLAT+'/fitting/GIFFittingToolbox/src')

import seaborn
import maplotlib.pyplot as plt

#### Import Files ####

dataPath=glob.glob('./data/*.dat')
assert dataPath is not None

expData=[[[],[]] for x in xrange(np.size(dataPath))]
def expLoad(dataPath=dataPath, cols=1,
            ExpStart=7000,ExpStop=280000,
            iStart=0,iE=0.6):
    for i,k in enumerate(dataPath):
        expFile=np.loadtxt(k,usecols=[cols])
        if iE is not 0:
            expData[i]=np.array([expFile,
                                 np.append(
                                     np.zeros(iStart),
                                     np.ones(np.size(
                                         expFile[iE:ExpStop]))*0.6)])
        else:
            expData[i]=np.array([
                expFile,
                np.ones(np.size(expFile[ExpStart:ExpStop])*iE)])


dataArray=expLoad()
V=[dataArray[n][0] for n,k in enumerate(dataPath)]
I=[dataArray[n][1] for n,k in enumerate(dataPath)]
V_units=10**-3
I_units=10**-9




