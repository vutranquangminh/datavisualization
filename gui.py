import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from PIL import Image, ImageTk

# Create the main Tkinter window
root = tk.Tk()
root.title("London Tube Map")
root.geometry("1000x1000")  # Adjusted window size to fit all elements

# Load and display the image of the London Tube Map
img = Image.open("London_Tube_Map.png")  # Ensure this image is in the same directory
img = img.resize((980, 580))  # Resize the image to fit at the top
img_tk = ImageTk.PhotoImage(img)

# Top Section: Image Display
image_label = tk.Label(root, image=img_tk)
image_label.pack(pady=10)  # Add some padding around the image

# Bottom Section: Split into two frames (Left: Results, Right: Inputs)
bottom_frame = tk.Frame(root)
bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Left Frame: ScrolledText for Results
left_frame = tk.Frame(bottom_frame)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

result_label = tk.Label(left_frame, text="Results", font=("Arial", 12, "bold"))
result_label.pack(anchor="w", pady=5)

result_text = scrolledtext.ScrolledText(left_frame, width=40, height=15, wrap=tk.WORD, state=tk.DISABLED)
result_text.pack(fill=tk.BOTH, expand=True)

# Right Frame: Inputs (Source, Target, Submit Button)
right_frame = tk.Frame(bottom_frame)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

source_label = tk.Label(right_frame, text="Source Station", font=("Arial", 12, "bold"))
source_label.pack(anchor="w", pady=5)

source_entry = tk.Entry(right_frame, width=30)
source_entry.pack(pady=5)

target_label = tk.Label(right_frame, text="Target Station", font=("Arial", 12, "bold"))
target_label.pack(anchor="w", pady=5)

target_entry = tk.Entry(right_frame, width=30)
target_entry.pack(pady=5)

submit_button = tk.Button(right_frame, text="Submit", command=lambda: on_submit())
submit_button.pack(pady=10)

# Function to handle the submit action
def on_submit():
    source_station = source_entry.get()
    target_station = target_entry.get()

    # Check if both fields are filled
    if not source_station or not target_station:
        messagebox.showwarning("Input Error", "Please enter both Source and Target Stations.")
        return

    # Display the result in the scrolled text
    output = f"Source Station: {source_station}\nTarget Station: {target_station}\n\nRouting information will appear here."
    
    # Insert the output into the scrolled text widget
    result_text.config(state=tk.NORMAL)  # Enable editing
    result_text.delete(1.0, tk.END)  # Clear previous content
    result_text.insert(tk.END, output)  # Insert new content
    result_text.config(state=tk.DISABLED)  # Disable editing

# Run the Tkinter event loop
root.mainloop()
