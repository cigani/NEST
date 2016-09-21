import numpy as np
import pylab
import h5py
import nest
from raster import raster
import nest.raster_plot
import seaborn
# reset nest kernel
nest.ResetKernel()
nest.sr("M_WARNING setverbosity")
nest.SetKernelStatus({"local_num_threads": 1})

# Parameters
i_e = 327.0
n = 40
m = 10
sd =2
p = 0.2
g = 5.0
eta = 2.0
delay = 1.5
tau_m = 20.0
v_th = 20.0
N_E = 8000
N_I = 2000
N_N = N_E + N_I
C_E = N_E/10
C_I = N_I/10
J_E = 0.1
J_I = -g*J_E
nu_ex = eta*v_th/(J_E*C_E*tau_m)
p_rate = 1000.0*nu_ex*C_E
nest.SetKernelStatus({'print_time': True})

#Create Network
nest.SetDefaults('iaf_psc_delta', {'C_m': 1.0, 'tau_m': tau_m, 't_ref': 2.0,
                                   'E_L': 0.0, 'V_th': v_th, 'V_reset': 10.0})
nodes = nest.Create('iaf_psc_delta', N_N)
nodes_E=nodes[:N_E]
nodes_I=nodes[N_E:]
noise = nest.Create('poisson_generator',1,{'rate': p_rate})
spikes = nest.Create('spike_detector',2,[{'label': 'brunel-py-ex'},
                                         {'label': 'bruntel-py-in'}])
spikes_E = spikes[:1]
spikes_I = spikes[1:]

#Connect Network
nest.CopyModel('static_synapse_hom_w', 'excitatory',
               {'weight':J_E, 'delay': delay})
nest.Connect(nodes_E, nodes,
             {'rule': 'fixed_indegree', 'indegree': C_E}, 'excitatory')
nest.CopyModel('static_synapse_hom_w', 'inhibitory',
               {'weight':J_I, 'delay': delay})
nest.Connect(nodes_E, nodes,
             {'rule': 'fixed_indegree', 'indegree': C_I}, 'inhibitory')
nest.Connect(noise,nodes, syn_spec='excitatory')

#Record Network
N_rec =50
nest.Connect(nodes_E[:N_rec], spikes_E)
nest.Connect(nodes_I[:N_rec], spikes_I)

#Sim
simtime=300
nest.Simulate(simtime)
events = nest.GetStatus(spikes,'n_events')
rate_ex = events[0]/simtime*1000.0/N_rec
print 'Excitatory Rate: %.2f 1/s' % rate_ex
rate_in = events[1]/simtime*1000.0/N_rec
print 'Inhibitory Rate: %.2f 1/s' %rate_in

#Plot
nest.raster_plot.from_device(spikes_E, hist=True)
pylab.show()
'''
# load network
#conn_dict = {'rule': 'pairwise_bernoulli', 'p': p}
nest.SetKernelStatus({'prin_time': True})
A = nest.Create("iaf_cond_exp",n,params=[{"I_e": i_e}])
B = nest.Create("iaf_cond_exp",m,params=[{"I_e": i_e}])
noise = nest.Create("poisson_generator", 2)
nest.SetStatus(noise, [{"rate": 80000.0}, {"rate": 15000.0}])
nest.Connect(noise[:1], A, syn_spec={'weight': 1.0, 'delay': 1.0})
nest.Connect(noise[1:], A, syn_spec={'weight': -1.0, 'delay': 1.0})
#nest.Connect(A,B,conn_dict)
nest.Connect(A,B)

# create spike detector
rec = nest.Create('spike_detector', sd)
nest.Connect(B, rec)
#nest.SetStatus(A, "I_e", 376.0)
# simulate
nest.Simulate(100.0)

# get sendee
sendee = nest.GetStatus(rec, 'events')[0]['senders']
times = nest.GetStatus(rec,'events')[0]['times']

# create raster plot
r = zip(sendee,times)
print r
if len(r) is not 0:
    raster(r, cell_count=np.max(sendee))
    pylab.show()

    '''
