Known Issues
============

Below is a list of known issues with ``brian2wasm``. For additional details or to report new issues, visit the `bug tracker on GitHub <https://github.com/brian-team/brian2wasm/issues>`_.

- **Automatic Device Setting**:
  Do not call ``set_device(...)`` in your ``Brian 2`` script, as ``brian2wasm`` automatically configures the device. Including this call may cause errors or unexpected behavior.

- **Plotly CDN Dependency**:
  The generated HTML files rely on Plotly charts that load assets from a CDN (``https://cdn.plot.ly/plotly-latest.min.js``). An internet connection is required for these charts to render properly.

.. warning::
   If the CDN is inaccessible (e.g., due to network issues or restrictions), Plotly charts will not load. Consider hosting Plotly locally for offline use.

.. tip::
   Check the GitHub issues page regularly for updates on fixes and workarounds for known problems.