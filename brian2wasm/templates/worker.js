importScripts('./wasm_module.js');

self.onmessage = e => {
    _arguments = [];
    if (e.data) {
        args = e.data;
        for (let key in args) {
            _arguments.push(`${key}=${args[key]}`);
        }
    }

    Module().then(function (module) {
        console.log(_arguments);
        module.callMain(_arguments);
        postMessage({ type: 'results', results: module['brian_results'] })
    });
};