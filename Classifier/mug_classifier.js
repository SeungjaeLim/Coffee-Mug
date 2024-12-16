// const Module = require('./node/edge-impulse-standalone'); // First module
// const Module2 = require('./node copy/edge-impulse-standalone'); // Second module
const Module_rotate = require('./node_rotate/edge-impulse-standalone'); // Second module
const Module_shake = require('./node_shake/edge-impulse-standalone'); // Second module
const Module_tilt = require('./node_tilt/edge-impulse-standalone'); // Second module
const Module_SR = require('./node_SR/edge-impulse-standalone'); // Second module
const fs = require('fs');
const { SerialPort, ReadlineParser } = require('serialport');

// const path = '/dev/tty.usbmodem101'; 
const path = 'COM4';

const baudRate = 115200;

const port = new SerialPort({ path, baudRate });
const parser = port.pipe(new ReadlineParser({delimiter: '\r\n'}));

// Buffer to collect incoming data
let buffer = [];
let loadSensorBuffer = [];
let lightSensorBuffer = [];

// Duration for data collection (in milliseconds)
const WINDOW_DURATION = 2000; // 2 seconds
//number of samples in rolling window
const N = 50;
let features = Array(N).fill(0);

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
            // Removed anomaly field
            results: []
        };

        for (let cx = 0; cx < ret.size(); cx++) {
            let c = ret.get(cx);
            if (props.model_type === 'object_detection' || props.model_type === 'constrained_object_detection') {
                jsResult.results.push({ 
                    label: c.label, 
                    value: c.value, 
                    x: c.x, 
                    y: c.y, 
                    width: c.width, 
                    height: c.height 
                });
            }
            else {
                jsResult.results.push({ label: c.label, value: c.value });
            }
            c.delete();
        }

        if (props.has_visual_anomaly_detection) {
            // Omitted anomaly-related fields
            // jsResult.visual_ad_max = ret.visual_ad_max;
            // jsResult.visual_ad_mean = ret.visual_ad_mean;
            // jsResult.visual_ad_grid_cells = [];
            // for (let cx = 0; cx < ret.visual_ad_grid_cells_size(); cx++) {
            //     let c = ret.visual_ad_grid_cells_get(cx);
            //     jsResult.visual_ad_grid_cells.push({
            //         label: c.label, value: c.value,
            //         x: c.x, y: c.y, width: c.width, height: c.height 
            //     });
            //     c.delete();
            // }
        }

        ret.delete();

        return jsResult;
    }

    classifyContinuous(rawData, enablePerfCal = true) {
        if (!this.classifierInitialized) throw new Error('Module is not initialized');

        let props = this.module.get_properties();

        const obj = this._arrayToHeap(rawData);
        let ret = this.module.run_classifier_continuous(obj.buffer.byteOffset, rawData.length, false, enablePerfCal);
        this.module._free(obj.ptr);

        if (ret.result !== 0) {
            throw new Error('Classification failed (err code: ' + ret.result + ')');
        }


        let jsResult = {
            anomaly: ret.anomaly,
            visual_ad_max: ret.visual_ad_max,
            visual_ad_mean: ret.visual_ad_mean,
            results: []
        };

        for (let cx = 0; cx < ret.size(); cx++) {
            let c = ret.get(cx);
            if (props.model_type === 'object_detection' || props.model_type === 'constrained_object_detection' || props.model_type === 'visual_anomaly') {
                jsResult.results.push({ label: c.label, value: c.value, x: c.x, y: c.y, width: c.width, height: c.height });
            }
            else {
                jsResult.results.push({ label: c.label, value: c.value });
            }
            c.delete();
        }

        ret.delete();

        return jsResult;
    }

    getProperties() {
        return this.module.get_properties();
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

//creating instance for shake classifier
let classifier_shake = new EdgeImpulseClassifier(Module_shake);
//creating instance for rotate classifier
let classifier_rotate = new EdgeImpulseClassifier(Module_rotate);
//creating instance for tilt classifier
let classifier_tilt = new EdgeImpulseClassifier(Module_tilt);

let classifier_SR = new EdgeImpulseClassifier(Module_SR);

// Function to determine event type: grabbed, shaken, or both
function determineEventType(results) {
    const shakeLabel = results.Shake?.results?.find(r => r.label === 'shake' && r.value > 0.9);
    const rotateLabel = results.Rotate?.results?.find(r => r.label === 'rotate' && r.value > 0.9);
    const tiltLabel = results.Tilt;

    if(tiltLabel){
        return "Mug tilted";
    }
    else if (shakeLabel && rotateLabel) {
        return "Mug rotated back and forth and shaken";
    } else if (shakeLabel) {
        return "Mug shaken";
    } else if (rotateLabel) {
        return "Mug rotated back and forth";
    }
    return null;
}

// Function to format results for summary
function formatResultsForSummary(results) {
    const timestamp = new Date(results.timestamp);
    const timeKey = timestamp.toTimeString().slice(0, 5); // Extract "HH:MM"

    const loadSensor = results.LoadSensor || 'Unknown';
    const lightSensor = results.LightSensor || 'Unknown';

    const eventType = determineEventType(results);

    if (!eventType) return null; // No valid event detected

    const summary = [
        eventType,  // "Mug grabbed", "Mug shaken", or both
        loadSensor, // Load sensor classification
        lightSensor // Light sensor classification
    ].join(", "); // Combine into "Mug grabbed, Halfway, Dim"

    return { [timeKey]: summary };
}

function writeResultsToFile(results) {
    if (determineEventType(results) === null) {
        return; // Do nothing if mug is not both grabbed and shaken
    }

    const summary = formatResultsForSummary(results);

    // Read and update existing JSON file
    fs.readFile('../input.json', 'utf8', (err, data) => {
        let summarizedData = {};

        if (!err && data.trim() !== '') {
            try {
                const jsonData = JSON.parse(data);
                summarizedData = Object.assign({}, ...jsonData.map(obj => obj));
            } catch (parseErr) {
                console.error('Error parsing JSON data:', parseErr);
            }
        }

        // Add the new summary entry
        summarizedData = { ...summarizedData, ...summary };

        // Write the updated data back to the file
        const dataToWrite = JSON.stringify([summarizedData], null, 2);
        fs.writeFile('../input.json', dataToWrite, (err) => {
            if (err) {
                console.error('Error writing to file:', err);
            } else {
                console.log('Results summarized and saved to input.json');
            }
        });
    });
}

Promise.all([
    // classifier_shake.init(),
    // classifier_rotate.init(),
    classifier_tilt.init(),
    classifier_SR.init()
]).then(()=>{
    setInterval(() => {
        if (buffer.length === 0) {
            console.log('No data collected in this window.');
            return;
        }
        if (buffer.length % 6 !== 0) {
            console.warn(`Buffer length (${buffer.length}) is not a multiple of 6. Trimming excess values.`);
            buffer = buffer.slice(0, Math.floor(buffer.length / 6) * 6);
        }
        const dataToClassify = [...buffer];
        const dataForSR = dataToClassify.filter((_, index) => index % 6 === 0 || index % 6 === 2 || index % 6 === 4);

        // console.log(dataToClassify);
        buffer = [];

        try{
            // Hard-Coding

            // Analyze the accelerometer and gyroscope data for tilt detection
            let tiltDetected = false; // Default value if no tilt is detected
            const TILT_THRESHOLD_ACCEL = 0.5; // Threshold for accelerometer tilt detection
            // const TILT_THRESHOLD_GYRO = 20;  // Threshold for gyroscope tilt detection

            // Iterate through the buffer (chunks of 6 values: ax, ay, az, gx, gy, gz)
            for (let i = 0; i < dataToClassify.length; i += 6) {
                const ax = dataToClassify[i];
                const ay = dataToClassify[i + 1];
                const az = dataToClassify[i + 2];
                const gx = dataToClassify[i + 3];
                const gy = dataToClassify[i + 4];
                const gz = dataToClassify[i + 5];
            
            // Hard-coded tilt detection based on accelerometer
                if (Math.abs(ay) < 0.7 && (Math.abs(ax) > TILT_THRESHOLD_ACCEL || Math.abs(az) > TILT_THRESHOLD_ACCEL)) {
                    // tiltDetected = 'Tilt Detected (Accelerometer)';
                    tiltDetected=true;
                    break;
                }

                // Additional detection based on gyroscope
                // if (Math.abs(gx) > TILT_THRESHOLD_GYRO  || Math.abs(gz) > TILT_THRESHOLD_GYRO) {
                //     tiltDetected = 'Tilt Detected (Gyroscope)';
                //     break;
                // }
            }
            
            // console.log('Tilt Detection:', tiltDetected);
            //////////////
            const shakeResult = classifier_shake.classify(dataToClassify);
            const rotateResult = classifier_rotate.classify(dataToClassify);
            // const tiltResult = classifier_tilt.classify(dataToClassify);
            const tiltResult = tiltDetected;
            const srResult=classifier_SR.classify(dataForSR);


            delete shakeResult.anomaly;
            delete rotateResult.anomaly;
            // delete tiltResult.anomaly;
            delete srResult.anomaly;

            const filterResults = (res, label) => ({
                results: res.results.filter(r => r.label === label || r.label === 'default')
            });

            const filteredShake = filterResults(srResult, 'shake');
            const filteredRotate = filterResults(srResult, 'rotate');
            // const filteredTilt = filterResults(tiltResult, 'tilt');
            

            const latestLoadValue = loadSensorBuffer.length > 0 ? loadSensorBuffer[loadSensorBuffer.length - 1] : null;
            const latestLightValue = lightSensorBuffer.length > 0 ? lightSensorBuffer[lightSensorBuffer.length - 1] : null;

            //i think these values are not correct
            let loadClassification = 'Unknown';
            if (latestLoadValue !== null) {
                if (latestLoadValue < 10000) {
                    loadClassification = 'Almost Empty';
                } else if (latestLoadValue >= 10000 && latestLoadValue < 46000) {
                    loadClassification = 'Halfway';
                } else if (latestLoadValue >= 46000) {
                    loadClassification = 'Almost Full';
                }
            }

            let lightClassification = 'Unknown';
            if (latestLightValue !== null) {
                //we need to adjust the thresholds here
                if (latestLightValue < 1000) {
                    lightClassification = 'Dark';
                } else if (latestLightValue >= 1000 && latestLightValue < 28000) {
                    lightClassification = 'Dim';
                } else if (latestLightValue >= 28000 && latestLightValue < 46000) {
                    lightClassification = 'Bright';
                } else if (latestLightValue >= 46000) {
                    lightClassification = 'Very Bright';
                }
            }

            console.log('live classification:');
            console.log('Shake:', filteredShake);
            console.log('Rotate:', filteredRotate);
            console.log('Tilt:', tiltResult);
            console.log('Load Sensor:', loadClassification);
            console.log('Light Sensor:', lightClassification);
            console.log('');


            const resultsToSave = {
                Shake: filteredShake,
                Rotate: filteredRotate,
                Tilt: tiltResult,
                LoadSensor: loadClassification,
                LightSensor: lightClassification,
                timestamp: new Date().toISOString()
            };
            writeResultsToFile(resultsToSave);

        } catch (err) {
            console.error('classification error:', err);
        }

    }, WINDOW_DURATION);
    parser.on('data', (data) => {
        const parts = data.trim().split(',');
        if (parts.length < 6) {
            console.warn(`Received data with insufficient values: ${data}`);
            return;
        }
        const firstSix = parts.slice(0, 6).map(value => parseFloat(value));

        const loadSensorValue = parseInt(parts[6], 10);
        const lightSensorValue = parseInt(parts[7], 10);

        buffer.push(...firstSix);
        loadSensorBuffer.push(loadSensorValue);
        lightSensorBuffer.push(lightSensorValue);
    });

}).catch(err=> {
    console.error('failed to initialize classifiers', err);
});