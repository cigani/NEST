import os
import sys
from bisect import bisect_left

import neuron
import numpy as np

import CurrentGenerator


def dataprint(data):
    """

    :rtype: Prints one line to Terminal
    """
    sys.stdout.write("\r\x1b[K" + data)
    sys.stdout.flush()


def take_closest(my_list, my_number):
    """
    Assumes my_list is sorted. Returns closest value to my_number.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(my_list, my_number)
    if pos == 0:
        return my_list[0]
    if pos == len(my_list):
        return my_list[-1]
    before = my_list[pos - 1]
    after = my_list[pos]
    print("Before: {0}. Before Pos-1: {1}".format(before, pos - 1))
    print("After: {0}. After Pos: {1}".format(after, pos))
    if after - my_number < my_number - before:
        return pos
    else:
        return pos - 1


def find_opt(input_list, val):
    return min(range(len(input_list)), key=lambda i: abs(input_list[i] - val))


def init_simulation():
    """Initialise simulation environment"""

    neuron.h.load_file("stdrun.hoc")
    neuron.h.load_file("import3d.hoc")

    print('Loading constants')
    neuron.h.load_file('constants.hoc')


class Simulator:
    def __init__(self):

        # Creation Variables
        self.currentFlag = False
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
        self.sigmaopt = 0.0
        self.variance = []
        self.varPlot = []
        self.sigmaoptPlot = []
        self.deltasigma = 0.01
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
        self.current = cg.generate_current()
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
        print('Running for %f ms' % neuron.h.tstop)
        neuron.h.run()
        self.rvoltage = np.array(self.recordings['soma(0.5)'])
        self.rcurrent = np.array(self.recordings['current'])

    def brute_optimize_ie(self):
        n = 1
        self.time = 3000.0
        while self.hz < 10:
            self.optmize_ie()
            self.spks = self.cg(voltage=self.rvoltage).detect_spikes()
            if self.spks.size:
                self.hz = len(self.spks) / (self.time / 1000.0)
            else:
                self.hz = 0.0
            dataprint("i_e0: {0}, Hz: {1}"
                      .format(self.i_e0,
                              self.hz))
            if self.hz <= 10:
                self.i_e0 += 0.1
            elif self.hz > 13:
                self.i_e0 -= 0.1
            assert (
                np.size(self.rvoltage == np.size(np.array(self.playVector))))
        CurrentGenerator.plotcurrent(self.current)

    def optmize_ie(self):
        self.time = 10000
        self.run_step(self.time)

    def run_optimize_sigma(self):
        self.optimize_sigma()
        self.playVector.play(self.stimuli._ref_amp, neuron.h.dt)
        neuron.h.run()
        self.rvoltage = np.array(self.recordings['soma(0.5)'])
        self.variance = self.cg(voltage=self.rvoltage).sub_threshold_var()

    def brute_optimize_sigma(self):
        n = 1
        while self.variance < 7 or not self.variance:
            self.run_optimize_sigma()

            dataprint("Optimizing Sigma: {0}. "
                      "Current Sigma: {1}. Current Var: {2}."
                      .format(n,
                              self.sigmaopt,
                              self.variance))
            self.varPlot.append(self.variance)
            self.sigmaoptPlot.append(self.sigmaopt)
            self.sigmaopt += self.deltasigma
            n += 1
            assert (
                np.size(self.rvoltage == np.size(np.array(self.playVector))))

        sminIndex = find_opt(self.varPlot, 3)
        smaxIndex = find_opt(self.varPlot, 7)
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
        self.time = 5000
        neuron.h.tstop = self.time
        self.i_e0 = 0.0
        cg = CurrentGenerator.CurrentGenerator(time=self.time,
                                               i_e0=self.i_e0,
                                               optsigma=self.sigmaopt)
        self.current = cg.opt_generate_current()
        self.playVector = neuron.h.Vector(np.size(self.current))

        for k in xrange(np.size(self.current)):
            self.playVector.set(k, self.current[k])
        return self.playVector

    def plot_trace(self, val):
        plot_traces = True
        if plot_traces:
            import pylab
            self.rtime = np.array(self.recordings['time'])
            pylab.figure()
            pylab.plot(self.rtime, val)
            pylab.xlabel('time (ms)')
            pylab.ylabel('Vm (mV)')
            pylab.show()

    def main(self, optimize=False):

        """Main"""

        init_simulation()
        self.cell = self.create_cell(add_synapses=False)
        self.stimuli = self.create_stimuli()
        self.recordings = self.create_recordings(self.cell)
        neuron.h.tstop = self.time
        neuron.h.cvode_active(0)
        if optimize:
            self.brute_optimize_sigma()
            self.brute_optimize_ie()
            self.plot_trace(np.array(self.recordings['soma(0.5)']))
            self.plot_trace(np.array(self.recordings['current']))
        else:
            self.run_step(1000)


Simulator().main(optimize=True)
