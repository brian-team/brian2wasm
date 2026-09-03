importScripts('./wasm_module.js');

self.onmessage = async e => {
    _arguments = [];
    if (e.data) {
        args = e.data;
        for (let key in args) {
            _arguments.push(`${key}=${args[key]}`);
        }
    }

    try {
        const module = await Module();
        console.log(_arguments);
        module.callMain(_arguments);
        postMessage({ type: 'results', results: module['brian_results'] });
    } catch (error) {
        postMessage({ type: 'error', message: (error && error.message) ? error.message : String(error) });
    }
};

// Safety net for synchronous errors that don't go through the promise
// chain above (e.g. errors thrown directly by the Emscripten runtime).
self.onerror = function (message, source, lineno, colno, error) {
    postMessage({ type: 'error', message: message });
};