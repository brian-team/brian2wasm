#source: https://brian2.readthedocs.io/en/stable/examples/non_reliability.html#example-non-reliability
from brian2 import *
import brian2wasm
set_device('wasm_standalone', directory='non_reliability')

N = 24
tau = 20*ms
sigma = .015
eqs_neurons = '''
dx/dt = (1.1 - x) / tau + sigma * (2 / tau)**.5 * xi : 1 (unless refractory)
'''
neurons = NeuronGroup(N, model=eqs_neurons, threshold='x > 1', reset='x = 0',
                      refractory=5*ms, method='euler')


spikes = SpikeMonitor(neurons)
run(500*ms,  report='text', report_period=0.1*second)
