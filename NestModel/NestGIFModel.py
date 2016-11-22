import nest
import nest.voltage_trace
import os
import numpy as np
import nest.raster_plot
import matplotlib.pyplot as plt


class NestModel:
    def __init__(self):

        self.name = self.__class__.__name__
        self.built = False
        self.connected = False

        # Model Fit Parameters
        self.tau_m = 19.779
        self.R = 36.655
        self.C_m = 0.540
        self.gl = 0.027281
        self.El = -66.226
        self.Tref = 4.000
        self.Vr = -55.984
        self.Vt_star = -63.897
        self.DV = 1.869
        self.eta = [-0.20546141, 0.21799896, 0.19400531]  # (stc)
        self.gamma = [7.54696118, 1.28987318, 1.3545157]  # (sfa)
        self.q_stc = []
        self.q_sfa = []
        self.eta_tau = [4.5049772097108223, 13.281196383992915,
                        179.30359998539814]
        self.gamma_tau = [10.0, 50.0, 250.0]
        self.neuron_params = {}

        # NEST Model Parameters
        self.neurons = 100
        self.p_ex = 0.3
        self.w_ex = 30.0
        self.threads = 2
        self.poisson_neurons = 50  # size of Poisson group
        self.rate_noise = 10.0  # firing rate of Poisson neurons (Hz)
        self.w_noise = 20.0  # synaptic weights from Poisson to population
        self.dt = 0.1
        self.simtime = 2000

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

        # q_eta_giftoolbox = q_eta_NEST * (1 - exp(-t_ref / tau_eta))

        for eta_index, eta in enumerate(self.eta):
            q_eta_temp = eta / (
                1 - np.exp(-self.Tref / self.eta_tau[eta_index]))
            self.q_stc.append(q_eta_temp)

        for gamma_index, gamma in enumerate(self.gamma):
            q_gamma_temp = gamma / (
                1 - np.exp(-self.Tref / self.gamma_tau[gamma_index]))
            self.q_sfa.append(q_gamma_temp)

        self.neuron_params = {"C_m": self.C_m,
                              "t_ref": self.Tref,
                              "E_L": self.El,
                              "V_reset": self.Vr,
                              "g_L": self.gl,
                              "lambda_0": 1.0,
                              "q_stc": self.q_stc,
                              "q_sfa": self.q_sfa,
                              "tau_stc": self.eta_tau,
                              "tau_sfa": self.gamma_tau
                              }

    def calibrate(self):
        """
        Compute all parameter dependent variables of the
        model.
        """
        self.set_model_params()

        nest.SetKernelStatus({"print_time": True,
                              "local_num_threads": self.threads,
                              "resolution": self.dt})

        self.population = nest.Create("gif_psc_exp", self.neurons,
                                      params=self.neuron_params)

        self.noise = nest.Create("poisson_generator", self.poisson_neurons,
                                 params={'rate': self.rate_noise})

        self.spike_det = nest.Create("spike_detector")

    def build(self):
        """
        Create all nodes, used in the model.
        """
        if self.built:
            return
        self.calibrate()
        nest.Connect(self.population, self.population,
                     {'rule': 'pairwise_bernoulli',
                      'p': self.p_ex},
                     syn_spec={"weight": self.w_ex})

        nest.Connect(self.noise, self.population, 'all_to_all',
                     syn_spec={"weight": self.w_noise})

        nest.Connect(self.population, self.spike_det)

        self.built = True

    def connect(self):
        """
        Connect all nodes in the model.
        """
        if self.connected:
            return
        if not self.built:
            self.build()

        neuron = nest.Create('gif_psc_exp')

        nest.Simulate(1000.0)

        self.connected = True

    def run(self):
        """
        Simulate the model for simtime milliseconds and print the
        firing rates of the network during htis period.
        """
        if not self.connected:
            self.connect()
        nest.Simulate(self.simtime)

        nest.raster_plot.from_device(self.spike_det, hist=True)
        plt.title('Population dynamics')
        plt.show()


NestModel().run()
