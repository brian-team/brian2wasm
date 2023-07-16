from brian2 import *
import brian2wasm
set_device('wasm_standalone', directory='brunel_hakim1999',
           html_content={"h1": "Fast Global Oscillations in Networks of Integrate-and-Fire Neurons with Low Firing Rates",
                         "h2": "Brunel & Hakim (1999)"})
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

group = NeuronGroup(N, eqs, threshold='V>theta',
                    reset='V=Vr', refractory=taurefr, method='euler')
group.V = Vr
conn = Synapses(group, group, on_pre='V += -J', delay=delta)
conn.connect(p=sparseness)
M = SpikeMonitor(group)
LFP = PopulationRateMonitor(group)

run(duration, report='text', report_period=0.1*second)
