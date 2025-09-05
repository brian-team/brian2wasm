Compilation and Code Generation Pipeline
=======================================

Overview
--------

The brian2wasm compilation pipeline transforms Brian2 neural network simulations into WebAssembly modules for browser execution. The system consists of three integrated components: template-based code generation, cross-platform build system, and Emscripten compilation toolchain.

Architecture
------------

The pipeline is orchestrated by the :code:`WASMStandaloneDevice` class, which inherits from Brian2's :code:`CPPStandaloneDevice` and redirects simulation execution toward WebAssembly compilation.

.. mermaid::
   :align: center

   %%{init: {'theme': 'default', 'themeVariables': { 'fontSize': '10px'}}}%%
   graph TB

        A[Brian2 Simulation Files]
        B[array_specs]
        C[dynamic_array_specs]
        D[networks]
        E[synapses]
        F[clocks]
        G["objects.cpp Template"]
        H["objects.h"]
        I["objects.cpp"]
        J["C++ Functions"]
        K["_init_arrays()"]
        L["_load_arrays()"]
        M["_write_arrays()"]
        N["set_variable_by_name()"]

        A --> G
        B --> G
        C --> G
        D --> G
        E --> G
        F --> G
        G --> H
        G --> I
        I --> J
        J --> K
        J --> L
        J --> M
        J --> N

Code Generation Templates
-------------------------

Objects Template System
~~~~~~~~~~~~~~~~~~~~~~~

The :code:`objects.cpp` template generates comprehensive C++ simulation code from Brian2 objects. Key components include:

* **Array Management**: Handles static arrays, dynamic arrays (1D/2D), and timed arrays with automatic memory allocation
* **Data Type Mapping**: Converts Brian2 types to C++ equivalents (:code:`double`, :code:`float`, :code:`int32_t`, :code:`int64_t`, :code:`char`)
* **Variable Setting**: Supports both scalar value assignment and binary file loading

The template generates four core functions:

* :code:`_init_arrays()`: Initialize simulation arrays with zero, arange, or file-based data
* :code:`_load_arrays()`: Load static arrays from binary files
* :code:`_write_arrays()`: Export results to browser via Emscripten interface
* :code:`set_variable_by_name()`: Runtime variable modification support

Template Integration
~~~~~~~~~~~~~~~~~~~~

The device generates templates through the :code:`generate_objects_source()` method, passing simulation specifications including array specs, dynamic arrays, networks, and synapses.

Build System
------------

Cross-Platform Makefile Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The build system generates platform-specific makefiles using Jinja2 templates:

* **Unix/Linux**: Standard makefile with dependency tracking
* **Windows**: nmake-compatible makefile with explicit compilation rules

Platform detection occurs in the :code:`generate_makefile()` method, which selects appropriate templates based on :code:`os.name`.

Emscripten Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

The build system configures Emscripten with optimized flags:

**Optimization Flags**:
* :code:`-O3`: Maximum optimization
* :code:`-ffast-math`: Fast floating-point operations
* :code:`-fno-finite-math-only`: Preserve NaN/infinity handling

**WebAssembly Flags**:
* :code:`-fwasm-exceptions`: Exception handling support
* :code:`-sALLOW_MEMORY_GROWTH`: Dynamic memory allocation
* :code:`-sMODULARIZE=1`: Modular WebAssembly generation
* :code:`-sENVIRONMENT=worker`: Web Worker compatibility

EMSDK Management
~~~~~~~~~~~~~~~~

The system handles Emscripten SDK activation through preference-based configuration:

* Automatic EMSDK path resolution from preferences or environment variables
* Conditional activation scripts for Unix systems
* Cross-platform compiler flag filtering to remove unsupported options

Compilation Pipeline Flow
-------------------------

1. **Device Activation**: :code:`WASMStandaloneDevice.activate()` configures templater and headers

2. **Code Generation**:
   * :code:`generate_objects_source()` creates C++ simulation code
   * :code:`generate_makefile()` produces build configuration
   * :code:`copy_source_files()` deploys runtime assets

3. **Compilation**: Emscripten compiles C++ to WebAssembly with:
   * Object file generation from source files
   * Dependency tracking through :code:`make.deps`
   * Final linking with JavaScript preamble and preloaded files

4. **Runtime Integration**: Generated :code:`wasm_module.js` integrates with browser runtime through Web Workers

Build Artifacts
---------------

The compilation produces:

* :code:`wasm_module.js`: Main WebAssembly module with JavaScript interface
* :code:`wasm_module.wasm`: WebAssembly bytecode
* :code:`index.html`: Default web interface (auto-generated if not provided)
* Binary result files for simulation output
* Static array files for preloaded data

Progress Reporting
------------------

The system implements C++ to JavaScript communication through Emscripten's :code:`EM_ASM` interface, enabling real-time progress updates during simulation execution.

Configuration
-------------

Key preferences control compilation behavior:

* :code:`devices.wasm_standalone.emsdk_directory`: EMSDK installation path
* :code:`devices.wasm_standalone.emsdk_version`: EMSDK version selection

The pipeline provides a seamless bridge from high-level Brian2 Python code to optimized WebAssembly execution in web browsers.