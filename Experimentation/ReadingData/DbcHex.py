from queue import Full
import cantools, can
import cantools.database
from bitstring import BitArray


VALID_IDs = [
    # UPDATED
    '02B',
    '02C'
]

DBC_FILE = 'Experimentation/DBC Data/LATEST_3_26.dbc'
SIM_DATA_FILE = 'Experimentation/ReadingData/TestData/CANData1/test_26.txt'

FIELDS = {
    'PackSOC',
    'PackCurrent',
    'PackInstVoltage',
    'HighTemp',
    'LowTemp',
    'Low Cell Voltage Fault',
    'Current Sensor Fault',
    'Pack Voltage Sensor Fault',
    'Thermistor Fault'
}

ERROR_DICT = {
    0: 'Low Cell Voltage Fault',
    1: 'Current Sensor Fault',
    2: 'Pack Voltage Sensor Fault',
    3: 'Thermistor Fault'
}

information = dict()
for field in FIELDS:
    information[field] = 0

# Load the DBC file
db = cantools.database.load_file(DBC_FILE)

# Load data fike
with open(SIM_DATA_FILE, 'r') as file:
    for line in file:
        # Process each line
        # first letter is useless
        # next three are the hex
        # next char is useless
        # final chars are the data
        hex_string = line[1:4]
        
        id = int(hex_string, 16)
        if(hex_string in VALID_IDs):
            data = bytes.fromhex(line[5:])
            message = db.decode_message(id, data)
            #print(f"Thermistor Temp: {message['ThermistorValue']} degrees Celsius")
            
            for key in message.keys():
                information[key] = message[key]
                """
                The following if statement converts the CustomFlag hex data into binary and checks
                the first 4 bits for 1's, as the Custom Flag id sends 1-byte message where the first 4 bits each
                represent a possible error (see ERROR_DICT for the order)
                """
                if (key == 'CustomFlag'):
                    #print(message[key])
                    bits = BitArray(message[key].to_bytes()).bin
                    #print(bits)
                    for index in range(0, 4):
                        if bits[index] == '1':
                            information[ERROR_DICT[index]] = 1
                    continue
            print(information)