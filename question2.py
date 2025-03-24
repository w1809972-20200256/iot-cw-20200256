import network
import socket
from machine import Pin, I2C
from time import sleep
import bme280

ssid = "Galaxy A53"
password = "abc123456"

sensor_temp = machine.ADC(4)
CONVERSION_FACTOR = 3.3 / (65535)
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
bmp = bme280.BMP280(i2c=i2c)

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid,password)
    while wlan.isconnected() == False:
        print("Waiting for connection...")
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f"Connected with IP address of {ip}")
    return ip

def open_socket(ip):
    address = (ip,80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return connection

def webpage(reading):
    ## HTML template
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Pico W Temperature</title>
    <meta http-equiv="refresh" content="10">
</head>
<body style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; text-align: center; background-color: #282c34; color: #ffffff; font-family: Arial, sans-serif;">

    <!-- Large Temperature Emoji -->
    <div style="font-size: 4rem; margin-bottom: 10px;">🌡️</div>

    <h1 style="font-size: 2.5rem; margin-bottom: 10px;">Pico W Live Temperature</h1>

    <p style="font-size: 1.8rem; font-weight: bold; background: #444; padding: 15px 25px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.3);">
        {reading}
    </p>

</body>
</html>
    """
    return str(html)

def serve(connection):
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        
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
        
        reading = bmp_reading + '<br>' + internal_sensor_reading
        html = webpage(reading)
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=UTF-8\r\n"
            "Connection: close\r\n"
            "\r\n"  # Important: Separates headers from the body
            + html
        )
        client.send(response.encode('utf-8'))
        client.close()
        
        
try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()