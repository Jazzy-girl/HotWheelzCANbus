

import cantools
import random
import time

# Load the CAN database
db = cantools.database.load_file('Experimentation/TestData/test2.dbc')  # Path to your .dbc file

# Simulate CANbus messages (for testing)
def simulate_can_data():
    message = {
        'arbitration_id': 256,  # Use the ID from your .dbc file
        'data': bytearray([random.randint(0, 255) for _ in range(8)])  # Converts to bytearray

    }
    return message

# Main loop
while True:
    msg = simulate_can_data()  # Get simulated CAN message
    decoded_msg = db.decode_message(msg['arbitration_id'], msg['data'])  # Decode the message
    print(f"Decoded Message: {decoded_msg}")
    time.sleep(1)  # Wait for a second before generating the next message


'''
import cantools
import can
from pprint import pprint 

db = cantools.database.load_file('dbcTest.dbc') #path of .dbc file
print( db.messages)
can_bus = can.interface.Bus('can0', interface='socketcan')
message = can_bus.recv()
for msg in can_bus:
     print ( db.decode_message(msg.arbitration_id, msg.data))
'''