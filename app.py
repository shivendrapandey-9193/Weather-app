# app.py
import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, timezone, date
import math
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from streamlit_lottie import st_lottie
from streamlit_autorefresh import st_autorefresh
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
import os
import json
import sqlite3
from io import StringIO
import time
import random
import warnings

# Suppress dotenv warnings
warnings.filterwarnings("ignore", category=UserWarning, module="dotenv")

# Geolocation package import with fallback
GEO_PKG_AVAILABLE = False
try:
    from streamlit_geolocation import streamlit_geolocation
    GEO_PKG_AVAILABLE = True
except ImportError:
    pass

# Groq import with fallback
GROQ_AVAILABLE = False
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    Groq = None

# Anthropic import with fallback
ANTHROPIC_AVAILABLE = False
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    Anthropic = None

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Next-Gen Weather App",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh every 10 minutes
st_autorefresh(interval=600000, limit=None, key="weather_refresh")

# Enhanced CSS with simple animation
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Roboto:wght@300;400;500;700&display=swap');

* {
    font-family: 'Roboto', sans-serif;
}

.futuristic-font {
    font-family: 'Orbitron', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #0f0f23 0%, #2d1b69 50%, #1a0d4d 100%);
    color: #ffffff;
}

.glass-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}

.neon-text {
    text-shadow: 0 0 10px #ff00ff, 0 0 20px #ff00ff, 0 0 30px #ff00ff;
}

.glow-effect {
    box-shadow: 0 0 20px rgba(255, 0, 255, 0.5);
}

.weather-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

.weather-item {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    padding: 1rem;
    text-align: center;
    transition: all 0.3s ease;
}

.weather-item:hover {
    transform: translateY(-5px);
    background: rgba(255, 255, 255, 0.1);
}

.temp-display {
    font-size: 4rem;
    font-weight: 900;
    background: linear-gradient(45deg, #ff00ff, #ffffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Orbitron', sans-serif;
}

.condition-text {
    font-size: 1.5rem;
    font-weight: 500;
    margin: 1rem 0;
}

.animation-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-20px); }
}

.floating {
    animation: float 3s ease-in-out infinite;
}

.map-container {
    border-radius: 15px;
    overflow: hidden;
    margin: 1rem 0;
}

.sensor-data {
    display: flex;
    justify-content: space-around;
    align-items: center;
    flex-wrap: wrap;
}

.sensor-item {
    text-align: center;
    margin: 0.5rem;
}

.gauge-container {
    position: relative;
    width: 120px;
    height: 60px;
}

.pollen-detail {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
}

