import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from PIL import Image, ImageTk
import networkx as nx
import numpy as np
import pandas as pd

# ------------------- Data Loading -------------------
# Load the station data
stations_file_path = 'London_stations.csv'  # Path to the CSV file
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

# ------------------- Create Tube Graph -------------------
def create_tube_graph():
    # Initialize the graph
    G = nx.Graph()

    # Add nodes to the graph (stations with coordinates)
    G.add_nodes_from(stations)

    # New connections (stations pairs)
    connections = [
        ("Elephant & Castle", "Lambeth North"),
        ("Lambeth North", "Waterloo"),
        ("Waterloo", "Embankment"),
        ("Embankment", "Charing Cross"),
        ("Charing Cross", "Piccadilly Circus"),
        ("Piccadilly Circus", "Oxford Circus"),
        ("Oxford Circus", "Regent's Park"),
        ("Regent's Park", "Baker Street"),
        ("Baker Street", "Marylebone"),
        ("Marylebone", "Edgware Road"),
        ("Edgware Road", "Paddington"),
        ("Lancaster Gate", "Marble Arch"),
        ("Marble Arch", "Bond Street"),
        ("Bond Street", "Oxford Circus"),
        ("Oxford Circus", "Tottenham Court Road"),
        ("Tottenham Court Road", "Holborn"),
        ("Holborn", "Chancery Lane"),
        ("Chancery Lane", "St. Paul's"),
        ("St. Paul's", "Liverpool Street"),
        ("Liverpool Street", "Aldgate"),
        ("Aldgate", "Tower Hill"),
        ("Tower Hill", "Monument"),
        ("Monument", "Cannon Street"),
        ("Cannon Street", "Mansion House"),
        ("Mansion House", "Blackfriars"),
        ("Blackfriars", "Temple"),
        ("Temple", "Embankment"),
        ("Embankment", "Westminster"),
        ("Westminster", "St. James's Park"),
        ("St. James's Park", "Victoria"),
        ("Victoria", "Sloane Square"),
        ("Sloane Square", "South Kensington"),
        ("Whitechapel", "Liverpool Street"),
        ("Liverpool Street", "Farringdon"),
        ("Farringdon", "Tottenham Court Road"),
        ("Tottenham Court Road", "Bond Street"),
        ("Bond Street", "Paddington"),
        ("Euston Square", "King's Cross St. Pancras"),
        ("King's Cross St. Pancras", "Farringdon"),
        ("Farringdon", "Barbican"),
        ("Barbican", "Moorgate"),
        ("Moorgate", "Liverpool Street"),
        ("Liverpool Street", "Aldgate East"),
        ("St. John's Wood", "Baker Street"),
        ("Baker Street", "Bond Street"),
        ("Bond Street", "Green Park"),
        ("Green Park", "Westminster"),
        ("Westminster", "Waterloo"),
        ("Waterloo", "Southwark"),
        ("Southwark", "London Bridge"),
        ("South Kensington", "Knightsbridge"),
        ("Knightsbridge", "Hyde Park Corner"),
        ("Hyde Park Corner", "Green Park"),
        ("Green Park", "Piccadilly Circus"),
        ("Piccadilly Circus", "Leicester Square"),
        ("Leicester Square", "Covent Garden"),
        ("Covent Garden", "Holborn"),
        ("Holborn", "Russell Square"),
        ("Russell Square", "King's Cross St. Pancras"),
        ("Stockwell", "Vauxhall"),
        ("Vauxhall", "Pimlico"),
        ("Pimlico", "Victoria"),
        ("Victoria", "Green Park"),
        ("Green Park", "Oxford Circus"),
        ("Oxford Circus", "Warren Street"),
        ("Warren Street", "Euston"),
        ("Euston", "King's Cross St. Pancras"),
        ("Stockwell", "Oval"),
        ("Oval", "Elephant & Castle"),
        ("Elephant & Castle", "Borough"),
        ("Borough", "London Bridge"),
        ("London Bridge", "Bank"),
        ("Bank", "Moorgate"),
        ("Moorgate", "Old Street"),
        ("Old Street", "Angel"),
        ("Angel", "King's Cross St. Pancras"),
    ]

    # Add edges with distances calculated using the Haversine formula
    for station1, station2 in connections:
        if station1 in stations and station2 in stations:
            lat1, lon1 = stations[station1]
            lat2, lon2 = stations[station2]
            distance = haversine(lat1, lon1, lat2, lon2)
            G.add_edge(station1, station2, weight=distance)

    return G

# Dijkstra's algorithm to find the shortest path based on calculated distances
def dijkstra_shortest_path(G, source, target):
    # Use Dijkstra's algorithm to find the shortest path from source to target
    length, path = nx.single_source_dijkstra(G, source, target)
    return length, path

# ------------------- Tkinter GUI -------------------
def on_submit():
    source_station = source_entry.get().strip()
    target_station = target_entry.get().strip()

    # Check if both fields are filled
    if not source_station or not target_station:
        messagebox.showwarning("Input Error", "Please enter both Source and Target Stations.")
        return

    # Validate if the source and target stations are valid (case insensitive)
    source_station_lower = source_station.lower()
    target_station_lower = target_station.lower()

    # Check if the stations exist in the stations dictionary
    valid_stations = [station.lower() for station in stations.keys()]
    
    if source_station_lower not in valid_stations or target_station_lower not in valid_stations:
        messagebox.showerror("Invalid Station", "Please enter valid Source and Target stations.")
        return

    # Normalize to the proper casing from the stations dictionary
    source_station_normalized = next(station for station in stations if station.lower() == source_station_lower)
    target_station_normalized = next(station for station in stations if station.lower() == target_station_lower)

    # Find the shortest path using Dijkstra's algorithm
    distance, path = dijkstra_shortest_path(G, source_station_normalized, target_station_normalized)

    # Format the path output to show the journey step by step
    path_output = "\n".join([f"{path[i]} to {path[i+1]}" for i in range(len(path) - 1)])

    # Display the result in the scrolled text
    output = f"Shortest path from {source_station} to {target_station}:\n"
    output += f"Path: {path_output}\n"
    output += f"Total distance: {distance:.2f} kilometers"
    
    # Insert the output into the scrolled text widget
    result_text.config(state=tk.NORMAL)  # Enable editing
    result_text.delete(1.0, tk.END)  # Clear previous content
    result_text.insert(tk.END, output)  # Insert new content
    result_text.config(state=tk.DISABLED)  # Disable editing

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

submit_button = tk.Button(right_frame, text="Submit", command=on_submit)
submit_button.pack(pady=10)

# Create the London Tube graph
G = create_tube_graph()

# Run the Tkinter event loop
root.mainloop()
