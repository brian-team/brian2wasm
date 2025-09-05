Using Brian2WASM
================

``brian2wasm`` enables running standard ``Brian 2`` Python scripts, which are converted to WebAssembly for execution in a browser environment.

Standard Usage
-------------

To run a ``Brian 2`` script with ``brian2wasm``, use the following command:

.. code-block:: bash

   python -m brian2wasm filename.py

.. important::
   - The ``filename.py`` must be a valid ``Brian 2`` Python script.
   - Do **not** include the ``set_device()`` function in your script, as ``brian2wasm`` automatically handles this.

.. note::
   Ensure your script adheres to ``Brian 2`` syntax and conventions. Refer to the `Brian 2 documentation <https://briansimulator.org/>`_ for guidance.

Command-Line Options
--------------------

``brian2wasm`` supports the following optional command-line flags to customize its behavior:

1. **--no-server**

   .. code-block:: bash

      python -m brian2wasm filename.py --no-server

   .. important::
      - Generates WebAssembly and HTML output files (e.g., ``filename.html``, ``filename.js``, ``filename.wasm``) without launching a local preview server.
      - Use this option if you want to manually serve or distribute the generated files.

   .. tip::
      This is useful for deploying the output to a web server or for further customization of the generated files.

2. **--skip-install**

   .. code-block:: bash

      python -m brian2wasm filename.py --skip-install

   .. important::
      - Bypasses the check and activation of the Emscripten SDK (EMSDK).
      - Use this only if the EMSDK is already configured and available in your environment (e.g., via Pixi, Conda, or a manual installation).

   .. warning::
      Running with ``--skip-install`` without a properly configured EMSDK will result in errors. Verify your EMSDK setup by running ``emcc --version`` before using this option.

.. note::
   The generated WebAssembly files can be hosted on any standard web server or viewed locally by opening the ``filename.html`` file in a web browser.