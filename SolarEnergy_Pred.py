import numpy as np
import cv2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkintermapview import TkinterMapView
import requests
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import pandas as pd
import math
import openmeteo_requests
import requests_cache
from retry_requests import retry

class SolarPotentialAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Solar Potential Analyzer")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1e1e1e")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()

        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)

        self.create_widgets()

    def configure_styles(self):
        self.style.configure("TFrame", background="#1e1e1e")
        self.style.configure("TButton", padding=10, relief="flat", background="#4CAF50", foreground="white")
        self.style.map("TButton", background=[("active", "#45a049")])
        self.style.configure("TEntry", padding=10, fieldbackground="#2d2d2d", foreground="white")
        self.style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Arial", 12))
        self.style.configure("TLabelframe", background="#1e1e1e", foreground="white")
        self.style.configure("TLabelframe.Label", background="#1e1e1e", foreground="white", font=("Arial", 14, "bold"))
        self.style.configure("TCheckbutton", background="#1e1e1e", foreground="white")
        self.style.map("TCheckbutton", background=[("active", "#2d2d2d")])

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel for map and controls
        left_panel = ttk.Frame(main_frame, width=600)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # API Key input
        api_frame = ttk.LabelFrame(left_panel, text="Mapbox API Key", padding="10")
        api_frame.pack(fill=tk.X, pady=10)
        
        self.api_key_entry = ttk.Entry(api_frame, width=50)
        self.api_key_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Map widget
        map_frame = ttk.LabelFrame(left_panel, text="Map View", padding="10")
        map_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.map_widget = TkinterMapView(map_frame, width=600, height=400, corner_radius=0)
        self.map_widget.pack(fill=tk.BOTH, expand=True)
        self.map_widget.set_position(51.5074, -0.1278)  # Set initial position to London
        self.map_widget.set_zoom(12)

        # Map type toggle
        self.map_type_var = tk.StringVar(value="normal")
        self.map_type_toggle = ttk.Checkbutton(
            map_frame,
            text="Satellite View",
            variable=self.map_type_var,
            onvalue="satellite",
            offvalue="normal",
            command=self.toggle_map_type
        )
        self.map_type_toggle.pack(pady=5)

        # Analyze button
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=10)

        self.analyze_button = ttk.Button(button_frame, text="Analyze Solar Potential", command=self.analyze_solar_potential)
        self.analyze_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Right panel for results and visualizations
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Results
        self.results_frame = ttk.LabelFrame(right_panel, text="Analysis Results", padding="10")
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.results_text = tk.Text(self.results_frame, wrap=tk.WORD, font=("Arial", 12), height=10, bg="#2d2d2d", fg="white")
        self.results_text.pack(fill=tk.BOTH, expand=True)

        # Visualizations
        self.viz_frame = ttk.LabelFrame(right_panel, text="Visualizations", padding="10")
        self.viz_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(6, 8), facecolor='#1e1e1e')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def toggle_map_type(self):
        if self.map_type_var.get() == "satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        else:
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")

    def analyze_solar_potential(self):
        center_position = self.map_widget.get_position()
        self.latitude, self.longitude = center_position
        self.satellite_image_path = self.fetch_satellite_image(self.latitude, self.longitude)
        
        if self.satellite_image_path:
            structure_mask, output_image_path = self.detect_structures_and_overlay(self.satellite_image_path)
            self.show_image_with_overlay(output_image_path)
            self.calculate_and_display_results(structure_mask)

    def fetch_satellite_image(self, latitude, longitude):
        mapbox_access_token = self.api_key_entry.get()
        if not mapbox_access_token:
            messagebox.showerror("Error", "Please enter a valid Mapbox API Key.")
            return None
        
        url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{longitude},{latitude},15/600x500@2x?access_token={mapbox_access_token}"
        response = requests.get(url)

        if response.status_code == 200:
            image_path = f"satellite_image_{latitude}_{longitude}.png"
            with open(image_path, 'wb') as img_file:
                img_file.write(response.content)
            return image_path
        else:
            messagebox.showerror("Error", "Failed to download satellite image.")
            return None

    def detect_structures_and_overlay(self, image_path):
        image = cv2.imread(image_path)
        # Crop the bottom 100 pixels
        image = image[:-100, :]
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_bound = np.array([0, 0, 100])
        upper_bound = np.array([180, 30, 255])
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        color_overlay = np.zeros_like(image)
        color_overlay[mask > 0] = [0, 255, 0]
        output_image = cv2.addWeighted(image, 0.7, color_overlay, 0.3, 0)
        output_image_path = "structure_detection_overlay.png"
        cv2.imwrite(output_image_path, output_image)
        return mask, output_image_path

    def show_image_with_overlay(self, image_path):
        img = Image.open(image_path)
        img.thumbnail((400, 400))
        img_tk = ImageTk.PhotoImage(img)
        
        if hasattr(self, 'image_label'):
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk
        else:
            self.image_label = ttk.Label(self.results_frame, image=img_tk)
            self.image_label.image = img_tk
            self.image_label.pack(pady=10)

    def calculate_and_display_results(self, structure_mask):
        # Calculate area using image scale
        zoom_level = 15  # From the Mapbox API call
        latitude = self.latitude
        meters_per_pixel = 156543.03392 * math.cos(latitude * math.pi / 180) / math.pow(2, zoom_level)
        pixel_area_sqm = meters_per_pixel * meters_per_pixel
        total_area_sqm = structure_mask.size * pixel_area_sqm
        structure_pixels = np.sum(structure_mask > 0)
        structure_area_sqm = structure_pixels * pixel_area_sqm

        # Fetch solar radiation data
        solar_data = self.fetch_solar_data(self.latitude, self.longitude)
        
        # Calculate solar potential
        avg_solar_panel_efficiency = 0.20  # 20% efficiency

        hourly_solar_potential = []
        for _, row in solar_data.iterrows():
            # Using global_tilted_irradiance as it's most relevant for solar panels
            hourly_potential = structure_area_sqm * avg_solar_panel_efficiency * row['global_tilted_irradiance'] / 1000  # Convert W to kW
            hourly_solar_potential.append(hourly_potential)

        daily_solar_potential = [sum(hourly_solar_potential[i:i+24]) for i in range(0, len(hourly_solar_potential), 24)]
        
        # Calculate average and total solar potential
        avg_daily_potential = np.mean(daily_solar_potential)
        total_weekly_potential = np.sum(daily_solar_potential)
        estimated_yearly_potential = avg_daily_potential * 365

        # Use adaptive units
        daily_unit, daily_value = self.adaptive_units(avg_daily_potential)
        weekly_unit, weekly_value = self.adaptive_units(total_weekly_potential)
        yearly_unit, yearly_value = self.adaptive_units(estimated_yearly_potential)

        # Display results
        results_text = f"Solar Potential Analysis Results\n\n"
        results_text += f"📏 Total Area: {total_area_sqm:.2f} sq. meters\n"
        results_text += f"🏠 Estimated Structure Area: {structure_area_sqm:.2f} sq. meters\n\n"
        results_text += f"☀️ Average Daily Solar Potential: {daily_value:.2f} {daily_unit}\n"
        results_text += f"📅 Total Weekly Solar Potential: {weekly_value:.2f} {weekly_unit}\n"
        results_text += f"📊 Estimated Yearly Solar Potential: {yearly_value:.2f} {yearly_unit}"
        
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert(tk.END, results_text)

        # Update visualizations
        self.update_visualizations(solar_data, daily_solar_potential)

    def fetch_solar_data(self, latitude, longitude):
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ["global_tilted_irradiance", "direct_normal_irradiance", "diffuse_radiation"],
            "timezone": "auto",
            "forecast_days": 7
        }
        responses = self.openmeteo.weather_api(url, params=params)
        response = responses[0]
        
        hourly = response.Hourly()
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "global_tilted_irradiance": hourly.Variables(0).ValuesAsNumpy(),
            "direct_normal_irradiance": hourly.Variables(1).ValuesAsNumpy(),
            "diffuse_radiation": hourly.Variables(2).ValuesAsNumpy()
        }
        
        return pd.DataFrame(data=hourly_data)

    def adaptive_units(self, value):
        if value < 1:
            return "Wh", value * 1000
        elif value < 1000:
            return "kWh", value
        elif value < 1000000:
            return "MWh", value / 1000
        else:
            return "GWh", value / 1000000

    def update_visualizations(self, solar_data, daily_solar_potential):
        # Ensure we have the correct number of dates
        dates = solar_data['date'].dt.floor('D').unique()[:len(daily_solar_potential)]

        # Solar radiation chart
        self.ax1.clear()
        self.ax1.plot(solar_data['date'], solar_data['global_tilted_irradiance'], label='Global Tilted Irradiance', color='#4CAF50')
        self.ax1.plot(solar_data['date'], solar_data['direct_normal_irradiance'], label='Direct Normal Irradiance', color='#FFC107')
        self.ax1.plot(solar_data['date'], solar_data['diffuse_radiation'], label='Diffuse Radiation', color='#2196F3')
        self.ax1.set_title('Solar Radiation Forecast', color='white')
        self.ax1.set_xlabel('Date', color='white')
        self.ax1.set_ylabel('Irradiance (W/m²)', color='white')
        self.ax1.legend()
        self.ax1.set_facecolor('#2d2d2d')
        self.ax1.tick_params(colors='white')
        self.ax1.spines['bottom'].set_color('white')
        self.ax1.spines['top'].set_color('white') 
        self.ax1.spines['right'].set_color('white')
        self.ax1.spines['left'].set_color('white')

        # Solar potential chart
        self.ax2.clear()
        self.ax2.bar(dates, daily_solar_potential, color='#FFA000')
        self.ax2.set_title('Estimated Daily Solar Potential', color='white')
        self.ax2.set_xlabel('Date', color='white')
        self.ax2.set_ylabel('Energy (kWh)', color='white')
        self.ax2.set_facecolor('#2d2d2d')
        self.ax2.tick_params(colors='white')
        self.ax2.spines['bottom'].set_color('white')
        self.ax2.spines['top'].set_color('white') 
        self.ax2.spines['right'].set_color('white')
        self.ax2.spines['left'].set_color('white')

        self.fig.patch.set_facecolor('#1e1e1e')
        self.fig.autofmt_xdate()  # Rotate and align the tick labels
        self.fig.tight_layout()
        self.canvas.draw()

# Main Function to Run the App
if __name__ == "__main__":
    root = tk.Tk()
    app = SolarPotentialAnalyzer(root)
    root.mainloop()