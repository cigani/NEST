
import nest
import nest.voltage_trace
import os
import pylab


# Membrane Parameters:
#     C_m        double - Capacity of the membrane in pF
#     t_ref      double - Duration of refractory period in ms.
#     V_reset    double - Reset value after a spike in mV.
#     E_L        double - Leak reversal potential in mV.
#     g_L        double - Leak conductance in nS.
#     I_e        double - Constant external input current in pA.
#   Spike adaptation and firing intensity parameters:
#     q_stc      vector of double - Values added to spike-triggered currents (stc)
#                                   after each spike emission in nA.
#     tau_stc    vector of double - Time constants of stc variables in ms.
#     q_sfa      vector of double - Values added to spike-frequency adaptation
#                                   (sfa) after each spike emission in mV.
#     tau_sfa    vector of double - Time constants of sfa variables in ms.
#     Delta_V    double - Stochasticity level in mV.
#     lambda_0   double - Stochastic intensity at firing threshold V_T in 1/s.
#     V_T_star   double - Base threshold in mV
#   Synaptic parameters
#     tau_syn_ex double - Time constant of the excitatory synaptic current in ms.
#     tau_syn_in double - Time constant of the inhibitory synaptic current in ms.

nest.ResetKernel()


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
        self.name = self.__class__.__name__
        self.data_path = self.name + "/"
        self.N_E = 8000
        self.N_I = 2000
        self.threads = 2

        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
        print("Writing data to: {0}".format(self.data_path))
        nest.ResetKernel()
        nest.SetKernelStatus({"data_path": self.data_path})

    def calibrate(self):
        """
        Compute all parameter dependent variables of the
        model.
        """
        print(nest.Models())
        nest.SetKernelStatus({"print_time": True,
                              "local_num_threads": self.threads})
        # nest.SetDefaults("gif_cond_exp",
        #                  {"C_m": self.C_m ,
        #                   "tau_m": self.tau_m,
        #                   "t_ref": self.Tref,
        #                   "E_L": self.El,
        #                   "V_reset": self.Vr,
        #                   "g_L": self.gl,
        #                   })

    def build(self):
        """
        Create all nodes, used in the model.
        """
        if self.built:
            return
        self.calibrate()
        neuron = nest.Create('gif_psc_exp')
        self.nodes = nest.Create("iaf_psc_delta", self.N_neurons)
        self.noise = nest.Create("poisson_generator", 1, {"rate": self.p_rate})
        self.spikes = nest.Create("spike_detector", 2,
                                  [{"label": "brunel-py-ex"},
                                   {"label": "brunel-py-in"}])
        self.nodes_E = self.nodes[:self.N_E]
        self.nodes_I = self.nodes[self.N_E:]
        self.spikes_E = self.spikes[:1]
        self.spikes_I = self.spikes[1:]
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

        sine = nest.Create('ac_generator', 1,
                           {'amplitude': 100.0,
                            'frequency': 2.0})

        noise = nest.Create('poisson_generator', 2,
                            [{'rate': 70000.0},
                             {'rate': 20000.0}])

        voltmeter = nest.Create('voltmeter', 1,
                                {'withgid': True})

        nest.Connect(sine, neuron)
        nest.Connect(voltmeter, neuron)
        nest.Connect(noise[:1], neuron, syn_spec={'weight': 1.0, 'delay': 1.0})
        nest.Connect(noise[1:], neuron,
                     syn_spec={'weight': -1.0, 'delay': 1.0})

        nest.Simulate(1000.0)

        nest.voltage_trace.from_device(voltmeter)

        self.connected = True

    def run(self, simtime=300.):
        """
        Simulate the model for simtime milliseconds and print the
        firing rates of the network during htis period.
        """
        if not self.connected:
            self.connect()
        nest.Simulate(simtime)
        events = nest.GetStatus(self.spikes, "n_events")
        self.rate_ex = events[0] / simtime * 1000.0 / self.N_rec
        print("Excitatory rate   : %.2f Hz" % self.rate_ex)
        self.rate_in = events[1] / simtime * 1000.0 / self.N_rec
        print("Inhibitory rate   : %.2f Hz" % self.rate_in)
        nest.raster_plot.from_device(self.spikes_E, hist=True)
        pylab.show()



NestModel().build()