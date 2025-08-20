WASM Standalone Device
======================

Overview
--------

The :code:`WASM Standalone Device` is the core component of brian2wasm that enables running Brian2 neural network simulations in web browsers through WebAssembly compilation. The device inherits from Brian2's :code:`CPPStandaloneDevice` and overrides key methods to redirect simulation execution toward WebAssembly compilation instead of native C++ execution.

**Architecture Overview**

.. mermaid::
   :align: center

   classDiagram
       class CPPStandaloneDevice {
           +activate()
           +build()
           +network_run()
           +generate_objects_source()
       }

       class WASMStandaloneDevice {
           -transfer_results : list
           +transfer_only(variableviews)
           +activate()
           +generate_objects_source()
           +generate_makefile()
           +copy_source_files()
           +get_report_func()
           +network_run()
           +run()
           +build()
       }

       class TemplateSystem {
           +objects()
           +makefile()
           +win_makefile()
           +html_template()
       }

       class PreferenceSystem {
           +emsdk_directory
           +emsdk_version
       }

       CPPStandaloneDevice <|-- WASMStandaloneDevice
       WASMStandaloneDevice --> TemplateSystem : uses
       WASMStandaloneDevice --> PreferenceSystem : configures

Key Methods
~~~~~~~~~~~

**activate()**
  Initializes the device by setting up the templater to use brian2wasm templates and ensuring :code:`emscripten.h` is included in headers.

**generate_objects_source()**
  Generates the main C++ source code for the simulation using the objects template with transfer results support.

**generate_makefile()**
  Creates platform-specific makefiles (Windows or Unix) with Emscripten-compatible compiler and linker flags.

Configuration
-------------

Preferences
~~~~~~~~~~~

The device uses Brian2's preference system for configuration:

- :code:`devices.wasm_standalone.emsdk_directory`: Path to the Emscripten SDK directory
- :code:`devices.wasm_standalone.emsdk_version`: Version of EMSDK to use (defaults to "latest")

The system also checks environment variables :code:`EMSDK` and :code:`CONDA_EMSDK_DIR` for SDK path resolution.

HTML Integration
~~~~~~~~~~~~~~~~

The device supports custom HTML files and content for the web interface:

- Default HTML template with configurable title, headers, description, and canvas dimensions
- Automatic HTML file generation if none exists
- Support for custom HTML files alongside Python scripts

Progress Reporting
------------------

The device implements a sophisticated progress reporting system that bridges C++ simulation execution with JavaScript through Emscripten's :code:`EM_ASM` interface.

The progress reporting includes:

- Time formatting utilities for human-readable duration display
- Real-time progress updates sent to the web interface via :code:`postMessage`
- Configurable output streams (:code:`stdout`, :code:`stderr`, or custom)

Network Execution
-----------------

The :code:`network_run()` method orchestrates the simulation execution:

1. Validates duration parameters
2. Processes network objects and code objects
3. Sets up progress reporting
4. Generates run lines for the simulation loop
5. Handles clock synchronization and caching

File Management
---------------

The device manages several types of files during compilation:

**Source Files**
  Copies JavaScript runtime files (:code:`worker.js`, :code:`brian.js`) and HTML templates to the build directory.

**Static Assets**
  Handles preloading of static arrays and other simulation data.

Platform Support
----------------

The device provides cross-platform support with platform-specific adaptations:

**Windows**
  Uses :code:`win_makefile` template and :code:`emrun` command directly.

**Unix-like Systems**
  Uses standard :code:`makefile` template and bash with :code:`emrun`.

Compiler Flag Handling
~~~~~~~~~~~~~~~~~~~~~~

The device filters out incompatible compiler and linker flags:

- Removes :code:`-march=native` from compiler flags
- Filters out MSVC-specific options
- Removes unsupported linker flags like :code:`--enable-new-dtags` and :code:`-R<path>`

Command Line Interface
----------------------

The device integrates with a CLI that automatically injects device setup code:

The CLI supports:

- Automatic device activation with :code:`set_device('wasm_standalone')`
- Custom HTML file detection and integration
- No-server mode for file generation without web server startup

Usage Example
-------------

To use the WASM Standalone Device in a Brian2 script::

    from brian2 import *
    import brian2wasm

    set_device('wasm_standalone', directory='my_simulation')

    # Your Brian2 simulation code here
    # ...

    run(100*ms)

Or via the command line::

    python -m brian2wasm my_script.py

Device Registration
-------------------

The device is automatically registered with Brian2's device system:

This allows it to be activated using Brian2's standard :code:`set_device()` function with the identifier :code:`'wasm_standalone'`.