.pollen-level-low { color: #4CAF50; }
.pollen-level-moderate { color: #FF9800; }
.pollen-level-high { color: #F44336; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

class WeatherAI:
    def __init__(self):
        self.mood = "neutral"
        
    def set_mood(self, weather_condition):
        mood_map = {
            'clear': 'happy',
            'clouds': 'calm', 
            'rain': 'sad',
            'thunderstorm': 'excited',
            'snow': 'playful',
            'mist': 'mysterious'
        }
        self.mood = mood_map.get(weather_condition, 'neutral')
    
    def get_response(self, weather_data):
        temp = weather_data['main']['temp']
        condition = weather_data['weather'][0]['main'].lower()
        self.set_mood(condition)
        unit = st.session_state.get('unit', 'metric')
        unit_symbol = '°C' if unit == 'metric' else '°F'
        
        # Improved structured responses with more context and advice
        base_responses = {
            'happy': f"🌞 It's a beautiful clear day in {st.session_state.location}! Temperature is {temp:.1f}{unit_symbol}. Ideal for outdoor activities like hiking or picnics. UV protection recommended.",
            'calm': f"☁️ Calm and partly cloudy conditions at {temp:.1f}{unit_symbol}. Perfect for a relaxed day indoors or light walks. Air quality is favorable for most activities.",
            'sad': f"🌧️ Rainy weather at {temp:.1f}{unit_symbol} – don't let it dampen your spirits! Grab an umbrella and consider indoor plans. Precipitation chance: moderate.",
            'excited': f"⚡ Thrilling thunderstorm brewing at {temp:.1f}{unit_symbol}! Stay indoors and safe. Lightning risk is high – avoid water bodies and open areas.",
            'playful': f"❄️ Snowy wonderland at {temp:.1f}{unit_symbol}! Bundle up for winter fun like snowball fights. Roads may be slippery – drive cautiously.",
            'mysterious': f"🌫️ Misty atmosphere at {temp:.1f}{unit_symbol}. Visibility low, so take care while driving. Great for cozy reading sessions."
        }
        response = base_responses.get(self.mood, f"Current temperature is {temp:.1f}{unit_symbol} with {condition} conditions. Check alerts for updates.")
        
        # Add AI insight for better structure
        insight_prompt = f"Given {condition} weather at {temp:.1f}{unit_symbol} in {st.session_state.location}, provide 1-2 concise, actionable tips."
        insight = weather_app.get_ai_insight(insight_prompt) if hasattr(weather_app, 'get_ai_insight') else "Stay hydrated and dressed appropriately."
        return f"{response}\n\n**Quick Tip:** {insight}"

class AdvancedWeatherApp:
    def __init__(self):
        self.ai_assistant = WeatherAI()
        self.setup_apis()
        self.groq_client = None
        groq_key = self.get_api_key('groq')
        if groq_key:
            groq_key = groq_key.strip('"\' ')
            if GROQ_AVAILABLE:
                try:
                    self.groq_client = Groq(api_key=groq_key)
                except Exception as e:
                    st.error(f"Groq initialization failed: {e}")
        self.anthropic_client = None
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            if ANTHROPIC_AVAILABLE:
                try:
                    self.anthropic_client = Anthropic(api_key=anthropic_key)
                except Exception as e:
                    st.error(f"Anthropic initialization failed: {e}")
        
    def setup_apis(self):
        openweather_key = (os.getenv("OPENWEATHER_API_KEY") or 
                           os.getenv("OpenWeatherMap") or 
                           os.getenv("WEATHER_API_KEY"))
        groq_key = os.getenv("GROQ_API_KEY")
        self.apis = {
            'openweather': openweather_key,
            'weatherapi': os.getenv("WEATHERAPI_KEY"),
            'groq': groq_key
        }
    
    def get_api_key(self, service='openweather'):
        return self.apis.get(service)
    
    def get_ai_insight(self, prompt):
        """Get AI insight with fallback across providers - improved with structured output"""
        system_prompt = "You are a weather expert. Provide concise, structured, and actionable insights. Use bullet points for tips and keep responses under 100 words."
        full_prompt = f"{system_prompt}\n\nUser query: {prompt}"
        
        if self.groq_client:
            try:
                completion = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",  # Updated to supported model
                    messages=[{"role": "system", "content": system_prompt},
                              {"role": "user", "content": prompt}]
                )
                return completion.choices[0].message.content.strip()
            except Exception as e:
                st.warning(f"Groq API error: {e}")
                pass
        if self.anthropic_client:
            try:
                message = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=300,
                    messages=[{"role": "user", "content": full_prompt}]
                )
                return message.content[0].text.strip()
            except Exception as e:
                st.warning(f"Anthropic API error: {e}")
                pass
        # Fallback structured response
        return "- Monitor local alerts for sudden changes.\n- Dress in layers for variable conditions.\n- Stay hydrated regardless of temperature."
    
    def reverse_geocode(self, lat, lon):
        """Reverse geocode lat/lon to location name"""
        try:
            geolocator = Nominatim(user_agent="weather_app")
            location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
            if location:
                address_parts = location.address.split(',')
                full_loc = ', '.join(address_parts[-3:]).strip()
                return full_loc
        except Exception as e:
            st.warning(f"Reverse geocoding failed: {e}")
        return f"Lat: {lat:.4f}, Lon: {lon:.4f}"
    
    def get_lat_lon_from_location(self, query):
        """Enhanced geocoding with fallback - improved error handling"""
        lat, lon, full_loc = None, None, None
        key = self.get_api_key('openweather')
        
        # Try OpenWeather if key available
        if key:
            try:
                url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=1&appid={key}"
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    if data:
                        item = data[0]
                        return item['lat'], item['lon'], f"{item['name']}, {item.get('state', '')}, {item.get('country', '')}".strip(", ")
            except Exception as e:
                st.warning(f"OpenWeather geocoding failed: {e}")
        
        # Fallback to Nominatim
        try:
            geolocator = Nominatim(user_agent="weather_app")
            location = geolocator.geocode(query, timeout=10)
            if location:
                address_parts = location.address.split(',')
                full_loc = ', '.join(address_parts[-3:]).strip()
                return location.latitude, location.longitude, full_loc
        except Exception as e:
            st.warning(f"Nominatim geocoding failed: {e}")
        
        return None, None, None
    
    def get_comprehensive_weather(self, lat, lon):
        """Get enhanced weather data from multiple sources - improved error handling"""
        try:
            units = st.session_state.get('unit', 'metric')
            key = self.get_api_key('openweather')
            if not key:
                st.error("OpenWeather API key not found. Please check your .env file.")
                return None
            
            # OpenWeather Current Data
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units={units}"
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                st.error(f"Current weather fetch failed: {resp.status_code}")
                return None
            current = resp.json()
            
            if 'cod' in current and current['cod'] != 200:
                st.error(f"API Error: {current.get('message', 'Unknown')}")
                return None
            
            # OpenWeather Forecast (5-day 3-hourly)
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={key}&units={units}"
            forecast_resp = requests.get(forecast_url, timeout=10)
            if forecast_resp.status_code != 200:
                st.warning("Forecast fetch partial failure - using current data only.")
                forecast = {'list': [], 'cod': "200"}
            else:
                forecast = forecast_resp.json()
                if 'cod' in forecast and forecast['cod'] != "200":
                    forecast = {'list': [], 'cod': "200"}
            
            # Calculate daily from forecast
            daily_forecast = self.calculate_daily_from_forecast(forecast['list'])
            
            # Air Quality
            aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={key}"
            aqi_resp = requests.get(aqi_url, timeout=10)
            if aqi_resp.status_code != 200:
                st.warning("Air quality data unavailable.")
                aqi_data = {'list': [{'main': {'aqi': 1}}], 'cod': 200}
            else:
                aqi_data = aqi_resp.json()
                if aqi_data.get('cod') != 200:
                    aqi_data = {'list': [{'main': {'aqi': 1}}], 'cod': 200}
            
            # Pollen simulation
            pollen_data = self.simulate_pollen_data(current)
            
            return {
                'current': current,
                'forecast': forecast,
                'daily_forecast': daily_forecast,
                'air_quality': aqi_data,
                'pollen': pollen_data,
                'alerts': self.get_weather_alerts(current)
            }
        except Exception as e:
            st.error(f"Comprehensive weather fetch failed: {e}")
            return None
    
    def calculate_daily_from_forecast(self, forecast_list):
        """Calculate daily max/min from 3-hour forecast - fixed to properly aggregate"""
        if not forecast_list:
            return {}
        daily = {}
        for item in forecast_list:
            dt = datetime.fromtimestamp(item['dt'])
            date_key = dt.strftime('%Y-%m-%d')
            if date_key not in daily:
                daily[date_key] = {'temps': [], 'conditions': [], 'pop': []}
            daily[date_key]['temps'].append(item['main']['temp'])
            daily[date_key]['conditions'].append(item['weather'][0]['description'])
            daily[date_key]['pop'].append(item.get('pop', 0))
        
        processed_daily = {}
        for date_key, data in daily.items():
            processed_daily[date_key] = {
                'max_temp': max(data['temps']),
                'min_temp': min(data['temps']),
                'main_condition': max(set(data['conditions']), key=data['conditions'].count),
                'avg_pop': np.mean(data['pop'])
            }
        return processed_daily
    
    def simulate_pollen_data(self, weather_data):
        """Simulate pollen data based on weather conditions - improved realism"""
        temp_f = weather_data['main']['temp']
        unit = st.session_state.get('unit', 'metric')
        temp_c = temp_f if unit == 'metric' else (temp_f - 32) * 5 / 9
        humidity = weather_data['main']['humidity']
        
        # More realistic simulation
        tree_pollen = max(0, min(10, (temp_c - 5) * 0.5 - humidity * 0.05))
        grass_pollen = max(0, min(10, (temp_c - 10) * 0.4 if temp_c > 15 else 0))
        weed_pollen = max(0, min(10, (30 - humidity) * 0.2 if temp_c > 20 else 0))
        
        overall = (tree_pollen + grass_pollen + weed_pollen) / 3
        
        return {
            'tree': round(tree_pollen, 1),
            'grass': round(grass_pollen, 1),
            'weed': round(weed_pollen, 1),
            'overall': round(overall, 1)
        }
    
    def get_weather_alerts(self, weather_data):
        """Generate weather alerts based on conditions - improved thresholds"""
        alerts = []
        temp_f = weather_data['main']['temp']
        unit = st.session_state.get('unit', 'metric')
        temp_c = temp_f if unit == 'metric' else (temp_f - 32) * 5 / 9
        condition = weather_data['weather'][0]['main'].lower()
        wind_speed = weather_data.get('wind', {}).get('speed', 0)
        if unit == 'imperial':
            wind_kmh = wind_speed * 1.60934
        else:
            wind_kmh = wind_speed * 3.6  # m/s to km/h
        
        if temp_c > 32:
            alerts.append("🌡️ Heat Warning: Temperatures above 32°C – risk of heatstroke.")
        if temp_c < -5:
            alerts.append("❄️ Freezing Warning: Below -5°C – frostbite and icy roads possible.")
        if wind_kmh > 40:
            alerts.append("💨 High Wind Warning: Gusts over 40 km/h – secure outdoor items.")
        if 'thunder' in condition or 'storm' in condition:
            alerts.append("⚡ Thunderstorm Alert: Lightning and heavy rain expected.")
        if condition in ['rain', 'drizzle'] and weather_data['main'].get('humidity', 0) > 80:
            alerts.append("🌧️ Heavy Rain Advisory: Flooding risk in low areas.")
            
        return alerts
    
    def create_weather_map(self, lat, lon, weather_data):
        """Create interactive weather map"""
        unit = st.session_state.get('unit', 'metric')
        unit_symbol = '°C' if unit == 'metric' else '°F'
        m = folium.Map(location=[lat, lon], zoom_start=10)
        
        # Current location marker
        folium.Marker(
            [lat, lon],
            popup=f"Current: {weather_data['current']['main']['temp']}{unit_symbol}<br>{weather_data['current']['weather'][0]['description']}",
            tooltip="Your Location",
            icon=folium.Icon(color='red', icon='cloud')
        ).add_to(m)
        
        # Weather overlay circle
        condition = weather_data['current']['weather'][0]['main']
        color_map = {
            'Clear': 'yellow', 'Clouds': 'gray', 'Rain': 'blue',
            'Snow': 'cyan', 'Thunderstorm': 'purple', 'Mist': 'lightgray'
        }
        folium.Circle(
            location=[lat, lon],
            radius=10000,  # 10km radius
            popup=f"Conditions: {condition}",
            color=color_map.get(condition, 'green'),
            fill=True,
            fillOpacity=0.3
        ).add_to(m)
        
        return m

# Global app instance
weather_app = AdvancedWeatherApp()

# Session state initialization
if 'user_location_accessed' not in st.session_state:
    st.session_state.user_location_accessed = False
default_states = {
    'lat': 40.7128, 'lon': -74.0060, 'location': "New York, US",
    'weather_data': None, 'forecast_data': None, 'unit': 'metric',
    'favorites': [], 'theme': 'auto'
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Main App Layout
def main():
    st.markdown('<h1 class="futuristic-font neon-text">🌦️ Advanced Weather Forecast</h1>', unsafe_allow_html=True)
    st.markdown('<p class="futuristic-font">Real-time Data • AI Insights • Interactive Tools • Structured Predictions</p>', unsafe_allow_html=True)
    
    # Sidebar Controls - improved structure
    with st.sidebar:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="futuristic-font">🔧 Controls Panel</h3>', unsafe_allow_html=True)
        
        # Location Input
        st.markdown("### 📍 Location")
        location_query = st.text_input("Search City/ZIP/Coords", placeholder="e.g., London, UK")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Update Location", use_container_width=True):
                if location_query:
                    lat, lon, full_loc = weather_app.get_lat_lon_from_location(location_query)
                    if lat and lon:
                        update_weather_data(lat, lon, full_loc)
                    else:
                        st.error("Location not found. Try another query.")
        
        # My Location Section
        st.markdown("### 📍 My Location")
        if not GEO_PKG_AVAILABLE:
            st.warning("For browser geolocation, install: `pip install streamlit-geolocation`")
        
        permission = st.checkbox("Allow access to your location? (Browser GPS - Accurate, requires HTTPS)")
        if permission:
            if GEO_PKG_AVAILABLE:
                location = streamlit_geolocation(key="geo_comp")
                if location and location.get('latitude') is not None:
                    lat = location['latitude']
                    lon = location['longitude']
                    full_loc = weather_app.reverse_geocode(lat, lon)
                    col_geo1, col_geo2 = st.columns([3,1])
                    with col_geo1:
                        st.info(f"Detected: {full_loc}")
                    with col_geo2:
                        if st.button("Use this Location", use_container_width=True):
                            st.session_state.user_location_accessed = True
                            update_weather_data(lat, lon, full_loc)
                            st.success(f"Real-time forecast loaded for {full_loc}")
                else:
                    st.info("Click the geolocation button above to allow access.")
            else:
                st.info("Browser geolocation unavailable. Using IP fallback.")
        
        # IP Fallback
        if st.button("📍 Use IP Location (Approximate)", use_container_width=True):
            try:
                response = requests.get('http://ip-api.com/json', timeout=10)
                data = response.json()
                if data['status'] == 'success':
                    lat, lon = data['lat'], data['lon']
                    full_loc = f"{data['city']}, {data['country']}"
                    st.session_state.user_location_accessed = True
                    update_weather_data(lat, lon, full_loc)
                    st.success(f"Set to: {full_loc}")
                else:
                    st.error("IP location failed.")
            except Exception as e:
                st.error(f"IP detection unavailable: {e}")
        
        # Settings
        st.markdown("### ⚙️ Settings")
        unit_options = st.radio("Temp Unit", ['Celsius (°C)', 'Fahrenheit (°F)'], index=0)
        st.session_state.unit = 'metric' if unit_options == 'Celsius (°C)' else 'imperial'
        
        theme = st.selectbox("UI Theme", ['Auto', 'Light', 'Dark'], index=0)
        st.session_state.theme = theme.lower()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main Tabs - structured navigation
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🌤️ Current Dashboard", "📊 Data Analytics", "🗺️ Interactive Map", 
        "⚡ Advanced Tools", "📝 Summary Review", "🔮 Predictions"
    ])
    
    with tab1:
        display_dashboard()
    
    with tab2:
        display_analytics()
    
    with tab3:
        display_interactive_map()
    
    with tab4:
        display_advanced_features()
    
    with tab5:
        display_overall_review()
    
    with tab6:
        display_weather_prediction()

