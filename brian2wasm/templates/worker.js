importScripts('./wasm_module.js');

self.onmessage = e => {
    Module().then(function (module) {
        postMessage({ type: 'results', results: module['brian_results'] })
    });
};