import os
import sys

import neuron
import numpy as np

import CurrentGenerator


class Simulator:

    def __init__(self):
        self.sigmaMinFlag = True
        self.sigmaMaxFlag = True
        self.recordings = []
        self.cell = []
        self.stimuli = []
        self.smax = 0.0
        self.smin = 0.0
        self.sigmaopt = 0.0
        self.playVector = []
        self.current = []
        self.currentFlag = True

    def create_cell(self, add_synapses=True):
        """Create the cell model"""
        # Load morphology
        neuron.h.load_file("morphology.hoc")
        # Load biophysics
        neuron.h.load_file("biophysics.hoc")
        # Load main cell template
        neuron.h.load_file("template.hoc")

        # Instantiate the cell from the template

        print("Loading cell cADpyr232_L5_TTPC1_0fb1ca4724")
        cell = neuron.h.cADpyr232_L5_TTPC1_0fb1ca4724(1 if add_synapses else 0)
        return cell


    def create_stimuli(self, cell):
        """Create the stimuli"""

        print('Attaching stimulus electrodes')

        stimuli = []

        iclamp = neuron.h.IClamp(0.5, sec=cell.soma[0])
        iclamp.delay = 0
        iclamp.dur = 1e9

        stimuli.append(iclamp)

        return stimuli
    def create_current(self, smax=0.8, smin=0.5, time=3000, i_e0=0.0):
        cg = CurrentGenerator.CurrentGenerator(time=time,
                                               i_e0=i_e0,
                                               sigmaMax=smax,
                                               sigmaMin=smin)
        self.current = cg.generatecurrent()
        self.currentFlag = False



    def create_recordings(self, cell, stim):
        """Create the recordings"""
        print('Attaching recording electrodes')

        self.recordings = {'time': neuron.h.Vector(), 'soma(0.5)':
            neuron.h.Vector(),
                      'current': neuron.h.Vector()}

        self.recordings['current'].record(stim._ref_amp, 0.1)
        self.recordings['time'].record(neuron.h._ref_t, 0.1)
        self.recordings['soma(0.5)'].record(cell.soma[0](0.5)._ref_v, 0.1)

        return self.recordings


    def run_step(self, smax=0.8, smin=0.3,
                 sigmaMaxFlag=True, sigmaMinFlag=True,
                 optsigma=0.0, voltage=[], time=3000, optFlag=False,
                 i_e0=0.0):
        """Run step current simulation with index step_number"""

        self.cell = self.create_cell(add_synapses=False)
        self.stimuli = self.create_stimuli(self.cell)
        self.recordings = self.create_recordings(self.cell, self.stimuli[0])

        neuron.h.tstop = time
        neuron.h.cvode_active(0)

        if not optFlag:
            if not self.currentFlag:
                inputNoisy = self.current
                VecStim = neuron.h.Vector(np.size(inputNoisy))
            else:
                self.create_current(smin=smin, smax=smax, i_e0=i_e0)
                inputNoisy = self.current
                VecStim = neuron.h.Vector(np.size(inputNoisy))
        else:
            pass


        for k in xrange(np.size(inputNoisy)):  # Hacky but stops seg errors
            VecStim.set(k, inputNoisy[k])
            # print VecStim.get(k)

        VecStim.play(self.stimuli[0]._ref_amp, neuron.h.dt)
        print('Running for %f ms' % neuron.h.tstop)
        neuron.h.run()
        time = np.array(self.recordings['time'])
        soma_voltage = np.array(self.recordings['soma(0.5)'])
        soma_current = np.array(self.recordings['current'])
        recordings_dir = 'python_recordings'
        if (sigmaMaxFlag or sigmaMinFlag):
            print "Flags"
            print sigmaMaxFlag
            print sigmaMinFlag
            self.optimize(time= neuron.h.tstop,
                     optsigma=optsigma,
                     voltage=soma_voltage)

        soma_voltage_filename = os.path.join(
            recordings_dir,
            'soma_voltage_step.dat')
        np.savetxt(
                soma_voltage_filename,
                np.transpose(
                   np.vstack((
                       time,
                       soma_voltage,
                       soma_current))))

        print('Soma voltage saved to: %s'
              % soma_voltage_filename)
        plot_traces=False
        if plot_traces:
            import pylab
            pylab.figure()
            pylab.plot(self.recordings['time'], self.recordings['soma(0.5)'])
            pylab.xlabel('time (ms)')
            pylab.ylabel('Vm (mV)')

    def optimize(self, time, voltage, optsigma=0.0, sigmaMaxFlag=True,
                 sigmaMinFlag=True):
        sigmaMaxFlag = sigmaMaxFlag
        sigmaMinFlag = sigmaMinFlag
        smax = 0.1
        smin = 0.1
        optsigma=optsigma

        os = CurrentGenerator.CurrentGenerator(time=time,
                                               subthresholdvoltage=voltage)
        tempSig = os.subthresholdVar()

        if 0.6 < tempSig > 0.8:
            sigmaMaxFlag=False
            print "Sigma Max: "
            print optsigma


        if sigmaMaxFlag:
            print "tempSig"
            print tempSig
            if 0.8 >= tempSig >= 0.6:
                sigmaMaxFlag = False
                print "Proper smax: "
                print optsigma
                run_step(smax=optsigma, optsigma=optsigma,
                         sigmaMaxFlag=sigmaMaxFlag)
            elif tempSig < 0.6:
                optsigma -= 0.1
                run_step(optsigma=optsigma)
            elif tempSig > 0.8:
                optsigma += 0.1
                run_step(optsigma=optsigma)

        if sigmaMinFlag:
            tempSig = os.optimizeSigma()
            print "tempSig"
            print tempSig
            if 0.4 >= tempSig >= 0.2:
                sigmaMinFlag = False
                print "Proper smin: "
                print optsigma
                run_step(smax=smax, smin=smin,
                         sigmaMaxFlag=sigmaMaxFlag, sigmaMinFlag=sigmaMinFlag)
            elif tempSig < 0.2:
                smin += 0.1
                run_step(smax=smax, smin=smin,
                         sigmaMaxFlag=sigmaMaxFlag, sigmaMinFlag=sigmaMinFlag)
            elif tempSig > 0.4:
                smin -= 0.1
                run_step(smax=smax, smin=smin,
                         sigmaMaxFlag=sigmaMaxFlag, sigmaMinFlag=sigmaMinFlag)

    def init_simulation(self):
        """Initialise simulation environment"""

        neuron.h.load_file("stdrun.hoc")
        neuron.h.load_file("import3d.hoc")

        print('Loading constants')
        neuron.h.load_file('constants.hoc')


    def main(self, plot_traces=True):

        """Main"""

        self.init_simulation()

        self.run_step()

