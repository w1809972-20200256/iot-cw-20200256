import time
from ustruct import unpack
from array import array

# BMP280 I2C Address
BMP280_I2CADDR = 0x76

# Registers
BMP280_REGISTER_CONTROL = 0xF4
BMP280_REGISTER_CONFIG = 0xF5
BMP280_REGISTER_DATA = 0xF7
BMP280_REGISTER_CALIB = 0x88

# Operating Modes
BMP280_OSAMPLE = {1: 0x20, 2: 0x40, 4: 0x60, 8: 0x80, 16: 0xA0}

class BMP280:
    def __init__(self, i2c, mode=1, address=BMP280_I2CADDR):
        if mode not in BMP280_OSAMPLE:
            raise ValueError("Invalid mode value")
        self.i2c = i2c
        self.address = address
        self._mode = BMP280_OSAMPLE[mode] | 0x03  # Set normal mode
        self._buffer = bytearray(6)
        self.t_fine = 0

        # Load calibration data
        calib_data = self.i2c.readfrom_mem(self.address, BMP280_REGISTER_CALIB, 24)
        self.dig_T1, self.dig_T2, self.dig_T3, self.dig_P1, \
        self.dig_P2, self.dig_P3, self.dig_P4, self.dig_P5, \
        self.dig_P6, self.dig_P7, self.dig_P8, self.dig_P9 = \
            unpack('<HhhHhhhhhhhh', calib_data)

        # Configure sensor
        self.i2c.writeto_mem(self.address, BMP280_REGISTER_CONTROL, bytearray([self._mode]))

    def _read_raw_data(self):
        time.sleep_ms(100)  # Allow conversion time
        self.i2c.readfrom_mem_into(self.address, BMP280_REGISTER_DATA, self._buffer)
        raw_press = ((self._buffer[0] << 16) | (self._buffer[1] << 8) | self._buffer[2]) >> 4
        raw_temp = ((self._buffer[3] << 16) | (self._buffer[4] << 8) | self._buffer[5]) >> 4
        return raw_temp, raw_press

    def _compensate_temperature(self, raw_temp):
        var1 = ((raw_temp >> 3) - (self.dig_T1 << 1)) * self.dig_T2 >> 11
        var2 = ((((raw_temp >> 4) - self.dig_T1) * ((raw_temp >> 4) - self.dig_T1)) >> 12) * self.dig_T3 >> 14
        self.t_fine = var1 + var2
        return (self.t_fine * 5 + 128) >> 8

    def _compensate_pressure(self, raw_press):
        var1 = self.t_fine - 128000
        var2 = var1 * var1 * self.dig_P6 >> 16
        var2 += (var1 * self.dig_P5) << 17
        var2 += self.dig_P4 << 35
        var1 = ((var1 * var1 * self.dig_P3) >> 8) + ((var1 * self.dig_P2) << 12)
        var1 = (((1 << 47) + var1) * self.dig_P1) >> 33
        if var1 == 0:
            return 0  # Avoid division by zero
        p = (((1048576 - raw_press) << 31) - var2) // var1
        var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
        var2 = (self.dig_P8 * p) >> 19
        return ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)

    def read_compensated_data(self):
        raw_temp, raw_press = self._read_raw_data()
        temp = self._compensate_temperature(raw_temp)
        pressure = self._compensate_pressure(raw_press)
        return temp / 100.0, pressure / 256.0

    @property
    def temperature(self):
        return self.read_compensated_data()[0]

    @property
    def pressure(self):
        return self.read_compensated_data()[1]
