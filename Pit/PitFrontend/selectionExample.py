import tkinter as tk

class SelectionMarqueeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Selection Marquee")

        self.canvas = tk.Canvas(root, bg="white", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.frame = tk.Frame()
        self.frame.bind("<Button-1>", self.on_button_press)

        # Bind mouse events to the canvas
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        # Variables to store the start coordinates and the marquee object ID
        self.start_x = None
        self.start_y = None
        self.marquee_id = None

    def on_button_press(self, event):
        # Record the start position and delete any existing marquee
        self.start_x = event.x
        self.start_y = event.y
        if self.marquee_id:
            self.canvas.delete(self.marquee_id)
        # Create a new rectangle (initial state, coords will be updated in motion)
        self.marquee_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="blue", dash=(2, 2), fill="", width=1
        )

    def on_mouse_drag(self, event):
        # Update the coordinates of the marquee rectangle as the mouse moves
        current_x, current_y = event.x, event.y
        self.canvas.coords(
            self.marquee_id,
            self.start_x, self.start_y, current_x, current_y
        )

    def on_button_release(self, event):
        # Finalize the selection area
        end_x, end_y = event.x, event.y
        # Use the coordinates to determine the final selection region
        print(f"Selection made from ({self.start_x}, {self.start_y}) to ({end_x}, {end_y})")
        
        # You can now use these coordinates to select items on the canvas,
        # for example, using canvas.find_enclosed() or similar methods.

        # The marquee remains visible until the next selection starts (or you delete it here)
        # If you want it to disappear immediately, uncomment the line below:
        # self.canvas.delete(self.marquee_id)


if __name__ == "__main__":
    root = tk.Tk()
    app = SelectionMarqueeApp(root)
    root.mainloop()
