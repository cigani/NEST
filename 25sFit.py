import numpy as np
import loading as l

import sys
PATH_FLAT = '/Users/mj/Documents/NEST/'
sys.path.append(PATH_FLAT+'/GIFFittingToolbox/src')

from Experiment import *
from GIF import *
from AEC_Badel import *
from AEC_Dummy import *
from Filter_Rect_LinSpaced import *
from Filter_Rect_LogSpaced import *
from Filter_Exps import *

import Tools


# import seaborn
# import matplotlib.pyplot as plt




####################################################
# Import Data. Create Arrays
####################################################


dataArray = l.expLoad()[0]
dataPath = l.expLoad()[1]
V = [dataArray[n][0] for n, k in enumerate(dataPath)]
I = [dataArray[n][1] for n, k in enumerate(dataPath)]
V_units = 10**-3
I_units = 10**-9

assert np.size(I) == np.size(V) # These need to be equal


####################################################
# Load Training Set
####################################################


myExp = Experiment('Experiment 1', 0.1)
myExp.addTrainingSetTrace(V[0], V_units,
                            I[0], I_units,
                            np.size(V[1])/10,
                            FILETYPE='Array')
for n,k in enumerate(dataPath[1:]):
                     myExp.addTestSetTrace(V[n], V_units,
                                           I[n], I_units,
                                           np.size(V[n])/10,
                                           FILETYPE='Array')


####################################################
# AEC
####################################################


myAEC = AEC_Dummy()
myExp.setAEC(myAEC)
myExp.performAEC()
'''
myExp.setAECTrace(V[0], V_units,
                            I[0], I_units,
                            np.size(V[0])/10,
                            FILETYPE='Array')
myAEC = AEC_Badel(myExp.dt)
# Define metaparametres
myAEC.K_opt.setMetaParameters(length=150.0, binsize_lb=myExp.dt,
                              binsize_ub=2.0, slope=30.0, clamp_period=1.0)
myAEC.p_expFitRange = [3.0,150.0]
myAEC.p_nbRep = 15

# Assign myAEC to myExp and compensate the voltage recordings
myExp.setAEC(myAEC)
myExp.performAEC()
'''
####################################################
# GIF Fitting
####################################################

myGIF_rect = GIF(0.1)
myGIF_rect.Tref = 4.0
myGIF_rect.eta.setMetaParameters(length=2000.0, binsize_lb=2.0,
                                 binsize_ub=1000.0, slope=4.5)
myGIF_rect.gamma = Filter_Rect_LogSpaced()
myGIF_rect.gamma.setMetaParameters(length=1000.0, binsize_lb=5.1,
                                   binsize_ub=1000.0, slope=5.0)
myGIF_rect.fit(myExp, DT_beforeSpike=2.0)
'''
# myGIF_exp = GIF(0.1)
# myGIF_exp.Tref = 4.0

# myGIF_exp.eta = Filter_Exps()
# myGIF_exp.eta.setFilter_Timescales([0.01, 0.1, 1.0,
#                                     5.0, 30.0, 100.0,
#                                     200.0, 500.0])

#Perform Fit
# myGIF_exp.fit(myExp, DT_beforeSpike=5.0)

# Create a new object GIF
myGIF = GIF(0.1)

# Define parameters
myGIF.Tref = 4.0

myGIF.eta = Filter_Rect_LogSpaced()
myGIF.eta.setMetaParameters(length=2000.0, binsize_lb=2.0,
                            binsize_ub=1000.0, slope=4.5)

myGIF.gamma = Filter_Rect_LogSpaced()
myGIF.gamma.setMetaParameters(length=1000.0, binsize_lb=5.0,
                              binsize_ub=1000.0, slope=5.0)

# Perform the fit
myGIF.fit(myExp, DT_beforeSpike=2.0)
'''
####################################################
# Compare Rect and Exp Models
####################################################

myPredictionGIF_rect = myExp.predictSpikes(myGIF_rect, nb_rep=500)
# myPredictionGIF_exp = myExp.predictSpikes(myGIF_exp, nb_rep=500)
myPredictionGIF_rect.plotRaster(delta=1000)

print "Model Performance"
print "GIF Rect: "
# myPredictionGIF_gene = myExp.predictSpikes(myGIF, nb_rep=500)
myPredictionGIF_rect.computeMD_Kistler(40.0, 0.1)
# print "GIF exp: "
# myPredictionGIF_exp.computeMD_Kistler(4.0,  0.1)
# myPredictionGIF_gene.computeMD_Kistler(4.0, 0.1)

####################################################
# Compare model Parameters
####################################################


# GIF.compareModels([myGIF_rect,  myGIF_exp], labels['GIF rect', 'GIF exp'])
