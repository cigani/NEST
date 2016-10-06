import numpy as np
import h5py
import glob


import sys
PATH_FLAT='/Users/michaeljaquier/Documents/gewaltig/'
sys.path.append(PATH_FLAT+'/nest-/lib/python2.7/site-packages')
sys.path.append(PATH_FLAT+'/fitting/GIFFittingToolbox/src')


#import seaborn
import matplotlib.pyplot as plt


from Experiment import *
from GIF import *
from AEC_Badel import *
from AEC_Dummy import *
from Filter_Rect_LinSpaced import *
from Filter_Rect_LogSpaced import *
from Filter_Exps import *


import Tools


####################################################
# Import Data. Create Arrays
####################################################



dataPath=glob.glob('./data/*.dat')
assert dataPath is not None

expData=[[[],[]] for x in xrange(np.size(dataPath))]
def expLoad(dataPath=dataPath, cols=1,expStart=7000,expEnd=280000):
    for i,k in enumerate(dataPath):
        expFile=np.loadtxt(k, usecols=[cols])
        expData[i]=np.array([
            expFile[expStart:expEnd],
            #np.append(
                #np.zeros(7000),
                np.ones(np.size(expFile[7000:expEnd]))*0.6])
    return expData

dataArray=expLoad()
V=[dataArray[n][0] for n,k in enumerate(dataPath)]
I=[dataArray[n][1] for n,k in enumerate(dataPath)]
V_units=10**-3
I_units=10**-9
print np.size(I)

####################################################
#Load Training Set
####################################################


myExp=Experiment('Experiment 1', 0.1)
myExp.addTrainingSetTrace(V[0],V_units,I[0],I_units,np.size(V[0])/10,
                          FILETYPE='Array')
myExp.trainingset_traces[0].setROI([[100,27000]])
#myExp.plotTrainingSet()
#plt.show()

for i,k in enumerate(dataPath[1:]):
    n = i+1
    myExp.addTestSetTrace(V[n],V_units, I[n], I_units,np.size(V[n])/10,
                      FILETYPE='Array')
#myExp.plotTestSet()
#plt.show()

####################################################
#AEC
####################################################


myAEC=AEC_Dummy()
myExp.setAEC(myAEC)
myExp.performAEC()
myExp.detectSpikes(0.0, 4.0)
#myExp.plotTestSet()

####################################################
#GIF Fitting
####################################################

myGIF_rect=GIF(0.1)
myGIF_rect.Tref=4.0
myGIF_rect.eta.setMetaParameters(length=5000.0, binsize_lb=2.0,
                                 binsize_ub=1000.0, slope=4.5)
myGIF_rect.fit(myExp, DT_beforeSpike=4.0)




myGIF_exp=GIF(0.1)
myGIF_exp.Tref=4.0

myGIF_exp.eta=Filter_Exps()
myGIF_exp.eta.setFilter_Timescales([0.1,1.0,5.0,30.0,100.0,500.0])

myGIF_exp.gamma=Filter_Exps()
myGIF_exp.gamma.setFilter_Timescales([0.1,1.0,5.0,30.0,100.0,500.0])

#Perform Fit
myGIF_exp.fit(myExp, DT_beforeSpike=5.0)


'''
myGIF=GIF(0.1)
myGIF.Tref=4.0
myGIF.eta=Filter_Rect_LogSpaced()
myGIF.eta.setMetaParameters(length=500.0,binsize_lb=2.0,
                            binsize_ub=1000,slope=4.5)
myGIF.gamma=Filter_Rect_LogSpaced()
myGIF.gamma.setMetaParameters(length=500.0,binsize_lb=5.0,
                        binsize_ub=1000,slope=5.0)
myGIF.fit(myExp,DT_beforeSpike=5.0)
myGIF.printParameters()
#myGIF.plotParameters()
prediction=myExp.predictSpikes(myGIF,nb_rep=500)
Md=prediction.computeMD_Kistler(4.0,0.1)
prediction.plotRaster(delta=1000.0)
'''
####################################################
#Compare Rect and Exp Models
####################################################

myPredictionGIF_rect = myExp.predictSpikes(myGIF_rect, nb_rep=500)
myPredictionGIF_exp = myExp.predictSpikes(myGIF_exp, nb_rep=500)


myPredictionGIF_rect.plotRaster(delta=100)
myPredictionGIF_exp.plotRaster(delta=100)

print "Model Performance"
print "GIF Rect: "
myPredictionGIF_rect.computeMD_Kistler(4.0,1)

print "GIF exp: "
myPredictionGIF_exp.computeMD_Kistler(4.0,1)



####################################################
# Compare model Parameters
####################################################


#GIF.compareModels([myGIF_rect, myGIF_exp], labels=['GIF rect', 'GIF exp'])
