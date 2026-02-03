# 🌾 CropSense: Data-Driven Crop Planning Framework

An intelligent AI-powered crop recommendation system that uses machine learning ensemble methods combined with real-time weather data to provide personalized crop recommendations for farmers.

## 📋 Overview

CropSense analyzes soil nutrients, geographic location, and current weather conditions to recommend the most suitable crops for a farmer's field. The system uses:

- **4 ML Models** (Random Forest, XGBoost, CatBoost, SVM) for robust predictions
- **Soft Voting Ensemble** combining all models for highest accuracy (99.55% on test data)
- **Real-time Weather API** (OpenWeatherMap) for weather-aware recommendations
- **Crop Cycle Database** with 22 crops and their metadata

## ✨ Features

✅ **Soil Analysis Integration** - Nitrogen, Phosphorus, Potassium, and pH levels  
✅ **Real Weather Data** - Integration with OpenWeatherMap API  
✅ **Accurate Predictions** - 99.55% ensemble model accuracy  
✅ **Top-N Recommendations** - Get ranked crop suggestions  
✅ **Crop Cycle Information** - Growing period, season, water needs  
✅ **Location-Based** - GPS coordinate support (latitude/longitude)  
✅ **Interactive Interface** - Easy-to-use Python CLI  

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/cropsense.git
cd cropsense
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Create a `.env` file in the project root:
```
OPENWEATHERMAP_API_KEY=your_api_key_here
```

Get free API key from: https://openweathermap.org/api

### 5a. Run Interactive CLI Test
```bash
python frontend/interactive_test.py
```

### 5b. Or Run React Web UI (Recommended)

**Terminal 1 - Start Backend API:**
```bash
cd backend
python app.py
# Runs on http://localhost:5000
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm install        # First time only
npm run dev
# Runs on http://localhost:3000
```

Then open **http://localhost:3000** in your browser.

For detailed setup instructions, see [REACT_FRONTEND_SETUP.md](REACT_FRONTEND_SETUP.md) and [FULL_STACK_GUIDE.md](FULL_STACK_GUIDE.md).

---

## 📁 Project Structure

```
implementation/
├── backend/                          # ML Core & API Backend
│   ├── src/                          # Source code
│   ├── models/                       # Trained ML models (*.pkl)
│   ├── data/                         # Training dataset
│   ├── crop_recommendation.py        # Main system (338 lines)
│   ├── app.py                        # Flask REST API
│   ├── inference.py                  # Inference engine
│   ├── test_integration.py           # Integration tests
│   └── requirements.txt              # Backend dependencies
│
├── frontend/                         # React Web UI
│   ├── src/
│   │   ├── components/               # React components
│   │   ├── services/                 # API client
│   │   └── App.jsx                   # Main app
│   ├── package.json                  # NPM dependencies
│   ├── vite.config.js                # Vite config
│   ├── index.html                    # HTML entry point
│   └── .env.example                  # Environment template
│
├── .env                              # Environment variables (API key) - DO NOT COMMIT
├── .gitignore                        # Git ignore file
├── README.md                         # This file
├── SETUP.md                          # Detailed setup guide
│
├── data/
│   ├── raw/
│   │   └── Crop_recommendation.csv   # Original dataset (2200 samples)
│   └── dataset/
│
├── src/
│   ├── data/
│   │   └── preprocess.py             # Data preprocessing pipeline
│   ├── models/
│   │   ├── train_rf.py               # Random Forest training
│   │   ├── train_xgb.py              # XGBoost training
│   │   ├── train_catboost.py         # CatBoost training
│   │   ├── train_svm.py              # SVM training
│   │   └── ensemble.py               # Soft voting ensemble
│   └── utils/
│       ├── crop_database.py          # 22 crops metadata
│       └── weather_fetcher.py        # OpenWeatherMap API integration
│
├── models/                           # Trained models (generated - in .gitignore)
│   ├── scaler.pkl
│   ├── label_encoder.pkl
│   ├── random_forest.pkl
│   ├── xgboost.pkl
│   ├── catboost.pkl
│   ├── svm.pkl
│   └── ensemble.pkl
│
├── crop_recommendation.py            # Main integrated system
├── inference.py                      # Standalone inference engine
├── interactive_test.py               # Interactive user interface
├── test_integration.py               # System integration tests
└── CROP_CYCLE_GUIDE.md              # Crop cycle documentation
```

---

## 🔧 Training Models

To retrain models from scratch:

```bash
# 1. Preprocess data
python src/data/preprocess.py

# 2. Train individual models
python src/models/train_rf.py
python src/models/train_xgb.py
python src/models/train_catboost.py
python src/models/train_svm.py

# 3. Create ensemble
python src/models/ensemble.py
```

**Training Results:**
- Random Forest: 99.55% test accuracy
- XGBoost: 98.86% test accuracy
- CatBoost: 99.32% test accuracy
- SVM: 98.86% test accuracy
- **Ensemble (Soft Voting): 99.55% test accuracy**

---

## 📊 Dataset

**Source:** Crop Recommendation Dataset  
**Samples:** 2,200 records  
**Crops:** 22 varieties  
**Features:** 7 (N, P, K, temperature, humidity, pH, rainfall)  
**Train/Test Split:** 80/20 with stratification

### Supported Crops (22 Total)
Apple, Banana, Blackgram, Chickpea, Coconut, Coffee, Cotton, Grapes, Jute, Kidneybeans, Lentil, Maize, Mango, Mothbeans, Mungbean, Muskmelon, Orange, Papaya, Pigeonpeas, Pomegranate, Rice, Watermelon

---

## 🌍 API Integration

### OpenWeatherMap API

The system fetches real-time weather data from OpenWeatherMap.

**Setup:**
1. Sign up at https://openweathermap.org/api
2. Get your free API key
3. Add to `.env` file: `OPENWEATHERMAP_API_KEY=your_key`

**Note:** System works in mock mode without API key (for testing)

---

## 💻 Usage

### Interactive CLI
```bash
python interactive_test.py
```

### Programmatic Usage
```python
from crop_recommendation import FarmerCropRecommender

# Initialize (auto-loads API key from .env)
recommender = FarmerCropRecommender()

# Get top 3 recommendations
recommendations = recommender.get_top_recommendations(
    N=90,              # Nitrogen
    P=42,              # Phosphorus
    K=43,              # Potassium
    ph=6.5,            # pH
    latitude=12.9716,
    longitude=77.5946,
    top_n=3
)

for rec in recommendations:
    print(f"{rec['crop']}: {rec['suitability_score']}")
    print(f"  Weather: {rec['temperature']}, {rec['humidity']}")
```

---

## 📈 Model Architecture

```
Soil Nutrients + Weather Data
        ↓
    ┌───┼───┬───┐
    ↓   ↓   ↓   ↓
   RF  XGB CAT SVM
    ↓   ↓   ↓   ↓
    └───┼───┼───┘
        ↓
   Soft Voting Ensemble
        ↓
   Final Prediction (99.55%)
        ↓
   Ranked Crop List
```

---

## 🧪 Testing

```bash
# Integration test
python test_integration.py

# Interactive test
python interactive_test.py
```

---

## 📦 Dependencies

See `requirements.txt`:
- scikit-learn
- xgboost
- catboost
- pandas
- numpy
- joblib
- requests
- python-dotenv
- flask (optional)

---

## 🛠️ Team Setup Guide

### Initial Setup (New Team Members)

1. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd implementation
   ```

2. **Create virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup .env file:**
   - Create `.env` in project root
   - Add: `OPENWEATHERMAP_API_KEY=your_key_here`
   - Get key from https://openweathermap.org/api

5. **Test installation:**
   ```bash
   python interactive_test.py
   ```

### Important Files & Permissions

⚠️ **NEVER commit:**
- `.env` (contains API key)
- `models/*.pkl` (large files)
- `__pycache__/` directories
- `.pyc` files

✅ **DO commit:**
- Source code (`.py` files)
- `requirements.txt`
- `.gitignore`
- Documentation (`.md` files)

### Git Workflow

```bash
# Update from main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature

# Make changes & test
python interactive_test.py

# Commit & push
git add .
git commit -m "descriptive message"
git push origin feature/your-feature

# Create Pull Request on GitHub
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: sklearn` | Run `pip install -r requirements.txt` |
| `OPENWEATHERMAP_API_KEY not found` | Create `.env` file with API key |
| `FileNotFoundError: ensemble.pkl` | Train models: `python src/models/ensemble.py` |
| `Permission denied` | Check file permissions or run with admin |

---

## 📞 Support

- Check GitHub Issues for solutions
- Create detailed issue with error message
- Include steps to reproduce

---

## 🎯 Next Steps

- [ ] Flask REST API backend
- [ ] Web interface (React/Vue)
- [ ] Mobile app
- [ ] Advanced weather analysis
- [ ] Multi-language support

---

**Status:** Production Ready ✅  
**Last Updated:** February 3, 2026  
**Model Accuracy:** 99.55% (Ensemble)
