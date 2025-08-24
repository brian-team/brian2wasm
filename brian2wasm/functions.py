'''
Convenience functions that inject JavaScript code into the generated code.
'''
from brian2.core.functions import implementation
from brian2.units.fundamentalunits import check_units
from brian2.units import second


@implementation('cpp', '''
double send_spike(int i, double t) {
    EM_ASM({
        postMessage({ type: 'spike', index: $0, time: $1});
    }, i, t);
    return 0.0;  // dummy return
}
''')
@check_units(i=1, t=second, result=1)
def send_spike(i, t):
    """
        Send a spike message to JavaScript.

        This function injects JavaScript code via Emscripten's ``EM_ASM`` to send a spike event
        message to the JavaScript environment, typically for visualization or processing in a
        browser-based WebAssembly simulation.

        Parameters
        ----------
        i : int
            The index of the neuron or synapse emitting the spike.
        t : Quantity
            The time of the spike event, with units of seconds.

        Returns
        -------
        float
            A dummy return value of 0.0, as the function's primary effect is the JavaScript
            message dispatch.

        Notes
        -----
        This function is implemented in C++ using the ``@implementation`` decorator, which
        defines a JavaScript ``postMessage`` call to send a message of type 'spike' with the
        neuron index and time. The Python function body is a no-op (``pass``), as the actual
        implementation is handled in C++ and executed in the WebAssembly environment.
    """
    pass