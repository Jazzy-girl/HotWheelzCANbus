import tkinter as tk

def hide_label():
    my_label.pack_forget()

def show_label():
    my_label.pack()

root = tk.Tk()

my_label = tk.Label(root, text="This is a label")
my_label.pack()

my_label2 = tk.Label(root, text="This is a label2")
my_label2.pack()

hide_button = tk.Button(root, text="Hide Label", command=hide_label)
hide_button.pack()

show_button = tk.Button(root, text="Show Label", command=show_label)
show_button.pack()

root.mainloop()