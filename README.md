### README.md

```markdown
# Advanced Solar Potential Analyzer

The **Advanced Solar Potential Analyzer** is a Python application designed to estimate the solar energy potential of a given location. It uses satellite imagery, Open-Meteo API for solar radiation data, and advanced computer vision techniques to analyze structures for solar panel feasibility. The app provides insights into daily, weekly, and yearly solar energy potential with clear visualizations.

---

## Features
- **Interactive Map**: Explore locations using a Mapbox-powered map interface.
- **Satellite Image Analysis**: Fetch and analyze satellite images for estimating structure area.
- **Solar Potential Calculation**: Compute solar energy potential based on structure area and irradiance data.
- **Data Visualization**: Generate insightful charts for solar radiation and potential energy output.
- **Adaptive Units**: Display results in appropriate units (Wh, kWh, MWh, GWh) based on energy magnitude.
- **Error Handling**: Implements robust error handling with caching and retry logic for API calls.

---

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Supreeth1997/Solar_Energy_Gen_AI.git
   cd solar-potential-analyzer
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install additional tools if needed:
   - [TkinterMapView](https://github.com/TomSchimansky/TkinterMapView) for interactive maps.
   - OpenCV for computer vision tasks.

---

## Usage
1. Run the application:
   ```bash
   python solar_potential_analyzer.py
   ```

2. Enter a valid Mapbox API key in the designated field to enable map features.

3. Navigate the map to the desired location. Use the **Satellite View** toggle to switch map modes.

4. Click **Analyze Solar Potential** to:
   - Fetch a satellite image of the selected area.
   - Analyze structure areas using computer vision.
   - Calculate solar potential based on retrieved weather data.

5. View results in the **Analysis Results** section and explore the visualizations under **Visualizations**.

---

## Requirements
- Python 3.8+
- A valid Mapbox API key for fetching satellite imagery.
- Open-Meteo API (no API key required but must adhere to usage limits).

---

## Technical Details
### Key Libraries
- **Tkinter**: GUI framework.
- **OpenCV**: Structure detection using image processing.
- **Matplotlib**: Data visualization for solar potential and irradiance.
- **Open-Meteo API**: Retrieve solar radiation forecasts.

### Functional Workflow
1. Fetch satellite images from Mapbox API.
2. Detect structures using HSV masking and morphology operations in OpenCV.
3. Calculate area of structures based on map zoom level and geographic latitude.
4. Retrieve solar irradiance data from Open-Meteo API for the selected location.
5. Estimate solar energy potential over daily, weekly, and yearly periods.
6. Visualize the analysis results and energy potential.

---

## Troubleshooting
- **Satellite Image Download Error**: Ensure you’ve provided a valid Mapbox API key.
- **No Solar Data**: Check network connectivity or retry later if Open-Meteo API is down.
- **App Crashes**: Verify all required dependencies are installed correctly.

---

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a pull request.

---

## Author
Developed by Supreeth Gowda (https://github.com/Supreeth1997). For inquiries, feel free to reach out!

---

## Acknowledgments
- **Mapbox** for satellite imagery.
- **Open-Meteo API** for free solar irradiance data.
- **TkinterMapView** for interactive map integration.
```

Let me know if you need additional sections or edits for this README!
