import sys

import numpy as np
import loading


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


# import seaborn
# import matplotlib.pyplot as plt

class Fit():
    def __init__(self):

        self.V_units = 10**-3
        self.I_units = 10**-9
        self.trainData = []
        self.testData = []
        self.DT_beforespike = 5.0
        self.T_ref = 3.0
        self.tau_gamma = [10.0, 50.0, 250.0]
        self.eta_tau_max = 1000.0
        self.tau_opt = []

    def importdata(self):

        # Data[0] = Voltage, Data[1] = Current, Data[2] = Time

        self.trainData, self.testData = loading.Loader().dataload()

        self.myExp = Experiment('Experiment 1', .1)

        for n in self.trainData:
            print "Trials"
            print n
            self.myExp.addTrainingSetTrace(n[0], self.V_units,
                                           n[1], self.I_units,
                                           np.size(n[2])/10,
                                           FILETYPE='Array')
            self.myExp.trainingset_traces[n].setROI([[1000, 120000.0]])

        for n in self.testData:
            self.myExp.addTestSetTrace([n][0], self.V_units,
                                       [n][1], self.I_units,
                                       np.size([n][2])/10,
                                       FILETYPE='Array')
            self.myExp.testset_traces[n].setROI([[1000, 20000]])

        self.fitaec(self, self.myExp)

    def fitaec(self, myExp):

        myAEC = AEC_Dummy()
        myExp.setAEC(myAEC)
        myExp.performAEC()

        self.optimizetimescales(self, myExp)



    def optimizetimescales(self, myExp):
        myExp.plotTrainingSet()
        myExp.plotTestSet()

        myGIF_rect = GIF(0.1)

        myGIF_rect.Tref = self.T_ref
        myGIF_rect.eta = Filter_Rect_LogSpaced()
        myGIF_rect.eta.setMetaParameters(length=500.0, binsize_lb=2.0,
                                         binsize_ub=100.0, slope=4.5)
        myGIF_rect.fitVoltageReset(myExp, myGIF_rect.Tref, do_plot=False)
        myGIF_rect.fitSubthresholdDynamics(myExp,
                                           DT_beforeSpike=self.DT_beforespike)

        myGIF_rect.eta.fitSumOfExponentials(3, [1.0, 0.5, 0.1],
                                            self.tau_gamma, ROI=None, dt=0.1)
        print "Optimal timescales: ", myGIF_rect.eta.tau0

        self.tau_opt = [t for t in myGIF_rect.eta.tau0 if t < self.eta_tau_max]

        self.fitmodel(self, myExp)

    def fitmodel(self, myExp):

        myGIF = GIF(0.1)

        myGIF.Tref = self.T_ref
        myGIF.eta = Filter_Exps()
        myGIF.eta.setFilter_Timescales(self.tau_opt)
        myGIF.gamma = Filter_Exps()
        myGIF.gamma.setFilter_Timescales(self.tau_gamma)

        myGIF.fit(myExp, DT_beforeSpike=self.DT_beforespike)

        # Use the myGIF model to predict the spiking data of the test data set in myExp
        myPrediction = myExp.predictSpikes(myGIF, nb_rep=500)

        # Compute Md* with a temporal precision of +/- 4ms
        Md = myPrediction.computeMD_Kistler(4.0, 0.1)

        # Plot data vs model prediction
        myPrediction.plotRaster(delta=1000.0)

Fit().importdata()