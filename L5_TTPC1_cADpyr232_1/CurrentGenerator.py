import numpy as np


class CurrentGenerator():

    def __init__(self):

        self.seed = np.random.seed(777)
        self.time = 10000
        self.tau = 100.0
        self.i_e0 = 0.48
        self.i_e = []
        self.sigma0 = 0.48
        self.sigma = 0.5
        self.variance = []
        self.duration = 0.0
        self.frequency = 0.2
        self.dt = 0.1

    def generatecurrent(self):

        timespan = np.arange(self.time)

        self.i_e = np.zeros(self.time)
        self.variance = self.sigma0*(1+self.sigma*np.sin(
                2*np.pi*timespan*self.frequency*10**-3))
        for n in np.arange(self.time - 1):
            self.i_e[n+1] = self.i_e[n] + \
                            ((self.i_e0-self.i_e[n])/self.tau) * self.dt + \
                            np.sqrt((2*np.power(self.variance[n],
                                                2) * self.dt)/ self.tau) * \
                            np.random.normal()
            self.i_e[n] = self.i_e[n+1]
        self.plotcurrent()
        return self.i_e

    def plotcurrent(self):
        import pylab
        pylab.plot(self.i_e)
        pylab.show()

CurrentGenerator().generatecurrent()
