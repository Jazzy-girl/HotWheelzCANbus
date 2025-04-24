import time
from bitstring import BitArray
from cantools import *
from can import *
import random
import tkinter as tk
from tkinter.ttk import *
import tkinter.font as tkFont
import PIL.Image, PIL.ImageTk  # For displaying images in Tkinter
import sys

import cantools
import can
import cv2
sys.path.append('/Users/divnamijic/Documents/HotWheelzCANbus-4/UI')
from Speedometer import Speedometer


"""
Single-Window UI to display 6 data fields, 4 possible faults, and the backup camera.
Uses tkinter's .grid() layout.

The 6 data fields each have a limit of 1 decimal place.
The 4 faults turn red when true and black when false.
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

CAMERA_RATIO = (480, 500) # originally 480 x 640

ID = [43, 44]  # Message 02B, 02C
db = cantools.database.load_file(DBC_FILE)

def get_bms_data():
    with can.Bus() as bus:
        for msg in bus:
            # do something
            print(msg.data)

# Simulate CANbus messages (for testing)
def simulate_can_data():
    return {
        'arbitration_id': ID[random.randint(0, 1)],
        'data': bytearray([random.randint(0, 255) for _ in range(8)])  # Simulated 8-byte CAN message
    }

# Create the main Tkinter window
def create_display_window():
    # the window
    root = tk.Tk()
    root.title("Car Monitoring System")
    root.geometry("800x480")  # Set the window size

    # background img attempt # 2
    # bg_image = PIL.ImageTk.PhotoImage(PIL.Image.open(BG_IMAGE))
    # bg_label = Label(root, image=bg_image)
    # bg_label.place(x=0,y=0, relwidth=1, relheight=1)

    # # Load the background image
    # bg_image = PIL.Image.open(BG_IMAGE)
    # bg_image = bg_image.resize((800, 480))  # Resize to window size
    # bg_image_tk = PIL.ImageTk.PhotoImage(bg_image)

    # # bg_label = Label(root, image=bg_image_tk)
    # # bg_label.image = bg_image_tk
    # # bg_label.place(x=0,y=0, relwidth=1, relheight=1)

    # canvas = Canvas(root)
    # canvas.pack()

    # canvas.bg_image_tk = bg_image_tk
    # canvas.create_image(0, 0, image=bg_image_tk, anchor=NW)
    # # canvas.lower()

    # # Create a label to hold the background image and ensure it persists
    # bg_label = Label(root, image=bg_image_tk)
    # bg_label.image = bg_image_tk  # Keep a reference to the image
    # bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Ensure it takes up the whole screen

    # Backup Camera Display: Frame
    # the frame to hold the camera
    cam_frame = tk.Frame(root, background="black")
    cam_frame.pack(side=tk.LEFT, pady=20, expand=True)

    video_label = Label(cam_frame)
    video_label.pack(expand=True)

    # Data Frame
    data_frame = tk.Frame(root, background="black")
    data_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

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
    data_frame.columnconfigure(2, weight=1)
    data_frame.columnconfigure(3, weight=1)
    for i in range(len(DATA_LABELS)*2 + len(FAULT_LABELS)):
        data_frame.rowconfigure(i, weight=1)

    data_font = tkFont.Font(family="Arial", size=20)
    output_font = tkFont.Font(family="Arial", size=20)
    fault_font = tkFont.Font(family="Arial", size=20)

    # make separator line
    line = Separator(data_frame, orient=tk.VERTICAL).grid(column=1, columnspan=2, row=0, rowspan=10, sticky=tk.NS)

    # make data name & output labels
    for i in range(len(DATA_LABELS)):
        # row will will jump by 2 every other label.
        row = (i // 2) * 2
        # col will either be 0 or 1
        if(i % 2 == 0):
            col = 0
        else:
            col = 3

        data_label = Label(data_frame, text=DATA_LABELS[i], font=data_font, justify=tk.CENTER, background="black", foreground="white")
        data_label.grid(row=row, column=col, sticky='NSEW')

        output_label = Label(data_frame, text="NULL", font=output_font, justify=tk.CENTER, background="black", foreground="white")
        output_label.grid(row=row+1, column=col, sticky='NSEW', pady=(5,10))

        # for accessing DBC data
        fields[PARAMETERS[i]] = output_label

    # make fault labels
    for i in range(len(FAULT_LABELS)):
        fault_label = Label(data_frame, text=FAULT_LABELS[i], font=fault_font, justify=tk.CENTER, background="black", foreground="white")
        row = ((i + len(DATA_LABELS)) // 2) * 2
        if(i % 2 == 0):
            col = 0
        else:
            col = 3
        fault_label.grid(row=row, column=col, sticky=tk.NSEW, pady=20)
        faultFields[FAULTS[i]] = fault_label
    
    def update_camera():
        # Create a black image (480x640)
        frame = cv2.UMat(CAMERA_RATIO[0], CAMERA_RATIO[1], cv2.CV_8UC3)  # Create a black image
        img = PIL.Image.fromarray(frame.get())  # Convert it to PIL image
        img_tk = PIL.ImageTk.PhotoImage(image=img)  # Convert to Tkinter-compatible image

        video_label.img_tk = img_tk  # Keep reference to avoid garbage collection
        video_label.config(image=img_tk)  # Update the label to show the image

        root.after(50, update_camera)  # Refresh every 50ms

    # Function to update display fields
    def update_display():
        message = simulate_can_data() # Use to simulate BMS data when not actually accessing BMS data
        # message = get_bms_data() # Use to actually access the BMS data
        try:
            decoded_msg = db.decode_message(message['arbitration_id'], message['data'])

            for param, label in fields.items():
                if param in decoded_msg:
                    value = decoded_msg[param]
                    label.configure(text=f"{value:.1f}", font=output_font)
                    label.update_idletasks()

            if 'CustomFlag' in decoded_msg:
                bits = BitArray(decoded_msg['CustomFlag'].to_bytes()).bin
                for index in range(0, 4):
                    label = faultFields[CUSTOM_FLAG_INDICES[index]]
                    label.config(foreground="white")
                    if bits[index] == '1':
                        label.config(foreground="red")
                    label.update_idletasks()

        except Exception as e:
            print(f"Error decoding CAN message: {e}")

        root.after(2000, update_display)

    # Start updating UI elements
    update_display()
    update_camera()

    root.mainloop()

if __name__ == "__main__":
    create_display_window()
