import os
import numpy as np
import glob
# Run simulator for X loops. Move each data iteration to /Data

dataPath = []
dataPath = [glob.glob('./python_recordings/soma_voltage_step*'),
            glob.glob('./python_recordings/soma_current_step*')]
recordings_dir = 'python_recordings/Data'
assert dataPath is not None


def looper(n=10):
    for i in xrange(n):
        os.system("sh run_py.sh --no-plots")
        stackedData = loader()
        for k in xrange(len(stackedData)):
            dataFile = os.path.join(
                recordings_dir, 'dataSet%drun.%d' % (i, k))
            np.savetxt(
                dataFile+"run.{}".format(k), stackedData[k])
            print('Data saved to %s' % dataFile)


def loader():
    voltagePath = dataPath[0]
    currentPath = dataPath[1]
    volt = []
    amp = []
    for i, k in enumerate(voltagePath):
        voltageData = np.loadtxt(k, usecols=[1])
        volt.append(voltageData)
    for i, k in enumerate(currentPath):
        currentData = np.loadtxt(k)
        v = np.append(np.array(np.ones(currentData[0][1]*10) *
                               currentData[1][0]), np.array(np.ones(
                                   (currentData[0][2]-currentData[0][1])*10) *
                                   (currentData[0][0] -
                                    currentData[1][0])))
        vv = np.append(v, np.ones(np.size(volt[i])-np.size(v)) *
                       currentData[1][0])
        amp.append(vv)
        stackedData = []
    for i in xrange(len(amp)):
        temp = (np.transpose(np.vstack(([volt[i]], [amp[i]]))))
        stackedData.append(temp)
    return stackedData

loop = looper()
