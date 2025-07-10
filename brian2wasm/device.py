"""
Module implementing the WASM/JS "standalone" device.
"""
import os
import platform
import re
import shutil
import tempfile
import time
from collections import Counter

import numpy as np

from brian2.units import second
from brian2.core.namespace import get_local_namespace
from brian2.core.preferences import prefs, BrianPreference
from brian2.synapses import Synapses
from brian2.utils.logger import get_logger
from brian2.utils.filetools import in_directory
from brian2.devices import all_devices
from brian2.devices.cpp_standalone.device import CPPStandaloneDevice, CPPWriter
from brian2.utils.filetools import ensure_directory

__all__ = []

logger = get_logger(__name__)

prefs.register_preferences(
    'devices.wasm_standalone',
    'Preferences for the WebAsm backend',
    emsdk_directory=BrianPreference(
        docs='''Path to the emsdk directory, containing the emsdk binary.''',
        default=''
    ),
    emsdk_version=BrianPreference(
        docs='''Version of the emsdk to use, defaults to "latest"''',
        default="latest"
    ),
    emcc_compile_args=BrianPreference(
        default=[
            "-w"
        ],
        docs="Extra flags appended to every emcc compile command",
    ),
    emcc_link_args=BrianPreference(
        default=[],
        docs="Extra flags passed at link time",
    ),
)


DEFAULT_HTML_CONTENT = {'title': 'Brian simulation',
                        'h1': '',
                        'h2': '',
                        'description': '',
                        'canvas_width': '95%',
                        'canvas_height': '500px'}

