.. brian2wasm documentation master file, created by
   sphinx-quickstart on Sun Aug 10 08:49:52 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Brian2WASM's Documentation
====================================

The ``brian2wasm`` package is a ``Brian 2`` simulator device that compiles ``Brian 2`` models into WebAssembly and JavaScript using the Emscripten toolchain. It generates a self-contained web folder containing HTML, JavaScript, and a ``.wasm`` binary, enabling simulations to run directly in any modern web browser.

.. figure:: ./images/result_ornstein_uhlenbeck.png
   :alt: Example simulation output
   :align: center

   Example output of a ``brian2wasm`` simulation.

Contributing
------------

We welcome contributions to ``brian2wasm``! If you're interested in contributing, please join the discussion on the `Brian Discourse Group <https://brian.discourse.group/>`_.

Bug Reports
-----------

To report issues or suggest improvements, use the `GitHub issue tracker <https://github.com/brian-team/brian2wasm/issues>`_ or post in the `Brian Discourse Group <https://brian.discourse.group/>`_.

.. tip::
   Before submitting a bug report, check the `known issues <user/issues.html>`_ page to see if your issue is already documented.

Contents
--------

.. toctree::
   :maxdepth: 2
   :titlesonly:

   user/index
   developer/index
   examples/index

API Reference
-------------

.. toctree::
   :maxdepth: 5
   :titlesonly:

   reference/brian2wasm