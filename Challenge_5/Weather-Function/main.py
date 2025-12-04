import functions_framework
import requests
import json

@functions_framework.http
def get_weather(request):
    """
    HTTP Cloud Function that retrieves weather from NOAA.
    Expected JSON body: {"lat": "40.7128", "lon": "-74.0060"}
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    lat = None
    lon = None

    if request_json and 'lat' in request_json:
        lat = request_json['lat']
        lon = request_json['lon']
    elif request_args and 'lat' in request_args:
        lat = request_args['lat']
        lon = request_args['lon']

    if not lat or not lon:
        return json.dumps({"error": "Please provide 'lat' and 'lon'."}), 400

    headers = {
        'User-Agent': '(my-weather-app.com, contact@my-weather-app.com)'
    }

    try:
        # Step 1: Get the Grid Point
        point_url = f"https://api.weather.gov/points/{lat},{lon}"
        point_resp = requests.get(point_url, headers=headers)
        point_data = point_resp.json()

        if point_resp.status_code != 200:
            return json.dumps({"error": "Failed to retrieve grid point data", "details": point_data}), 500

        # Extract forecast URL
        forecast_url = point_data['properties']['forecast']

        # Step 2: Get the Forecast
        forecast_resp = requests.get(forecast_url, headers=headers)
        forecast_data = forecast_resp.json()
        
        if forecast_resp.status_code != 200:
            return json.dumps({"error": "Failed to retrieve forecast data"}), 500

        # Return the first period forecast (e.g., "Tonight" or "Today")
        periods = forecast_data['properties']['periods']
        current_forecast = periods[0]

        return json.dumps({
            "name": current_forecast['name'],
            "temperature": current_forecast['temperature'],
            "unit": current_forecast['temperatureUnit'],
            "forecast": current_forecast['detailedForecast']
        }), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return json.dumps({"error": str(e)}), 500
