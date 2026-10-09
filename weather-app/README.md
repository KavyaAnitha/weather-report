# Weather Information Web Application

A simple beginner-friendly weather application built with Python, Flask, HTML, CSS, and the Open-Meteo API. It displays current weather information for any city or village **in India** only (locations outside India are not shown).

## Features

- Search for weather by Indian city or village name (India only)
- Displays location, temperature, weather condition, humidity, wind speed, and rain status
- Shows rain timing information if available
- Friendly error messages for invalid locations, empty input, API errors, and network errors
- Simple and responsive UI

## Technologies Used

- Python
- Flask
- HTML
- CSS
- Requests
- Open-Meteo API (free, no API key required)

## Setup and Installation

1. Navigate to the project directory:
   ```bash
   cd weather-app
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser and go to: `http://localhost:5000`

## How to Use

1. Enter a city or village name in the search box
2. Click "Get Weather"
3. View the current weather information

## Testing

- Test with a valid location (e.g., "London", "New York", "Tokyo")
- Test with an invalid location (e.g., "xyz123nonexistent")
- Test with empty input

## Notes

- This app uses the Open-Meteo API which is free and does not require an API key
- Rain timing information may not be available for all locations or weather conditions; if not, it will display "Rain timing information is not available."
- Geocoding is provided by Open-Meteo's Geocoding API