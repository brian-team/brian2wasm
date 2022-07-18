var brian_results = {};
const ctx = document.getElementById('canvas').getContext('2d');
const brian_chart = new Chart(ctx, {type: 'line',
options: {
    scales: {
        xAxis: {
            ticks: {
                maxTicksLimit: 10
            }
        }
    }
}});

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

function plot_variable(qualified_name) {
    const name_parts = qualified_name.split('.');
    const owner = name_parts[0];
    const varname = name_parts[1];
    // only working for StateMonitor right now
    const time = brian_results[owner]['t'];
    const values = brian_results[owner][varname];
    var datasets = [];
    var labels = [];
    for (let i=0; i < values.length; i++) {
        const per_neuron_points = values[i];
        let dataset = [];
        for (let j=0; j < per_neuron_points.length; j++) {
            dataset.push({x: time[j], y: per_neuron_points[j]});
        }
        datasets.push({data: dataset,
                       label: `Neuron ${i}`});
    }
    brian_chart.data = {datasets: datasets, labels: time};
    brian_chart.update();
}
