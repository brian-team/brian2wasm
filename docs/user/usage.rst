Using Brian2WASM
=========================

``brian2wasm`` can run any ``Brian2`` script which are standard python scripts, and therefore be run in the same way.

Standard Usage
--------------------------

You can run ``Brian2`` scripts using ``brian2wasm`` using::

        python -m brian2wasm filename.py

.. important::
        * filename.py must be a valid Brian2 python script
        * Do not call ``set_device()`` function inside the script; brian2wasm inserts it automatically


Command-Line Options
--------------------------

``brian2wasm`` provides a few optional flags to customize its behavior:

1. ``--no-server`` ::

        python -m brian2wasm filename.py --no-server

.. important::
        * Generates the WebAssembly/HTML output, but does not launch the local preview server.
        * Useful if you only want the build artifacts (e.g. filename.html, filename.js, filename.wasm) and plan to serve them yourself.

2. ``--skip-install`` ::

        python -m brian2wasm filename.py --skip-install

.. important::
        * Runs brian2wasm without checking for or activating Emscripten SDK (EMSDK).
        * Use this if EMSDK is already installed and available in your environment (e.g. via Conda, Pixi, or a manual install).
