import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from PIL import Image, ImageTk
import pandas as pd
import numpy as np
import networkx as nx

# ------------------- Load Data -------------------
stations_file_path = './csv/station_coordinates.csv'  # Path to the CSV file
stations_data = pd.read_csv(stations_file_path)
stations_data.columns = stations_data.columns.str.strip()
stations = dict(zip(stations_data['Station'], zip(stations_data['Latitude'], stations_data['Longitude'])))

# Load the connections from the CSV file
connections_file_path = './csv/station_connections.csv'
connections_data = pd.read_csv(connections_file_path)
connections_data.columns = connections_data.columns.str.strip()
connections = list(zip(connections_data['Source'], connections_data['Target'], connections_data['Line']))

# ------------------- Haversine Function -------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])  # Convert to radians
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

# ------------------- Create Tube Graph -------------------
def create_tube_graph(connections):
    G = nx.Graph()
    G.add_nodes_from(stations)
    for station1, station2, line in connections:
        if station1 in stations and station2 in stations:
            lat1, lon1 = stations[station1]
            lat2, lon2 = stations[station2]
            distance = haversine(lat1, lon1, lat2, lon2)
            G.add_edge(station1, station2, weight=distance, line=line)

    return G
G = create_tube_graph(connections)

# ------------------- Dijkstra's Algorithm -------------------
def dijkstra_shortest_path(G, source, target):
    length, path = nx.single_source_dijkstra(G, source, target)
    return length, path

# ------------------- Tkinter GUI -------------------
root = tk.Tk()
root.title("London Tube Map")
root.geometry("1000x800")
root.iconbitmap("./picture/london_underground_logo.ico")

original_img = Image.open("./picture/london_map.png")
zoom_level = 0.3

# Function to zoom in
def zoom_in():
    global zoom_level, img_tk, img
    zoom_level *= 1.1
    img = original_img.resize((int(original_img.width * zoom_level), int(original_img.height * zoom_level)), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, image=img_tk, anchor="nw")
    update_scroll_region()

def zoom_out():
    global zoom_level, img_tk, img
    zoom_level /= 1.1
    img = original_img.resize((int(original_img.width * zoom_level), int(original_img.height * zoom_level)), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, image=img_tk, anchor="nw")
    update_scroll_region()

def update_scroll_region():
    canvas.config(scrollregion=canvas.bbox("all"))

# Create a frame to hold the canvas and add scrollbars
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Add vertical and horizontal scrollbars
vsb = tk.Scrollbar(frame, orient="vertical")
hsb = tk.Scrollbar(frame, orient="horizontal")

# Create a canvas widget
canvas = tk.Canvas(frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
canvas.grid(row=0, column=0, sticky="nsew")

# Configure the scrollbars
vsb.config(command=canvas.yview)
hsb.config(command=canvas.xview)

# Pack the scrollbars
vsb.grid(row=0, column=1, sticky="ns")
hsb.grid(row=1, column=0, sticky="ew")

# Initial display of the image on the canvas
img = original_img.resize((int(original_img.width * zoom_level), int(original_img.height * zoom_level)), Image.Resampling.LANCZOS)
img_tk = ImageTk.PhotoImage(img)
canvas.create_image(0, 0, image=img_tk, anchor="nw")

# Make the canvas expandable
frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)

# Update the scrollable region when the window is resized
update_scroll_region()

# ------------------- Results and Input Section -------------------
# Bottom Section: Split into two frames (Left: Results, Right: Inputs)
bottom_frame = tk.Frame(root)
bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Left Frame: ScrolledText for Results
left_frame = tk.Frame(bottom_frame)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

result_label = tk.Label(left_frame, text="Results", font=("Arial", 12, "bold"))
result_label.pack(anchor="w", pady=5)

result_text = scrolledtext.ScrolledText(left_frame, width=40, height=10, wrap=tk.WORD, state=tk.DISABLED,font=("Arial", 15))
result_text.pack(fill=tk.BOTH, expand=True)

# Right Frame: Inputs (Source, Target, Submit Button, Zoom in Button, Zoom out Button)
right_frame = tk.Frame(bottom_frame)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

# Zoom in and zoom out buttons (arranged horizontally at the top)
zoom_frame = tk.Frame(right_frame)
zoom_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

zoom_in_button = tk.Button(zoom_frame, text="Zoom In", command=zoom_in)
zoom_in_button.pack(side=tk.LEFT, padx=5)

zoom_out_button = tk.Button(zoom_frame, text="Zoom Out", command=zoom_out)
zoom_out_button.pack(side=tk.LEFT, padx=5)

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
    source_station = source_entry.get().strip().title()
    target_station = target_entry.get().strip().title()

    # Check if both fields are filled
    if not source_station or not target_station:
        messagebox.showwarning("Input Error", "Please enter both Source and Target Stations.")
        return

    # Check if the stations are valid
    if source_station not in stations or target_station not in stations:
        messagebox.showerror("Invalid Station", "One or both of the stations are invalid. Please check the input.")
        return

    # Find the shortest path and its length
    distance, path = dijkstra_shortest_path(G, source_station, target_station)

    # Calculate the total distance
    total_distance = distance

    # Calculate the average time (in minutes) using the given speed (35 km/h)
    speed_kmh = 35  # Average speed in km/h
    total_time_minutes = (total_distance / speed_kmh) * 60  # Convert time to minutes

    # Format the result
    result = f"Shortest path from {source_station} to {target_station}:\n"
    for i in range(len(path) - 1):
        result += f"{path[i]} to {path[i + 1]} in {G[path[i]][path[i + 1]]['line']} Line\n"
    
    result += f"\nTotal distance: {total_distance:.2f} kilometers"
    result += f"\nThe average time: {total_time_minutes:.2f} minutes"

    # Display the result in the text box
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, result)
    result_text.config(state=tk.DISABLED)

root.mainloop()