import time
from bitstring import BitArray
import cantools
import random
from tkinter import *
from tkinter.ttk import *
import tkinter.font as tkFont
import PIL.Image, PIL.ImageTk  # For displaying images in Tkinter
import sys

import cv2
sys.path.append('/Users/divnamijic/Documents/HotWheelzCANbus-4/UI')
from Speedometer import Speedometer


"""
Single-Window UI to display 6 data fields, 4 possible faults, and the backup camera.
Uses tkinter's .grid() layout.
"""

# Load the CAN database
#DBC_FILE = '/Users/divnamijic/Documents/HotWheelzCANbus-4/Experimentation/DBC Data/LATEST_DBC.dbc'
#SIM_DATA_FILE = '/Users/divnamijic/Documents/HotWheelzCANbus-4/Experimentation/ReadingData/TestData/CANData1/LATEST_DATA.txt'
#BG_IMAGE = "/Users/divnamijic/Documents/HotWheelzCANbus-4/Experimentation/ReadingData/Resources/images/bg.jpg"
DBC_FILE = 'Experimentation/DBC Data/LATEST_DBC.dbc'
SIM_DATA_FILE = 'Experimentation/ReadingData/TestData/CANData1/LATEST_DATA.txt'
BG_IMAGE = 'Experimentation/ReadingData/Resources/images/bg.jpg'
VALID_IDs = ['02B', '02C']

PARAMETERS = ['PackSOC', 'PackCurrent', 'PackInstVoltage', 'HighTemp', 'LowTemp', '_12vSupply']
FAULTS = ['Low Cell Voltage Fault', 'Current Sensor Fault', 'Pack Voltage Sensor Fault', 'Thermistor Fault']
DATA_LABELS = ['SOC', 'CURR', 'VOLT', '_12', 'HI', 'LO']
FAULT_LABELS = ['L. CELL', 'CURRENT', 'PACK', 'THERM']
CUSTOM_FLAG_INDICES = {
        0: 'Low Cell Voltage Fault',
        1: 'Current Sensor Fault',
        2: 'Pack Voltage Sensor Fault',
        3: 'Thermistor Fault'
    }


ID = 43  # Message 02B
db = cantools.database.load_file(DBC_FILE)

# Simulate CANbus messages (for testing)
def simulate_can_data():
    return {
        'arbitration_id': ID,
        'data': bytearray([random.randint(0, 255) for _ in range(8)])  # Simulated 8-byte CAN message
    }

# Create the main Tkinter window
def create_display_window():
    # the window
    root = Tk()
    root.title("Car Monitoring System")
    root.geometry("800x480")  # Set the window size

    # Backup Camera Display: Frame
    # the frame to hold the camera
    cam_frame = Frame(root)
    cam_frame.pack(side=LEFT, pady=20)

    # the label to hold 
    cam_label = Label(cam_frame, text="Backup Camera", font=("Arial", 16))
    cam_label.pack()

    video_label = Label(cam_frame)
    video_label.pack()

    # Data Frame
    data_frame = Frame(root)
    data_frame.pack(side=LEFT)

    """
    This section makes the grid. There are 3 types of labels:
        1. Data name labels. These don't update. They correspond with #2. use DATA_LABELS.
        2. Data output labels. They correspond with #1. These update with new input. Must correspond with a dict of the params for the DBC interpretation.
        3. Fault labels. Change color(?) if return true.
    
    The grid is 8 x 2
    """

    fields = {}
    faultFields = {}
    data_frame.columnconfigure(0, weight=1)
    data_frame.columnconfigure(1, weight=1)

    data_font = tkFont.Font(family="Arial", size=15)
    output_font = tkFont.Font(family="Arial", size=15)
    fault_font = tkFont.Font(family="Arial", size=12)

    # make separator line
    line = Separator(data_frame, orient=VERTICAL).grid(column=1, columnspan=2, row=0, rowspan=10, sticky=NS)

    # make data name & output labels
    for i in range(len(DATA_LABELS)):
        data_frame.rowconfigure(i, weight=1)
        # row will will jump by 2 every other label.
        row = (i // 2) * 2
        # col will either be 0 or 1
        if(i % 2 == 0):
            col = 0
        else:
            col = 3

        data_label = Label(data_frame, text=DATA_LABELS[i], font=data_font, justify=CENTER)
        data_label.grid(row=row, column=col, sticky=NSEW)

        output_label = Label(data_frame, text="NULL", font=output_font, justify=CENTER)
        output_label.grid(row=row+1, column=col,sticky=NSEW, pady=(5,10))

        # for accessing DBC data
        fields[PARAMETERS[i]] = output_label

    # make fault labels
    for i in range(len(FAULT_LABELS)):
        fault_label = Label(data_frame, text=FAULT_LABELS[i], font=fault_font, justify=CENTER)
        row = ((i + len(DATA_LABELS)) // 2) * 2
        if(i % 2 == 0):
            col = 0
        else:
            col = 3
        fault_label.grid(row=row, column=col, sticky=NSEW, pady=20)
        faultFields[FAULTS[i]] = fault_label
    
    def update_camera():
        # Create a black image (480x640)
        frame = cv2.UMat(480, 640, cv2.CV_8UC3)  # Create a black image
        img = PIL.Image.fromarray(frame.get())  # Convert it to PIL image
        img_tk = PIL.ImageTk.PhotoImage(image=img)  # Convert to Tkinter-compatible image

        video_label.img_tk = img_tk  # Keep reference to avoid garbage collection
        video_label.config(image=img_tk)  # Update the label to show the image

        root.after(50, update_camera)  # Refresh every 50ms

    # Function to update display fields
    def update_display():
        message = simulate_can_data()
        try:
            decoded_msg = db.decode_message(message['arbitration_id'], message['data'])

            for param, label in fields.items():
                if param in decoded_msg:
                    value = decoded_msg[param]
                    label.configure(text=f"{value:.1f}", font=output_font)
                    label.update_idletasks()

            # if 'CustomFlag' in decoded_msg:
            #     bits = BitArray(decoded_msg['CustomFlag'].to_bytes()).bin
            #     for index in range(0, 4):
            #         label = faultFields[CUSTOM_FLAG_INDICES[index]]
            #         value = "ERROR!" if bits[index] == '1' else ""
            #         label.config(text=f"{value}")
            #         label.update_idletasks()

        except Exception as e:
            print(f"Error decoding CAN message: {e}")

        root.after(2000, update_display)

    # Start updating UI elements
    update_display()
    update_camera()

    root.mainloop()

if __name__ == "__main__":
    create_display_window()
