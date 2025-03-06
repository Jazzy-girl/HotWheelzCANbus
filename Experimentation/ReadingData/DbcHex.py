import cantools, can
import cantools.database

# Load the DBC file
db = cantools.database.load_file("Experimentation/DBC Data/start2.dbc")

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
    '03B',
    '3CB',
    '6B2'
]

# Needed Ids:
# 0x08, 0x81, 0x82

filename = "Experimentation/ReadingData/TestData/CANData1/2025-03-01-14-24-30.txt"
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
            print(message)
        else:
            print(f"Unknown CAN ID {hex(id)}, check DBC file.")
        
"""

for can_id, data_hex in messages:
    data = bytes.fromhex(data_hex)
    try:
        message = db.decode_message(can_id, data)
        print(message)
    except KeyError:
        print(f"Unknown CAN ID {hex(can_id)}, check DBC file.")
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
ex:

t03B5FFFE00003DCE09
t0804061600A0CE0C
t0814151600B0CE0C
t082800151600030300BBCE0C

so:
use 03B

"""

# Decode the message