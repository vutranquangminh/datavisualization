import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from PIL import Image, ImageTk
import pandas as pd
import networkx as nx
import numpy as np

# ------------------- Data Loading -------------------
# Load the station data
stations_file_path = 'London_Stations.csv'  # Path to the CSV file
stations_data = pd.read_csv(stations_file_path)

# Ensure column names are stripped of extra spaces
stations_data.columns = stations_data.columns.str.strip()

# Create a dictionary to map station names to their (latitude, longitude) pairs
stations = dict(zip(stations_data['Station'], zip(stations_data['Latitude'], stations_data['Longitude'])))

# ------------------- Haversine Function -------------------
# Haversine formula to calculate the distance between two latitude/longitude points
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])  # Convert to radians
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c  # Return distance in kilometers

# ------------------- Load Connections from CSV -------------------
def load_connections_from_csv(csv_path):
    # Load the connections CSV file using pandas
    df = pd.read_csv(csv_path)
    
    # Convert the dataframe to a list of tuples
    connections = list(zip(df['Source'], df['Target']))
    
    return connections

# ------------------- Create Tube Graph -------------------
def create_tube_graph(connections):
    G = nx.Graph()

    # Add nodes to the graph (stations with coordinates)
    G.add_nodes_from(stations)

    # Add edges with distances calculated using the Haversine formula
    for station1, station2 in connections:
        if station1 in stations and station2 in stations:
            lat1, lon1 = stations[station1]
            lat2, lon2 = stations[station2]
            distance = haversine(lat1, lon1, lat2, lon2)
            G.add_edge(station1, station2, weight=distance)

    return G

# ------------------- Dijkstra's Algorithm -------------------
def dijkstra_shortest_path(G, source, target):
    # Use Dijkstra's algorithm to find the shortest path from source to target
    length, path = nx.single_source_dijkstra(G, source, target)
    return length, path

# ------------------- Tkinter GUI -------------------
# Create the main Tkinter window
root = tk.Tk()
root.title("London Tube Map")
root.geometry("1000x1000")  # Adjusted window size to fit all elements

# Load and display the image of the London Tube Map
original_img = Image.open("London_Tube_Map.png")  # Ensure this image is in the same directory
img = original_img.resize((980, 580))  # Resize the image to fit at the top

# ------------------- Zoom Functionality -------------------
zoom_factor = 1.0  # Initial zoom factor (1.0 means no zoom)

def zoom_in():
    global zoom_factor
    zoom_factor *= 1.1  # Increase zoom factor by 10%
    zoom_image()

def zoom_out():
    global zoom_factor
    zoom_factor /= 1.1  # Decrease zoom factor by 10%
    zoom_image()

def zoom_image():
    global img_tk
    new_width = int(original_img.width * zoom_factor)
    new_height = int(original_img.height * zoom_factor)
    img_resized = original_img.resize((new_width, new_height), Image.LANCZOS)  # High-quality resampling
    img_tk = ImageTk.PhotoImage(img_resized)  # Convert resized image to ImageTk

    # Update the image displayed on the canvas
    canvas.itemconfig(image_id, image=img_tk)  # Update image without resizing the box

# Top Section: Canvas for Image Display (Fixed Size Box)
canvas = tk.Canvas(root, width=980, height=580)
canvas.pack(pady=10)  # Add some padding around the image

# Add the image to the canvas, but only once
img_tk = ImageTk.PhotoImage(img)
image_id = canvas.create_image(0, 0, anchor="nw", image=img_tk)

# Zoom buttons
zoom_in_button = tk.Button(root, text="Zoom In", command=zoom_in)
zoom_in_button.pack(side=tk.LEFT, padx=10, pady=10)

zoom_out_button = tk.Button(root, text="Zoom Out", command=zoom_out)
zoom_out_button.pack(side=tk.LEFT, padx=10, pady=10)

# Load the connections from the CSV file
connections = load_connections_from_csv('Station_Connections.csv')

# Create the London Tube graph using the connections
G = create_tube_graph(connections)

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
    source_station = source_entry.get().strip().title()  # Capitalize to handle case-insensitive input
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

    # Format the result
    result = f"Shortest path from {source_station} to {target_station}:\n"
    result += "\n".join([f"{path[i]} to {path[i+1]}" for i in range(len(path)-1)])
    result += f"\nTotal distance: {distance:.2f} kilometers"

    # Display the result in the text box
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, result)
    result_text.config(state=tk.DISABLED)

# Start the Tkinter main loop
root.mainloop()
