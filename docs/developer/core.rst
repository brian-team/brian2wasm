Core Architecture
=================

The :code:`brian2wasm` architecture is built around a custom Brian2 device that intercepts the normal simulation execution flow and redirects it to WebAssembly compilation. The system transforms Python/Brian2 code into C++, compiles it with Emscripten, and packages the result with JavaScript runtime components for browser execution.

System Overview
---------------

.. mermaid::
   :align: center

   %%{init: {'theme': 'default', 'themeVariables': { 'fontSize': '7px'}}}%%
   graph TB

    %% User Interface Layer
    subgraph UI[User Interface Layer]
        A[Python Script<br/>.py files]
        B[CLI Interface<br/>__main__.py]
        A --> B
    end

    %% Core Processing Layer
    subgraph CP[Core Processing Layer]
        C[WASMStandaloneDevice<br/>device.py]
        D[Template System<br/>brian2wasm templates]
        E[Code Generation<br/>objects.cpp, makefile]
        C --> D
        C --> E
    end

    %% Compilation Layer
    subgraph CL[Compilation Layer]
        F[Static Assets<br/>brian.js, worker.js]
        G[Emscripten Toolchain<br/>emcc, wasm-ld]
    end

    %% Runtime Layer
    subgraph RL[Runtime Layer]
        H[WebAssembly Module<br/>wasm_module.js]
        I[Development Server<br/>emrun]
        J[Browser Environment]
    end

    %% Connections
    B --> C
    D --> F
    E --> G
    F --> J
    G --> H
    H --> J
    I --> J

Device Architecture
-------------------

**Key Device Methods:**

* :code:`activate()` - Sets up the WASM-specific templater and headers
* :code:`generate_objects_source()` - Generates C++ source code with WASM-specific templates
* :code:`copy_source_files()` - Copies JavaScript runtime files to output directory

Template and Asset Management
-----------------------------

The device integrates with Brian2's templating system while adding WebAssembly-specific templates and runtime assets.

**Core Components:**

* :code:`objects.cpp` template - C++ simulation code generation
* :code:`makefile` / :code:`win_makefile` - Cross-platform build configuration
* :code:`worker.js` - Web Worker runtime
* :code:`brian.js` - Main JavaScript interface
* :code:`html_template` - Default web interface

Configuration Management
------------------------

The system uses Brian2's preference system to manage Emscripten SDK configuration and build options.

**Key Configuration Areas:**

* EMSDK path resolution from environment variables
* HTML file configuration for custom interfaces
* Debug/release build flags
* Cross-platform compiler settings

Cross-Platform Support
----------------------

The architecture includes robust cross-platform support with platform-specific adaptations:

* **Windows**: MSVC filtering and :code:`win_makefile` template
* **Unix-like**: Standard flags and :code:`makefile` template
* **Server execution**: Platform-specific :code:`emrun` command handling

The modular design allows for extension and customization while ensuring reliable cross-platform operation across Linux, macOS, and Windows environments.