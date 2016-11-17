import sys

PATH_FLAT = '/Users/mj/Documents/NEST/'
sys.path.append(PATH_FLAT + '/GIFFittingToolbox/src')
sys.path.append(PATH_FLAT + '/GIFFittingToolbox/src/HBP')

import loading
import numpy as np

from Experiment import *
from GIF import *
from AEC_Badel import *
from AEC_Dummy import *
from Filter_Rect_LinSpaced import *
from Filter_Rect_LogSpaced import *
from Filter_Exps import *
from GIF_HT import *

import seaborn


class Fit():
    def __init__(self):
        self.V_units = 10 ** -3
        self.I_units = 10 ** -9
        self.trainData = []
        self.testData = []
        self.DT_beforespike = 5.0
        self.T_ref = 4.0
        self.tau_gamma = [10.0, 50.0, 250.0]
        self.eta_tau_max = 1000.0
        self.tau_opt = []

    @staticmethod
    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in xrange(0, len(l), n):
            yield l[i:i + n]

    def importdata(self):
        # Data[0] = Voltage, Data[1] = Current, Data[2] = Time

        self.trainData, self.testData = loading.Loader().dataload()

        self.myExp = Experiment('Experiment 1', .1)
        for voltage, current, time in zip(self.trainData[0], self.trainData[1],
                                          self.trainData[2]):
            self.myExp.addTrainingSetTrace(voltage[10000:], self.V_units,
                                           current[10000:], self.I_units,
                                           np.size(time[10000:]) / 10,
                                           FILETYPE='Array')

        for voltage, current, time in zip(self.testData[0], self.testData[1],
                                          self.testData[2]):
            for voltageChunk, currentChunk, timeChunk in zip(
                    self.chunks(voltage, 100000),
                    self.chunks(current, 100000),
                    self.chunks(time, 100000)):
                self.myExp.addTestSetTrace(voltageChunk, self.V_units,
                                           currentChunk, self.I_units,
                                           np.size(timeChunk) / 10,
                                           FILETYPE='Array')

        self.fitaec(self.myExp)

    def fitaec(self, myExp):
        myAEC = AEC_Dummy()
        myExp.setAEC(myAEC)
        myExp.performAEC()

        self.optimizetimescales(myExp)

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

        self.fitmodel(myExp)

    def fitmodel(self, myExp):
        myGIF = GIF(0.1)
        myGIF.Tref = self.T_ref
        myGIF.eta = Filter_Exps()
        myGIF.eta.setFilter_Timescales(self.tau_opt)
        myGIF.gamma = Filter_Exps()
        myGIF.gamma.setFilter_Timescales(self.tau_gamma)
        myGIF.fit(myExp, DT_beforeSpike=self.DT_beforespike)

        myPrediction = myExp.predictSpikes(myGIF, nb_rep=500)
        Md = myPrediction.computeMD_Kistler(4.0, 0.1)
        myPrediction.plotRaster(delta=1000.0)


Fit().importdata()
