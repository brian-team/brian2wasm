class BrianSimulation {
    constructor(result_plots, progress, run_button) {
        this.worker = new Worker('worker.js');
        this.result_plots = (typeof result_plots !== "undefined") ? result_plots : [];
        this.plot_funcs = [];
        this.progress = (typeof progress !== "undefined") ? progress : {};
        this.run_button = run_button;

    }

    init() {
        this.run_button = document.getElementById(this.run_button);
        this.progress_bar = document.getElementById(this.progress.bar_id);
        this.progress_text = document.getElementById(this.progress.text_id);
        // Progress reports
        if (this.progress.type === 'bar') {
            this.report = (event) => {
                this.progress_bar.value = event.data.completed;
                this.progress_text.innerHTML = `${Math.round(event.data.completed * event.data.duration * 1000, 0)}ms (<b>${Math.round(event.data.completed * 100., 0)} %</b>).`
            }
        } else {
            console.warn('Unknown progress type ' + this.progress.type);
        }

        // result plots
        this.result_plots.forEach(result_plot => {
            if (result_plot.type === 'raster') {
                let plot = (event) => {
                    let layout = {
                        title: {
                            text: 'Spiking activity'
                        },
                        xaxis: {
                            title: {
                                text: 'Time (s)'
                            }
                        },
                        yaxis: {
                            title: {
                                text: 'Neuron index'
                            }
                        }
                    };
                    var brian_results = event.data.results;
                    var spikes = {
                        x: brian_results['spikemonitor'].t,
                        y: brian_results['spikemonitor'].i,
                        mode: 'markers',
                        marker: { size: 2 },
                        type: 'scatter'
                    };
                    Plotly.react(result_plot.canvas, [spikes], layout);
                };
                this.plot_funcs.push(plot);
            } else {
                console.warn('Unsupported plot type ' + result_plot.type);
            }
        });

        // Trigger report and plots by worker messages
        this.worker.onmessage = (e) => {
            if (e.data.type === 'results') {
                this.plot_funcs.forEach(plot => {
                    plot(e);
                });
                this.run_button.disabled = false;
            }
            else if (e.data.type == 'progress') {
                if (this.report)
                    this.report(e);
            } else {
                console.log('Received unknown message type');
                console.log(e);
            }
        }
    }

    run() {
        // disable run button
        this.run_button.disabled = true;
        // set progress bar to undetermined state
        if (this.progress.type == 'bar')
            document.getElementById(this.progress.bar_id).removeAttribute('value');
        // send message to worker
        this.worker.postMessage({});
    }
}