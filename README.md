# Brian2Wasm

Wasm code generation for the [Brian simulator](https://briansimulator.org).

Using the [emscripten](https://emscripten.org/) toolchain, this "device" generates code in WebAssembly and JavaScript, enabling users to run Brian simulations in the browser.

You can directly access the built examples on this website: https://brian-team.github.io/brian2wasm/

**UNDER CONSTRUCTION, not for general use**

> [!WARNING]
> The package currently only targets Linux – it might work on macOS and on Windows via the WSL, but this hasn't been tested.

Usage/Installation:
- Install `brian2wasm` with `pip`, either by cloning this repository and using `pip install .`, or by using
  ```console
  $ pip install git+https://github.com/brian-team/brian2wasm/
  ```
- Install the [emsdk](https://emscripten.org/docs/getting_started/downloads.html) and activate it following the instructions
- You should then be able to run one of the examples in the [`examples` folder](/examples)

> [!NOTE]
> Plotting will not work in the website that gets started automatically by the example script, since it needs to download the `plotly.js` library from a CDN.
> You can work around this limitation by going into the generated folder that contains the `index.html` file and run a Python webserver via `python -m http.server`. You can then open the displayed link in your browser.
