import numpy as np
# import h5py
import glob


# Import Files


dataPath = glob.glob('./data/*.dat')
assert dataPath is not None

expData = [[[], []] for x in xrange(np.size(dataPath))]


def expLoad(dataPath=dataPath, cols=1,
            ExpStart=7000, ExpStop=280000,
            iStart=0, iE=0.6):
    expData = [[[], []] for x in xrange(np.size(dataPath))]
    for i, k in enumerate(dataPath):
        expFile = np.loadtxt(k, usecols=[cols])

        if iStart is not 0:  # TODO size.V != size.I
            expData[i] = np.array([expFile,
                                   np.append(
                                       np.zeros(iStart),
                                       np.ones(np.size(
                                           expFile[iE:ExpStop]))*iE)])
        else:
            expData[i] = np.array([
                expFile[ExpStart:ExpStop],
                np.ones(np.size(expFile[ExpStart:ExpStop]))*0.6])
    return expData, dataPath


# dataArray = expLoad()[0]
# data2 = expLoad()[1]


# V = [dataArray[n][0] for n, k in enumerate(dataPath)]
# I = [dataArray[n][1] for n, k in enumerate(dataPath)]
# V_units = 10**-3
# I_units = 10**-9
