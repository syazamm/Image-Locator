Here’s a complete `README.md` for your **Image Locator Tool**:

---

# 🖼️ Image Locator Tool

The **Image Locator Tool** is a Python-based GUI application that extracts and displays metadata, including GPS coordinates, from JPEG images. It supports both single and batch processing, generates interactive maps for image locations, and shows detailed EXIF data like camera info, date, and time. The tool uses `Tkinter` for the interface and opens image locations in a browser using Folium-based maps.

---

## ✨ Features

* 📍 **Extract GPS Data** using both `ExifRead` and `Pillow`
* 🌍 **Map Visualization** with markers for GPS locations using `Folium`
* 🖼️ **Image Preview** with support for batch processing
* 🧾 **Metadata Extraction**: Camera brand, model, timestamp, ISO, focal length, and more
* 🔐 **File Hash (MD5)** generation for integrity checking
* 🌐 **Reverse Geocoding** to retrieve city and country names using `Geopy`
* 📑 **Processing Logs** viewable from the GUI
* 💡 **Dark-Themed Interface** using `ttkthemes`

---

## 🛠️ Dependencies

Install these Python packages before running the tool:

```bash
pip install exifread pillow folium geopy ttkthemes
```

---

## 🚀 How to Run

1. Save the script as `image_locator_tool.py`.
2. Run the script:

```bash
python image_locator_tool.py
```

---

## 📂 How to Use

### 📥 Select Image(s)

* **Select Image File**: Load a single image and view its metadata, image preview, and map.
* **Batch Process**: Load multiple images. All detected GPS coordinates will be displayed on a combined map.

### 📸 Image Tab

* View the selected image(s).
* Click on a GPS-tagged image to open its location in a web browser.

### 📊 Metadata Tab

* Choose an image from the dropdown to see its EXIF data and location details.
* Click **View Processing Log** to see all EXIF extraction messages and statuses.

---

## 🧠 How It Works

* **EXIF Extraction**: Uses `exifread` and `Pillow` to parse image metadata.
* **GPS Conversion**: Extracted GPS coordinates are converted into decimal format.
* **Reverse Geocoding**: Uses `Nominatim` (OpenStreetMap) to get city/country from coordinates.
* **Mapping**: `Folium` creates HTML maps showing where each image was taken.
* **Logging**: A hidden text log stores processing details for each file.

---

## 📌 Notes

* Only JPEG (`.jpg`, `.jpeg`) files are currently supported.
* GPS data must exist in the image EXIF data to generate maps.
* The app does not upload any data; all processing is local.

---

## 📷 Example Output

* Metadata:

  ```
  File Name: image1.jpg
  Latitude: 3.1390
  Longitude: 101.6869
  City: Kuala Lumpur
  Country: Malaysia
  Brand: Canon
  Model: EOS 70D
  File Hash (MD5): 8f1d909db82eabc234...
  ```

* Map:
  ![Map Output](https://user-images.githubusercontent.com/placeholder/map.png) *(Example visualization)*

---

## 🔒 License

This project is provided for educational and non-commercial use. Attribution appreciated.

---

Let me know if you want a version with screenshots or Markdown badge enhancements (like for Python version, etc).
