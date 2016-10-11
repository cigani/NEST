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
                            np.size(V[0])/10,
                            FILETYPE='Array')
print np.size(V[0])/10
for n,k in enumerate(dataPath[1:]):
                     myExp.addTestSetTrace(V[n], V_units,
                                           I[n], I_units,
                                           np.size(V[n])/10,
                                           FILETYPE='Array')
                     print np.size(V[n])/10


####################################################
# AEC
####################################################


myAEC = AEC_Dummy()
myExp.setAEC(myAEC)
myExp.performAEC()


####################################################
# GIF Fitting
####################################################

myGIF_rect = GIF(0.1)
myGIF_rect.Tref = 4.0
myGIF_rect.eta.setMetaParameters(length=3000.0, binsize_lb=2.0,
                                 binsize_ub=1000.0, slope=4.5)
myGIF_rect.fit(myExp, DT_beforeSpike=3.0)
'''
myGIF_exp = GIF(0.1)
myGIF_exp.Tref = 4.0

myGIF_exp.eta = Filter_Exps()
myGIF_exp.eta.setFilter_Timescales([1.0,  5.0,30.0,100.0,500.0])

#Perform Fit
myGIF_exp.fit(myExp,  DT_beforeSpike = 5.0)
'''

####################################################
# Compare Rect and Exp Models
####################################################

myPredictionGIF_rect = myExp.predictSpikes(myGIF_rect,  nb_rep=500)
# myPredictionGIF_exp = myExp.predictSpikes(myGIF_exp,  nb_rep=500)


print "Model Performance"
print "GIF Rect: "
myPredictionGIF_rect.computeMD_Kistler(40.0,  0.1)
# print "GIF exp: "
# myPredictionGIF_exp.computeMD_Kistler(4.0,  0.1)


####################################################
# Compare model Parameters
####################################################


# GIF.compareModels([myGIF_rect,  myGIF_exp], labels['GIF rect', 'GIF exp'])
