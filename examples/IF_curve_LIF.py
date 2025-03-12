from brian2 import *
import brian2wasm
set_device('wasm_standalone', directory='IF_curve_LIF')

n = 1000
duration = 1*second
tau = 10*ms
eqs = '''
dv/dt = (v0 - v) / tau : volt (unless refractory)
v0 : volt
'''
group = NeuronGroup(n, eqs, threshold='v > 10*mV', reset='v = 0*mV',
                    refractory=5*ms, method='exact')
group.v = 0*mV
group.v0 = '20*mV * i / (n-1)'

monitor = SpikeMonitor(group)

run(duration)

# source : https://brian2.readthedocs.io/en/stable/examples/IF_curve_LIF.html
