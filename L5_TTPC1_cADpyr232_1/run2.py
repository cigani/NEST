import os
import sys

import neuron
import numpy as np


def generatecurrent(f0, dur, delt=0.8, i_e0=0.48):
    np.random.seed(777)
    t = np.arange(dur)
    i_e = np.zeros(dur)
    tau = 20  # Lower = More Sinusoid
    delt0 = .37  # Higher = Larger noise contribution
    var = delt0*(1+delt*np.sin(2*np.pi*t*f0))
    for n in np.arange(dur-1):
        i_e[n+1] = i_e[n] + ((i_e0-i_e[n])/tau)*neuron.h.dt + \
            np.sqrt((2*np.power(var[n], 2) * neuron.h.dt) / tau) * \
            np.random.normal()
        # print(np.power(var[n],2))
        i_e[n] = i_e[n+1]
        # print("Step: %s" %n)

    return i_e


def create_cell(add_synapses=True):
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


def create_stimuli(cell):
    """Create the stimuli"""

    print('Attaching stimulus electrodes')

    stimuli = []

    iclamp = neuron.h.IClamp(0.5, sec=cell.soma[0])
    iclamp.delay = 0
    iclamp.dur = 1e9

    stimuli.append(iclamp)

    return stimuli


def create_recordings(cell, stim):
    """Create the recordings"""
    print('Attaching recording electrodes')

    recordings = {'time': neuron.h.Vector(), 'soma(0.5)': neuron.h.Vector(),
                  'current': neuron.h.Vector()}

    recordings['current'].record(stim._ref_amp, 0.1)
    recordings['time'].record(neuron.h._ref_t, 0.1)
    recordings['soma(0.5)'].record(cell.soma[0](0.5)._ref_v, 0.1)

    return recordings


def run_step(plot_traces=None):
    """Run step current simulation with index step_number"""

    cell = create_cell(add_synapses=False)
    stimuli = create_stimuli(cell)
    recordings = create_recordings(cell, stimuli[0])
    print('Setting simulation time to 3s for the step currents')
    neuron.h.tstop = 150000

    print('Disabling variable timestep integration')
    neuron.h.cvode_active(0)

    inputNoisy = generatecurrent(0.00002, (neuron.h.tstop / neuron.h.dt + 1))

    VecStim = neuron.h.Vector(np.size(inputNoisy))
    for k in xrange(np.size(inputNoisy)):  # Hacky but stops seg errors
        VecStim.set(k, inputNoisy[k])
        # print VecStim.get(k)

    VecStim.play(stimuli[0]._ref_amp, neuron.h.dt)
    print('Running for %f ms' % neuron.h.tstop)
    neuron.h.run()

    time = np.array(recordings['time'])
    soma_voltage = np.array(recordings['soma(0.5)'])
    soma_current = np.array(recordings['current'])
    recordings_dir = 'python_recordings'

    import pylab
    pylab.plot(soma_current)
    pylab.show()

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

    if plot_traces:
        import pylab
        pylab.figure()
        pylab.plot(recordings['time'], recordings['soma(0.5)'])
        pylab.xlabel('time (ms)')
        pylab.ylabel('Vm (mV)')
    #import h5Xchange
    #hfpy = h5Xchange
    #print hfpy


def init_simulation():
    """Initialise simulation environment"""

    neuron.h.load_file("stdrun.hoc")
    neuron.h.load_file("import3d.hoc")

    print('Loading constants')
    neuron.h.load_file('constants.hoc')


def main(plot_traces=True):
    """Main"""

    # Import matplotlib to plot the traces
    if plot_traces:
        import matplotlib
        matplotlib.rcParams['path.simplify'] = False

    init_simulation()

    run_step(plot_traces=plot_traces)

    if plot_traces:
        import pylab
        pylab.show()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        main(plot_traces=True)
    elif len(sys.argv) == 2 and sys.argv[1] == '--no-plots':
        main(plot_traces=False)
    else:
        raise Exception(
            "Script only accepts one argument: --no-plots, not %s" %
            str(sys.argv))
