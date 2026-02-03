# Crop Cycle Duration - Data Sources & Implementation

## **Where to Get Crop Cycle Duration Data:**

### **1. Built-in Database (Already Created)** ✅
- File: `src/utils/crop_database.py`
- Contains: 22 crops with duration, season, water needs, temperature
- Data sourced from: FAO standards + Agricultural research

### **2. Official Sources** 📚

| Source | Website | Quality | Coverage |
|--------|---------|---------|----------|
| FAO | https://www.fao.org/faostat/ | ⭐⭐⭐⭐⭐ | Global |
| ICAR (India) | https://www.icar.org.in/ | ⭐⭐⭐⭐ | India focus |
| ICRISAT | https://www.icrisat.org/ | ⭐⭐⭐⭐ | Crop research |
| Agri Ministry | Country-specific | ⭐⭐⭐ | Official |

### **3. How We're Using It** 🔧

```python
from src.utils.crop_database import get_crop_cycle

# Automatically get cycle duration
rice_cycle = get_crop_cycle('rice')  # Returns 120 days
```

---

## **Architecture - Weather Data Flow:**

```
Farmer Input:
├── Soil Report (N, P, K, pH)
├── Location (GPS/Postal Code)
└── Crop Name (Rice/Maize/etc)
        ↓
Crop Database Lookup:
├── Get cycle duration (e.g., 120 days for rice)
├── Get optimal temperature range
├── Get water requirements
└── Get planting season
        ↓
Weather API Call:
├── OpenWeatherMap API
├── Historical weather for last 120 days
├── Daily temperature, humidity, rainfall
└── Coordinates: latitude, longitude
        ↓
Data Averaging:
├── Average temperature over 120 days
├── Average humidity over 120 days
├── Total rainfall over 120 days
└── Validation against optimal ranges
        ↓
Ensemble Prediction:
├── Scaled input: [N, P, K, avg_temp, avg_humidity, pH, avg_rainfall]
├── Soft voting from 4 models
└── Crop recommendation + confidence
        ↓
Output to Farmer:
├── Recommended crop
├── Suitability score
├── Top 5 alternatives
└── Seasonal advice
```

---

## **Current Implementation:**

### **File 1: `src/utils/crop_database.py`** ✅
```python
CROP_CYCLE_DURATION = {
    'rice': 120,        # 4 months
    'maize': 100,       # 3.3 months
    'cotton': 180,      # 6 months
    'watermelon': 80,   # 2.7 months
    # ... 18 more crops
}

# Usage:
get_crop_cycle('rice')  # → 120
get_crop_season('rice')  # → 'Monsoon (Jun-Sep)'
get_crop_info('rice')  # → Full information
```

### **File 2: `src/utils/weather_fetcher.py`** ✅
```python
fetcher = WeatherDataFetcher()

# Get weather period for a crop
period = fetcher.get_weather_period('rice')
# → {'crop': 'Rice', 'cycle_days': 120, 'start_date': '2025-10-06', ...}

# Average weather data
averages = fetcher.calculate_averages(weather_list)
# → {'avg_temperature': 25.6, 'avg_humidity': 66.2, 'total_rainfall': 11.0}
```

---

## **Next Steps - Weather API Integration:**

### **Phase 1: API Setup** (1-2 hours)
1. Get OpenWeatherMap API key (free tier available)
2. Implement historical weather fetcher
3. Handle rate limiting & errors

### **Phase 2: Integration** (2-3 hours)
1. Connect to inference.py
2. Add location input (GPS/postal code)
3. Auto-fetch weather data
4. Combine with soil nutrients

### **Phase 3: Farmer App** (Future)
1. Simple form: Soil report + Location
2. Auto-filled weather from API
3. One-click recommendation

---

## **Data Quality Tips:**

✅ **Good Data Sources:**
- Government meteorological departments
- Weather API providers (OpenWeatherMap, WeatherAPI)
- Historical weather databases
- Agricultural extension offices

⚠️ **Be Careful With:**
- Local manual weather records (may be inaccurate)
- Outdated crop cycle data
- Assuming same cycle for all regions

---

## **Cost Consideration:**

| Option | Cost | Limitations |
|--------|------|------------|
| OpenWeatherMap Free | $0/month | 5-day history, 60 calls/min |
| OpenWeatherMap Pro | $15-60/month | Full historical data |
| WeatherAPI | Free-$15/month | 7-day history free tier |
| Government API | $0 | Country-specific availability |

**Recommendation:** Start with **OpenWeatherMap Free** tier (sufficient for MVP)

---

## **Ready to Implement?**

✅ Crop database: **READY**
✅ Weather fetcher framework: **READY**
⏳ API integration: **NEXT**

Would you like me to implement the actual OpenWeatherMap API integration?
