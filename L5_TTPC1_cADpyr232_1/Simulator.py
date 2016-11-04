import os

from bisect import bisect_left

import neuron
import numpy as np
import sys

import CurrentGenerator


class Simulator:
    def __init__(self):

        # Creation Variables
        self.recordings = []
        self.stimuli = []
        self.cell = []

        """
                :param time: simulation time
                :param sigmamax: sigmaMax used to determine Sigma and DeltaSigma
                :param sigmamin: sigmaMin used to determine Sigma and DeltaSigma
                :param i_e0: Injected current without noise
        """

        self.time = 3000.0
        self.sigmamax = 1.05
        self.sigmamin = 0.35
        self.sigmaopt = 0.0
        self.i_e0 = 0.0
        self.dt = 0.1

        # Injection current
        self.playVector = []
        self.current = []

        # Recorded values
        self.rvoltage = []
        self.rtime = []
        self.rcurrent = []

        # Optimization
        self.variance = []
        self.varPlot = []
        self.sigmaoptPlot = []
        self.deltasigma = 0.05
        self.spks = []
        self.hz = 0.0

        # Current generating class
        self.cg = CurrentGenerator.CurrentGenerator

    def create_cell(self, add_synapses=True):
        # Load morphology
        """
        Creates the cell in Neuron
        :return: Cell
        :rtype: Hoc
        """
        neuron.h.load_file("morphology.hoc")
        # Load biophysics
        neuron.h.load_file("biophysics.hoc")
        # Load main cell template
        neuron.h.load_file("template.hoc")

        # Instantiate the cell from the template

        self.cell = neuron.h.cADpyr232_L5_TTPC1_0fb1ca4724(1 if add_synapses
                                                           else 0)

        return self.cell

    def create_stimuli(self):
        """
        Create stimulus input
        :return: Current Clamp
        :rtype: Neuron <HOC> Object
        """
        self.stimuli = neuron.h.IClamp(0.5, sec=self.cell.soma[0])
        self.stimuli.delay = 0
        self.stimuli.dur = 1e9

        return self.stimuli

    def create_current(self):
        """
        Generate the noisy current needed for injection
        """
        cg = CurrentGenerator.CurrentGenerator(time=self.time, i_e0=self.i_e0,
                                               sigmaMax=self.sigmamax,
                                               sigmaMin=self.sigmamin)
        self.current = cg.generatecurrent()
        self.playVector = neuron.h.Vector(np.size(self.current))

        for k in xrange(np.size(self.current)):
            self.playVector.set(k, self.current[k])

        self.currentFlag = False

    def create_recordings(self, cell):
        """
        Generates the Dictionary and Vectors used to store Neuron data
        :return: Time, Voltage, Current
        :rtype:  Dictionary ['time', 'soma(0.5)', 'current']
        """
        self.recordings = {'time': neuron.h.Vector(), 'soma(0.5)':
            neuron.h.Vector(), 'current': neuron.h.Vector()}
        self.recordings['current'].record(self.stimuli._ref_amp, 0.1)
        self.recordings['time'].record(neuron.h._ref_t, 0.1)
        self.recordings['soma(0.5)'].record(cell.soma[0](0.5)._ref_v, 0.1)

        return self.recordings

    def record_recordings(self):
        self.rtime = np.array(self.recordings['time'])
        self.rvoltage = np.array(self.recordings['soma(0.5)'])
        self.rcurrent = np.array(self.recordings['current'])
        recordings_dir = 'python_recordings'
        soma_voltage_filename = os.path.join(
            recordings_dir,
            'soma_voltage_step.dat')
        np.savetxt(
            soma_voltage_filename,
            np.transpose(
                np.vstack((
                    self.rtime,
                    self.rvoltage,
                    self.rcurrent))))

    def run_step(self, time):
        self.time = time
        neuron.h.tstop = self.time
        self.create_current()
        self.playVector.play(self.stimuli._ref_amp, neuron.h.dt)
        print("playVector Sum: {0}".format(np.sum(np.array(self.playVector))))
        print('Running for %f ms' % neuron.h.tstop)
        neuron.h.run()
        self.rvoltage = np.array(self.recordings['soma(0.5)'])
        self.rcurrent = np.array(self.recordings['current'])

    def brute_optimize_ie(self):
        n = 1
        self.i_e0 = 0.5
        self.time = 5000.0
        while self.hz < 10:
            self.optmize_ie()
            self.spks = self.cg(voltage=self.rvoltage).detectSpikes()
            if self.spks.size:
                self.hz = len(self.spks) / (self.time / 1000.0)
            else:
                self.hz = 0.0
            self.dataprint("Spikes: {0}, Hz: {5}, Current: {1}, Voltage: {2}, "
                           "RCurrent {3}, Max Voltage: {4}".format(
                self.spks,
                self.i_e0,
                self.rvoltage,
                self.rcurrent,
                np.max(self.rvoltage),
                self.hz))

            if self.hz <= 10:
                self.i_e0 += 0.4
            elif self.hz > 13:
                self.i_e0 -= 0.1
        CurrentGenerator.plotcurrent(self.current)

    def optmize_ie(self):
        self.time = 5000
        self.run_step(self.time)

    def run_optimize_sigma(self):
        self.optimize_sigma()
        self.playVector.play(self.stimuli._ref_amp, neuron.h.dt)
        neuron.h.run()
        self.rvoltage = np.array(self.recordings['soma(0.5)'])
        self.variance = self.cg(voltage=self.rvoltage).subthresholdVar()

    def brute_optimize_sigma(self):
        n = 1
        while self.variance < 7 or not self.variance:
            self.dataprint("Optimizing Sigma: {0}".format(n))
            self.run_optimize_sigma()
            self.varPlot.append(self.variance)
            self.sigmaoptPlot.append(self.sigmaopt)
            self.sigmaopt += self.deltasigma
            if np.min(self.varPlot) > 3 and self.varPlot:
                raise Exception("Need a lower Sigma starting point")
            n += 1

        sminIndex = self.findOpt(self.varPlot, 3)
        smaxIndex = self.findOpt(self.varPlot, 7)
        self.sigmamin = self.sigmaoptPlot[sminIndex]
        self.sigmamax = self.sigmaoptPlot[smaxIndex]

        if self.varPlot[sminIndex] > 4:
            raise Exception("Sigma Minimum is above acceptable range."
                            "Initiate fitting with smaller Sigma")
        elif self.varPlot[sminIndex] < 2:
            raise Exception("Sigma Minimum is below acceptable range."
                            "Initiate fitting with smaller d_sigma")
        if 5 > self.varPlot[smaxIndex] > 9:
            raise Exception("Sigma Maximum is out of bounds."
                            "Initiate fitting with smaller d_sigma.")
        print("")
        print("Optimization Complete: Sigma Min: {0}. Sigma Max {1}.".format(
            self.sigmamin, self.sigmamax))
        CurrentGenerator.plotcurrent(self.current)

    def optimize_sigma(self):
        self.time = 3000
        neuron.h.tstop = self.time
        self.i_e0 = 0.0
        cg = CurrentGenerator.CurrentGenerator(time=self.time,
                                               i_e0=self.i_e0,
                                               optsigma=self.sigmaopt)
        self.current = cg.optgeneratecurrent()
        self.playVector = neuron.h.Vector(np.size(self.current))

        for k in xrange(np.size(self.current)):
            self.playVector.set(k, self.current[k])
        return self.playVector

    def plottrace(self):
        plot_traces = True
        if plot_traces:
            import pylab
            self.rvoltage = np.array(self.recordings['soma(0.5)'])
            self.rtime = np.array(self.recordings['time'])
            pylab.figure()
            pylab.plot(self.rtime, self.rvoltage)
            pylab.xlabel('time (ms)')
            pylab.ylabel('Vm (mV)')
            pylab.show()

    def findOpt(self, list, val):
        return min(range(len(list)), key=lambda i: abs(list[i] - val))

    def takeClosest(self, myList, myNumber):
        """
        Assumes myList is sorted. Returns closest value to myNumber.

        If two numbers are equally close, return the smallest number.
        """
        pos = bisect_left(myList, myNumber)
        if pos == 0:
            return myList[0]
        if pos == len(myList):
            return myList[-1]
        before = myList[pos - 1]
        after = myList[pos]
        print("Before: {0}. Before Pos-1: {1}".format(before, pos - 1))
        print("After: {0}. After Pos: {1}".format(after, pos))
        if after - myNumber < myNumber - before:
            return pos
        else:
            return pos - 1

    def init_simulation(self):
        """Initialise simulation environment"""

        neuron.h.load_file("stdrun.hoc")
        neuron.h.load_file("import3d.hoc")

        print('Loading constants')
        neuron.h.load_file('constants.hoc')

    def main(self, optimize=False):

        """Main"""

        self.init_simulation()
        self.cell = self.create_cell(add_synapses=False)
        self.stimuli = self.create_stimuli()
        self.recordings = self.create_recordings(self.cell)
        neuron.h.tstop = self.time
        neuron.h.cvode_active(0)
        if optimize:
            self.brute_optimize_sigma()
            self.brute_optimize_ie()
            self.plottrace()
        else:
            self.run_step(1000)

    def dataprint(self, data):
        sys.stdout.write("\r\x1b[K" + data)
        sys.stdout.flush()


Simulator().main(optimize=True)
