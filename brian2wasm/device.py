"""
Module implementing the WASM/JS "standalone" device.
"""
import os
import shutil
import subprocess
import time

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
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        shutil.copy(os.path.join(template_dir, 'main.html'), directory)

    def run(self, directory, results_directory, with_output, run_args):
        with in_directory(directory):
            if not with_output:
                stdout = open(results_directory + 'stdout.txt', 'w')
            else:
                stdout = None
            run_cmd = ['emrun', 'main.html']
            start_time = time.time()
            x = subprocess.call(run_cmd + run_args, stdout=stdout)
            self.timers['run_binary'] = time.time() - start_time


wasm_standalone_device = WASMStandaloneDevice()
all_devices['wasm_standalone'] = wasm_standalone_device
