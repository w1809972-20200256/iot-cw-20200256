# Internet of Things (IoT) Coursework for UoW/IIT
This project contains the code for fulfilling the requirements of 6NTCM009W Internet of Things (IoT) Coursework - An IoT prototype.

# IoT Prototype

This project utilizes a **Raspberry Pi Pico W** and a **BME280 sensor** to collect environmental data (temperature and pressure). The data is sent to a **Google Sheets App Script** via HTTP requests for real-time logging and visualization.

## Features
- Reads **temperature** and **pressure** using the BMP280 sensor
- Connects to **Wi-Fi** and handles **reconnection** if lost
- Sends data to **Google Sheets** via App Script, Displays them in a web-server or console
- Implements **retry logic** for failed transmissions
- **Stores data locally** when offline and resends it when Wi-Fi is restored

## Hardware Requirements
- **Raspberry Pi Pico W**
- **BMP280 sensor** (I2C)
- **Wi-Fi network**

## Software Requirements
- **MicroPython** firmware on Raspberry Pi Pico W
- Required Python libraries:
  - `bme280`
  - `machine`
  - `network`
  - `urequests`
  - `json`
  - `gc`

## Installation
1. **Flash MicroPython** on your Raspberry Pi Pico W.
2. Install required libraries in your MicroPython environment.
3. Clone this repository and upload the script to your Pico W.
4. Update the Wi-Fi credentials (`SSID`, `PASSWORD`) in the script.
5. Replace `SCRIPT_URL` with your Google Sheets App Script URL.

## Handling Wi-Fi Disconnections
- If Wi-Fi is lost, the system **attempts reconnection** up to 10 times.
- If reconnection fails, data is stored in a **buffer file (`buffer.json`)**.
- When Wi-Fi is restored, the system **automatically resends buffered data**.
---
Developed by **Sudam Mahagamage** (sudamtm@gmail.com/sudam.20200256@iit.ac.lk) 🚀
