# 🌩️ Next-Gen Weather App

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-v1.38.0-orange) ![AI-Powered](https://img.shields.io/badge/AI-Powered-Yes-green)

A futuristic, AI-powered **Streamlit web application** for **real-time weather forecasting**, data analytics, interactive visualizations, and advanced tools. Features a sleek **glassmorphism UI** with neon effects, voice commands, and multi-API integrations for comprehensive weather insights.

---

## 📖 Description

This app delivers **live weather data** from OpenWeatherMap, enhanced with **AI-driven insights, predictions, and advice** using Groq, Mistral, or Anthropic LLMs (optional).  

It includes:  
- Auto-refresh every 10 minutes  
- Location-based geocoding  
- Simulated pollen & UV data  
- Weather alerts  
- Interactive visualizations with Folium maps & Plotly charts  
- Celsius/Fahrenheit units, themes, and favorites  

Ideal for users seeking an **all-in-one, engaging weather dashboard** with mood-based AI commentary and actionable tips.

---

## ✨ Features

- 🌤️ **Current Dashboard:** Temperature, weather icon, key metrics (feels like, humidity, wind, pressure), AI insights, air quality, pollen index, UV, sun times, and alerts.  
- 📅 **5-Day Forecast:** Aggregated daily cards with icons, averages, and conditions.  
- 📊 **Data Analytics:** 24-hour trends, 5-day bar charts, conditions pie chart, radar visualizations.  
- 🗺️ **Interactive Map:** Folium map with location marker & 10km weather overlay.  
- ⚡ **Advanced Tools:** Real-feel calculator, pollen progress bars, voice assistant (speech-to-text & TTS), and favorites CRUD.  
- 📝 **Summary Review:** Core metrics overview, AI-generated summaries with pros/cons/advice.  
- 🔮 **Predictions:** Hourly line chart, daily DataFrame, AI 7-day forecast with confidence scores.  
- 🤖 **AI Integration:** Mood-based responses (happy/calm/sad), concise tips, engaging predictions.  
- 🎨 **UI/UX Enhancements:** Orbitron/Roboto fonts, gradient backgrounds, hover animations, glass cards, neon glows, responsive grids.  
- ⚙️ **Settings:** Location search/IP detection, unit toggle, theme selector (auto/light/dark).

---

## 🛠️ Tech Stack

- **Framework:** Streamlit (wide layout, tabs, session state)  
- **Data Sources:** OpenWeatherMap, IP-API, Nominatim  
- **AI Providers:** Groq (Llama 3.3), Mistral (Large), Anthropic (Claude 3.5)  
- **Visualizations:** Plotly (line, bar, pie, radar, subplots), Folium (maps)  
- **Voice:** SpeechRecognition (Google API), pyttsx3 (TTS)  
- **Other:** Pandas, Numpy, Geopy, dotenv, streamlit-autorefresh/lottie/folium  

---

## ⚡ Prerequisites

- Python 3.8+ (tested on 3.12)  
- Internet connection for APIs  
- Microphone & speakers for voice features (optional)  

---

## 🚀 Installation

```bash
# Clone the project
git clone <repo-url>
cd next-gen-weather-app

# Set up virtual environment
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
requirements.txt (example):

ini
Copy code
streamlit==1.38.0
requests==2.32.3
plotly==5.24.0
pandas==2.2.3
numpy==2.1.1
geopy==2.4.1
streamlit-lottie==0.0.5
streamlit-autorefresh==1.8.0
folium==0.20.0
streamlit-folium==0.19.0
python-dotenv==1.0.1
speechrecognition==3.10.0  # Optional
pyttsx3==2.91  # Optional
groq==0.9.0  # Optional
mistralai==0.1.0  # Optional
anthropic==0.34.2  # Optional
⚙️ Configuration
Create a .env file in the root:

ini
Copy code
OPENWEATHER_API_KEY=your_openweathermap_key
GROQ_API_KEY=your_groq_key        # Optional
MISTRAL_API_KEY=your_mistral_key  # Optional
ANTHROPIC_API_KEY=your_anthropic_key  # Optional
🖥️ Usage
bash
Copy code
streamlit run app.py
Opens at: http://localhost:8501

Sidebar: Search location or use IP button

Toggle units/themes

Explore tabs: Dashboard (overview), Predictions (forecasts)

Voice Mode: Click "Listen" and speak commands like "temperature", "weather", "forecast"

Favorites: Add, load, or remove locations.

Note: Auto-refresh every 10 min. Pollen/UV simulation & alerts enhance realism.

📸 Screenshots
Add images in /screenshots/:

Dashboard: Futuristic temp & grid metrics

Analytics: Multi-chart views

Map: Interactive overlay

Predictions: AI forecast example

🛠️ Troubleshooting
API Errors: Check .env keys; console logs help.

Voice Issues: Install optional libraries; allow mic access.

Geocoding Fails: Uses Nominatim fallback.

Charts/Maps Blank: Ensure Plotly & Folium installed; refresh.

🤝 Contributing
Fork the repo

Branch: git checkout -b feature/your-feature

Commit: git commit -m "Add your feature"

Push: git push origin feature/your-feature

Open a Pull Request

Ideas: Integrate more APIs (AccuWeather), add ML predictions, radar feeds.

📄 License
MIT License. See LICENSE for details.

❤️ Author
Built with ❤️ by Shivendra Pandey.
Questions? Open an issue or reach out! 🚀