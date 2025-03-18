# https://brian2.readthedocs.io/en/stable/examples/advanced.Ornstein_Uhlenbeck.html
from brian2 import *
import brian2wasm
set_device('wasm_standalone', directory='ornstein_uhlenbeck')

N = NeuronGroup(
    1,
    """
    tau : second
    sigma : 1
    dy/dt = -y/tau + sqrt(2*sigma**2/tau)*xi : 1
    """,
    method="euler"
)

N.tau = 0.5 * second
N.sigma = 0.1
N.y = 1

M = StateMonitor(N, "y", record=True)

run(10 * second)
