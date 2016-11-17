import re

import numpy as np
import glob
import h5py


class Loader:

    """Loads data from hd5f format data structure. One set of files for Testing.
    One set of files for training.
    File needs the following:

    @:param Voltage
    @:param Current
    @:param Time

    Returns two arrays composed of [Voltage, Current, Time] for Train and
    Test"""

    def __init__(self):

        # Path Setting
        self.PATH_FLAT = '/Users/mj/Documents/NEST/'
        self.CELL_PATH = 'L5_TTPC1_cADpyr232_1/'
        self.TRAIN_PATH = '/python_recordings/Data/H5Data/Train/*.hdf5'
        self.TEST_PATH = '/python_recordings/Data/H5Data/Test/*.hdf5'
        self.TRAIN_DATA_PATH = glob.glob(self.PATH_FLAT + self.CELL_PATH +
                                         self.TRAIN_PATH)
        self.TEST_DATA_PATH = glob.glob(self.PATH_FLAT + self.CELL_PATH +
                                        self.TEST_PATH)

        try:
            assert self.TRAIN_DATA_PATH
        except:
            raise Exception("Training data path is not set")
        try:
            assert self.TEST_DATA_PATH
        except:
            raise Exception("Test data path is not set")

        for n, k in zip(self.TEST_DATA_PATH, self.TRAIN_DATA_PATH):
            trainPattern = re.search('(\d+)\.hdf5$', k)
            testPattern = re.search('(\d+)\.hdf5$', n)
            try:
                assert testPattern
            except:
                raise Exception("Test data is not formatted in hdf5")
            try:
                assert trainPattern
            except:
                raise Exception("Training data is not formatted in hdf5")

        # Initialize Variables
        self.V_test = []
        self.V_train = []
        self.I_test = []
        self.I_train = []
        self.T_test = []
        self.T_train = []
        self.h5datatest = []
        self.h5datatrain = []
        self.Train = []
        self.Test = []

    def dataload(self):

        """ Returns two arrays: [0]: Train and [1]: Test composed of:
        [Voltage, Current, Time] nested arrays"""

        for n, k in enumerate(self.TRAIN_DATA_PATH):
            with h5py.File(k, 'r') as f:
                np.transpose(self.I_train.append(f['current'][()]))
                np.transpose(self.V_train.append(f['voltage'][()]))
                np.transpose(self.T_train.append(f['time'][()]))

        for n, k in enumerate(self.TEST_DATA_PATH):
            with h5py.File(k, 'r') as f:
                np.transpose(self.I_test.append(f['current'][()]))
                np.transpose(self.V_test.append(f['voltage'][()]))
                np.transpose(self.T_test.append(f['time'][()]))

        self.Train = [self.V_train, self.I_train, self.T_train]
        self.Test = [self.V_test, self.I_test, self.T_test]

        self.testcoverage()

        return self.Train, self.Test

    def testcoverage(self):

        """ Tests to ensure that our data is correctly formatted. """

        assert (np.size(self.V_test) == np.size(self.I_test))
        assert (np.size(self.V_train) == np.size(self.I_train))
        assert (np.size(self.Test) == np.size(
            self.V_test + self.I_test + self.T_test))
        assert (np.size(self.Train) == np.size(
            self.V_train + self.T_train + self.I_train)
        )
# Loader().dataload()
