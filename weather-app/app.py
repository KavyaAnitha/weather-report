from flask import Flask, render_template, request, flash
from weather_service import WeatherService, WeatherServiceError, LocationNotFoundError, APIError, NetworkError

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Simple key for demo purposes

weather_service = WeatherService()


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    error = None
    
    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        
        # Handle empty input
        if not city:
            error = "Please enter a city or village name."
            return render_template('index.html', weather_data=weather_data, error=error)
        
        try:
            # Get weather data
            weather_data = weather_service.get_current_weather(city)
        except LocationNotFoundError as e:
            error = str(e)
        except APIError as e:
            error = str(e)
        except NetworkError as e:
            error = str(e)
        except WeatherServiceError as e:
            error = str(e)
        except Exception as e:
            error = "An unexpected error occurred. Please try again."
            print(f"Unexpected error: {e}")
    
    return render_template('index.html', weather_data=weather_data, error=error)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
