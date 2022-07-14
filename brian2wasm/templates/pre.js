var brian_results = {};

function add_results(owner, varname, dtype, array_filename) {
    let data = null;
    if (dtype == 'double') {
        data = new Float64Array(FS.readFile(array_filename).buffer);
    } else if (dtype == 'float') {
        data = new Float32Array(FS.readFile(array_filename).buffer);
    } else if (dtype == 'int32_t') {
        data = new Int32Array(FS.readFile(array_filename).buffer);
    } else if (dtype == 'int64_t') {
        data = new BigInt64Array(FS.readFile(array_filename).buffer);
    } else {
        console.log('Unknown dtype: ' + dtype);
    }
    if (!(owner in brian_results)) {
        brian_results[owner] = {};
    }
    brian_results[owner][varname] = data;
}