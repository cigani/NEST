import numpy as np
import pylab
import h5py
import sys
sys.path.append('/Users/michaeljaquier/Documents/gewaltig/nest-/lib/python2.7/site-packages')
import nest
from raster import raster
import nest.raster_plot
import seaborn
# reset nest kernel
nest.ResetKernel()
nest.sr("M_WARNING setverbosity")
nest.SetKernelStatus({"local_num_threads":4})

# Parameters
msd = 1000
n_vp = nest.GetKernelStatus('total_num_virtual_procs')
msdrange1 = range(msd,msd+n_vp)
pyrngs = [np.random.RandomState(s) for s in msdrange1]
msdrange2 = range(msd+n_vp+1, msd+1+2*n_vp)
nest.SetKernelStatus({'grng_seed': msd+n_vp,
                      'rng_seeds': msdrange2})

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
nu_ex = eta*v_th/(J_E)
p_rate = 1000.0*nu_ex*C_E
nest.SetKernelStatus({'print_time': True})

#Create Network
nest.SetDefaults('gif_cond_exp', {'C_m': 1.0,
                                  't_ref': 2.0,'E_L': 0.0})
nodes = nest.Create('gif_cond_exp', N_N)
nodes_E=nodes[:N_E]
nodes_I=nodes[N_E:]
node_info = nest.GetStatus(nodes)
local_nodes = [(ni['global_id'], ni['vp'])
               for ni in node_info if ni['local']]
for gid,vp in local_nodes:
    nest.SetStatus([gid], {'V_m': pyrngs[vp].uniform(-v_th, v_th)})
noise = nest.Create('poisson_generator',1,{'rate': p_rate})
spikes = nest.Create('spike_detector',2,[{'label': 'brunel-py-ex'},
                                         {'label': 'bruntel-py-in'}])
spikes_E = spikes[:1]
spikes_I = spikes[1:]

#Connect Network
nest.CopyModel('static_synapse', 'excitatory')
nest.Connect(nodes_E, nodes, {'rule': 'fixed_indegree', 'indegree': C_E},
             {'model': 'excitatory','delay': delay,'weight':
              {'distribution':'uniform','low': 0.5 *J_E,'high': 1.5*J_E}})

#nest.CopyModel('static_synapse', 'inhibitory',
#               {'weight':J_I, 'delay': delay})
#nest.Connect(nodes_E, nodes, {'rule': 'fixed_indegree', 'indegree': C_I},
#             {'model': 'inhibitory','delay': delay,'weight':
#              {'distribution':'uniform','low': 0.5 *-J_I,'high': 1.5*-J_I}})

nest.Connect(noise,nodes, syn_spec='excitatory')

#Record Network
N_rec =50
nest.Connect(nodes_E[:N_rec], spikes_E)
nest.Connect(nodes_I[:N_rec], spikes_I)

#Visualize
#pylab.figure()
#V_E=nest.GetStatus(nodes_E[:N_rec], 'V_m')
#pylab.hist(V_E, bins=10)
#pylab.figure()
#ex_conns = nest.GetConnections(nodes_E[:N_rec],
#                               synapse_model='excitatory')
#w = nest.GetStatus(ex_conns, 'weight')
#pylab.hist(w,bins=100)

#Sim
simtime=90
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