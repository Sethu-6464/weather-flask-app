import sys
import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

# Force UTF-8 Encoding
sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
load_dotenv()

# OpenWeather API Key
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city):
    """Fetch current weather data from OpenWeather API."""
    print(f"\n[INFO] Fetching current weather for city: {city}")

    if not OPENWEATHER_API_KEY:
        print("[ERROR] API Key is missing! Check .env file")
        return None

    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"

    try:
        response = requests.get(weather_url)
        response.raise_for_status()
        weather_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Weather API request failed: {e}")
        return None

    if "main" not in weather_data:
        print("[ERROR] Invalid response format")
        return None

    # Extract required weather details
    weather_details = {
        "city": city,
        "temperature": weather_data["main"].get("temp", "N/A"),
        "humidity": weather_data["main"].get("humidity", "N/A"),
        "pressure": weather_data["main"].get("pressure", "N/A"),
        "wind_speed": weather_data["wind"].get("speed", "N/A"),
        "rainfall": weather_data.get("rain", {}).get("1h", 0),  # Rainfall in last 1 hour
        "weather_description": weather_data["weather"][0].get("description", "N/A"),
    }

    return weather_details

def get_forecast(city):
    """Fetch 5-day weather forecast from OpenWeather API."""
    print(f"\n[INFO] Fetching 5-day forecast for city: {city}")

    if not OPENWEATHER_API_KEY:
        print("[ERROR] API Key is missing! Check .env file")
        return None

    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"

    try:
        response = requests.get(forecast_url)
        response.raise_for_status()
        forecast_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Forecast API request failed: {e}")
        return None

    if "list" not in forecast_data:
        print("[ERROR] Invalid forecast response format")
        return None

    # Extract upcoming forecast (next 5 days, every 3 hours)
    upcoming_forecast = []
    for entry in forecast_data["list"]:
        forecast_details = {
            "datetime": entry["dt_txt"],
            "temperature": entry["main"].get("temp", "N/A"),
            "humidity": entry["main"].get("humidity", "N/A"),
            "rainfall": entry.get("rain", {}).get("3h", 0),  # Rainfall in last 3 hours
            "weather_description": entry["weather"][0].get("description", "N/A"),
        }
        upcoming_forecast.append(forecast_details)

    return upcoming_forecast

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    city = request.form['city']
    weather_data = get_weather(city)
    forecast_data = get_forecast(city)

    if weather_data and forecast_data:
        return render_template('result.html', weather=weather_data, forecast=forecast_data)
    else:
        return jsonify({"error": "City not found or API error"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)