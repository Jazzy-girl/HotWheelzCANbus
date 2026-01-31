"""
Author: Ryanne Wilson
Code to transfer data from the Raspberry Pi to the transceiver (to send to the Pit)
"""

"""
Setup:

pip3 install adafruit-circuitpython-rfm9x

pip3 install adafruit-circuitpython-lis3dh

pip3 install adafruit_ssd1306 ???
"""

"""
format:
46 byte packet
Header: 0 - 8
    - 0-2: "HW"
    - 2-4: checksum
    - 4-8: millis since program start (32-bit unsigned int)
GPS: 8-24
    - 8-16: longitude (64-bit double)
    - 16-24: latitude (64-bit double)
Cockpit temp: 24-26 (16-bit unsigned int)
BMS: 26-39
    - ....
Padding: 39
    - 4-byte alignment
    - fill with 0xAA?
Speed: 40-46
    - 40-44: GPS speed (32-bit float km/h)
    - 44-46: Motor speed (16-bit unsigned int, pulses/second)
"""

# System libraries
import time
# Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# import SSD1306 module (for display-- not necessary)
# import adafruit_ssd1306
# import RFM9x
import adafruit_rfm9x

# Configure LoRa Radio

# Pin for Chip Select; enables device for comms
CS_PIN = board.CE1 
CS = DigitalInOut(CS_PIN) # Chip Select accessor

# Pin for Reset
RESET_PIN = board.D25
RESET = DigitalInOut(RESET_PIN) # Reset accessor
MOSI = board.MOSI # Main Output, Secondary Input; data sent from board to transceiver
MISO = board.MISO # Main Input, Secondary Output; data sent from transceiver to board
FREQUENCY = 915.0
spi = busio.SPI(board.SCK, MOSI=MOSI, MISO=MISO)
rfm9x = adafruit_rfm9x(spi, CS, RESET, FREQUENCY)
rfm9x.tx_power = 23
prev_packet = None

