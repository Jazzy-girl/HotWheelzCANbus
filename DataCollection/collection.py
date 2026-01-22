import time

import board
import busio
import digitalio

import adafruit_rfm9x
import adafruit_gps
import adafruit_mcp2515
from adafruit_mcp2515.canio import Message, RemoteTransmissionRequest
import adafruit_mcp3xxx.mcp3008 as mcp
from adafruit_mcp3xxx.analog_in import AnalogIn

uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
spi0 = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
spi1 = busio.SPI(board.SCK_1, MOSI=board.MOSI_1, MISO=board.MISO_1)

lora_rst = digitalio.DigitalInOut(board.D5)
# lora_int = digitalio.DigitalInOut(board.D6)
lora_cs = digitalio.DigitalInOut(board.D13)

adc_cs = digitalio.DigitalInOut(board.D24)
can_cs = digitalio.DigitalInOut(board.D25)

gps = adafruit_gps.GPS(uart, debug=False)
can = adafruit_mcp2515.MCP2515(spi1, can_cs, loopback=False, silent=False)
adc = mcp.MCP3008(spi1, adc_cs)
lora = adafruit_rfm9x.RFM9x(spi0, lora_cs, lora_rst, 915.0)

thermistor = AnalogIn(adc, mcp.P0)