import os
import exifread
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS, GPSTAGS
import folium
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import hashlib
from geopy.geocoders import Nominatim
import webbrowser
from ttkthemes import ThemedTk


# Constants
FONT = ("Arial", 12)
THEME = "equilux"

# Function to extract GPS data using exifread
def extract_gps_data_exifread(image_path):
    try:
        with open(image_path, 'rb') as image_file:
            tags = exifread.process_file(image_file)
            gps_data = {tag: value for tag, value in tags.items() if tag.startswith("GPS")}
            return gps_data
    except Exception as e:
        print(f"Error reading GPS data using exifread: {e}")
    return {}

# Function to extract GPS data using Pillow
def extract_gps_data_pillow(image_path):
    try:
        img = Image.open(image_path)
        exif_data = img._getexif() or {}
        gps_info = {}
        if exif_data:
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag)
                if tag_name == "GPSInfo":
                    for key in value.keys():
                        gps_tag_name = GPSTAGS.get(key, key)
                        gps_info[gps_tag_name] = value[key]
        return gps_info
    except Exception as e:
        print(f"Error reading GPS data using Pillow: {e}")
    return {}

# Function to convert GPS coordinates into decimal format
def convert_to_decimal(coord, ref):
    degrees, minutes, seconds = coord
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

# Function to process an image and extract GPS information
def process_image(image_path, log_text):
    log_text.insert(tk.END, f"Processing image: {image_path}\n")

    gps_data = extract_gps_data_exifread(image_path)
    if not gps_data:
        log_text.insert(tk.END, "No GPS data found using exifread. Trying Pillow...\n")
        gps_data = extract_gps_data_pillow(image_path)

    if not gps_data:
        log_text.insert(tk.END, "No GPS data found in the image.\n")
        return None

    log_text.insert(tk.END, "--- EXIF Data ---\n")
    for key, value in gps_data.items():
        log_text.insert(tk.END, f"{key}: {value}\n")

    if "GPS GPSLatitude" in gps_data and "GPS GPSLongitude" in gps_data:
        latitude = [float(x.num) / float(x.den) for x in gps_data["GPS GPSLatitude"].values]
        longitude = [float(x.num) / float(x.den) for x in gps_data["GPS GPSLongitude"].values]
        lat_ref = gps_data.get("GPS GPSLatitudeRef", "N").values[0]
        lon_ref = gps_data.get("GPS GPSLongitudeRef", "E").values[0]
        lat_decimal = convert_to_decimal(latitude, lat_ref)
        lon_decimal = convert_to_decimal(longitude, lon_ref)
        log_text.insert(tk.END, f"Coordinates: Latitude {lat_decimal}, Longitude {lon_decimal}\n")
        return lat_decimal, lon_decimal
    else:
        log_text.insert(tk.END, "GPS data tags not found.\n")
        return None

# Function to reverse geocode and get location info (City, Country)
def reverse_geocode(lat, lon):
    geolocator = Nominatim(user_agent="image_locator")
    location = geolocator.reverse((lat, lon), language='en')
    location_info = location.raw.get('address', {})
    city = location_info.get('city', 'N/A')
    country = location_info.get('country', 'N/A')
    return city, country

# Function to process metadata and return formatted information
def process_metadata(image_path):
    img = Image.open(image_path)
    exif_data = img._getexif() or {}

    metadata = [
        ("File Name", os.path.basename(image_path)),
        ("Image Size", f"{img.size[0]} x {img.size[1]}"),
        ("Resolution", img.info.get('dpi', 'N/A')),
        ("Date", exif_data.get(36867, 'N/A')),
        ("Time", exif_data.get(36868, 'N/A')),
        ("Time Zone", exif_data.get(42036, 'N/A')),
        ("Brand", exif_data.get(271, 'N/A')),
        ("Model", exif_data.get(272, 'N/A')),
        ("Lens Info", exif_data.get(42034, 'N/A')),
        ("Shutter", exif_data.get(33434, 'N/A')),
        ("F Number", exif_data.get(33437, 'N/A')),
        ("Iso Speed", exif_data.get(34855, 'N/A')),
        ("Flash", exif_data.get(37385, 'N/A')),
        ("Focal Length", exif_data.get(37386, 'N/A'))
    ]

    # GPS Information
    gps_data = extract_gps_data_exifread(image_path) or extract_gps_data_pillow(image_path)
    if gps_data:
        latitude = [float(x.num) / float(x.den) for x in gps_data.get("GPS GPSLatitude", {}).values]
        longitude = [float(x.num) / float(x.den) for x in gps_data.get("GPS GPSLongitude", {}).values]
        lat_ref = gps_data.get("GPS GPSLatitudeRef", "N").values[0]
        lon_ref = gps_data.get("GPS GPSLongitudeRef", "E").values[0]
        lat_decimal = convert_to_decimal(latitude, lat_ref)
        lon_decimal = convert_to_decimal(longitude, lon_ref)

        metadata.append(("Latitude", lat_decimal))
        metadata.append(("Longitude", lon_decimal))
        metadata.append(("Coordinate", f"({lat_decimal}, {lon_decimal})"))

        # Reverse Geocoding to get location info (City, Country)
        city, country = reverse_geocode(lat_decimal, lon_decimal)
        metadata.append(("City", city))
        metadata.append(("Country", country))
    else:
        metadata.append(("GPS Data", "No GPS data found."))

    # Hash Information
    try:
        with open(image_path, 'rb') as f:
            original_data = f.read()
            original_hash = hashlib.md5(original_data).hexdigest()
            metadata.append(("File Hash (MD5)", original_hash))
    except Exception as e:
        metadata.append(("File Hash (MD5)", f"Error: {e}"))

    return metadata

