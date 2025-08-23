Installation Instructions
========================

The ``brian2wasm`` package is compatible with **Linux**, **macOS**, and **Windows**. It depends on the `Brian 2 simulator <https://briansimulator.org/>`_ and the `Emscripten <https://emscripten.org/>`_ toolchain. Using the Pixi package manager is recommended, as it automatically handles these dependencies.

Installation with Pixi
---------------------

`Pixi <https://pixi.sh>`_ is a modern, cross-platform package and environment manager that simplifies the setup of ``brian2wasm`` and its dependencies.

To install and use ``brian2wasm`` with Pixi:

1. **Install Pixi**:

   - For **Linux** or **macOS**:

     .. code-block:: bash

        curl -fsSL https://pixi.sh/install.sh | sh

   - For **Windows**:

     .. code-block:: powershell

        powershell -ExecutionPolicy Bypass -c "irm -useb https://pixi.sh/install.ps1 | iex"

   Alternatively, refer to the official `Pixi installation instructions <https://pixi.sh/latest/installation/>`_.

2. **Set up brian2wasm**:

   .. code-block:: bash

      git clone https://github.com/brian-team/brian2wasm.git
      cd brian2wasm
      pixi install          # Installs Python, Emscripten, Brian 2, and other dependencies
      pixi run setup        # Activates Emscripten SDK (one-time step)
      pixi shell            # Enters the environment shell

   .. tip::
      Run ``pixi shell`` whenever you start a new session to access the configured environment.

   .. warning::
      Ensure you are in the ``brian2wasm`` directory before running ``pixi install`` to avoid setup errors.

Installation with Conda (Experimental)
-------------------------------------

.. warning::
   The Conda installation method is under development and may not be fully stable. Consider using Pixi for a more reliable experience.

To install and use ``brian2wasm`` with Conda:

1. **Create a Conda environment**:

   .. code-block:: bash

      conda create -n brian2wasm python

2. **Activate the environment**:

   .. code-block:: bash

      conda activate brian2wasm

3. **Install brian2wasm**:

   .. code-block:: bash

      conda install brian2wasm -c conda-forge

   .. note::
      Ensure the ``conda-forge`` channel is added to your Conda configuration. Run ``conda config --add channels conda-forge`` if needed.

Installation with PIP
--------------------

If you have a pre-configured `Emscripten SDK (EMSDK) <https://emscripten.org/docs/getting_started/downloads.html>`_ installed, you can install ``brian2wasm`` using PIP.

To install ``brian2wasm`` with PIP:

.. code-block:: bash

   pip install brian2wasm

.. warning::
   PIP installation requires a properly configured Emscripten SDK. Without it, the installation will fail. Refer to the `Emscripten documentation <https://emscripten.org/docs/getting_started/downloads.html>`_ for setup instructions.

.. tip::
   Verify your Emscripten installation by running ``emcc --version`` before using PIP to install ``brian2wasm``.