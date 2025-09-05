Runtime System
==============

The Runtime System provides the JavaScript interface layer that enables Brian2 simulations to execute within web browsers through WebAssembly modules.

.. mermaid::
   :align: center

   %%{init: {'theme': 'default', 'themeVariables': { 'fontSize': '15px'}}}%%
   graph TB

    subgraph WWT[Web Worker Thread]
        A["worker.js<br/>"]
        B["WebAssembly Module<br/>(wasm_module.js)"]
        A --> B
    end

    subgraph MT[Main Thread]
        C["BrianSimulation Class<br/>(brian.js)"]
        D["HTML Interface<br/>(progress bar, buttons)"]
        E["Visualization<br/>(Plotly/Chart.js)"]
        C --> D
        C --> E
    end

    subgraph WASM[WASM Runtime Environment]
        F["Emscripten File System"]
        G["pre.js<br/>(Module Configuration)"]
        H["add_results() function"]
        I["brian_result_object"]
        F --> H
        H --> I
        G --> I
    end

    %% Connections
    A --> C
    B --> G

JavaScript Interface
--------------------

BrianSimulation Class
~~~~~~~~~~~~~~~~~~~~~

The core interface is implemented through the :code:`BrianSimulation` class, which manages simulation execution, progress reporting, and result visualization.

The constructor accepts three optional parameters:

- :code:`result_plots`: Array of plot configurations for visualization
- :code:`progress`: Progress reporting configuration (defaults to progress bar)
- :code:`run_button`: ID of the HTML run button element

Initialization and Setup
+++++++++++++++++++++++

The :code:`init()` method configures DOM elements and establishes event handlers:

Progress Reporting
++++++++++++++++++

Progress updates are handled through configurable reporting functions. The default 'bar' type updates both a progress bar element and text display:

Result Visualization
++++++++++++++++++++

The system supports multiple plot types including raster plots for spike visualization:

Custom plot functions can be registered through the :code:`result_plots` configuration.

Simulation Execution
++++++++++++++++++++

The :code:`run()` method initiates simulation by disabling the run button and sending data to the web worker:

Web Worker Extension
--------------------

Worker Implementation
~~~~~~~~~~~~~~~~~~~~~

The web worker handles WebAssembly module execution in a separate thread to maintain UI responsiveness:

The worker accepts command-line style arguments and passes them to the WebAssembly module's main function.

Message Communication
+++++++++++++++++++++

Communication between the main thread and worker uses a structured message protocol:

Two message types are supported:

- :code:`progress`: Real-time simulation progress updates
- :code:`results`: Final simulation data and results

Web Template System
------------------

Module Configuration
~~~~~~~~~~~~~~~~~~~

The :code:`pre.js` template configures the Emscripten environment before WebAssembly execution:

Data Transfer Functions
+++++++++++++++++++++++

The :code:`add_results()` function handles conversion of binary simulation data to JavaScript typed arrays:

Supported data types include:

- :code:`double` → :code:`Float64Array`
- :code:`float` → :code:`Float32Array`
- :code:`int32_t` → :code:`Int32Array`
- :code:`int64_t` → :code:`BigInt64Array`
- :code:`char` → :code:`Uint8Array`

Console Integration
+++++++++++++++++++

Standard output and error streams are redirected to the browser console:

Default HTML Template
--------------------

Template Configuration
~~~~~~~~~~~~~~~~~~~~~

The system generates default HTML interfaces when no custom template is provided. Default content includes configurable title, headers, and canvas dimensions:

HTML Generation Process
+++++++++++++++++++++++

HTML files are automatically created during the build process if not explicitly provided:

The template system uses the device's templater to generate complete HTML pages with embedded JavaScript runtime components.

Asset Management
++++++++++++++++

Static assets including JavaScript files are copied to the project directory during compilation:

Notes
-----

The Runtime System integrates tightly with the Emscripten compilation pipeline and requires proper EMSDK configuration. Progress reporting uses Emscripten's :code:`EM_ASM` interface to bridge C++ simulation code with JavaScript event handling. The modular design allows for custom visualization functions and HTML templates while maintaining compatibility with the core Brian2 simulation framework.