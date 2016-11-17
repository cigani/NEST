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

        if iStart is not 0:  # TODO Needs to be tested
            expData[i] = np.array([expFile[ExpStart:ExpStop],
                                   np.append(
                                       np.zeros(iStart),
                                       np.ones(np.size(
                                           expFile[iStart:ExpStop]))*iE)])
        else:
            expData[i] = np.array([
                expFile[ExpStart:ExpStop],
                np.ones(np.size(expFile[ExpStart:ExpStop]))*0.6])
    return expData, dataPath

