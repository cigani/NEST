import numpy as np
import glob
# import loading as l

import sys
PATH_FLAT = '/Users/mj/Documents/NEST/'
sys.path.append(PATH_FLAT+'/GIFFittingToolbox/src')

EXPERIMENT_PATH = '/L5_TTPC1_cADpyr232_1/python_recordings/Data/*.dat'

DATA_PATH = glob.glob(PATH_FLAT+EXPERIMENT_PATH)
volt = []
amp = []
for i, k in enumerate(DATA_PATH):
    tempV = np.loadtxt(k, usecols=[0])
    tempA = np.loadtxt(k, usecols=[1])
    volt.append([tempV])
    amp.append([tempA])
print volt[0]
print volt[2]
