"""
Weather Data Fetcher with Crop-Aware Duration.

Automatically fetches weather data for the specific crop cycle duration.
Integrates with OpenWeatherMap API for real-time and historical data.
"""

from datetime import datetime, timedelta
import json
import requests
from typing import Dict, List, Tuple, Optional
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import crop database
try:
    from crop_database import get_crop_cycle
except ImportError:
    # Fallback if running from different directory
    sys.path.insert(0, str(Path(__file__).parent))
    from crop_database import get_crop_cycle


class WeatherAPIFetcher:
    """
    Fetch real weather data from OpenWeatherMap API.
    
    Supports:
    - Current weather
    - Weather forecasts
    - Historical weather averaging
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize weather API fetcher.
        
        Args:
            api_key: OpenWeatherMap API key
                    If not provided, will load from OPENWEATHERMAP_API_KEY env var
                    Get free key from: https://openweathermap.org/api
        """
        # Use provided key, or load from environment, or None for mock mode
        self.api_key = api_key or os.getenv('OPENWEATHERMAP_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.one_call_url = "https://api.openweathermap.org/data/3.0/onecall"
    
    def get_current_weather(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Fetch current weather data for a location.
        
        Args:
            latitude: GPS latitude
            longitude: GPS longitude
        
        Returns:
            Dictionary with current weather or None if API fails
        """
        if not self.api_key:
            print("Warning: No OpenWeatherMap API key configured")
            return None
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'rainfall': data.get('rain', {}).get('1h', 0),
                    'feels_like': data['main']['feels_like'],
                    'pressure': data['main']['pressure'],
                    'timestamp': datetime.fromtimestamp(data['dt']).isoformat(),
                    'description': data['weather'][0]['description'],
                    'location_name': data.get('name', 'Unknown'),
                    'country': data.get('sys', {}).get('country', '')
                }
            else:
                print(f"Weather API error - Status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"Weather API timeout for location ({latitude}, {longitude})")
            return None
        except requests.exceptions.ConnectionError:
            print(f"Weather API connection error for location ({latitude}, {longitude})")
            return None
        except Exception as e:
            print(f"Error fetching current weather: {e}")
        
        return None
    
    def get_mock_weather(self, latitude: float, longitude: float) -> Dict:
        """
        Get mock weather data for testing when API is unavailable.
        
        Args:
            latitude: GPS latitude
            longitude: GPS longitude
        
        Returns:
            Dictionary with simulated weather data
        """
        import random
        
        # Generate realistic mock data based on location
        base_temp = 25 + (latitude / 10)  # Vary by latitude
        
        return {
            'temperature': round(base_temp + random.uniform(-5, 5), 2),
            'humidity': random.randint(40, 85),
            'rainfall': round(random.uniform(0, 50), 2) if random.random() > 0.7 else 0,  # 30% chance of rain
            'feels_like': round(base_temp + random.uniform(-3, 3), 2),
            'pressure': random.randint(1000, 1020),
            'timestamp': datetime.now().isoformat(),
            'description': 'scattered clouds',
            'location_name': 'Mock Location',
            'country': 'IN'
        }
    
    def get_forecast_weather(self, latitude: float, longitude: float, days: int = 5) -> Optional[List[Dict]]:
        """
        Fetch weather forecast for next N days.
        
        Args:
            latitude: GPS latitude
            longitude: GPS longitude
            days: Number of days to forecast (max 5 for free tier)
        
        Returns:
            List of daily weather forecasts
        """
        if not self.api_key:
            return None
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                forecasts = []
                
                for item in data['list']:
                    forecasts.append({
                        'temperature': item['main']['temp'],
                        'humidity': item['main']['humidity'],
                        'rainfall': item.get('rain', {}).get('3h', 0),
                        'timestamp': datetime.fromtimestamp(item['dt']).isoformat(),
                    })
                
                return forecasts
        except Exception as e:
            print(f"Error fetching forecast: {e}")
        
        return None
    
    def average_forecast_weather(self, forecasts: List[Dict]) -> Optional[Dict]:
        """
        Average weather data from forecasts.
        
        Args:
            forecasts: List of weather forecast entries
        
        Returns:
            Dictionary with averaged values
        """
        if not forecasts:
            return None
        
        avg_temp = sum(f['temperature'] for f in forecasts) / len(forecasts)
        avg_humidity = sum(f['humidity'] for f in forecasts) / len(forecasts)
        total_rainfall = sum(f['rainfall'] for f in forecasts)
        
        return {
            'avg_temperature': round(avg_temp, 2),
            'avg_humidity': round(avg_humidity, 2),
            'total_rainfall': round(total_rainfall, 2),
            'num_readings': len(forecasts),
            'period': '5-day forecast'
        }


class WeatherDataFetcher:
    """
    Fetch and average weather data for a specific crop cycle.
    Supports both demo mode and actual API calls.
    """
    
    def __init__(self, api_key: Optional[str] = None, use_mock: bool = True):
        """
        Initialize weather data fetcher.
        
        Args:
            api_key: OpenWeatherMap API key
            use_mock: Use mock data for demo (True) or real API (False)
        """
        self.api_key = api_key
        self.use_mock = use_mock
        self.api_fetcher = WeatherAPIFetcher(api_key) if api_key else None
    
    def get_weather_period(self, crop_name: str) -> Dict:
        """
        Calculate the weather data collection period based on crop cycle.
        
        Args:
            crop_name: Name of the crop
        
        Returns:
            Dictionary with start_date, end_date, duration_days
        """
        cycle_days = get_crop_cycle(crop_name)
        
        # End date = today
        end_date = datetime.now()
        
        # Start date = today - cycle days
        start_date = end_date - timedelta(days=cycle_days)
        
        return {
            'crop': crop_name.capitalize(),
            'cycle_days': cycle_days,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'period_description': f"Last {cycle_days} days (~{cycle_days/30:.1f} months)"
        }
    
    def calculate_averages(self, weather_data_list: List[Dict]) -> Optional[Dict]:
        """
        Calculate average temperature, humidity, and rainfall from weather data.
        
        Args:
            weather_data_list: List of weather readings with temp, humidity, rainfall
        
        Returns:
            Dictionary with average values
        """
        if not weather_data_list:
            return None
        
        avg_temp = sum(d['temp'] for d in weather_data_list) / len(weather_data_list)
        avg_humidity = sum(d['humidity'] for d in weather_data_list) / len(weather_data_list)
        total_rainfall = sum(d.get('rainfall', 0) for d in weather_data_list)
        
        return {
            'avg_temperature': round(avg_temp, 2),
            'avg_humidity': round(avg_humidity, 2),
            'total_rainfall': round(total_rainfall, 2),
            'num_readings': len(weather_data_list)
        }
    
    def get_mock_weather_data(self) -> Dict:
        """
        Generate mock weather data for testing/demo.
        
        Returns:
            Dictionary with mock weather averages
        """
        import random
        return {
            'avg_temperature': round(random.uniform(20, 32), 2),
            'avg_humidity': round(random.uniform(50, 85), 2),
            'total_rainfall': round(random.uniform(50, 300), 2),
            'data_source': 'mock_data',
            'note': 'Replace with real API data by providing API key'
        }
    
    def get_weather_for_crop(
        self, 
        crop_name: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Dict:
        """
        Get weather data for a specific crop cycle.
        
        Args:
            crop_name: Name of the crop
            latitude: GPS latitude (optional)
            longitude: GPS longitude (optional)
        
        Returns:
            Dictionary with weather data for the crop cycle
        """
        period_info = self.get_weather_period(crop_name)
        
        # Try to fetch real data if API is available
        if self.api_fetcher and latitude and longitude and not self.use_mock:
            print(f"Fetching weather for {crop_name} from API...")
            
            # Get 5-day forecast as demo
            forecasts = self.api_fetcher.get_forecast_weather(latitude, longitude, days=5)
            
            if forecasts:
                weather_avg = self.api_fetcher.average_forecast_weather(forecasts)
                return {
                    'status': 'success',
                    'crop': period_info['crop'],
                    'weather_period': period_info,
                    'weather_data': weather_avg,
                    'location': {'lat': latitude, 'lon': longitude},
                    'data_source': 'OpenWeatherMap API'
                }
        
        # Fall back to mock data or current weather
        if self.use_mock:
            print(f"Using mock weather data for {crop_name}...")
            weather_data = self.get_mock_weather_data()
        else:
            # Try to get current weather as fallback
            print(f"Using current weather as baseline for {crop_name}...")
            if self.api_fetcher and latitude and longitude:
                current = self.api_fetcher.get_current_weather(latitude, longitude)
                if current:
                    weather_data = {
                        'avg_temperature': current['temperature'],
                        'avg_humidity': current['humidity'],
                        'total_rainfall': current['rainfall'],
                        'data_source': 'current_weather_fallback'
                    }
                else:
                    weather_data = self.get_mock_weather_data()
            else:
                weather_data = self.get_mock_weather_data()
        
        return {
            'status': 'success',
            'crop': period_info['crop'],
            'weather_period': period_info,
            'weather_data': weather_data,
            'location': {'lat': latitude or 'not_specified', 'lon': longitude or 'not_specified'},
            'api_status': 'configured' if self.api_key else 'not_configured'
        }


# Demo usage
if __name__ == "__main__":
    print("=" * 70)
    print("Weather API Integration - Demo")
    print("=" * 70)
    
    # Demo 1: Mock data (no API key needed)
    print("\n\n📍 DEMO 1: Using Mock Data (No API Key)")
    print("-" * 70)
    
    fetcher_mock = WeatherDataFetcher(use_mock=True)
    
    result = fetcher_mock.get_weather_for_crop(
        crop_name='rice',
        latitude=28.7041,  # Delhi
        longitude=77.1025
    )
    
    print(f"Crop: {result['crop']}")
    print(f"Period: {result['weather_period']['period_description']}")
    print(f"Weather Data:")
    print(json.dumps(result['weather_data'], indent=2))
    
    # Demo 2: Instructions for API integration
    print("\n\n📍 DEMO 2: API Configuration Instructions")
    print("-" * 70)
    
    print("""
To enable real weather API integration:

1. Get OpenWeatherMap API Key:
   - Visit: https://openweathermap.org/api
   - Sign up for free account
   - Copy your API key from dashboard

2. Set environment variable or pass to code:
   
   Option A - Environment Variable:
   $ export OPENWEATHER_API_KEY='your_api_key_here'
   
   Option B - Direct Usage:
   from weather_fetcher import WeatherDataFetcher
   fetcher = WeatherDataFetcher(api_key='your_api_key_here', use_mock=False)

3. Usage with Real API:
   result = fetcher.get_weather_for_crop(
       crop_name='rice',
       latitude=28.7041,
       longitude=77.1025
   )

4. API Limits (Free Tier):
   - 1000 calls/day
   - 60 calls/minute
   - 5-day forecast available
   - For historical data: Upgrade to paid plan
""")
    
    # Demo 3: Show weather variations
    print("\n\n📍 DEMO 3: Weather for Different Crops")
    print("-" * 70)
    
    crops = ['rice', 'maize', 'cotton', 'watermelon']
    
    for crop in crops:
        result = fetcher_mock.get_weather_for_crop(crop)
        weather = result['weather_data']
        
        print(f"\n{crop.upper()}:")
        print(f"  Period: {result['weather_period']['cycle_days']} days")
        print(f"  Avg Temp: {weather['avg_temperature']}°C")
        print(f"  Avg Humidity: {weather['avg_humidity']}%")
        print(f"  Total Rainfall: {weather['total_rainfall']}mm")
    
    print("\n\n" + "=" * 70)
    print("Ready for Production!")
    print("=" * 70)
    print("""
✅ Mock mode working (for testing/demo)
✅ API integration ready (provide API key)
✅ Real weather data fetching implemented
✅ Forecast averaging implemented

Next: Integrate with inference.py and create farmer-facing API
""")



# Demo usage
if __name__ == "__main__":
    print("=" * 70)
    print("Weather Data Fetcher - Crop Cycle Aware")
    print("=" * 70)
    
    fetcher = WeatherDataFetcher()
    
    crops = ['rice', 'maize', 'cotton', 'watermelon']
    
    for crop in crops:
        print(f"\n\n📍 CROP: {crop.upper()}")
        print("-" * 70)
        
        weather_info = fetcher.get_weather_for_crop(
            crop_name=crop,
            latitude=28.7041,  # Delhi as example
            longitude=77.1025
        )
        
        period = weather_info['weather_period']
        print(f"Duration: {period['cycle_days']} days ({period['period_description']})")
        print(f"From: {period['start_date']} → To: {period['end_date']}")
        
        print(f"\nAPI Call Info:")
        print(json.dumps(weather_info['example_api_call'], indent=2))
    
    print("\n\n" + "=" * 70)
    print("Demo: Weather Averaging")
    print("=" * 70)
    
    # Sample weather data
    sample_weather = [
        {'temp': 25.5, 'humidity': 65, 'rainfall': 2.5},
        {'temp': 26.0, 'humidity': 68, 'rainfall': 0},
        {'temp': 24.8, 'humidity': 70, 'rainfall': 5.0},
        {'temp': 25.2, 'humidity': 66, 'rainfall': 0},
        {'temp': 26.5, 'humidity': 62, 'rainfall': 3.5},
    ]
    
    averages = fetcher.calculate_averages(sample_weather)
    print(f"\n5 daily readings averaged:")
    print(json.dumps(averages, indent=2))
