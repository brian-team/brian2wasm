Installation instructions
=========================

The ``brian2wasm`` package can be installed on **Linux**, **macOS**, and **Windows**.

It requires the `Brian 2 simulator <https://briansimulator.org/>`_ and the `Emscripten <https://emscripten.org/>`_ tool-chain, which are handled automatically when using the Pixi package manager.

Installation with Pixi
--------------------------

`Pixi <https://pixi.sh>`_ is a modern, cross-platform package and environment manager that simplifies setting up brian2wasm and its dependencies.

To install and use brian2wasm with Pixi::

        # 1 – install Pixi for Linux/macOS
        curl -fsSL https://pixi.sh/install.sh | sh

        # 2 - install Pixi for Windows
        powershell -ExecutionPolicy ByPass -c "irm -useb https://pixi.sh/install.ps1 | iex"
You can also follow the installation instructions on Pixi's website (https://pixi.sh/latest/installation/)

After installing Pixi we need to setup ``brian2wasm``::

        git clone https://github.com/brian-team/brian2wasm.git
        cd brian2wasm
        pixi install          # creates the full env (Python, emsdk, brian2, …)
        pixi run setup        # one-time EMSDK activation
        pixi shell            # enter the environment shell

Installation with Conda (Under Development)
--------------------------

