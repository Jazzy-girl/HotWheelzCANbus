import collections
import time
import threading
import struct
import functools

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

adc_cs = digitalio.DigitalInOut(board.D24)
can_cs = digitalio.DigitalInOut(board.D25)


gps = adafruit_gps.GPS(uart, debug=False)
can = adafruit_mcp2515.MCP2515(spi1, can_cs, loopback=False, silent=False)
adc = mcp.MCP3008(spi1, adc_cs)

thermistor = AnalogIn(adc, mcp.P0)

gps.send_command(b"PMTK314,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0") # magic data goes brrrr
gps.send_command(b"PMTK220,500")

class SpeedWorker(threading.Thread):
    def __init__(self):
        self.queue = collections.deque()
        self.daemon = True
        self.motor = digitalio.DigitalInOut(board.D12)
        self.motor.direction = digitalio.Direction.INPUT
        self.start()
    def run(self):
        while True:
            while not self.motor.value:
                time.sleep(0.001)
            while self.motor.value:
                time.sleep(0.001)
            now = time.monotonic()
            while self.queue and now - self.queue[0] > 1:
                self.queue.popleft()
            self.queue.append(now)
    def pulses(self) -> int:
        return len(self.queue)

class SenderWorker(threading.Thread):
    def __init__(self):
        self.to_send = None
        self.lora_rst = digitalio.DigitalInOut(board.D5)
        # self.lora_int = digitalio.DigitalInOut(board.D6)
        self.lora_cs = digitalio.DigitalInOut(board.D13)
        self.lora = adafruit_rfm9x.RFM9x(spi0, self.lora_cs, self.lora_rst, 915.0)
    def run(self):
        while True:
            if self.to_send is None:
                time.sleep(0.001)
            else:
                data= self.to_send
                self.to_send = None
                self.lora.send(data)

speed = SpeedWorker()
sender = SenderWorker()

while True:
    gps.update()
    timestamp = time.monotonic_ns() // 1000
    lon = gps.longitude if gps.has_fix else 0
    lat = gps.latitude if gps.has_fix else 0
    temp = thermistor.value
    curr = 0
    volt = 0
    soc = 0
    health = 0
    amph = 0
    hitemp = 0
    lotemp = 0
    avgtemp = 0
    hstemp = 0
    faults = 0
    gpsSpeed = gps.speed_kmh if gps.has_fix and gps.speed_kmh is not None else 0
    motorSpeed = speed.pulses()
    data = struct.pack("<4xI dd H hHBBH5B x fH", timestamp, lon, lat, temp, curr, volt, soc, health, amph, hitemp, lotemp, avgtemp, hstemp, faults, gpsSpeed, motorSpeed)
    data = bytearray(data)
    data[0:2] = b"HW"
    checksum = functools.reduce(int.__xor__, struct.unpack("<4x21H", data))
    data[2:4] = checksum.to_bytes(2, "little")
    sender.to_send = data
    print(data.hex())