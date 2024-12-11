from machine import Pin, I2C
import time

# Define I2C pins and bus
i2c = I2C(1, scl=Pin(27), sda=Pin(26), freq=400000) 

# MPU-6500 I2C address (typically 0x68, can be 0x69 if AD0 is high)
MPU6500_ADDR = 0x68

# MPU-6500 Register Addresses
PWR_MGMT_1 = 0x6B
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
ACCEL_XOUT_H = 0x3B
ACCEL_XOUT_L = 0x3C
ACCEL_YOUT_H = 0x3D
ACCEL_YOUT_L = 0x3E
ACCEL_ZOUT_H = 0x3F
ACCEL_ZOUT_L = 0x40
GYRO_XOUT_H = 0x43
GYRO_XOUT_L = 0x44
GYRO_YOUT_H = 0x45
GYRO_YOUT_L = 0x46
GYRO_ZOUT_H = 0x47
GYRO_ZOUT_L = 0x48

# Moving average filter parameters
N = 10  # Number of samples for moving average
accel_window = {'X': [0] * N, 'Y': [0] * N, 'Z': [0] * N}
gyro_window = {'X': [0] * N, 'Y': [0] * N, 'Z': [0] * N}

def moving_average(axis, value, window):
    # Update the moving average window for the given axis
    window[axis] = window[axis][1:] + [value]
    return sum(window[axis]) / N

# Initialize MPU-6500
def initialize_mpu():
    # Wake up the MPU-6500
    i2c.writeto_mem(MPU6500_ADDR, PWR_MGMT_1, b'\x00')  # Set to 0 to wake up
    time.sleep(0.1)

    # Set accelerometer range to ±2g
    i2c.writeto_mem(MPU6500_ADDR, ACCEL_CONFIG, b'\x00')  # 0x00 for ±2g

    # Set gyroscope range to ±250 degrees per second
    i2c.writeto_mem(MPU6500_ADDR, GYRO_CONFIG, b'\x00')  # 0x00 for ±250 dps

# Read 2 bytes from a register
def read_word(reg):
    high = i2c.readfrom_mem(MPU6500_ADDR, reg, 1)[0]
    low = i2c.readfrom_mem(MPU6500_ADDR, reg + 1, 1)[0]
    val = (high << 8) + low
    if val >= 0x8000:  # Convert to signed value
        val -= 0x10000
    return val

# Constants for scaling
ACCEL_SCALE = 2.0 / 32768  # ±2g (16-bit, raw count range -32768 to 32767)
GYRO_SCALE = 250.0 / 32768  # ±250°/s (16-bit, raw count range -32768 to 32767)

# Read accelerometer data and scale to g's
def read_accel_data():
    ax = read_word(ACCEL_XOUT_H) * ACCEL_SCALE
    ay = read_word(ACCEL_YOUT_H) * ACCEL_SCALE
    az = read_word(ACCEL_ZOUT_H) * ACCEL_SCALE
    return ax, ay, az

# Read gyroscope data and scale to degrees per second
def read_gyro_data():
    gx = read_word(GYRO_XOUT_H) * GYRO_SCALE
    gy = read_word(GYRO_YOUT_H) * GYRO_SCALE
    gz = read_word(GYRO_ZOUT_H) * GYRO_SCALE
    return gx, gy, gz

# Main loop
initialize_mpu()

while True:
    # Read data from MPU-6500
    ax, ay, az = read_accel_data()
    gx, gy, gz = read_gyro_data()

    # Apply moving average filter
    ax_filtered = moving_average('X', ax, accel_window)
    ay_filtered = moving_average('Y', ay, accel_window)
    az_filtered = moving_average('Z', az, accel_window)

    gx_filtered = moving_average('X', gx, gyro_window)
    gy_filtered = moving_average('Y', gy, gyro_window)
    gz_filtered = moving_average('Z', gz, gyro_window)

    # Print filtered accelerometer and gyroscope data
    # print(f"Accel: X={ax_filtered:.3f}g Y={ay_filtered:.3f}g Z={az_filtered:.3f}g")
    # print(f"Gyro: X={gx_filtered:.3f} deg Y={gy_filtered:.3f} deg Z={gz_filtered:.3f} deg")
    data=[ax_filtered,ay_filtered,az_filtered, gx_filtered,gy_filtered,gz_filtered]
    tilt=[ax_filtered,ay_filtered,az_filtered]
    rotate=[gy_filtered]
    shake=[ax_filtered,az_filtered]
    print(*data, sep=',')
    # print(*shake, sep=',')
    # print(*rotate, sep=',')
    # Wait for a short time before reading again
    time.sleep(0.01)