# Function to create an interactive map with GPS coordinates
def create_map(coordinates, output_file="map.html"):
    if not coordinates:
        return None

    # Calculate the bounds of all coordinates
    lat_min = min(coord[0] for coord in coordinates)
    lat_max = max(coord[0] for coord in coordinates)
    lon_min = min(coord[1] for coord in coordinates)
    lon_max = max(coord[1] for coord in coordinates)

    # Create a map centered on the midpoint of all coordinates
    map_center = [(lat_min + lat_max) / 2, (lon_min + lon_max) / 2]
    map_obj = folium.Map(location=map_center, zoom_start=10)

    # Add markers for all coordinates
    for i, (lat, lon) in enumerate(coordinates):
        folium.Marker([lat, lon], popup=f"Image {i+1}").add_to(map_obj)

    # Fit the map to the bounds of all markers
    map_obj.fit_bounds([[lat_min, lon_min], [lat_max, lon_max]])

    map_obj.save(output_file)
    return output_file

# Function to display the image in Tkinter
def display_image(image_path, canvas, size=(200, 200)):
    if image_path:
        img = Image.open(image_path)
        img = img.resize(size)  # Resize to fit the window
        photo = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        canvas.image = photo  # Keep a reference to the image
    else:
        canvas.create_image(0, 0, anchor=tk.NW, image=None)  # Clear the image if no path is provided

# Function to handle single file selection in GUI
def select_file(tree, image_frame, status_bar, progress_bar, log_text, metadata_dict):
    file_path = filedialog.askopenfilename(
        title="Select an Image File",
        filetypes=(("JPEG files", "*.jpg;*.jpeg"), ("All files", "*.*"))
    )
    if file_path:
        # Clear previous results
        for widget in image_frame.winfo_children():
            widget.destroy()
        log_text.delete(1.0, tk.END)
        status_bar.config(text="Processing...")

        # Process the image
        gps_coordinates = process_image(file_path, log_text)
        metadata = process_metadata(file_path)
        metadata_dict[os.path.basename(file_path)] = metadata

        # Display the image in the Image tab
        canvas = tk.Canvas(image_frame, width=500, height=500)
        canvas.pack(fill=tk.BOTH, expand=True)
        display_image(file_path, canvas, size=(500, 500))  # Larger image in Image tab

        # Update the dropdown menu
        update_dropdown(metadata_dict, tree)

        # Display the map in the default web browser (if GPS data exists)
        if gps_coordinates:
            map_file = create_map([gps_coordinates], output_file="map.html")
            webbrowser.open(f"file://{os.path.abspath(map_file)}")
            status_bar.config(text="Processing complete. Map opened in browser.")
        else:
            messagebox.showwarning("No GPS Data", "No GPS data found in the selected image.")
            status_bar.config(text="Processing complete. No GPS data found.")