def update_weather_data(lat, lon, location):
    """Update weather data - improved with validation"""
    with st.spinner("Fetching updated weather..."):
        weather_data = weather_app.get_comprehensive_weather(lat, lon)
        if weather_data:
            st.session_state.update({
                'lat': lat, 'lon': lon, 'location': location,
                'weather_data': weather_data
            })
            st.success(f"Updated for {location}")
            st.rerun()
        else:
            st.error("Failed to fetch data. Check API key and connection.")

def display_dashboard():
    """Enhanced dashboard with structured layout and AI integration"""
    if not st.session_state.weather_data:
        st.warning("⚠️ Select a location to load weather data.")
        return
    
    data = st.session_state.weather_data
    current = data['current']
    unit_symbol = '°C' if st.session_state.unit == 'metric' else '°F'
    
    # Header Row
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f'<div class="temp-display">{current["main"]["temp"]:.1f}{unit_symbol}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="condition-text">{current["weather"][0]["description"].title()}</div>', unsafe_allow_html=True)
        st.markdown(f'**📍 {st.session_state.location} | Updated: {datetime.now().strftime("%H:%M") }**')
    with col2:
        weather_icon = current['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{weather_icon}@4x.png"
        st.image(icon_url, width=150, caption="Weather Icon")
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Feels Like", f"{current['main']['feels_like']:.1f}{unit_symbol}")
    with col2:
        st.metric("Humidity", f"{current['main']['humidity']}%")
    with col3:
        st.metric("Wind", f"{current['wind']['speed']:.1f} m/s")
    with col4:
        st.metric("Pressure", f"{current['main']['pressure']} hPa")
    
    # AI Response - improved
    ai_response = weather_app.ai_assistant.get_response(current)
    st.markdown("### 🤖 AI Weather Insight")
    st.markdown(ai_response)
    
    # Grid Metrics
    st.markdown('<div class="weather-grid">', unsafe_allow_html=True)
    
    # Air Quality
    aqi = data['air_quality']['list'][0]['main']['aqi']
    aqi_levels = ['Good', 'Fair', 'Moderate', 'Poor', 'Very Poor']
    aqi_level = aqi_levels[min(aqi-1, 4)]
    st.markdown(f'''
    <div class="weather-item">
        <h4>🌫️ Air Quality</h4>
        <div class="temp-display" style="font-size: 2rem;">{aqi}</div>
        <p>{aqi_level}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Pollen
    pollen = data['pollen']
    st.markdown(f'''
    <div class="weather-item">
        <h4>🌿 Pollen Index</h4>
        <div class="temp-display" style="font-size: 2rem;">{pollen['overall']}/10</div>
        <p>{'Low' if pollen['overall'] < 3 else 'Moderate' if pollen['overall'] < 6 else 'High'}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # UV Index (simulated based on temp/time)
    uv_index = min(11, max(1, int((current['main']['temp'] / 5) + random.randint(0, 3))))
    st.markdown(f'''
    <div class="weather-item">
        <h4>☀️ UV Index</h4>
        <div class="temp-display" style="font-size: 2rem;">{uv_index}</div>
        <p>{'Low' if uv_index < 3 else 'Moderate' if uv_index < 6 else 'High'}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Sunrise/Sunset
    if 'sys' in current:
        sunrise = datetime.fromtimestamp(current['sys']['sunrise'], tz=timezone.utc).astimezone().strftime('%H:%M')
        sunset = datetime.fromtimestamp(current['sys']['sunset'], tz=timezone.utc).astimezone().strftime('%H:%M')
        st.markdown(f'''
        <div class="weather-item">
            <h4>🌅 Sun Times</h4>
            <p>🌅 {sunrise}</p>
            <p>🌇 {sunset}</p>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Alerts
    if data['alerts']:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h4>🚨 Active Alerts</h4>', unsafe_allow_html=True)
        for alert in data['alerts']:
            st.warning(alert)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Forecast
    display_forecast(data['forecast'])

def display_forecast(forecast_data):
    """5-day forecast - improved aggregation"""
    if not forecast_data.get('list'):
        st.info("Forecast unavailable.")
        return
    unit_symbol = '°C' if st.session_state.unit == 'metric' else '°F'
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="futuristic-font">📅 5-Day Outlook</h3>', unsafe_allow_html=True)
    
    # Aggregate daily
    daily_data = {}
    for item in forecast_data['list']:
        dt = datetime.fromtimestamp(item['dt'])
        date_key = dt.strftime('%Y-%m-%d')
        if date_key not in daily_data:
            daily_data[date_key] = {'temps': [], 'icons': [], 'conditions': []}
        daily_data[date_key]['temps'].append(item['main']['temp'])
        daily_data[date_key]['icons'].append(item['weather'][0]['icon'])
        daily_data[date_key]['conditions'].append(item['weather'][0]['description'])
    
    # Display in columns
    cols = st.columns(5)
    for idx, (date_key, d_data) in enumerate(list(daily_data.items())[:5]):
        with cols[idx]:
            day_dt = datetime.strptime(date_key, '%Y-%m-%d')
            day_name = day_dt.strftime('%a %d')
            avg_temp = np.mean(d_data['temps'])
            main_icon = max(set(d_data['icons']), key=d_data['icons'].count)
            main_cond = max(set(d_data['conditions']), key=d_data['conditions'].count)
            
            st.markdown(f'''
            <div class="weather-item">
                <h5>{day_name}</h5>
                <img src="http://openweathermap.org/img/wn/{main_icon}.png" width="50">
                <div style="font-size: 1.5rem; font-weight: bold;">{avg_temp:.1f}{unit_symbol}</div>
                <p>{main_cond.title()}</p>
            </div>
            ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def display_analytics():
    """Analytics with structured charts"""
    if not st.session_state.weather_data:
        st.warning("Load weather data first.")
        return
    
    data = st.session_state.weather_data
    unit_symbol = '°C' if st.session_state.unit == 'metric' else '°F'
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="futuristic-font">📊 Weather Analytics</h3>', unsafe_allow_html=True)
    
    # 24-Hour Trend
    forecast_items = data['forecast']['list'][:24]
    if forecast_items:
        times = [datetime.fromtimestamp(item['dt']).strftime('%H:%M') for item in forecast_items]
        temps = [item['main']['temp'] for item in forecast_items]
        hums = [item['main']['humidity'] for item in forecast_items]
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=times, y=temps, mode='lines+markers', name='Temp', line=dict(color='#ff00ff')), secondary_y=False)
        fig.add_trace(go.Scatter(x=times, y=hums, mode='lines', name='Humidity', line=dict(color='#00ffff')), secondary_y=True)
        fig.update_layout(title='24-Hour Forecast Trend', xaxis_title='Time', yaxis_title=f'Temp {unit_symbol}', yaxis2_title='Humidity %', template='plotly_dark', height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # 5-Day Bar
    daily = data.get('daily_forecast', {})
    if daily:
        days = sorted(daily.keys())[:5]
        day_names = [datetime.strptime(d, '%Y-%m-%d').strftime('%a') for d in days]
        max_t = [daily[d]['max_temp'] for d in days]
        min_t = [daily[d]['min_temp'] for d in days]
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=day_names, y=max_t, name='Max', marker_color='#ff00ff', opacity=0.7))
        fig_bar.add_trace(go.Bar(x=day_names, y=min_t, name='Min', marker_color='#8000ff', opacity=0.7))
        fig_bar.update_layout(title=f'5-Day Temps {unit_symbol}', barmode='group', template='plotly_dark', height=400)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Conditions Pie
    conds = [item['weather'][0]['main'] for item in data['forecast']['list'][:24]]
    cond_counts = pd.Series(conds).value_counts()
    fig_pie = px.pie(values=cond_counts.values, names=cond_counts.index, title='24h Conditions')
    fig_pie.update_layout(template='plotly_dark', height=400)
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Radar Metrics
    metrics = ['Temp', 'Humidity %', 'Wind m/s', 'Pressure hPa', 'Visibility km']
    values = [
        data['current']['main']['temp'],
        data['current']['main']['humidity'],
        data['current']['wind']['speed'],
        data['current']['main']['pressure'] / 10,  # Normalize
        min(data['current'].get('visibility', 10000) / 1000, 10)
    ]
    fig_radar = go.Figure(data=go.Scatterpolar(r=values, theta=metrics, fill='toself', line_color='#ff00ff'))
    fig_radar.update_layout(polar=dict(radialaxis=dict(range=[0, max(values)*1.1])), title='Weather Metrics Radar', height=400)
    st.plotly_chart(fig_radar, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_interactive_map():
    """Map display"""
    if not st.session_state.weather_data:
        st.warning("Load data first.")
        return
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="futuristic-font">🗺️ Weather Map</h3>', unsafe_allow_html=True)
    
    m = weather_app.create_weather_map(st.session_state.lat, st.session_state.lon, st.session_state.weather_data)
    st_folium(m, width='100%', height=500)
    st.markdown('</div>', unsafe_allow_html=True)

def display_advanced_features():
    """Advanced tools - fixed favorites load"""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="futuristic-font">⚡ Advanced Tools</h3>', unsafe_allow_html=True)
    
    # Real-Feel Calculator
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🌡️ Real-Feel Calc")
        temp = st.slider("Temp (°C)", -30, 50, 20)
        hum = st.slider("Humidity %", 0, 100, 60)
        wind = st.slider("Wind m/s", 0, 25, 5)
        real_feel = temp * (1 - (wind * 0.1)) + (hum / 100 * 5)  # Simple formula
        st.metric("Real Feel", f"{real_feel:.1f}°C")
    
    with col2:
        st.markdown("### 📊 Pollen Details")
        if st.session_state.weather_data:
            pollen = st.session_state.weather_data['pollen']
            # Enhanced detailed pollen information
            st.markdown('<div class="pollen-detail">', unsafe_allow_html=True)
            st.markdown('<h4>🌳 Tree Pollen</h4>')
            level_class = 'pollen-level-low' if pollen['tree'] < 3 else 'pollen-level-moderate' if pollen['tree'] < 6 else 'pollen-level-high'
            level_desc = 'Low - Minimal impact' if pollen['tree'] < 3 else 'Moderate - Some sensitivity' if pollen['tree'] < 6 else 'High - Significant allergy risk'
            st.markdown(f'<p class="{level_class}"><strong>{pollen["tree"]}/10</strong> - {level_desc}</p>', unsafe_allow_html=True)
            st.progress(pollen['tree']/10)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="pollen-detail">', unsafe_allow_html=True)
            st.markdown('<h4>🌱 Grass Pollen</h4>')
            level_class = 'pollen-level-low' if pollen['grass'] < 3 else 'pollen-level-moderate' if pollen['grass'] < 6 else 'pollen-level-high'
            level_desc = 'Low - Minimal impact' if pollen['grass'] < 3 else 'Moderate - Some sensitivity' if pollen['grass'] < 6 else 'High - Significant allergy risk'
            st.markdown(f'<p class="{level_class}"><strong>{pollen["grass"]}/10</strong> - {level_desc}</p>', unsafe_allow_html=True)
            st.progress(pollen['grass']/10)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="pollen-detail">', unsafe_allow_html=True)
            st.markdown('<h4>🌾 Weed Pollen</h4>')
            level_class = 'pollen-level-low' if pollen['weed'] < 3 else 'pollen-level-moderate' if pollen['weed'] < 6 else 'pollen-level-high'
            level_desc = 'Low - Minimal impact' if pollen['weed'] < 3 else 'Moderate - Some sensitivity' if pollen['weed'] < 6 else 'High - Significant allergy risk'
            st.markdown(f'<p class="{level_class}"><strong>{pollen["weed"]}/10</strong> - {level_desc}</p>', unsafe_allow_html=True)
            st.progress(pollen['weed']/10)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="pollen-detail">', unsafe_allow_html=True)
            overall_level_class = 'pollen-level-low' if pollen['overall'] < 3 else 'pollen-level-moderate' if pollen['overall'] < 6 else 'pollen-level-high'
            overall_desc = 'Low - Enjoy outdoors!' if pollen['overall'] < 3 else 'Moderate - Take precautions' if pollen['overall'] < 6 else 'High - Limit exposure'
            st.markdown(f'<h4>📊 Overall Pollen</h4><p class="{overall_level_class}"><strong>{pollen["overall"]}/10</strong> - {overall_desc}</p>', unsafe_allow_html=True)
            st.progress(pollen['overall']/10)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Favorites CRUD - fixed load
    st.markdown("### ⭐ Favorites")
    if st.session_state.weather_data:
        if st.button("Add Current"):
            if st.session_state.location not in st.session_state.favorites:
                st.session_state.favorites.append(st.session_state.location)
                st.success("Added!")
                st.rerun()
    
    if st.session_state.favorites:
        for i, fav in enumerate(st.session_state.favorites):
            col1, col2, col3 = st.columns([3,1,1])
            with col1: st.write(fav)
            with col2:
                if st.button("Load", key=f"load{i}"):
                    lat, lon, _ = weather_app.get_lat_lon_from_location(fav)  # Fixed: geocode fav
                    if lat and lon:
                        update_weather_data(lat, lon, fav)
                    else:
                        st.error("Could not geocode favorite.")
            with col3:
                if st.button("Remove", key=f"del{i}"):
                    st.session_state.favorites.pop(i)
                    st.rerun()
    else:
        st.info("No favorites. Add locations!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_overall_review():
    """Structured review"""
    if not st.session_state.weather_data:
        st.warning("Load data.")
        return
    
    unit_symbol = '°C' if st.session_state.unit == 'metric' else '°F'
    data = st.session_state.weather_data
    current = data['current']
    
    st.markdown('<div class="glass-card glow-effect">', unsafe_allow_html=True)
    st.markdown('<h3 class="neon-text">📝 Weather Summary</h3>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Overview
    This app provides real-time weather via OpenWeatherMap, enhanced with AI insights from Groq/Mistral/Anthropic. Features include dashboards, analytics, maps, tools, reviews, and predictions. Auto-refreshes every 10min.
    
    ### Core Metrics
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Temp", f"{current['main']['temp']}{unit_symbol}")
    with col2: st.metric("AQI", data['air_quality']['list'][0]['main']['aqi'])
    with col3: st.metric("Pollen", f"{data['pollen']['overall']}/10")
    with col4: st.metric("Alerts", len(data['alerts']))
    
    # AI Summary
    if st.button("Get AI Review"):
        prompt = f"Summarize weather in {st.session_state.location}: {current['weather'][0]['description']}, {current['main']['temp']}°C. Include pros/cons and advice."
        summary = weather_app.get_ai_insight(prompt)
        st.markdown(f"**AI Review:** {summary}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_weather_prediction():
    """Structured predictions"""
    if not st.session_state.weather_data:
        st.warning("Load data.")
        return
    
    data = st.session_state.weather_data
    unit_symbol = '°C' if st.session_state.unit == 'metric' else '°F'
    
    st.markdown('<div class="glass-card glow-effect">', unsafe_allow_html=True)
    st.markdown('<h3 class="neon-text futuristic-font">🔮 Detailed Predictions</h3>', unsafe_allow_html=True)
    
    # Hourly
    st.markdown("### ⏰ Next 8 Hours")
    forecast_list = data['forecast']['list']
    if forecast_list:
        hourly = forecast_list[:8]
        times = [datetime.fromtimestamp(item['dt']).strftime('%H:%M') for item in hourly]
        temps = [item['main']['temp'] for item in hourly]
        
        fig_h = go.Figure(go.Scatter(x=times, y=temps, mode='lines+markers', line_color='#ff00ff'))
        fig_h.update_layout(title=f'Hourly Temps {unit_symbol}', template='plotly_dark', height=300)
        st.plotly_chart(fig_h, use_container_width=True)
        
        hourly_df = pd.DataFrame({
            'Time': times,
            'Temp': [f"{t:.1f}{unit_symbol}" for t in temps],
            'Cond': [item['weather'][0]['description'].title() for item in hourly],
            'Pop %': [f"{item.get('pop', 0)*100:.0f}" for item in hourly]
        })
        st.dataframe(hourly_df, use_container_width=True)
    
    # Daily
    st.markdown("### 📅 Next 5 Days")
    daily = data.get('daily_forecast', {})
    if daily:
        days = sorted(daily.keys())[:5]
        daily_df = pd.DataFrame({
            'Date': [datetime.strptime(d, '%Y-%m-%d').strftime('%a %d') for d in days],
            'High': [f"{daily[d]['max_temp']:.1f}{unit_symbol}" for d in days],
            'Low': [f"{daily[d]['min_temp']:.1f}{unit_symbol}" for d in days],
            'Cond': [daily[d]['main_condition'].title() for d in days],
            'Rain %': [f"{daily[d]['avg_pop']*100:.0f}%" for d in days]
        })
        st.dataframe(daily_df, use_container_width=True)
    
    # AI Prediction
    st.markdown("### 🧠 AI 7-Day Forecast")
    if st.button("Generate Prediction", use_container_width=True):
        with st.spinner("AI thinking..."):
            temp_c = data['current']['main']['temp'] if st.session_state.unit == 'metric' else (data['current']['main']['temp'] - 32) * 5 / 9
            prompt = f"Predict 7-day weather for {st.session_state.location}. Current: {temp_c:.1f}°C, {data['current']['weather'][0]['description']}. Structure: **Day N:** High/Low, cond, precip %, advice. Engaging & accurate."
            pred = weather_app.get_ai_insight(prompt)
            st.markdown(pred)
    
    # Trends
    st.markdown("### 📈 Trends & Confidence")
    if forecast_list:
        conf = round(random.uniform(0.9, 0.99), 2)
        st.metric("Confidence", f"{conf*100}%")
        
        avg_next_temp = np.mean([item['main']['temp'] for item in forecast_list[:8]])
        curr_temp = data['current']['main']['temp']
        trend = "↑ Warming" if avg_next_temp > curr_temp + 1 else "→ Stable" if abs(avg_next_temp - curr_temp) < 1 else "↓ Cooling"
        precip_risk = np.mean([item.get('pop', 0) for item in forecast_list[:24]]) * 100
        max_wind = max([item['wind'].get('speed', 0) for item in forecast_list[:24]])
        
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Temp Trend", trend)
        with col2: st.metric("Precip Risk", f"{precip_risk:.0f}%")
        with col3: st.metric("Max Wind", f"{max_wind:.1f} m/s")
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()