from machine import Pin, I2C
import time

class IMU:
    def __init__(self, i2c_bus=0, scl_pin=21, sda_pin=20, freq=400000):
        """
        Initializes the IMU sensor (MPU-6500).

        Parameters:
        - i2c_bus: int - I2C bus number.
        - scl_pin: int - GPIO pin for SCL.
        - sda_pin: int - GPIO pin for SDA.
        - freq: int - I2C frequency in Hz.
        """
        self.i2c = I2C(i2c_bus, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=freq)
        print("I2C addresses:", self.i2c.scan())
        self.MPU6500_ADDR = 0x68
        
        self.PWR_MGMT_1 = 0x6B
        self.GYRO_CONFIG = 0x1B
        self.ACCEL_CONFIG = 0x1C
        self.ACCEL_XOUT_H = 0x3B
        self.GYRO_XOUT_H = 0x43

        self.ACCEL_SCALE = 2.0 / 32768  # Scaling for accelerometer (±2g)
        self.GYRO_SCALE = 250.0 / 32768  # Scaling for gyroscope (±250°/s)

        self.N = 10  # Moving average window size
        self.accel_window = {'X': [0] * self.N, 'Y': [0] * self.N, 'Z': [0] * self.N}
        self.gyro_window = {'X': [0] * self.N, 'Y': [0] * self.N, 'Z': [0] * self.N}

        self._initialize_mpu()

    def _initialize_mpu(self):
        """Initializes the MPU-6500 sensor."""
        self.i2c.writeto_mem(self.MPU6500_ADDR, self.PWR_MGMT_1, b'\x00')  # Wake up MPU
        time.sleep(0.1)
        self.i2c.writeto_mem(self.MPU6500_ADDR, self.ACCEL_CONFIG, b'\x00')  # Set accelerometer to ±2g
        self.i2c.writeto_mem(self.MPU6500_ADDR, self.GYRO_CONFIG, b'\x00')  # Set gyroscope to ±250°/s

    def _read_word(self, reg):
        """Reads a signed 16-bit value from the specified register."""
        high = self.i2c.readfrom_mem(self.MPU6500_ADDR, reg, 1)[0]
        low = self.i2c.readfrom_mem(self.MPU6500_ADDR, reg + 1, 1)[0]
        val = (high << 8) + low
        if val >= 0x8000:  # Convert to signed value
            val -= 0x10000
        return val

    def _moving_average(self, axis, value, window):
        """Applies a moving average filter to the given axis value."""
        window[axis] = window[axis][1:] + [value]
        return sum(window[axis]) / self.N

    def read_accel_data(self):
        """Reads and returns filtered accelerometer data (g's)."""
        ax = self._read_word(self.ACCEL_XOUT_H) * self.ACCEL_SCALE
        ay = self._read_word(self.ACCEL_XOUT_H + 2) * self.ACCEL_SCALE
        az = self._read_word(self.ACCEL_XOUT_H + 4) * self.ACCEL_SCALE

        ax_filtered = self._moving_average('X', ax, self.accel_window)
        ay_filtered = self._moving_average('Y', ay, self.accel_window)
        az_filtered = self._moving_average('Z', az, self.accel_window)

        return ax_filtered, ay_filtered, az_filtered

    def read_gyro_data(self):
        """Reads and returns filtered gyroscope data (degrees per second)."""
        gx = self._read_word(self.GYRO_XOUT_H) * self.GYRO_SCALE
        gy = self._read_word(self.GYRO_XOUT_H + 2) * self.GYRO_SCALE
        gz = self._read_word(self.GYRO_XOUT_H + 4) * self.GYRO_SCALE

        gx_filtered = self._moving_average('X', gx, self.gyro_window)
        gy_filtered = self._moving_average('Y', gy, self.gyro_window)
        gz_filtered = self._moving_average('Z', gz, self.gyro_window)

        return gx_filtered, gy_filtered, gz_filtered

# Example usage in main.py:
# imu = IMU()
# accel_data = imu.read_accel_data()
# gyro_data = imu.read_gyro_data()