# Function to handle batch processing of multiple files
def batch_process(tree, image_frame, status_bar, progress_bar, log_text, metadata_dict):
    file_paths = filedialog.askopenfilenames(
        title="Select Image Files for Batch Processing",
        filetypes=(("JPEG files", "*.jpg;*.jpeg"), ("All files", "*.*"))
    )
    if file_paths:
        # Clear previous results
        for widget in image_frame.winfo_children():
            widget.destroy()
        log_text.delete(1.0, tk.END)
        status_bar.config(text="Processing...")

        coordinates = []
        progress_bar["maximum"] = len(file_paths)
        for i, file_path in enumerate(file_paths):
            log_text.insert(tk.END, f"Processing file {i+1} of {len(file_paths)}: {file_path}\n")
            gps_coordinates = process_image(file_path, log_text)
            metadata = process_metadata(file_path)
            metadata_dict[os.path.basename(file_path)] = metadata

            # Display the image in the Image tab
            canvas = tk.Canvas(image_frame, width=200, height=200)
            canvas.grid(row=i // 4, column=i % 4, padx=5, pady=5)
            display_image(file_path, canvas, size=(200, 200))  # Smaller images in Image tab for batch

            # Collect GPS coordinates for the map
            if gps_coordinates:
                coordinates.append(gps_coordinates)
            else:
                messagebox.showwarning("No GPS Data", f"No GPS data found in the image: {file_path}")
            progress_bar["value"] = i + 1
            root.update_idletasks()

        # Update the dropdown menu
        update_dropdown(metadata_dict, tree)

        # Display the map in the default web browser (if at least one image has GPS data)
        if coordinates:
            map_file = create_map(coordinates, output_file="combined_map.html")
            webbrowser.open(f"file://{os.path.abspath(map_file)}")
            status_bar.config(text="Batch processing complete. Map opened in browser.")
        else:
            messagebox.showwarning("No GPS Data", "No GPS data found in any of the selected images.")
            status_bar.config(text="Batch processing complete. No GPS data found.")
        progress_bar["value"] = 0

# Function to update the dropdown menu with file names
def update_dropdown(metadata_dict, tree):
    dropdown["values"] = list(metadata_dict.keys())
    if dropdown["values"]:
        dropdown.current(0)
        update_treeview(tree, metadata_dict[dropdown.get()])

# Function to update the treeview with metadata for the selected file
def update_treeview(tree, metadata):
    for row in tree.get_children():
        tree.delete(row)
    for key, value in metadata:
        tree.insert("", "end", values=(key, value))

# Function to show the processing log in a new window
def show_log(log_text):
    log_window = tk.Toplevel(root)
    log_window.title("Processing Log")
    log_window.geometry("600x400")

    log_display = scrolledtext.ScrolledText(log_window, width=60, height=20, font=FONT)
    log_display.pack(pady=10, fill=tk.BOTH, expand=True)
    log_display.insert(tk.END, log_text.get(1.0, tk.END))
    log_display.config(state=tk.DISABLED)  # Make the log read-only

# Main GUI application
def main():
    global root, dropdown
    root = ThemedTk(theme=THEME)
    root.title("Image Locator Tool")

    # Create tabs
    tab_control = ttk.Notebook(root)
    tab_image = ttk.Frame(tab_control)
    tab_metadata = ttk.Frame(tab_control)

    tab_control.add(tab_image, text="Image")
    tab_control.add(tab_metadata, text="Metadata")
    tab_control.pack(expand=1, fill="both")

    # Image tab
    image_frame = tk.Frame(tab_image)
    image_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    # Buttons for file selection and batch processing
    button_frame = tk.Frame(tab_image)
    button_frame.pack(pady=5)

    # Log text (hidden in the background)
    log_text = scrolledtext.ScrolledText(root, width=60, height=10, font=FONT)
    log_text.pack_forget()  # Hide the log text widget

    # Dictionary to store metadata for all files
    metadata_dict = {}

    tk.Button(button_frame, text="Select Image File", command=lambda: select_file(tree, image_frame, status_bar, progress_bar, log_text, metadata_dict),
              font=FONT).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Batch Process", command=lambda: batch_process(tree, image_frame, status_bar, progress_bar, log_text, metadata_dict),
              font=FONT).pack(side=tk.LEFT, padx=5)

    # Metadata tab
    dropdown_frame = tk.Frame(tab_metadata)
    dropdown_frame.pack(pady=10)

    dropdown_label = tk.Label(dropdown_frame, text="Select File:", font=FONT)
    dropdown_label.pack(side=tk.LEFT, padx=5)

    dropdown = ttk.Combobox(dropdown_frame, state="readonly", font=FONT)
    dropdown.pack(side=tk.LEFT, padx=5)
    dropdown.bind("<<ComboboxSelected>>", lambda event: update_treeview(tree, metadata_dict[dropdown.get()]))

    tree = ttk.Treeview(tab_metadata, columns=("Key", "Value"), show="headings")
    tree.heading("Key", text="Key")
    tree.heading("Value", text="Value")
    tree.column("Key", width=150)
    tree.column("Value", width=400)
    tree.pack(pady=10, fill=tk.BOTH, expand=True)

    # Button to show processing log
    log_button = tk.Button(tab_metadata, text="View Processing Log", command=lambda: show_log(log_text), font=FONT)
    log_button.pack(pady=10)

    # Status bar
    status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Progress bar
    progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=100, mode='determinate')
    progress_bar.pack(side=tk.BOTTOM, fill=tk.X)

    root.mainloop()

if __name__ == "__main__":
    main()
