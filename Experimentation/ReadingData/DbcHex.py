import cantools, can
import cantools.database

# Load the DBC file
db = cantools.database.load_file("Experimentation/DBC Data/start2.dbc")

# Example raw CAN frame
can_id = 0x03B
data = bytes.fromhex("00003DCE09")



# Decode the message
message = db.decode_message(can_id, data)
print(message)