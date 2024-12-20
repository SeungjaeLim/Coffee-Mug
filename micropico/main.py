import os
from collections import deque
import time
from light import LightSensor
from load import LoadSensor
from imu import IMU

# Debugging: Print current working directory and file list
print(os.getcwd())  # Current working directory
print(os.listdir())  # List of files in the current directory

# Initialize sensors
imu = IMU()
light_sensor = LightSensor(pin=27, threshold=30000)  # Light threshold
load_sensor = LoadSensor(pin=26, threshold=15000)    # Load threshold

# Sliding window settings
WINDOW_DURATION = 2         # Sliding window duration in seconds
SAMPLE_INTERVAL = 0.01      # Data collection interval (10ms)
WINDOW_SIZE = int(WINDOW_DURATION / SAMPLE_INTERVAL)  # Number of samples in the window

# Buffers for sliding window
load_sensor_buffer = deque(maxlen=WINDOW_SIZE)
light_sensor_buffer = deque(maxlen=WINDOW_SIZE)

def calculate_sliding_average(buffer):
    """
    Calculate the average value of a sliding window buffer.

    Parameters:
    - buffer (deque): Sliding window buffer containing sensor values.

    Returns:
    - float: Average value of the buffer.
    """
    if len(buffer) == 0:
        return 0.0
    return sum(buffer) / len(buffer)

def classify_coffee(light_sensor, load_sensor, light_avg, load_avg):
    """
    Classify coffee type based on light and load sensor readings.

    Parameters:
    - light_sensor (LightSensor): Instance of LightSensor.
    - load_sensor (LoadSensor): Instance of LoadSensor.
    - light_avg (float): Average light sensor value.
    - load_avg (float): Average load sensor value.

    Returns:
    - str: 'Night Coffee', 'Day Coffee', or 'No Coffee Detected'.
    """
    if load_avg > 1000:  # Load sensor detects coffee
        if light_avg >= light_sensor.threshold:  # Bright light indicates day
            return "Day Coffee"
        else:  # Dim or dark light indicates night
            return "Night Coffee"
    return "No Coffee Detected"

# Main loop
if __name__ == "__main__":
    while True:
        # Collect IMU data
        accel_data = imu.read_accel_data()
        gyro_data = imu.read_gyro_data()

        # Read sensor data
        load_value = load_sensor.read()
        light_value = light_sensor.read()

        # Append data to sliding window buffers
        load_sensor_buffer.append(load_value)
        light_sensor_buffer.append(light_value)

        # Calculate sliding window averages
        load_avg = calculate_sliding_average(load_sensor_buffer)
        light_avg = calculate_sliding_average(light_sensor_buffer)

        # Classify coffee based on sensor averages
        coffee_type = classify_coffee(light_sensor, load_sensor, light_avg, load_avg)

        # Print data output
        data = [
            accel_data[0], accel_data[1], accel_data[2],  # Accelerometer data
            gyro_data[0], gyro_data[1], gyro_data[2],    # Gyroscope data
            load_avg, light_avg, coffee_type             # Averages and classification
        ]
        print(*data, sep=',')

        # Additional derived metrics
        tilt = [accel_data[0], accel_data[1], accel_data[2]]
        rotate_and_shake = [accel_data[0], accel_data[2], gyro_data[1]]

        # Optional debug prints
        # print("Tilt Data:", *tilt, sep=',')
        # print("Rotate and Shake:", *rotate_and_shake, sep=',')

        # Delay to match the sampling interval
        time.sleep(SAMPLE_INTERVAL)