class WASMStandaloneDevice(CPPStandaloneDevice):
    """
    The `Device` used for WASM simulations.
    """
    def __init__(self, *args, **kwds):
        self.transfer_results = None
        super(WASMStandaloneDevice, self).__init__(*args, **kwds)

    def transfer_only(self, variableviews):
        assert self.transfer_results is None
        self.transfer_results = []
        for variableview in variableviews:
            self.transfer_results.append(variableview.variable)

    def activate(self, *args, **kwargs):
        super(WASMStandaloneDevice, self).activate(*args, **kwargs)
        # Overwrite the templater to prefer our templates
        self.code_object_class().templater = self.code_object_class().templater.derive('brian2wasm')
        if '<emscripten.h>' not in prefs.codegen.cpp.headers:
            prefs.codegen.cpp.headers += ['<emscripten.h>']

    def generate_objects_source(
        self,
        writer,
        arange_arrays,
        synapses,
        static_array_specs,
        networks,
        timed_arrays,
    ):
        arr_tmp = self.code_object_class().templater.objects(
            None,
            None,
            array_specs=self.arrays,
            dynamic_array_specs=self.dynamic_arrays,
            dynamic_array_2d_specs=self.dynamic_arrays_2d,
            zero_arrays=self.zero_arrays,
            arange_arrays=arange_arrays,
            synapses=synapses,
            clocks=self.clocks,
            static_array_specs=static_array_specs,
            networks=networks,
            get_array_filename=self.get_array_filename,
            get_array_name=self.get_array_name,
            profiled_codeobjects=self.profiled_codeobjects,
            code_objects=list(self.code_objects.values()),
            timed_arrays=timed_arrays,
            transfer_results=self.transfer_results,
        )
        writer.write("objects.*", arr_tmp)

    def generate_makefile(
            self,
            writer,
            compiler,
            compiler_flags,
            linker_flags,
            nb_threads,
            debug,
    ):

        preload_flags = " ".join(f"--preload-file static_arrays/{name}"
                                 for name in sorted(self.static_arrays))
        rm_cmd = "rm $(OBJS) $(PROGRAM) $(DEPS)"
        compiler_dbg = "-g -DDEBUG" if debug else ""
        linker_dbg = "-g" if debug else ""

        source_files = " ".join(sorted(writer.source_files))
        header_files = " ".join(sorted(writer.header_files))
        preamble_path = os.path.join(os.path.dirname(__file__), "templates", "pre.js")

        emsdk_path = (
                prefs.devices.wasm_standalone.emsdk_directory
                or os.environ.get("EMSDK")
                or os.environ.get("CONDA_EMSDK_DIR")
                or ""
        )
        emsdk_version = prefs.devices.wasm_standalone.emsdk_version

        if not emsdk_path and (
                not os.environ.get("EMSDK") or os.environ["EMSDK"] not in os.environ["PATH"]
        ):
            raise ValueError(
                "Please provide the path to the EMSDK directory in the preferences."
            )

        templater = self.code_object_class().templater
        makefile_fn = templater.win_makefile if os.name == "nt" else templater.makefile
        output_name = "win_makefile" if os.name == "nt" else "makefile"

        makefile_content = makefile_fn(
            None,
            None,
            source_files=source_files,
            header_files=header_files,
            compiler_flags=compiler_flags,
            compiler_debug_flags=compiler_dbg,
            linker_debug_flags=linker_dbg,
            linker_flags=linker_flags,
            preloads=preload_flags,
            preamble_file=preamble_path,
            rm_cmd=rm_cmd,
            emsdk_path=emsdk_path,
            emsdk_version=emsdk_version,
        )

        writer.write(output_name, makefile_content)

    def copy_source_files(self, writer, directory):
        super(WASMStandaloneDevice, self).copy_source_files(writer, directory)
        shutil.copy(os.path.join(os.path.dirname(__file__), 'templates', 'worker.js'), directory)
        shutil.copy(os.path.join(os.path.dirname(__file__), 'templates', 'brian.js'), directory)
        if self.build_options['html_file']:
            shutil.copy(self.build_options['html_file'], os.path.join(directory, 'index.html'))

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
                %STREAMNAME% << completed*duration << " s (" << (int)(completed*100.) << "%) simulated in " << _format_time(elapsed) << " (" << elapsed << "s)";
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
        if duration < 0:
            raise ValueError(
                f"Function 'run' expected a non-negative duration but got '{duration}'"
            )

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
        html_file = self.build_options['html_file']
        html_content = self.build_options['html_content']
        if html_file is None:
            import __main__
            html_file = os.path.splitext(__main__.__file__)[0] + '.html'
            if not os.path.exists(html_file):
                if html_content is None:
                    html_content = dict(DEFAULT_HTML_CONTENT)
                else:
                    for key in html_content:
                        if key not in DEFAULT_HTML_CONTENT:
                            raise KeyError(f"Key '{key} is not a valid key for html_content. Allowed keys: {', '.join(DEFAULT_HTML_CONTENT.keys())}")
                    for key in DEFAULT_HTML_CONTENT:
                        if key not in html_content:
                            html_content[key] = DEFAULT_HTML_CONTENT[key]
                html_file = os.path.join(self.project_dir, 'index.html')

                # Create HTML file from template in code directory
                html_tmp = self.code_object_class().templater.html_template(None, None,
                                                                            **html_content)
                with open(html_file, 'w') as f:
                    f.write(html_tmp)
            else:  # HTML file exists, copy it to the project directory
                shutil.copy(html_file, os.path.join(self.project_dir, 'index.html'))

        with in_directory(directory):
            if os.environ.get('BRIAN2WASM_NO_SERVER','0') == '1':
                print("Skipping server startup (--no-server flag set)")
                return
            
            if platform.system() == "Windows":
                cmd_line = f'emrun "index.html"'
                try:
                    os.system(cmd_line)
                except Exception as e:
                    raise RuntimeError(f"Failed to run emrun command: {cmd_line}. "
                                       "Please ensure that emrun is installed and available in your PATH.") from e

            if prefs.devices.wasm_standalone.emsdk_directory:
                emsdk_path = prefs.devices.wasm_standalone.emsdk_directory
                run_cmd = ['source', f'{emsdk_path}/emsdk_env.sh', '&&', 'emrun', 'index.html']
            else:
                run_cmd = ['emrun', 'index.html']
            start_time = time.time()
            os.system(f"/bin/bash -c '{' '.join(run_cmd + run_args)}'")
            self.timers['run_binary'] = time.time() - start_time

    def build(self, html_file=None, html_content=None, **kwds):
        self.build_options.update({'html_file': html_file,
                                   'html_content': html_content})

        direct_call = kwds.get('direct_call', True)
        additional_source_files = kwds.get('additional_source_files', [])
        run_args = kwds.get('run_args', [])
        directory = kwds.get('directory') or tempfile.mkdtemp(prefix="brian_standalone_")
        run = kwds.get('run', True)
        debug = kwds.get('debug', False)
        clean = kwds.get('clean', False)
        with_output = kwds.get('with_output', True)
        results_directory = kwds.get('results_directory', 'results')
        compile = kwds.get('compile', True)

        if self.build_on_run and direct_call:
            raise RuntimeError(
                "You used set_device with build_on_run=True "
                "(the default option), which will automatically "
                "build the simulation at the first encountered "
                "run call - do not call device.build manually "
                "in this case. If you want to call it manually, "
                "e.g. because you have multiple run calls, use "
                "set_device with build_on_run=False."
            )
        if self.has_been_run:
            raise RuntimeError(
                "The network has already been built and run "
                "before. To build several simulations in "
                'the same script, call "device.reinit()" '
                'and "device.activate()". Note that you '
                "will have to set build options (e.g. the "
                "directory) and defaultclock.dt again."
            )

        self.project_dir = directory
        ensure_directory(directory)
        if os.path.isabs(results_directory):
            raise TypeError(
                "The 'results_directory' argument needs to be a relative path but was "
                f"'{results_directory}'."
            )
        # Translate path to absolute path which ends with /
        self.results_dir = os.path.join(
            os.path.abspath(os.path.join(directory, results_directory)), ""
        )

        compiler = "emcc"
        extra_compile_args = self.extra_compile_args + prefs["devices.wasm_standalone.emcc_compile_args"]
        extra_link_args = self.extra_link_args + prefs["devices.wasm_standalone.emcc_link_args"]

        define_macros = (
            self.define_macros
            + prefs["codegen.cpp.define_macros"]
            + [m for c in self.code_objects.values() for m in c.compiler_kwds.get("define_macros", [])]
        )
        include_dirs = (
            self.include_dirs
            + prefs["codegen.cpp.include_dirs"]
            + [d for c in self.code_objects.values() for d in c.compiler_kwds.get("include_dirs", [])]
        )
        library_dirs = (
            self.library_dirs
            + prefs["codegen.cpp.library_dirs"]
            + [d for c in self.code_objects.values() for d in c.compiler_kwds.get("library_dirs", [])]
        )
        libraries = (
            self.libraries
            + prefs["codegen.cpp.libraries"]
            + [l for c in self.code_objects.values() for l in c.compiler_kwds.get("libraries", [])]
        )

        macro_flags = []
        for m in define_macros:
            if isinstance(m, (list, tuple)):
                name, val = m if len(m) == 2 else (m[0], None)
            else:
                name, val = m, None
            macro_flags.append(f"-D{name}={val}" if val is not None else f"-D{name}")

        compiler_flags = (
                extra_compile_args
                + macro_flags
                + [f"-I{d}" for d in include_dirs]
        )
        linker_flags = (
                extra_link_args
                + [f"-L{d}" for d in library_dirs]
                + [f"-l{l}" for l in libraries]
        )

        additional_source_files += [
            f for c in self.code_objects.values() for f in c.compiler_kwds.get("sources", [])
        ]
        for d in ("code_objects", "results", "static_arrays"):
            ensure_directory(os.path.join(directory, d))

        self.writer = CPPWriter(directory)
        nb_threads = prefs.devices.cpp_standalone.openmp_threads
        if nb_threads < 0:
            raise ValueError("OpenMP threads cannot be negative.")
        self.check_openmp_compatible(nb_threads)

        self.write_static_arrays(directory)

        names = [o.name for n in self.networks for o in n.sorted_objects]
        dupes = [n for n, c in Counter(names).items() if c > 1]
        if dupes:
            raise ValueError("Duplicate object names: " + ", ".join(f"'{n}'" for n in dupes))

        self.generate_objects_source(self.writer, self.arange_arrays, self.synapses,
                                     self.static_array_specs, self.networks, self.timed_arrays)
        self.generate_main_source(self.writer)
        self.generate_codeobj_source(self.writer)
        self.generate_network_source(self.writer, compiler)
        self.generate_synapses_classes_source(self.writer)
        self.generate_run_source(self.writer)
        self.copy_source_files(self.writer, directory)
        self.writer.source_files.update(additional_source_files)

        self.generate_makefile(
            self.writer,
            compiler,
            compiler_flags=" ".join(compiler_flags),
            linker_flags=" ".join(linker_flags),
            nb_threads=nb_threads,
            debug=debug,
        )

        if compile:
            self.compile_source(directory, compiler, debug, clean)
            if run:
                self.run(directory, results_directory, with_output, run_args)

        tm = self.timers
        logger.debug("Time measurements: " + ", ".join(
            f"{lbl}: {tm[g][k]:.2f}s" if isinstance(tm[g], dict) else f"{lbl}: {tm[g]:.2f}s"
            for lbl, g, k in (
                ("'make clean'", "compile", "clean"),
                ("'make'", "compile", "make"),
                ("running 'main'", "run_binary", None),
            )
            if (k and tm[g][k] is not None) or (not k and tm[g] is not None)
        ))


wasm_standalone_device = WASMStandaloneDevice()
all_devices['wasm_standalone'] = wasm_standalone_device