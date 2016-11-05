import numpy as np


def plotcurrent(val):
    import pylab
    pylab.plot(val)
    pylab.show()


class CurrentGenerator:
    def __init__(self, seed=777, time=10000, tau=100, i_e0=0.0, sigmaMax=0.8,
                 sigmaMin=0.5, frequency=0.2, dt=0.025, voltage=[],
                 threshold=0.0,
                 optsigma=0.5):

        self.seed = np.random.seed(seed)
        self.time = time
        self.tau = tau
        self.i_e0 = i_e0
        self.i_e = []
        self.sigmaMax = sigmaMax
        self.sigmaMin = sigmaMin
        self.sigma = (self.sigmaMax + self.sigmaMin) / 2
        self.delta_sigma = (self.sigmaMax - self.sigmaMin) / (2 * self.sigma)
        self.variance = []
        self.duration = 0.0
        self.frequency = frequency
        self.dt = dt
        self.voltage = voltage
        self.tolerance = 0.2
        self.spks = []
        self.spks_flag = False
        self.threshold = threshold
        self.optsigma = optsigma
        self.spks = []

    def generate_current(self):
        timespan = np.arange(self.time / self.dt)
        self.i_e = np.zeros(self.time / self.dt)
        self.variance = self.sigma * (1 + self.delta_sigma * np.sin(
            2 * np.pi * timespan * self.frequency * self.dt * 10 ** -3))
        for n in np.arange(self.time / self.dt - 1):
            self.i_e[n + 1] = self.i_e[n] + \
                              ((self.i_e0 - self.i_e[n]) / self.tau) * \
                              self.dt + \
                              np.sqrt((2 * np.power(self.variance[n],
                                                    2) * self.dt) / self.tau) \
                              * \
                              np.random.normal()
            self.i_e[n] = self.i_e[n + 1]
        #  plotcurrent(self.i_e)
        print("Sigma: {0}. DeltaSigma: {1}. i_e0: {2}".format(self.sigma,
                                                              self.delta_sigma,
                                                              self.i_e0))
        return self.i_e

    def sub_threshold_var(self):
        selection = self.get_far_from_spikes()
        sv = np.var(self.voltage[selection])
        assert (np.max(self.voltage[selection]) < self.threshold)

        return sv

    def opt_generate_current(self):
        timespan = np.arange(self.time / self.dt)
        self.i_e = np.zeros(self.time / self.dt)
        self.variance = self.optsigma * (1 + 0.2 * np.sin(
            2 * np.pi * timespan * self.frequency*self.dt * 10 ** -3))
        for n in np.arange(self.time / self.dt - 1):
            self.i_e[n + 1] = self.i_e[n] + \
                              ((self.i_e0 - self.i_e[n]) / self.tau) * \
                              self.dt + \
                              np.sqrt((2 * np.power(self.variance[n],
                                                    2) * self.dt) / self.tau) \
                              * np.random.normal()
            self.i_e[n] = self.i_e[n + 1]
        plotcurrent(self.i_e)

        return self.i_e

    def detect_spikes(self, ref=3.0):

        """
        Detect action potentials by threshold crossing (parameter threshold,
        mV) from below (i.e. with dV/dt>0).
        To avoid multiple detection of same spike due to noise, use an
        'absolute refractory period' ref, in ms.
        """

        ref_ind = int(ref / self.dt)
        t = 0
        while t < len(self.voltage) - 1:

            if (self.voltage[t] >= self.threshold >=
                    self.voltage[t - 1]):
                self.spks.append(t)
                t += ref_ind
            t += 1

        self.spks = np.array(self.spks)
        self.spks_flag = True
        return self.spks

    def get_far_from_spikes(self, d_t_before=8.0, d_t_after=8.0):

        """
        Return indices of the trace which are in ROI. Exclude all datapoints
        which are close to a spike.
        d_t_before: ms
        d_t_after: ms
        These two parameters define the region to cut around each spike.
        """
        if not self.spks_flag:
            self.detect_spikes()

        L = len(self.voltage)
        LR_flag = np.ones(L)

        LR_flag[:] = 0.0

        # Remove region around spikes
        DT_before_i = int(d_t_before / self.dt)
        DT_after_i = int(d_t_after / self.dt)

        for s in self.spks:
            lb = max(0, s - DT_before_i)
            ub = min(L, s + DT_after_i)

            LR_flag[lb: ub] = 1

        indices = np.where(LR_flag == 0)[0]

        return indices

CurrentGenerator().opt_generate_current()
