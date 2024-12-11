// const Module = require('./node/edge-impulse-standalone'); // First module
// const Module2 = require('./node copy/edge-impulse-standalone'); // Second module
const Module_rotate = require('./node_rotate/edge-impulse-standalone'); // Second module
const Module_shake = require('./node_shake/edge-impulse-standalone'); // Second module
const Module_tilt = require('./node_tilt/edge-impulse-standalone'); // Second module
const fs = require('fs');

class EdgeImpulseClassifier {
    constructor(module) {
        this.module = module;
        this.classifierInitialized = false;
        this.module.onRuntimeInitialized = () => {
            this.classifierInitialized = true;
        };
    }

    init() {
        if (this.classifierInitialized) return Promise.resolve();

        return new Promise((resolve) => {
            this.module.onRuntimeInitialized = () => {
                this.classifierInitialized = true;
                this.module.init();
                resolve();
            };
        });
    }

    getProjectInfo() {
        if (!this.classifierInitialized) throw new Error('Module is not initialized');
        return this.module.get_project();
    }

    classify(rawData, debug = false) {
        if (!this.classifierInitialized) throw new Error('Module is not initialized');

        let props = this.module.get_properties();

        const obj = this._arrayToHeap(rawData);
        let ret = this.module.run_classifier(obj.buffer.byteOffset, rawData.length, debug);
        this.module._free(obj.ptr);

        if (ret.result !== 0) {
            throw new Error('Classification failed (err code: ' + ret.result + ')');
        }

        let jsResult = {
            anomaly: ret.anomaly,
            results: []
        };

        for (let cx = 0; cx < ret.size(); cx++) {
            let c = ret.get(cx);
            if (props.model_type === 'object_detection' || props.model_type === 'constrained_object_detection') {
                jsResult.results.push({ label: c.label, value: c.value, x: c.x, y: c.y, width: c.width, height: c.height });
            } else {
                jsResult.results.push({ label: c.label, value: c.value });
            }
            c.delete();
        }

        if (props.has_visual_anomaly_detection) {
            jsResult.visual_ad_max = ret.visual_ad_max;
            jsResult.visual_ad_mean = ret.visual_ad_mean;
            jsResult.visual_ad_grid_cells = [];
            for (let cx = 0; cx < ret.visual_ad_grid_cells_size(); cx++) {
                let c = ret.visual_ad_grid_cells_get(cx);
                jsResult.visual_ad_grid_cells.push({ label: c.label, value: c.value, x: c.x, y: c.y, width: c.width, height: c.height });
                c.delete();
            }
        }

        ret.delete();

        return jsResult;
    }

    _arrayToHeap(data) {
        let typedArray = new Float32Array(data);
        let numBytes = typedArray.length * typedArray.BYTES_PER_ELEMENT;
        let ptr = this.module._malloc(numBytes);
        let heapBytes = new Uint8Array(this.module.HEAPU8.buffer, ptr, numBytes);
        heapBytes.set(new Uint8Array(typedArray.buffer));
        return { ptr: ptr, buffer: heapBytes };
    }
}

// Example input: replace this with your features or file
// const inputFeatures = fs.readFileSync('./node/data.txt', 'utf-8').trim().split(',').map(Number); // Input data
const temp = fs.readFileSync('./rotate.txt', 'utf-8').trim().split('\r\n'); // Input data
const inputFeatures_shake = temp.map(row => [row.split(',')[0], row.split(',')[2]]).flat().map(Number);
const inputFeatures_rotate = temp.map(row => [row.split(',')[4]]).flat();
const inputFeatures_tilt = temp.map(row => [row.split(',')[0],row.split(',')[1],row.split(',')[2]]).flat();
// console.log(inputFeatures_shake)
// console.log(temp)

let classifier_shake = new EdgeImpulseClassifier(Module_shake);
classifier_shake.init().then(() => {
    // let project = classifier_shake.getProjectInfo();
    // console.log('Running inference for classifier shake:', project.owner + ' / ' + project.name + ' (version ' + project.deploy_version + ')');

    let result = classifier_shake.classify(inputFeatures_shake);
    console.log('Result from classifier shake:', result);
}).catch(err => {
    console.error('Failed to initialize classifier shake', err);
});

let classifier_rotate = new EdgeImpulseClassifier(Module_rotate);
classifier_rotate.init().then(() => {
    // let project = classifier_rotate.getProjectInfo();
    // console.log('Running inference for classifier rotate:', project.owner + ' / ' + project.name + ' (version ' + project.deploy_version + ')');

    let result = classifier_rotate.classify(inputFeatures_rotate);
    console.log('Result from classifier rotate:', result);
}).catch(err => {
    console.error('Failed to initialize classifier rotate', err);
});

let classifier_tilt = new EdgeImpulseClassifier(Module_tilt);
classifier_tilt.init().then(() => {
    // let project = classifier_tilt.getProjectInfo();
    // console.log('Running inference for classifier rotate:', project.owner + ' / ' + project.name + ' (version ' + project.deploy_version + ')');

    let result = classifier_tilt.classify(inputFeatures_tilt);
    console.log('Result from classifier tilt:', result);
}).catch(err => {
    console.error('Failed to initialize classifier rotate', err);
});
