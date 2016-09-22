import numpy as np
import nest
import seaborn
import pylab
import h5py
import os
class Brunnel2000(object):
    """
    Implementation of Spars connected random network.
    """
    g=5.0
    eta=2.0
    delay=1.5
    tau_m=20.0
    V_th=20.0
    N_E=8000
    N_I=2000
    J_E=0.1
    N_Rec=50
    threads=4
    built=False
    connected=False

    def __init__(self):
        """
        Initialize an onject of this class.
        """
        self.name=self.__class__.__name__
        self.data_path=self.name+'/'
        nest.ResetKernel()
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
        print "Writing data to: "+self.data_path
        nest.SetKernelStatus({'data_path': self.data_path})

    def build(self):
        """
        Create all nodes
        """
        if self.built: return
        #self.calibrate()
        nn=self.N_E + self.N_I
        ce=self.N_E/10
        ci=self.N_I/10
        ji=-self.g*self.J_E
        nuex=self.eta*self.V_th/(self.J_E*ce*self.tau_m)
        prate=1000.0*nuex*ce
        nest.SetDefaults('iaf_psc_delta',{'C_m': 1.0, 'tau_m': self.tau_m,
                                          't_ref': 2.0, 'E_L': 0.0, 'V_th':
                                          self.V_th,'V_reset': 10.0})
        nodes=nest.Create('iaf_psc_delta',nn)
        nodesE=nodes[:self.N_E]
        nodesI=nodes[self.N_E:]
        noise=nest.Create('poisson_generator',1,{'rate': prate})
        spikes=nest.Create('spike_detector',2,[{'label': 'ex'},
                                               {'label': 'in'}])
        spikesE=spikes[:1]
        spikesI=spikes[1:]
        self.built=True

    def connect(self):
        """connect all nodes in the model"""
        if self.connected: return
        if not self.built:
            self.build()
        nest.CopyModel('static_synpase_hom_w', 'excitatory',
                       {'weight': J_E, 'delay': delay})
        nest.Connect(nodesE, nodes, {'rule': 'fixed_indegree', 'indegree': ce},
                    'excitatory')
        nest.CopyModel('static_synpase_hom_w', 'inhibitory',
                       {'weight': J_E, 'delay': delay})
        nest.Connect(nodesE, nodes, {'rule': 'fixed_indegree', 'indegree': ce},
                    'inhibitory')
        nest.Connect(nodesE[:N_Rec], spikesE)
        nest.Connect(nodesI[:N_Rec], spikesI)
        self.connected=True

    def run(self,simtime=300):
        """Simulate model for simtime"""
        if not self.connected:
            self.connect()
        nest.SetKernelStatus({'print_time':True})
        nest.Simulate(simtime)
        events=nest.GetStatus(spikes,'n_events')
        rate_ex=events[0]/simtime*1000.0/N_rec
        rate_in=events[1]/simtime*1000.0/N_rec
        print 'Excite Rate: %.2f 1/s' % rate_ex
        print 'Inhib Rate: %.2f 1/s' % rate_in






