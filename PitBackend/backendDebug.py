import serial
import os
import sys
import io
import base64
import struct
import functools
import math

PULSES_PER_ROTATION = 48

KM_TO_MI = 0.6213712

WHEEL_DIAMETER_IN = 21
WHEEL_CIRCUMFERENCE_FT = WHEEL_DIAMETER_IN * math.pi / 12
FT_TO_MI = 1 / 5280
S_TO_HR = 3600

PULSE_SPEED_MUL = WHEEL_CIRCUMFERENCE_FT / PULSES_PER_ROTATION * FT_TO_MI * S_TO_HR

def thermistor_temp(reading: int) -> tuple[float, float, float]:
    LOW_SIDE_RESISTOR = 10000
    voltage = reading / 1024
    resistance = LOW_SIDE_RESISTOR / voltage - LOW_SIDE_RESISTOR
    temperature = 0
    return voltage, resistance, temperature

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print(f"Usage: {sys.argv[0]} <PORT | FILE> [baudrate]")
    sys.exit(1)

port = sys.argv[1]
baud = int(sys.argv[2]) if len(sys.argv) == 3 else 9600

if not os.path.exists(port):
    print(f"{port} does not exist")
    sys.exit(2)

def load_serial() -> io.TextIOWrapper:
    ser = serial.Serial(port, baud)
    ser.open()
    return io.TextIOWrapper(io.BufferedReader(ser), newline='\n')

interface = open(port) if os.path.isfile(port) else load_serial()

for line in interface:
    if len(line) == 0:
        print()
    elif line[0] == '!':
        print("Text:", line[1:])
    else:
        print("Escaped:", line)
        data = base64.decodebytes(line.encode('ascii'))
        print("Hex:", data.hex(" "))
        if len(data) == 46 and data[:2] == b"HW":
            print("Decoded data:")
            checksum = functools.reduce(lambda x, y: x ^ y, struct.unpack("<4x21H", data))
            fields = struct.unpack("<xxHI dd iIBBI5B x fH", data)
            provided, timestamp, lon, lat, temp, curr, volt, soc, health, amph, hitemp, lotemp, avgtemp, hstemp, faults, gpsSpeed, motorSpeed = fields
            cvol, cres, ctemp = thermistor_temp(temp)
            print("Header:")
            print(f"  Provided checksum:     {hex(provided)}")
            print(f"  Calculated checksum:   {hex(checksum)}")
            print(f"  Checksums match:       {provided == checksum}")
            print(f"  Timestamp:             {timestamp} ms")
            print("GPS:")
            print(f"  Longitude:             {lon}°")
            print(f"  Latitude:              {lat}°")
            print("Cockpit temperature:")
            print(f"  Raw reading:           {ctemp}")
            print(f"  Voltage:               {cvol * 5} V")
            print(f"  Resistance:            {cres} Ω")
            print(f"  Temperature:           {ctemp}°C")
            print("BMS data:")
            print(f"  Pack current:          {curr * 0.1} A")
            print(f"  Pack voltage:          {volt * 0.1} V")
            print(f"  Pack SOC:              {soc * 0.5}%")
            print(f"  Pack health:           {health * 0.5}%")
            print(f"  Pack amphours:         {amph * 0.1} Ah")
            print(f"  High temperature:      {hitemp - 40}°C")
            print(f"  Low temperature:       {lotemp - 40}°C")
            print(f"  Average temperature:   {avgtemp - 40}°C")
            print(f"  Heat sink temperature: {hitemp - 40}°C")
            print(f"  Low cell voltage:      {faults & 1 != 0}")
            print(f"  Current sensor fault:  {faults & 2 != 0}")
            print(f"  Pack voltage fault:    {faults & 4 != 0}")
            print(f"  Thermistor fault:      {faults & 8 != 0}")
            print("Speed:")
            print(f"  GPS speed:             {gpsSpeed * KM_TO_MI} mph")
            print(f"  Motor speed:           {motorSpeed * PULSE_SPEED_MUL} mph")
        else:
            print("Unknown data")