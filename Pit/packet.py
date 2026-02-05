import struct
import functools
import math
from typing import NamedTuple

PACKET_FORMAT = "<xxHI dd H hHBBH5B x fH"

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

def checksum_of_data(data: bytes | bytearray) -> int:
    return functools.reduce(int.__xor__, struct.unpack("<4x21H", data))

def write_checksum(data: bytearray):
    cs = checksum_of_data(data)
    data[2:4] = cs.to_bytes(2, "little")

class RawPacket(NamedTuple):
    """
    A raw packet, with fields in the same format that they're passed in the packed format
    """
    checksum: int
    timestamp: int
    gps_lon: float
    gps_lat: float
    temp: int
    curr: int
    volt: int
    soc: int
    health: int
    amph: int
    hitemp: int
    lotemp: int
    avgtemp: int
    hstemp: int
    faults: int
    gps_speed: float
    motor_speed: int
    @staticmethod
    def without_bms(timestamp: int, gps_lon: float, gps_lat: float, temp: int, gps_speed: float, motor_speed: int) -> 'RawPacket':
        return RawPacket(
            checksum=0, 
            timestamp=timestamp,
            gps_lon=gps_lon,
            gps_lat=gps_lat,
            temp=temp,
            curr=0,
            volt=0,
            soc=0,
            health=0,
            amph=0,
            hitemp=0,
            lotemp=0,
            avgtemp=0,
            hstemp=0,
            faults=0,
            gps_speed=gps_speed,
            motor_speed=motor_speed
        )
    @staticmethod
    def unpack_bytes(data: bytes | bytearray) -> 'RawPacket':
        return RawPacket(*struct.unpack(PACKET_FORMAT, data))
    def pack_bytes(self, with_checksum = False) -> bytearray:
        data = bytearray(struct.pack(PACKET_FORMAT, *self))
        data[0:2] = b"HW"
        if with_checksum:
            write_checksum(data)
        return data
    def calc_checksum(self) -> int:
        data = struct.pack(PACKET_FORMAT, *self)
        return checksum_of_data(data)
    def with_checksum(self) -> 'RawPacket':
        return self._replace(checksum=self.calc_checksum())
    def parse(self) -> 'ParsedPacket':
        tv, tr, tt = thermistor_temp(self.temp)
        return ParsedPacket(
            checksum=self.checksum,
            timestamp=self.timestamp,
            gps_lon=self.gps_lon,
            gps_lat=self.gps_lat,
            therm_reading=self.temp,
            therm_voltage=tv,
            therm_resistance=tr,
            therm_temp=tt,
            bms_current=self.curr * 0.1,
            bms_voltage=self.volt * 0.1,
            bms_soc=self.soc * 0.5,
            bms_health=self.health * 0.5,
            bms_amphours=self.amph * 0.1,
            bms_hi_temp=self.hitemp - 40,
            bms_lo_temp=self.lotemp - 40,
            bms_avg_temp=self.avgtemp - 40,
            bms_heatsink_temp=self.hstemp,
            fault_low_cell_voltage=self.faults & 1 != 0,
            fault_current_sensor=self.faults & 2 != 0,
            fault_pack_voltage=self.faults & 4 != 0,
            fault_thermistor=self.faults & 8 != 0,
            gps_speed=self.gps_speed * KM_TO_MI,
            motor_speed=self.motor_speed * PULSE_SPEED_MUL
        )

class ParsedPacket(NamedTuple):
    """
    The packet data, with all of the fields parsed to more useful units
    """
    checksum: int
    timestamp: int
    gps_lon: float
    gps_lat: float
    therm_reading: int
    therm_voltage: float
    therm_resistance: float
    therm_temp: float
    bms_current: float
    bms_voltage: float
    bms_soc: float
    bms_health: float
    bms_amphours: float
    bms_hi_temp: int
    bms_lo_temp: int
    bms_avg_temp: int
    bms_heatsink_temp: int
    fault_low_cell_voltage: bool
    fault_current_sensor: bool
    fault_pack_voltage: bool
    fault_thermistor: bool
    gps_speed: float
    motor_speed: float
    def pack(self) -> RawPacket:
        faults = 0
        if self.fault_low_cell_voltage:
            faults |= 1
        if self.fault_current_sensor:
            faults != 2
        if self.fault_pack_voltage:
            faults |= 4
        if self.fault_thermistor:
            faults |= 8
        return RawPacket(
            checksum=self.checksum,
            timestamp=self.timestamp,
            gps_lon=self.gps_lon,
            gps_lat=self.gps_lat,
            temp=self.therm_reading,
            curr=int(self.bms_current * 10),
            volt=int(self.bms_voltage * 10),
            soc=int(self.bms_soc * 2),
            health=int(self.bms_health * 2),
            amph=int(self.bms_amphours * 10),
            hitemp=int(self.bms_hi_temp + 40),
            lotemp=int(self.bms_lo_temp + 40),
            avgtemp=int(self.bms_avg_temp + 40),
            hstemp=int(self.bms_heatsink_temp + 40),
            faults=faults,
            gps_speed=self.gps_speed / KM_TO_MI,
            motor_speed=int(self.motor_speed / PULSE_SPEED_MUL),
        )
