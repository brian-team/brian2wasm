var brian_results = {};
Module['brian_results'] = brian_results;

function add_results(owner, varname, dtype, array_filename, n1, n2 = 0) {
    let data = null;
    let array_class = null;
    if (dtype == 'double') {
       array_class = Float64Array;
    } else if (dtype == 'float') {
        array_class = Float32Array;
    } else if (dtype == 'int32_t') {
        array_class = Int32Array;
    } else if (dtype == 'int64_t') {
        array_class = BigInt64Array;
    } else if (dtype == 'char') {
        array_class = Uint8Array;
    } else {
        console.log('Unknown dtype: ' + dtype);
        return;
    }
    if (n2 === 0) {
        data = new array_class(FS.readFile(array_filename).buffer);
    } else {
        const flat_data = new array_class(FS.readFile(array_filename).buffer);
        data = [];
        for (let i=0; i < n2; i++) {
            let neuron_values = [];
            for (let j=0; j < n1; j++) {
                neuron_values.push(flat_data[j*n2 + i]);
            }
            data.push(new array_class(neuron_values));
        }
    }
    if (!(owner in brian_results)) {
        brian_results[owner] = {};
    }
    brian_results[owner][varname] = data;
}

Module['print'] = function(text) { console.log('Brian stdout: ' + text) };
Module['printErr'] = function(text) { console.log('Brian stderr: ' + text) };
