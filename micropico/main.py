"""
Main Module: Coffee Sensor System
Classifies coffee as 'Day Coffee' or 'Night Coffee' based on sensor readings.
"""



import os
print(os.getcwd())  # Should print D:\micropico
print(os.listdir())

from light import LightSensor
from load import LoadSensor
from imu import IMU
import time

# Initialize sensors
imu = IMU()
light_sensor = LightSensor(pin=27, threshold=30000)  # Set light threshold
load_sensor = LoadSensor(pin=26, threshold=15000)    # Set load threshold
# Almost empty is under 1000
# Halfway is around 28000
# Almost full is around 46000


def classify_coffee(light_sensor, load_sensor):
    """
    Classifies coffee based on light and load sensor readings.

    Parameters:
    - light_sensor: LightSensor - Instance of LightSensor.
    - load_sensor: LoadSensor - Instance of LoadSensor.

    Returns:
    - str: 'Night Coffee', 'Day Coffee', or 'No Coffee Detected'
    """
    if load_sensor.is_load():
        if light_sensor.is_light():
            return "Day Coffee"
        else:
            return "Night Coffee"
    return "No Coffee Detected"

# Main loop
if __name__ == "__main__":
    while True:
        accel_data = imu.read_accel_data()
        gyro_data = imu.read_gyro_data()
        coffee_type = classify_coffee(light_sensor, load_sensor)
        # print(f"Light: {light_sensor.read()}, Load: {load_sensor.read()}, Coffee Type: {coffee_type}")
        data=[accel_data[0],accel_data[1],accel_data[2],gyro_data[0],gyro_data[1],gyro_data[2], load_sensor.read(), light_sensor.read()]
        print(*data, sep=',')
        tilt=[accel_data[0],accel_data[1],accel_data[2]]
        # rotate=[gyro_data[1]]
        # shake=[accel_data[0],accel_data[2]]
        rotate_and_shake=[accel_data[0],accel_data[2],gyro_data[1]]
        # print(*rotate_and_shake, sep=',')
        time.sleep(0.01)  # Delay to avoid spamming
