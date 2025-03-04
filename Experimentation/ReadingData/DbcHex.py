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
data = bytes.fromhex("00003DCE09") # this is skipping



# Decode the message
message = db.decode_message(can_id, data)
print(message)