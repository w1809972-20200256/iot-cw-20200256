import bme280
from machine import Pin, I2C
from time import sleep



led = machine.Pin('LED', Pin.OUT)
led.off()
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
bmp = bme280.BMP280(i2c=i2c)

while(True):
    # Turn LED on when taking reading
    led.on()
    
    # BMP Sensor
    bmp_tempC = bmp.temperature
    bmp_tempF = (bmp_tempC) * (9/5) + 32
    bmp_pressure = bmp.pressure
    bmp_reading = f'BMP Sensor Readings -> Temperature: {bmp_tempC:.2f}°C / {bmp_tempF:.2f}°F. Pressure: {bmp_pressure:.2f}hPa'

    # Internal Sensor
    CONVERSION_FACTOR = 3.3 / (65535)
    sensor_temp = machine.ADC(4)
    raw_sensor_data = sensor_temp.read_u16() * CONVERSION_FACTOR
    sensor_temperatureC = 27 - (raw_sensor_data - 0.706)/0.001721
    sensor_temperatureF = (sensor_temperatureC) * (9/5) + 32
    internal_sensor_reading = f'Internal Sensor Readings -> Temperature: {sensor_temperatureC:.2f}°C / {sensor_temperatureF:.2f}°F.'

    # Print Data
    print("===========================================================================")
    print(internal_sensor_reading)
    print(bmp_reading)
    print("===========================================================================")

    # Prepare for next cycle
    led.off()
    sleep(1)