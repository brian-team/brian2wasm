Known Issues
============

Below is a list of known issues with ``brian2wasm``. For additional details or to report new issues, visit the `bug tracker on GitHub <https://github.com/brian-team/brian2wasm/issues>`_.

- **Automatic Device Setting**:
    When using the brian2wasm CLI tool, do not call ``set_device(...)`` in your Brian 2 script. The CLI automatically configures the device, and adding your own call may cause errors or unexpected behavior.

    However, if you are not using the CLI (e.g. running a script directly in Python), you can still manually set the device to ``wasm_standalone`` with ``set_device("wasm_standalone")``.

- **Plotly CDN Dependency**:
  The generated HTML files rely on Plotly charts that load assets from a CDN (``https://cdn.plot.ly/plotly-latest.min.js``). An internet connection is required for these charts to render properly.

.. warning::
   If the CDN is inaccessible (e.g., due to network issues or restrictions), Plotly charts will not load. Consider hosting Plotly locally for offline use.

.. tip::
   Check the GitHub issues page regularly for updates on fixes and workarounds for known problems.