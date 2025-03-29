import time
from bitstring import BitArray
import cantools
import random
import tkinter as tk
from tkinter import ttk
import cv2
import PIL.Image, PIL.ImageTk  # For displaying images in Tkinter

# Load the CAN database

DBC_FILE = 'Experimentation/DBC Data/LATEST_DBC.dbc'
SIM_DATA_FILE = 'Experimentation/ReadingData/TestData/CANData1/LATEST_DATA.txt'
VALID_IDs = [
    '02B', 
    '02C'
    ]

ID = 43 # Message 02B
db = cantools.database.load_file(DBC_FILE)

# Simulate CANbus messages (for testing)
def simulate_can_data():
    # Simulating realistic values for each parameter
    # You can replace these with actual simulated byte values that match your DBC format
    return {
        'arbitration_id': ID,
        'data': bytearray([random.randint(0, 255) for _ in range(8)])  # Simulated 8-byte CAN message
    }

# Create the main Tkinter window
def create_display_window():
    root = tk.Tk()
    root.title("Car Monitoring System")

    # Define parameters to display (now aligned with the actual DBC signal names)
    parameters = ['PackSOC', 'PackCurrent', 'PackInstVoltage', 'HighTemp', 'LowTemp', '_12vSupply']  # Add all the parameters you want + ADD _12vSupply
    fields = {}  # Store Label widgets

    # Define faults and indices of faults in the Custom Flag
    
    # if a fault is equal to one, show it
    faults = {'Low Cell Voltage Fault', 'Current Sensor Fault', 'Pack Voltage Sensor Fault', 'Thermistor Fault'}
    faultFields = {}
    # this is the indices of the faults in the first 4 bits of the 8 bit Custom Flag signal
    customFlagIndices = {
        0: 'Low Cell Voltage Fault',
        1: 'Current Sensor Fault',
        2: 'Pack Voltage Sensor Fault',
        3: 'Thermistor Fault'
    }

    # Create UI elements for BMS data
    for param in parameters:
        frame = ttk.Frame(root)
        frame.pack(pady=5, padx=20, fill="x")

        label = ttk.Label(frame, text=f"{param}:", font=("Arial", 14))
        label.pack(side="left", padx=5)

        data_label = ttk.Label(frame, text="0", font=("Arial", 14), width=15, anchor="e")  # Default 0 value
        data_label.pack(side="right", padx=5)

        fields[param] = data_label  # Store Label widget
    
    # Create Custom Flag Fields
    for fault in faults:
        frame = ttk.Frame(root)
        frame.pack(pady=5, padx=20, fill="x")

        label = ttk.Label(frame, text=f"{fault}:", font=("Arial", 14))
        label.pack(side="left", padx=5)

        data_label = ttk.Label(frame, text="0", font=("Arial", 14), width=15, anchor="e")  # Default 0 value
        data_label.pack(side="right", padx=5)

        faultFields[fault] = data_label # Store Label widget

    # Function to update display fields
    def update_display():
        message = simulate_can_data()
        try:
            # Decode the message from CAN data
            decoded_msg = db.decode_message(message['arbitration_id'], message['data'])

            # Print the decoded message and keys to debug
            print("Decoded Message:", decoded_msg)
            print("Keys in decoded message:", decoded_msg.keys())

            for param, label in fields.items():
                # Directly use the parameter name as the key
                if param in decoded_msg:
                    value = decoded_msg[param]
                    print(f"Updating {param} with value: {value}")  # Debug line to see the value being set
                    label.config(text=f"{value}")  # Update the label text directly
                    label.update_idletasks()  # Force update of the label
                else:
                    print(f"Key {param} not found in decoded message")
            
            # Check Custom Flag
            if ('CustomFlag' in decoded_msg):
                bits = BitArray(decoded_msg['CustomFlag'].to_bytes()).bin
                for index in range(0, 4):
                    label = faultFields[customFlagIndices[index]]
                    value = ""
                    if(bits[index] == '1'):
                        value = "ERROR!"
                    label.config(text=f"{value}")
                    label.update_idletasks()

                        

        except Exception as e:
            print(f"Error decoding CAN message: {e}")

        # Update every 2 seconds
        root.after(2000, update_display)
    
    def read_data():
        fileLines = []
        with open(SIM_DATA_FILE, 'r') as file:
            print("Opening file")
            for line in file:
                # Process each line
                # first letter is useless
                # next three are the hex
                # next char is useless
                # final chars are the data
                fileLines.append(line.strip())
            print("Done reading!")

        return fileLines

    def show_data(list=None, i=0):
        print(i)
        if(list == None):
            return 
        if(i >= len(list)):
            return
        line = list[i]
        hex_string = line[1:4]
        if(hex_string in VALID_IDs):
            id = int(hex_string, 16)
            data = bytes.fromhex(line[5:])
            message = db.decode_message(id, data)
            # Print the decoded message and keys to debug
            print("Decoded Message:", message)
            print("Keys in decoded message:", message.keys())

            for param, label in fields.items():
                # Directly use the parameter name as the key
                if param in message:
                    value = message[param]
                    print(f"Updating {param} with value: {value}")  # Debug line to see the value being set
                    label.config(text=f"{value}")  # Update the label text directly
                    label.update_idletasks()  # Force update of the label
                else:
                    print(f"Key {param} not found in decoded message")
            
            # Check Custom Flag
            if ('CustomFlag' in message):
                bits = BitArray(message['CustomFlag'].to_bytes()).bin
                for index in range(0, 4):
                    label = faultFields[customFlagIndices[index]]
                    value = ""
                    if(bits[index] == '1'):
                        value = "ERROR!"
                    label.config(text=f"{value}")
                    label.update_idletasks()

        root.after(0, show_data, list, i+1)


    # Backup Camera Display
    cam_frame = ttk.Frame(root)
    cam_frame.pack(pady=20)

    cam_label = ttk.Label(cam_frame, text="Backup Camera", font=("Arial", 16))
    cam_label.pack()

    video_label = tk.Label(cam_frame)
    video_label.pack()

    # Function to simulate black camera screen
    def update_camera():
        # Create a black image (480x640)
        frame = cv2.UMat(480, 640, cv2.CV_8UC3)  # Create a black image
        img = PIL.Image.fromarray(frame.get())  # Convert it to PIL image
        img_tk = PIL.ImageTk.PhotoImage(image=img)  # Convert to Tkinter-compatible image

        video_label.img_tk = img_tk  # Keep reference to avoid garbage collection
        video_label.config(image=img_tk)  # Update the label to show the image

        root.after(50, update_camera)  # Refresh every 50ms

    # Start updating UI elements
    #update_display() Replaced with...
    show_data(read_data(), 0)
    update_camera()

    root.mainloop()

if __name__ == "__main__":
    create_display_window()