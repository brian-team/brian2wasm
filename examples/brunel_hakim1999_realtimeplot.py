from brian2 import *
import brian2wasm
set_device('wasm_standalone', directory='brunel_hakim1999_realtime')

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
muext = 25*mV
sigmaext = 1*mV

eqs = """
dV/dt = (-V+muext + sigmaext * sqrt(tau) * xi)/tau : volt
"""

from brian2wasm.functions import send_spike
group = NeuronGroup(N, eqs, threshold='V > theta',
                    reset='V = Vr; dummy = send_spike(i, t)',
                    refractory=2*ms, method='euler')
group.V = Vr
conn = Synapses(group, group, on_pre='V += -J', delay=delta)
conn.connect(p=sparseness)
M = SpikeMonitor(group[:5000])
LFP = PopulationRateMonitor(group)

run(duration, report='text', report_period=0.1*second)
