import numpy as np
import glob
import h5py
import seaborn

import sys
PATH_FLAT = '/Users/mj/Documents/NEST/'
sys.path.append(PATH_FLAT+'/GIFFittingToolbox/src')
sys.path.append(PATH_FLAT+'/GIFFittingToolbox/src/HBP')


from Experiment import *
from GIF import *
from AEC_Badel import *
from AEC_Dummy import *
from Filter_Rect_LinSpaced import *
from Filter_Rect_LogSpaced import *
from Filter_Exps import *
from GIF_HT import *

import Tools


# import seaborn
# import matplotlib.pyplot as plt


####################################################
# Import Data. Create Arrays
####################################################

TRAIN_PATH = 'L5_TTPC1_cADpyr232_1/python_recordings/Data/H5Data/Train/*.hdf5'
TEST_PATH = 'L5_TTPC1_cADpyr232_1/python_recordings/Data/H5Data/Test/*.hdf5'
TRAIN_DATA_PATH = glob.glob(PATH_FLAT+TRAIN_PATH)
TEST_DATA_PATH = glob.glob(PATH_FLAT+TEST_PATH)

V_units = 10**-3
I_units = 10**-9

V_test = []
V_train = []
I_test = []
I_train = []
T_test = []
T_train = []
h5DataTest = []
h5DataTrain = []

for n, k in enumerate(TRAIN_DATA_PATH):
    print n, k
    h5DataTrainTemp = h5py.File(k, 'r')
    h5DataTrain.append(h5DataTrainTemp)

for n, k in enumerate(TEST_DATA_PATH):
    h5DataTestTemp = h5py.File(k, 'r')
    h5DataTest.append(h5DataTestTemp)

for n, k, i in zip(h5DataTest.get('current'), h5DataTest.get('voltage'),
                   h5DataTest.get('time')):
    Itemp = np.array(n)
    I_test.append(Itemp)
    Vtemp = np.array(k)
    V_test.append(Vtemp)
    Ttemp = np.array(i)
    T_test.append(Ttemp)

assert(np.size(V_test) == np.size(I_test))


for n, k, i in zip(h5DataTrain.get('current'), h5DataTrain.get('voltage'),
                   h5DataTrain.get('time')):
    Itemp = np.array(n)
    I_train.append(Itemp)
    Vtemp = np.array(k)
    V_train.append(Vtemp)
    Ttemp = np.array(i)
    T_train.append(Ttemp)

assert(np.size(V_train) == np.size(I_train))


####################################################
# Load Training Set
####################################################


myExp = Experiment('Experiment 1', .1)

for n, k in enumerate(V_test):
    print "Trials"
    print n
    myExp.addTrainingSetTrace(V_train[n], V_units, I_train[n], I_units,
                              np.size(T_train[n])/10,FILETYPE='Array')
    myExp.trainingset_traces[n].setROI([[1000,120000.0]])

for n, k in enumerate(V_train):
    myExp.addTestSetTrace(V_test[n], V_units, I_test[n], I_units,
                              np.size(T_test[n])/10, FILETYPE='Array')
    myExp.testset_traces[n].setROI([[1000,20000]])

myExp.plotTrainingSet()
#myExp.plotTestSet()

####################################################
# AEC
####################################################


myAEC = AEC_Dummy()
myExp.setAEC(myAEC)
myExp.performAEC()


#################################################
# METAPARAMETERS - MODEL
#################################################


DT_beforespike = 5.0
T_ref = 3.0
tau_gamma = [10.0, 50.0, 250.0]
eta_tau_max = 1000.0


####################################################
# GIF Fitting
####################################################

myGIF_rect = GIF(0.1)

myGIF_rect.Tref = T_ref
myGIF_rect.eta = Filter_Rect_LogSpaced()
myGIF_rect.eta.setMetaParameters(length=500.0, binsize_lb=2.0, binsize_ub=100.0, slope=4.5)
myGIF_rect.fitVoltageReset(myExp, myGIF_rect.Tref, do_plot=False)
myGIF_rect.fitSubthresholdDynamics(myExp, DT_beforeSpike=DT_beforespike)

# Fit sum of 3 exps on spike-triggered current (timescales slower than 500ms are excluded)
myGIF_rect.eta.fitSumOfExponentials(3, [ 1.0, 0.5, 0.1], tau_gamma, ROI=None, dt=0.1)
print "Optimal timescales: ", myGIF_rect.eta.tau0

tau_opt = [t for t in myGIF_rect.eta.tau0 if t < eta_tau_max]


#####################################################################################################################
# FIT GIF
#####################################################################################################################

myGIF = GIF(0.1)

myGIF.Tref = T_ref
myGIF.eta = Filter_Exps()
myGIF.eta.setFilter_Timescales(tau_opt)
myGIF.gamma = Filter_Exps()
myGIF.gamma.setFilter_Timescales(tau_gamma)

myGIF.fit(myExp, DT_beforeSpike=DT_beforespike)

# Use the myGIF model to predict the spiking data of the test data set in myExp
myPrediction = myExp.predictSpikes(myGIF, nb_rep=500)

# Compute Md* with a temporal precision of +/- 4ms
Md = myPrediction.computeMD_Kistler(4.0, 0.1)

# Plot data vs model prediction
myPrediction.plotRaster(delta=1000.0)
