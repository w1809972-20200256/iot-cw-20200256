import bme280
import machine
import time
from machine import Pin, I2C
import network
import urequests
import json
import gc
import random

def getTime():
    """
    This function fetches the time from a public API endpoint, with the specified timezone in the endpoint parameters
    and parses the time value using the json librarys
    """
    res=urequests.get(url=TIME_URL)
    time=json.loads(res.text)["dateTime"]
    res.close()
    return time

def connectWifi():
    """
    This function uses the Pico W's inbuilt-wifi module to attempt to connect to a mobile hotspot using the hard-coded credentials
    and obtain and IP address.
    """
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        while not wlan.isconnected() and wlan.status() >= 0:
            print("Waiting to connect: ")
            time.sleep(1)
        print(wlan.ifconfig()[0])
    else:
        print("Wifi is already connected...")
        print(wlan.ifconfig()[0])
        print(getTime())
        
def sendToSpreadsheet(time, temp, pressure):
    """
    This function sends the collected data from the sensors to the data logger source, In this case the Appscript for Google Sheets.
    """
    try:
        url=f"{SCRIPT_URL}?time={time}&temp={temp}&pressure={pressure}"
        print(url)
        res=urequests.get(url=url)
        res.close()
        gc.collect()

    except NameError:
        print("An Error has occured: " + NameError)
        
        
wlan = network.WLAN(network.STA_IF)
board_led=machine.Pin("LED", machine.Pin.OUT)
board_led.off()

ssid = "Galaxy A53"
password = "abc123456"


SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz6yKjic2ygZpyFZFPdMy6BYjJPMlfMjt385p27YiSSGAhIQWlUp3UtkpqLgAokY9cS9g/exec"
TIME_URL = "https://timeapi.io/api/Time/current/zone?timeZone=Asia/Colombo"
connectWifi()
wlan.active(True)
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
bmp = bme280.BMP280(i2c=i2c)

for i in range(10):
    timestamp = f"{getTime()}" #print timestamp value
    # Turn LED on when taking reading
    board_led.on()
    
    # BMP Sensor
    bmp_tempC = bmp.temperature
    bmp_pressure = bmp.pressure
    print("Time stamp is" + timestamp)
    sendToSpreadsheet(time=timestamp, temp=bmp_tempC, pressure=bmp_pressure) #send values
    board_led.off()   
    time.sleep(60)