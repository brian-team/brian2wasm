# Brian2Wasm

**Brian2Wasm** is a [Brian 2](https://briansimulator.org/) “device” that compiles Brian models to WebAssembly and JavaScript via the [Emscripten](https://emscripten.org/) tool-chain.  
The result is a self-contained web folder (`index.html`, `wasm_module.js`, and the `.wasm` binary) that runs your simulation in any modern browser.

Live examples: <https://brian-team.github.io/brian2wasm/>

> **Status** – functional, but still under active development.

[![PyPI](https://img.shields.io/pypi/v/brian2wasm.svg)](https://pypi.org/project/brian2wasm/)

## Installation & Usage (Pixi)

```bash
# 1 – install Pixi (https://pixi.sh)
curl -fsSL https://pixi.sh/install.sh | bash

# 2 – set up Brian2Wasm
git clone https://github.com/brian-team/brian2wasm.git
cd brian2wasm
pixi install          # creates the full env (Python, emsdk, brian2, …)
pixi run setup        # one-time EMSDK activation
pixi shell            # enter the environment shell

# 3 – build and run an example
python -m brian2wasm examples/brunel_hakim1999.py
```

## Headless build (no preview server)
```bash
python -m brian2wasm --no-server my_model.py
```
```--no-server``` skips the temporary web-server and only generates the files.


> **⚠️ Limitations / Warnings**
> * **Do not call `set_device(...)`** in your script—Brian2Wasm sets the device automatically.
> * Plotly charts inside the generated HTML load assets from a CDN.


## Contributing

Contributions are welcome!  
If you encounter a bug or have a feature request, please open an issue first.  
Pull requests should target the `main` branch and follow conventional commit messages.

---

## License

Brian2Wasm is released under the same open-source license as the core Brian 2 simulator (BSD-style).  
See the `LICENSE` file in this repository for full details.