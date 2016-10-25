import numpy as np
import glob
import h5py
import time


DATA_PATH = [glob.glob('./python_recordings/soma_voltage_step*'),
             glob.glob('./python_recordings/soma_current_step*')]
RECORDING_DIR = 'python_recordings/Data'
PATH_FLAT = '/Users/mj/Documents/NEST/'
EXPERIMENT_PATH = '/L5_TTPC1_cADpyr232_1/python_recordings/Data/'
DATA_PATH = glob.glob(PATH_FLAT+EXPERIMENT_PATH+'/*.dat')


PATH_FLAT = '/Users/mj/Documents/NEST/'
EXPERIMENT_PATH = '/L5_TTPC1_cADpyr232_1/python_recordings/Data/*.dat'
DATA_PATH = glob.glob(PATH_FLAT+EXPERIMENT_PATH)
H5_PATH = PATH_FLAT+EXPERIMENT_PATH+'/H5Data/'
V = []
I = []
for i, k in enumerate(DATA_PATH):

    tempV = np.loadtxt(k, usecols=[0])
    tempA = np.loadtxt(k, usecols=[1])
    V.append(tempV)
    I.append(tempA)

timestr = time.strftime("%H%M%S")
data = h5py.File(
    'python_recordings/Data/H5Data/dataFile_{}.hdf5'.format(timestr), 'w')
volt_dset = data.create_dataset('voltage', data=V, compression='gzip')
amp_dset = data.create_dataset('current', data=I, compression='gzip')
data.close()

mega = h5py.File('python_recordings/Data/H5Data/dataFile_{}.hdf5'.
                 format(timestr), 'r')
for n, k in enumerate(zip(V, mega['voltage'])):
    assert(all(V[n] == mega['voltage'][n]))
for n, k in enumerate(zip(I, mega['current'])):
    assert(all(I[n] == mega['current'][n]))
mega.close()
