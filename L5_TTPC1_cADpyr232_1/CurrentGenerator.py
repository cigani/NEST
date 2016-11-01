import numpy as np
from scipy import weave


class CurrentGenerator:

    def __init__(self,
                 seed=777,
                 time=3000,
                 tau=100,
                 i_e0=0.0,
                 sigmaMax=0.8,
                 sigmaMin=0.5,
                 frequency=0.2,
                 dt=0.1,
                 subthresholdvoltage=[],
                 threshold=0.0,
                 optsigma = 0.5):

        self.seed = np.random.seed(seed)
        self.time = time
        self.tau = tau
        self.i_e0 = i_e0
        self.i_e = []
        self.sigmaMax = sigmaMax
        self.sigmaMin = sigmaMin
        self.sigma = (self.sigmaMax+self.sigmaMin)/2
        self.deltsigma = (self.sigmaMax-self.sigmaMax)/(2*self.sigma)
        self.variance = []
        self.duration = 0.0
        self.frequency = frequency
        self.dt = dt
        self.subthresholdVoltage = subthresholdvoltage
        self.tolerance = 0.2
        self.spks = 0
        self.spks_flag = False
        self.threshold = threshold
        self.optsigma = optsigma

    def generatecurrent(self):
        timespan = np.arange(self.time)
        self.i_e = np.zeros(self.time)
        self.variance = self.sigma*(1+self.deltsigma*np.sin(
                2*np.pi*timespan*self.frequency*10**-3))
        for n in np.arange(self.time - 1):
            self.i_e[n+1] = self.i_e[n] + \
                            ((self.i_e0-self.i_e[n])/self.tau) * self.dt + \
                            np.sqrt((2*np.power(self.variance[n],
                                                2) * self.dt)/ self.tau) * \
                            np.random.normal()
            self.i_e[n] = self.i_e[n+1]
        #self.plotcurrent()
        return self.i_e

    def subthresholdVar(self):
        selection = self.getFarFromSpikes()
        subthresholdVariance = np.var(self.subthresholdVoltage[selection])
        print('Subthresh Var: ')
        print subthresholdVariance

        return subthresholdVariance

    def optgeneratecurrent(self):
        timespan = np.arange(self.time)
        print "self.time: "
        print self.time
        self.i_e = np.zeros(self.time)
        self.variance = self.optsigma*(1+0.5*np.sin(
            2*np.pi*timespan*self.frequency*10**-3))
        for n in np.arange(self.time - 1):
            self.i_e[n+1] = self.i_e[n] + \
                            ((self.i_e0-self.i_e[n])/self.tau) * self.dt + \
                            np.sqrt((2*np.power(self.variance[n],
                                                2) * self.dt)/ self.tau) * \
                            np.random.normal()
            self.i_e[n] = self.i_e[n+1]
        return self.i_e

    def plotcurrent(self):
        import pylab
        pylab.plot(self.variance)
        pylab.show()

    def detectSpikes(self, ref=3.0):

        """
        Detect action potentials by threshold crossing (parameter threshold,
        mV) from below (i.e. with dV/dt>0).
        To avoid multiple detection of same spike due to noise, use an
        'absolute refractory period' ref, in ms.
        """

        self.spks = []
        ref_ind = int(ref / self.dt)
        t = 0
        while (t < len(self.subthresholdVoltage) - 1):

            if (self.subthresholdVoltage[t] >= self.threshold >=
                    self.subthresholdVoltage[t -1]):
                self.spks.append(t)
                t += ref_ind
            t += 1

        self.spks = np.array(self.spks)
        self.spks_flag = True

    def getFarFromSpikes(self, DT_before=5.0, DT_after=5.0):

        """
        Return indices of the trace which are in ROI. Exclude all datapoints
        which are close to a spike.
        DT_before: ms
        DT_after: ms
        These two parameters define the region to cut around each spike.
        """
        if not self.spks_flag:
            self.detectSpikes()

        L = len(self.subthresholdVoltage)

        LR_flag = np.ones(L)

        LR_flag[:] = 0.0

        # Remove region around spikes
        DT_before_i = int(DT_before / self.dt)
        DT_after_i = int(DT_after / self.dt)

        for s in self.spks:
            lb = max(0, s - DT_before_i)
            ub = min(L, s + DT_after_i)

            LR_flag[lb: ub] = 1

        indices = np.where(LR_flag == 0)[0]

        return indices


CurrentGenerator().generatecurrent()
