
'''
Data that must be interpreted:
    BMS:
        battery voltage
        the max and min temp of batteries
        the current coming out of the batteries  
    Camera:
        the display from the backup camera
    ???:
        speed of the vehicle -  WIP on how we are actually going to do this, chances are, we take some measurements, put them into a formula and calculate the speed
'''

import cantools
import random
import time
import tkinter as tk
from tkinter import ttk


# Define the ID constant
ID = 256
FILE_PATH = "Experimentation/ReadingData/TestData/test2.dbc"

# Load the CAN database
db = cantools.database.load_file(FILE_PATH)  # Path to your .dbc file

# Simulate CANbus messages (for testing)
def simulate_can_data():
    message = {
        'arbitration_id': ID,  # Use the ID from your .dbc file
        'data': bytearray([random.randint(0, 255) for _ in range(8)])  # Converts to bytearray
    }
    return message

"""
# Main loop
while True:
    msg = simulate_can_data()  # Get simulated CAN message
    decoded_msg = db.decode_message(msg['arbitration_id'], msg['data'])  # Decode the message
    print(f"Decoded Message: {decoded_msg}")
    time.sleep(1)  # Wait for a second before generating the next message
"""


# Create a simple TKinter window
def create_display_window():
    root = tk.Tk()
    root.title("Car Monitoring System")

    # Add a label to display the CAN data
    label = ttk.Label(root, text="Data will appear here", font=("Arial, 16"))
    label.pack(pady=20)

    # Nested Function to update the display
    def update_display():
        message = simulate_can_data()
        try:
            # Decode the message using the DBC file
            decoded_msg = db.decode_messsage(message['arbitration_id'], message['data'])
            decoded_str = f"Decoded Data:\n{decoded_msg}"

            # Update the label w/ the decoded data
            label.config(text=decoded_str)
        except Exception as e:
            label.config(text=f"Error: {e}")
    
        #Update the display every 2? seconds
        root.after(2000, update_display)
    
    # Start the update loop
    update_display()

    # Run the Tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    create_display_window()