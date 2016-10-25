import os
import numpy as np
import glob
# Run simulator for X loops. Move each data iteration to /Data


DATA_PATH = [glob.glob('./python_recordings/soma_voltage_step*'),
             glob.glob('./python_recordings/soma_current_step*')]
RECORDING_DIR = 'python_recordings/Data'
PATH_FLAT = '/Users/mj/Documents/NEST/'
EXPERIMENT_PATH = '/L5_TTPC1_cADpyr232_1/python_recordings/Data/*.dat'
H5PY_PATH = glob.glob(PATH_FLAT+EXPERIMENT_PATH)

assert DATA_PATH is not None


def looper(n=2):
    for i in xrange(n):
        os.system("sh run_py.sh --no-plots")
        stackedData = loader()
        for k in xrange(len(stackedData)):
            dataFile = os.path.join(
                RECORDING_DIR, 'dataSet_%d_run.%d.dat' % (k, i))
            np.savetxt(
                dataFile, stackedData[k])
            print('Data saved to %s' % dataFile)


def loader():
    voltagePath = DATA_PATH[0]
    currentPath = DATA_PATH[1]
    volt = []
    amp = []
    stackedData = []
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
    for i in xrange(len(amp)):
        temp = (np.transpose(np.vstack(([volt[i]], [amp[i]]))))
        stackedData.append(temp)
    return stackedData

loop = looper()

# Not the cleanest implementation
print('Running .Dat to H5 Format exchange')
os.system("python h5Xchange.py")
