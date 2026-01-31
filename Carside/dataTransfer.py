"""
Author: Ryanne Wilson
Code to transfer data from the Raspberry Pi to the transceiver (to send to the Pit)
"""

"""
Setup:

pip3 install adafruit-circuitpython-rfm9x

and maybe also:

pip3 install adafruit-circuitpython-lis3dh

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

