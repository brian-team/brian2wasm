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
    '''
    Send a spike message to JavaScript
    '''
    pass