from queue import Full
import cantools, can
import cantools.database



# Example raw CAN frame
"""
The example data:
t03B5FFFE00003DCE09

the id: 03B
skip: the 5FFFE
use: the 00003DCE09
"""
can_id = 0x03B # Just use the base hex, not the letters after?
data = bytes.fromhex("FFFE00003DCE09") # this is skipping

VALID_IDs = [
    #'03B',
    #'3CB',
    #'6B2',
    #'080',
    #'081',
    '082'
]

MESSAGES = set()
INVALID_IDs = set()

FIELDS = set()

information = dict()
information['CRCChecksum'] = None
information['PackCurrent'] = None
information['PackDCL'] = None
information['PackInstVoltage'] = None
information['PackAmphours'] = None
information['SimulatedSOC'] = None
information['PackOpenVolt'] = None
information['PackCCL'] = None
information['ThermistorValue'] = None
information['PackRes'] = None
information['FaultPresent'] = None
information['HighTemp'] = None
information['CustomFlag'] = None # ?? tbis is not the right implementation. CustomFlag currently contains multiple pieces of information.
                                # consider you've implemented the CustomFlag .dbc w/out interpreting data that used the CustomFlag correctly.
                                # '28' as a value is vestigial. Test with new data from Rachael.
information['LowTemp'] = None
information['HighLowIndicator'] = None
information['PackSOC'] = None

# Need to update each specified field whenever it is updated.
# Have a Dict of fields & values. The UI accesses and displays the field : value s of the dict.
# Recognize which field and value is being returned, update the specified value.

# How does Custom Flag work?? right now it just returns 28... 
# isn't it supposed to return discrete and separate pieces of information in bits?

# Needed Ids:
# 0x08, 0x81, 0x82

# Load the DBC file
db = cantools.database.load_file("Experimentation/DBC Data/FaultsWithThermistorData.dbc")

# Load data fike
filename = "Experimentation/ReadingData/TestData/CANData1/3.17_SMALL.txt"
with open(filename, 'r') as file:
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
            """
            for key in message.keys():
                information[key] = message[key]
                if(information['HighLowIndicator'] == 5):
                    information['HighLowIndicator'] = 'Low'
                else:
                    information['HighLowIndicator'] = 'High'
            """
            print(message)
            #print(information)
        else:
           # print(f"Unknown CAN ID {hex(id)}.")
            INVALID_IDs.add(id)
    print(f"Unknown IDs: {INVALID_IDs}")
    print(f"Fields: {FIELDS}")
        
"""

for can_id, data_hex in messages:
    data = bytes.fromhex(data_hex)
    try:
        message = db.decode_message(can_id, data)
        print(message)
    except KeyError:
        print(f"Unknown CAN ID {hex(can_id)}, check DBC file.")
"""

"""
messages = [
    (0x03B, "FFFE00003DCE09"),
    (0x3CB, "061600A0CE0C"),
    (0x6B2, "00151600030300BBCE0C")
]

print("Messages in DBC file:")
for message in db.messages:
    print(f"ID: {hex(message.frame_id)} - Name: {message.name}")

"""


"""
ex:

t03B5FFFE00003DCE09
t0804061600A0CE0C
t0814151600B0CE0C
t082800151600030300BBCE0C

so:
use 03B

"""

# Decode the message