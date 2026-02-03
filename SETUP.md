# 🛠️ Detailed Setup Guide for Team Members

Welcome to CropSense! This guide will help you get the project running locally.

---

## 📋 Prerequisites

Before starting, ensure you have:

- **Python 3.8+** (check with `python --version`)
- **Git** (check with `git --version`)
- **pip** (Python package manager, usually comes with Python)
- **OpenWeatherMap API key** (free, from https://openweathermap.org/api)

### Check Python Installation

```bash
python --version
python -m pip --version
```

---

## 🚀 Step-by-Step Setup

### Step 1: Clone Repository

```bash
# Using HTTPS
git clone https://github.com/yourusername/cropsense.git

# Using SSH (if configured)
git clone git@github.com:yourusername/cropsense.git

# Navigate to project
cd cropsense/implementation
```

### Step 2: Create Virtual Environment

A virtual environment keeps project dependencies isolated.

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

You should see `(venv)` in your terminal prompt when activated.

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- scikit-learn (machine learning)
- xgboost, catboost (gradient boosting)
- pandas, numpy (data processing)
- requests (API calls)
- python-dotenv (environment variables)
- And others...

### Step 4: Get OpenWeatherMap API Key

1. Go to https://openweathermap.org/api
2. Sign up for free account (if not done)
3. Go to **API keys** section
4. Copy your **default API key**

### Step 5: Create .env File

Create `.env` file in project root (`implementation/.env`):

```bash
# Windows (using PowerShell)
echo "OPENWEATHERMAP_API_KEY=your_key_here" > .env

# macOS/Linux (using bash)
echo "OPENWEATHERMAP_API_KEY=your_key_here" > .env
```

Or manually:
1. Create file named `.env` in `implementation/` folder
2. Add this single line:
   ```
   OPENWEATHERMAP_API_KEY=your_actual_api_key_here
   ```

### Step 6: Test Installation

```bash
python interactive_test.py
```

You should see:
```
======================================================================
🌾 CropSense: Farmer Crop Recommendation System
======================================================================

⏳ Initializing AI recommendation system...
✅ System ready!
```

---

## 🧪 Testing Your Setup

### Quick Test

```bash
python test_integration.py
```

Expected output: Top 3 crop recommendations

### Interactive Test

```bash
python interactive_test.py
```

When prompted, enter:
- Nitrogen: `90`
- Phosphorus: `42`
- Potassium: `43`
- pH: `6.5`
- Latitude: `12.9716` (or press Enter)
- Longitude: `77.5946` (or press Enter)
- Top N recommendations: `5`

---

## 🔄 Common Setup Issues & Solutions

### Issue: `python: command not found`

**Solution:**
- Python not installed or not in PATH
- Try `python3` instead
- On Windows, reinstall Python and check "Add Python to PATH"

### Issue: `pip: command not found`

**Solution:**
```bash
python -m pip install --upgrade pip
```

### Issue: `ModuleNotFoundError: No module named 'sklearn'`

**Solution:**
```bash
# Deactivate and reactivate virtual env
deactivate  # or on Windows: venv\Scripts\deactivate

# Then activate again
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall
pip install -r requirements.txt
```

### Issue: `.env` file not found

**Solution:**
```bash
# Windows - create empty file first
type nul > .env

# Then add content with your API key
# macOS/Linux
touch .env
echo "OPENWEATHERMAP_API_KEY=your_key" >> .env
```

### Issue: `OPENWEATHERMAP_API_KEY not found`

**Solutions:**
1. Check `.env` file exists in project root
2. Verify file contains: `OPENWEATHERMAP_API_KEY=your_actual_key`
3. Restart Python/terminal after creating `.env`

### Issue: `FileNotFoundError: ensemble.pkl`

**Solution:**
Retrain models:
```bash
python src/data/preprocess.py
python src/models/train_rf.py
python src/models/train_xgb.py
python src/models/train_catboost.py
python src/models/train_svm.py
python src/models/ensemble.py
```

---

## 📂 Project Structure Explained

```
implementation/
├── .env                     ← Your API key (SECRET - never commit!)
├── .gitignore              ← Tells Git what to ignore
├── requirements.txt        ← List of Python packages
├── README.md               ← Project overview
├── SETUP.md               ← This file
│
├── src/
│   ├── data/
│   │   └── preprocess.py   ← Loads and prepares data
│   ├── models/
│   │   ├── train_rf.py     ← Random Forest model
│   │   ├── train_xgb.py    ← XGBoost model
│   │   ├── train_catboost.py ← CatBoost model
│   │   ├── train_svm.py    ← SVM model
│   │   └── ensemble.py     ← Combines all 4 models
│   └── utils/
│       ├── crop_database.py ← 22 crops info
│       └── weather_fetcher.py ← Gets weather data
│
├── models/                 ← Trained models (auto-generated)
│   ├── scaler.pkl
│   ├── label_encoder.pkl
│   ├── random_forest.pkl
│   ├── xgboost.pkl
│   ├── catboost.pkl
│   ├── svm.pkl
│   └── ensemble.pkl
│
├── data/
│   └── raw/
│       └── Crop_recommendation.csv ← Dataset
│
└── crop_recommendation.py  ← Main system
    interactive_test.py     ← User interface
    test_integration.py     ← System test
```

---

## 📝 How the System Works

1. **Farmer Input** → Soil nutrients (N, P, K, pH) + Location (lat, lon)
2. **Preprocessing** → Scale features, encode labels
3. **Weather Fetch** → Get real weather from OpenWeatherMap
4. **ML Models** → 4 models make predictions independently
5. **Ensemble** → Average predictions for best accuracy
6. **Ranking** → Sort crops by suitability score
7. **Output** → Top N recommendations with weather info

---

## 🔐 Security Checklist

Before committing, ensure:

- ✅ `.env` is in `.gitignore` (never commit API keys)
- ✅ Virtual environment activated during development
- ✅ `pip freeze > requirements.txt` run after installing packages
- ✅ No hardcoded credentials in code
- ✅ No model files committed (too large, in .gitignore)

---

## 📊 Training Your Own Models

If you want to retrain from scratch:

```bash
# 1. Preprocess data (creates scaler & label encoder)
python src/data/preprocess.py
# Output: models/scaler.pkl, models/label_encoder.pkl

# 2. Train individual models (each ~30-60 seconds)
python src/models/train_rf.py      # ~45s
python src/models/train_xgb.py     # ~30s
python src/models/train_catboost.py # ~60s
python src/models/train_svm.py     # ~40s

# 3. Create ensemble (combines all 4)
python src/models/ensemble.py      # ~20s

# Total time: ~4-5 minutes
```

---

## 🌐 Working with Git

### First Time Setup

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Making Changes

```bash
# Create feature branch
git checkout -b feature/my-feature-name

# Make changes to files
# Test: python interactive_test.py

# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature description"

# Push to GitHub
git push origin feature/my-feature-name

# Create Pull Request on GitHub website
```

### Getting Latest Changes

```bash
# Update main branch
git pull origin main

# Rebase on main (clean history)
git rebase main
```

---

## 📞 Getting Help

### If Something Goes Wrong

1. **Check error message** - Read full error carefully
2. **Search GitHub Issues** - Someone might have solved it
3. **Check README & SETUP.md** - Solutions might be here
4. **Create GitHub Issue** with:
   - Error message (exact text)
   - Steps to reproduce
   - Your OS and Python version
   - What you were trying to do

### Useful Commands

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Upgrade a package
pip install --upgrade package_name

# See virtual environment info
pip show scikit-learn

# Deactivate virtual environment
deactivate

# Delete virtual environment (to start fresh)
rm -rf venv  # macOS/Linux
rmdir venv /s  # Windows
```

---

## ✅ Checklist: Ready to Contribute?

- [ ] Python 3.8+ installed
- [ ] Git installed and configured
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] `pip install -r requirements.txt` successful
- [ ] `.env` file created with API key
- [ ] `python interactive_test.py` runs successfully
- [ ] `python test_integration.py` shows recommendations
- [ ] Understood project structure
- [ ] Read contribution guidelines

---

## 🎯 Next Steps After Setup

1. **Explore the code:**
   ```bash
   # Check out the main recommendation system
   code crop_recommendation.py
   
   # Look at individual models
   code src/models/train_rf.py
   ```

2. **Run tests:**
   ```bash
   python test_integration.py
   python interactive_test.py
   ```

3. **Check issues:**
   - Go to GitHub Issues
   - Pick a task to work on

4. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## 📚 Learning Resources

- **scikit-learn:** https://scikit-learn.org/
- **XGBoost:** https://xgboost.readthedocs.io/
- **CatBoost:** https://catboost.ai/
- **OpenWeatherMap API:** https://openweathermap.org/api
- **Git Guide:** https://git-scm.com/doc
- **Python Docs:** https://docs.python.org/3/

---

**Last Updated:** February 3, 2026  
**Questions?** Create an issue on GitHub!
