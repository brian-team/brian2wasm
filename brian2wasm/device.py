"""
Module implementing the WASM/JS "standalone" device.
"""
import os
import shutil
import subprocess
import time

import numpy as np

from brian2.units import second
from brian2.core.namespace import get_local_namespace
from brian2.synapses import Synapses
from brian2.utils.logger import get_logger
from brian2.utils.filetools import in_directory
from brian2.devices import all_devices
from brian2.devices.cpp_standalone.device import CPPStandaloneDevice

__all__ = []

logger = get_logger(__name__)


class WASMStandaloneDevice(CPPStandaloneDevice):
    """
    The `Device` used for WASM simulations.
    """
    def __init__(self, *args, **kwds):
        super(WASMStandaloneDevice, self).__init__(*args, **kwds)

    def activate(self, *args, **kwargs):
        super(WASMStandaloneDevice, self).activate(*args, **kwargs)
        # Overwrite the templater to prefer our templates
        self.code_object_class().templater = self.code_object_class().templater.derive('brian2wasm')

    def generate_makefile(self, writer, compiler, compiler_flags, linker_flags, nb_threads, debug):
        compiler_flags = '-Ibrianlib/randomkit'
        linker_flags = '-Lbrianlib/randomkit'
        preloads = ' '.join(f'--preload-file static_arrays/{static_array}'
                            for static_array in sorted(self.static_arrays.keys()))
        rm_cmd = 'rm $(OBJS) $(PROGRAM) $(DEPS)'
        if debug:
            compiler_debug_flags = '-g -DDEBUG'
            linker_debug_flags = '-g'
        else:
            compiler_debug_flags = ''
            linker_debug_flags = ''
        
        source_files = ' '.join(sorted(writer.source_files))
        source_files = source_files.replace('brianlib/randomkit/randomkit.c', 
                                            'brianlib/randomkit/randomkit.cpp')
        preamble_file = os.path.join(os.path.dirname(__file__), 'templates', 'pre.js')
        makefile_tmp = self.code_object_class().templater.makefile(None, None,
            source_files=source_files,
            header_files=' '.join(sorted(writer.header_files)),
            compiler_flags=compiler_flags,
            compiler_debug_flags=compiler_debug_flags,
            linker_debug_flags=linker_debug_flags,
            linker_flags=linker_flags,
            preloads=preloads,
            preamble_file=preamble_file,
            rm_cmd=rm_cmd)
        writer.write('makefile', makefile_tmp)
        

    def copy_source_files(self, writer, directory):
        super(WASMStandaloneDevice, self).copy_source_files(writer, directory)
        # Rename randomkit.c so that emcc compiles it to wasm
        os.rename(os.path.join(directory, 'brianlib', 'randomkit', 'randomkit.c'),
                  os.path.join(directory, 'brianlib', 'randomkit', 'randomkit.cpp'))
        shutil.copy(os.path.join(os.path.dirname(__file__), 'templates', 'worker.js'), directory)
        shutil.copy(os.path.join(os.path.dirname(__file__), 'templates', 'brian.js'), directory)
        shutil.copy(self.build_options['html_file'], directory)

    def get_report_func(self, report):
        # Code for a progress reporting function
        standard_code = """
        std::string _format_time(float time_in_s)
        {
            float divisors[] = {24*60*60, 60*60, 60, 1};
            char letters[] = {'d', 'h', 'm', 's'};
            float remaining = time_in_s;
            std::string text = "";
            int time_to_represent;
            for (int i =0; i < sizeof(divisors)/sizeof(float); i++)
            {
                time_to_represent = int(remaining / divisors[i]);
                remaining -= time_to_represent * divisors[i];
                if (time_to_represent > 0 || text.length())
                {
                    if(text.length() > 0)
                    {
                        text += " ";
                    }
                    text += (std::to_string(time_to_represent)+letters[i]);
                }
            }
            //less than one second
            if(text.length() == 0) 
            {
                text = "< 1s";
            }
            return text;
        }
        void report_progress(const double elapsed, const double completed, const double start, const double duration)
        {
            // Send progress to javascript
            EM_ASM({
            (postMessage({ type: 'progress', elapsed: $0, completed: $1, start: $2, duration: $3}));
            }, elapsed, completed, start, duration);
            if (completed == 0.0)
            {
                %STREAMNAME% << "Starting simulation at t=" << start << " s for duration " << duration << " s";
            } else
            {
                %STREAMNAME% << completed*duration << " s (" << (int)(completed*100.) << "%) simulated in " << _format_time(elapsed);
                if (completed < 1.0)
                {
                    const int remaining = (int)((1-completed)/completed*elapsed+0.5);
                    %STREAMNAME% << ", estimated " << _format_time(remaining) << " remaining.";
                }
            }

            %STREAMNAME% << std::endl << std::flush;
        }
        """
        if report is None:
            report_func = ''
        elif report == 'text' or report == 'stdout':
            report_func = standard_code.replace('%STREAMNAME%', 'std::cout')
        elif report == 'stderr':
            report_func = standard_code.replace('%STREAMNAME%', 'std::cerr')
        elif isinstance(report, str):
            report_func = """
            void report_progress(const double elapsed, const double completed, const double start, const double duration)
            {
            %REPORT%
            }
            """.replace('%REPORT%', report)
        else:
            raise TypeError("report argument has to be either 'text', "
                            "'stdout', 'stderr', or the code for a report "
                            "function")
        return report_func

    def network_run(self, net, duration, report=None, report_period=10*second,
                    namespace=None, profile=None, level=0, **kwds):
        self.networks.add(net)
        if kwds:
            logger.warn(('Unsupported keyword argument(s) provided for run: '
                         '%s') % ', '.join(kwds.keys()))
        # We store this as an instance variable for later access by the
        # `code_object` method
        self.enable_profiling = profile

        # Allow setting `profile` in the `set_device` call (used e.g. in brian2cuda
        # SpeedTest configurations)
        if profile is None:
            self.enable_profiling = self.build_options.get('profile', False)

        all_objects = net.sorted_objects
        net._clocks = {obj.clock for obj in all_objects}
        t_end = net.t+duration
        for clock in net._clocks:
            clock.set_interval(net.t, t_end)

        # Get the local namespace
        if namespace is None:
            namespace = get_local_namespace(level=level+2)

        net.before_run(namespace)
        self.synapses |= {s for s in net.objects
                          if isinstance(s, Synapses)}
        self.clocks.update(net._clocks)
        net.t_ = float(t_end)

        # TODO: remove this horrible hack
        for clock in self.clocks:
            if clock.name=='clock':
                clock._name = '_clock'
            
        # Extract all the CodeObjects
        # Note that since we ran the Network object, these CodeObjects will be sorted into the right
        # running order, assuming that there is only one clock
        code_objects = []
        for obj in all_objects:
            if obj.active:
                for codeobj in obj._code_objects:
                    code_objects.append((obj.clock, codeobj))

        report_func = self.get_report_func(report)

        if report_func != '':
            if self.report_func != '' and report_func != self.report_func:
                raise NotImplementedError("The C++ standalone device does not "
                                          "support multiple report functions, "
                                          "each run has to use the same (or "
                                          "none).")
            self.report_func = report_func

        if report_func:
            report_call = 'report_progress'
        else:
            report_call = 'NULL'

        # Generate the updaters
        run_lines = [f'{net.name}.clear();']
        all_clocks = set()
        for clock, codeobj in code_objects:
            run_lines.append(f'{net.name}.add(&{clock.name}, _run_{codeobj.name});')
            all_clocks.add(clock)

        # Under some rare circumstances (e.g. a NeuronGroup only defining a
        # subexpression that is used by other groups (via linking, or recorded
        # by a StateMonitor) *and* not calculating anything itself *and* using a
        # different clock than all other objects) a clock that is not used by
        # any code object should nevertheless advance during the run. We include
        # such clocks without a code function in the network.
        for clock in net._clocks:
            if clock not in all_clocks:
                run_lines.append(f'{net.name}.add(&{clock.name}, NULL);')

        run_lines.extend(self.code_lines['before_network_run'])
        if not self.run_args_applied:
            run_lines.append('set_from_command_line(args);')
            self.run_args_applied = True
        run_lines.append(f'{net.name}.run({float(duration)!r}, {report_call}, {float(report_period)!r});')
        run_lines.extend(self.code_lines['after_network_run'])
        self.main_queue.append(('run_network', (net, run_lines)))

        net.after_run()

        # Manually set the cache for the clocks, simulation scripts might
        # want to access the time (which has been set in code and is therefore
        # not accessible by the normal means until the code has been built and
        # run)
        for clock in net._clocks:
            self.array_cache[clock.variables['timestep']] = np.array([clock._i_end])
            self.array_cache[clock.variables['t']] = np.array([clock._i_end * clock.dt_])

        if self.build_on_run:
            if self.has_been_run:
                raise RuntimeError("The network has already been built and run "
                                   "before. Use set_device with "
                                   "build_on_run=False and an explicit "
                                   "device.build call to use multiple run "
                                   "statements with this device.")
            self.build(direct_call=False, **self.build_options)

    def run(self, directory, results_directory, with_output, run_args):
        with in_directory(directory):
            run_cmd = ['emrun', os.path.basename(self.build_options['html_file'])]
            start_time = time.time()
            x = subprocess.call(run_cmd + run_args)
            self.timers['run_binary'] = time.time() - start_time

    def build(self, html_file=None, **kwds):
        if html_file is None:
            import __main__
            html_file = os.path.splitext(__main__.__file__)[0] + '.html'
            if not os.path.exists(html_file):
                raise ValueError(f"Need to provide 'html_file' argument, or store the HTML file "
                                 f"as '{html_file}'.")
        
        self.build_options['html_file'] = html_file
        super(WASMStandaloneDevice, self).build(**kwds)


wasm_standalone_device = WASMStandaloneDevice()
all_devices['wasm_standalone'] = wasm_standalone_device
