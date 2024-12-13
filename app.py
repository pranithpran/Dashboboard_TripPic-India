from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/nextpage.html")
def source():
    return render_template("source_data.html")

# Route to handle form submission
global start_date
global end_date
global departure
@app.route("/submit", methods=["POST"])
def submit():
    # Fetch data from the form
    departure = request.form.get("departure")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    
    # Pass the data to the dashboard template
    return render_template("dashboard.html", departure=departure, start_date=start_date, end_date=end_date)

# Route to handle city data retrieval
import requests
from datetime import datetime

def fetch_weather_forecast( start_date, end_date,city):
    """
    Fetches weather forecast for a given city and date range using OpenWeatherMap API.
    
    Args:
        city (str): Name of the city.
        start_date (str): Starting date in 'YYYY-MM-DD' format.
        end_date (str): Ending date in 'YYYY-MM-DD' format.

    Returns:
        list: List of weather data for the given city and date range.
    """
    API_KEY = "4af276f0c7f4969789e272dae0a06f5e"  # Your API key
    try:
        # API URL for forecast (5-day/3-hour data)
        url = "https://api.openweathermap.org/data/2.5/forecast"
        
        # Parameters to pass in the request
    
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric",  # To get temperatures in Celsius
        }
        
        # Send GET request
        response = requests.get(url, params=params)
        
        # Check if the API request was successful
        if response.status_code != 200:
            print("Error fetching weather data:", response.json())
            return []
        
        data = response.json()
        forecast_list = data.get("list", [])
        
        # Convert input dates to datetime.date objects
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        # Filter the forecast between start_date and end_date
        filtered_data = []
        for forecast in forecast_list:
            forecast_datetime = datetime.utcfromtimestamp(forecast["dt"])
            forecast_date = forecast_datetime.date()
            if start_date <= forecast_date <= end_date:
                filtered_data.append({
                    "date": forecast_date.strftime("%Y-%m-%d"),
                    "time": forecast["dt_txt"],
                    "temperature": forecast["main"]["temp"],
                    "weather": forecast["weather"][0]["description"],
                })
        
        return filtered_data
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []



@app.route("/get_city_data")
def get_city_data():
    city = request.args.get("city")  # Fetch the city name from the query parameters

    if not city:
        return jsonify({"error": "City parameter is missing"}), 400
    wd = fetch_weather_forecast("2024-12-16","2024-12-20",city)
    # Mocked data for demonstration purposes (replace with real data retrieval logic)
    print(wd)
    city_data = {
        "Mumbai": {
            "weather": "27°C, Mostly Sunny",
            "news": "Mumbai to host the upcoming tech summit.",
            "flights": "Average flight price: $120"
        },
        "Delhi": {
            "weather": "24°C, Cloudy",
            "news": "Delhi's air quality improves after rains.",
            "flights": "Average flight price: $100"
        },
        "Bangalore": {
            "weather": "22°C, Rainy",
            "news": "Bangalore startup raises $10M in funding.",
            "flights": "Average flight price: $110"
        }
    }

    # Fetch data for the requested city, or return a default response
    data = city_data.get(city, {
        "weather": "Weather data not available.",
        "news": "News data not available.",
        "flights": "Flight data not available."
    })

    # Log the city for backend debugging
    print(f"City requested: {city}")

    return jsonify({
        "weather": wd,
        "news": data["news"],
        "flights": data["flights"]
    })

if __name__ == "__main__":
    app.run(debug=True)

