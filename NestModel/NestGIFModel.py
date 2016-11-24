import nest
import nest.voltage_trace
import os
import numpy as np
import nest.raster_plot
import matplotlib.pyplot as plt
import cPickle as pickle


class NestModel:
    def __init__(self):

        self.name = self.__class__.__name__
        self.built = False
        self.connected = False

        # Model Fit Parameters
        self.neuron_params = {}

        # NEST Model Parameters
        self.neurons = 10
        self.p_ex = 0.3
        self.w_ex = 30.0
        self.threads = 1
        self.poisson_neurons = 1  # size of Poisson group
        self.rate_noise = 10.0  # firing rate of Poisson neurons (Hz)
        self.w_noise = 20.0  # synaptic weights from Poisson to population
        self.dt = 0.1
        self.simtime = 20000

        # Misc
        self.name = self.__class__.__name__
        self.data_path = self.name + "/"
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
        print("Writing data to: {0}".format(self.data_path))
        nest.ResetKernel()
        nest.SetKernelStatus({"data_path": self.data_path})
        nest.SetKernelStatus({"resolution": self.dt})

    def set_model_params(self):
        self.neuron_params = pickle.load(open(
            "/Users/mj/Documents/NEST/gif_model/NestModel/param/save.p", "rb"))
        print self.neuron_params

    def calibrate(self):
        """
        Compute all parameter dependent variables of the
        model.
        """
        self.set_model_params()

        nest.SetKernelStatus({"print_time": True,
                              "local_num_threads": self.threads,
                              "resolution": self.dt})

    def build(self):
        """
        Create all nodes, used in the model.
        """
        if self.built:
            return
        self.calibrate()

        self.population = nest.Create("gif_psc_exp", self.neurons,
                                      params=self.neuron_params)
        self.noise = nest.Create("poisson_generator", self.poisson_neurons,
                                 params={'rate': self.rate_noise})
        self.spike_det = nest.Create("spike_detector")
        self.voltmeter = nest.Create("voltmeter")

        self.built = True

    def connect(self):
        """
        Connect all nodes in the model.
        """
        if self.connected:
            return
        if not self.built:
            self.build()

        nest.Connect(self.population, self.population,
                     {'rule': 'pairwise_bernoulli',
                      'p': self.p_ex},
                     syn_spec={"weight": self.w_ex})

        nest.Connect(self.noise, self.population, 'all_to_all',
                     syn_spec={"weight": self.w_noise})

        nest.Connect(self.population, self.spike_det)
        nest.Connect(self.voltmeter, self.population)
        nest.SetStatus(self.voltmeter, [{"withgid": True}])

        self.connected = True

    def run(self):
        """
        Simulate the model for simtime milliseconds and print the
        firing rates of the network during htis period.
        """
        if not self.connected:
            self.connect()
        nest.Simulate(self.simtime)
        nest.voltage_trace.from_device(self.voltmeter)
        nest.raster_plot.from_device(self.spike_det, hist=True)
        plt.title('Population dynamics')
        plt.show()
        print(self.neuron_params)

NestModel().run()
