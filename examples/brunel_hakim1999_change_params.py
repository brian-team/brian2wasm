from brian2 import *
import brian2wasm
set_device('wasm_standalone', directory='basic_example_change')
prefs.devices.wasm_standalone.emsdk_directory = '/home/marcel/programming/emsdk'
N = 5000
Vr = 10*mV
theta = 20*mV
tau = 20*ms
delta = 2*ms
taurefr = 2*ms
duration = .1*second
C = 1000
sparseness = float(C)/N
J = .1*mV

eqs = """
dV/dt = (-V+muext + sigmaext * sqrt(tau) * xi)/tau : volt
muext : volt (constant, shared)
sigmaext : volt (constant, shared)
"""

group = NeuronGroup(N, eqs, threshold='V>theta',
                    reset='V=Vr', refractory=taurefr, method='euler')
group.V = Vr
conn = Synapses(group, group, on_pre='V += -J', delay=delta)
conn.connect(p=sparseness)
M = SpikeMonitor(group)
LFP = PopulationRateMonitor(group)

run(duration, report='text', report_period=0.1*second)
