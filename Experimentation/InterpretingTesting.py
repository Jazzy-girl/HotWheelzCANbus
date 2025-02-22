
import cantools
import can
from pprint import pprint 

db = cantools.database.load_file('dbcTest.dbc') #path of .dbc file
print( db.messages)
can_bus = can.interface.Bus('can0', interface='socketcan')
message = can_bus.recv()
for msg in can_bus:
     print ( db.decode_message(msg.arbitration_id, msg.data))