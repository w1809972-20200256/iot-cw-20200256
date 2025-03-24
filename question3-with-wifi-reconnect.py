import bme280
import machine
import time
from machine import Pin, I2C, RTC
import network
import urequests
import json
import gc

def getTime():
    """
    Fetches the time from a public API, handling connection errors.
    Falls back to the RTC if the API call fails.
    """
    rtc = RTC()
    try:
        res = urequests.get(url=TIME_URL)
        api_response = json.loads(res.text)
        api_time = api_response["dateTime"]
        res.close()
        
        # Update RTC with the time from API
        try:
            # Parse the ISO 8601 format
            if 'T' in api_time:
                date_part, time_part = api_time.split('T')
                year, month, day = map(int, date_part.split('-'))
                
                # Handle the time part with potential milliseconds
                if '.' in time_part:
                    time_basic, milliseconds = time_part.split('.')
                    hour, minute, second = map(int, time_basic.split(':'))
                else:
                    hour, minute, second = map(int, time_part.split(':'))
                    milliseconds = "0000000"
                
                # Set the RTC
                rtc.datetime((year, month, day, 0, hour, minute, second, 0))
                print("RTC updated successfully")
            else:
                print("API time format not recognized:", api_time)
        except Exception as e:
            print("Failed to update RTC:", e)
            
        # Return the API time directly even if update RTC fails
        return api_time
    except Exception as e:
        print("Error fetching time from API:", e)
        # Fall back to RTC time
        current_time = rtc.datetime()
        
        # Format to match the required format "2025-03-24T02:17:03.6777499"
        year, month, day, _, hour, minute, second, _ = current_time
        formatted_time = f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}.0000000"
        print("Using RTC time:", formatted_time)
        
        return formatted_time

def connectWifi():
    """
    Ensures Wi-Fi connectivity, attempts reconnection if lost.
    """
    wlan.active(True)
    
    if wlan.isconnected():
        print("Already connected with IP address:", wlan.ifconfig()[0])
        return True
    
    print("Connecting to Wi-Fi...")
    wlan.connect(ssid, password)
    
    max_attempts = 10
    attempt = 0
    
    while not wlan.isconnected() and wlan.status() >= 0 and attempt < max_attempts:
        print(f"Attempt {attempt+1}...")
        time.sleep(3)
        attempt += 1
    
    if wlan.isconnected():
        print("Connected with IP address:", wlan.ifconfig()[0])
        return True
    else:
        print("Failed to connect after multiple attempts.")
        return False

def sendToSpreadsheet(time, temp, pressure):
    """
    Attempts to send data to Google Sheets. If unsuccessful, stores data in a buffer.
    Returns True if successful, False otherwise.
    """
    url = f"{SCRIPT_URL}?time={time}&temp={temp}&pressure={pressure}"
    if not wlan.isconnected():
        print("Wi-Fi is disconnected. Attempting to reconnect...")
        if not connectWifi():
            print("Wi-Fi reconnection failed. Storing data locally.")
            store_data_locally(time, temp, pressure)
            return False

    for attempt in range(3):  # Retry sending data up to 3 times
        try:
            print(f"Sending data (Attempt {attempt+1}): {url}")
            res = urequests.get(url=url)
            res.close()
            print("Data sent successfully.")
            gc.collect()
            return True
        except Exception as e:
            print(f"Error sending data (Attempt {attempt+1}): {e}")
            time.sleep(5)

    # Only executes if all send attempts fail
    print("All send attempts failed. Storing data locally.")
    store_data_locally(time, temp, pressure)
    return False

def store_data_locally(time, temp, pressure):
    """
    Saves failed data entries to a local file for later resending.
    """
    try:
        with open("buffer.txt", "a") as file:
            file.write(f"{time},{temp},{pressure}\n")
        print("Data saved locally for retry.")
    except Exception as e:
        print("Failed to store data locally:", e)

def resend_buffered_data():
    """
    Attempts to resend any locally stored data once Wi-Fi is restored.
    Returns the number of successfully resent items.
    """
    if not wlan.isconnected():
        print("Cannot resend buffered data: Wi-Fi not connected")
        return 0        
    try:
        # Check if buffer file exists and read the data
        try:
            with open("buffer.txt", "r") as test_file:
                pass
        except OSError:
            print("No buffer file found.")
            return 0
        with open("buffer.txt", "r") as file:
            lines = file.readlines()
        if not lines:
            print("Buffer is empty.")
            return 0    
        print(f"Found {len(lines)} buffered entries to resend.")
        successful_sends = 0
        remaining_lines = []
        # Process each buffered entry
        for line in lines:
            try:
                time_val, temp, pressure = line.strip().split(",")
                if sendToSpreadsheet(time_val, temp, pressure):
                    successful_sends += 1
                else:
                    # Keep failed sends in the buffer
                    remaining_lines.append(line)
            except Exception as e:
                print(f"Error processing buffered entry: {e}")
                remaining_lines.append(line)
        # Write back any remaining entries
        with open("buffer.txt", "w") as file:
            for line in remaining_lines:
                file.write(line)
            
        print(f"Resent {successful_sends} of {len(lines)} buffered entries.")
        return successful_sends
    except Exception as e:
        print(f"Error in resend_buffered_data: {e}")
        return 0

# Configuration
ssid = "Galaxy A53"
password = "abc123456"

# API URLs
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz6yKjic2ygZpyFZFPdMy6BYjJPMlfMjt385p27YiSSGAhIQWlUp3UtkpqLgAokY9cS9g/exec"
TIME_URL = "https://timeapi.io/api/Time/current/zone?timeZone=Asia/Colombo"

# Setup
wlan = network.WLAN(network.STA_IF)
connectWifi()

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
bmp = bme280.BMP280(i2c=i2c)
board_led = machine.Pin("LED", machine.Pin.OUT)

reading_count = 0
while True:
    reading_count += 1
    print(f"\n--- Reading #{reading_count} ---")
    
    # Turn LED on when taking reading
    board_led.on()
    timestamp = getTime()    
    # Read sensor data
    bmp_tempC = bmp.temperature
    bmp_pressure = bmp.pressure
    
    print(f"Temp: {bmp_tempC}°C, Pressure: {bmp_pressure} hPa")
    sendToSpreadsheet(time=timestamp, temp=bmp_tempC, pressure=bmp_pressure)
    
    # Try to resend buffered data if we're connected
    if wlan.isconnected():
        resend_buffered_data()

    board_led.off()  # Turn off LED
    
    if reading_count >= 10:
        break
        
    print(f"Waiting 60 seconds until next reading...")
    time.sleep(60)