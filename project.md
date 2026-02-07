# CropSense: Unified Project Documentation

---

## 1. Project Overview

CropSense is an AI-powered crop recommendation system for farmers. It uses four ML models (Random Forest, XGBoost, CatBoost, SVM) combined via a soft voting ensemble for robust, accurate predictions. The system integrates real-time weather data (OpenWeatherMap API) and a crop cycle database (22 crops, with metadata).

- **Backend:** Python (Flask REST API), ML/data processing, weather integration
- **Frontend:** React (Vite), user interface for input and results

---

## 2. Quick Start & Setup

### Backend
- Python 3.8+, pip, Git required
- Clone repo, create virtual environment, install requirements
- Add `.env` with OpenWeatherMap API key
- Run backend: `python app.py` (default port 5000)

### Frontend
- Node.js 16+, npm required
- `cd frontend`, `npm install`, `cp .env.example .env`, `npm run dev` (default port 3000)

---

## 3. Project Structure

```
implementation/
├── backend/         # ML core & data processing
│   ├── src/
│   │   ├── data/    # Preprocessing
│   │   ├── models/  # Model training
│   │   └── utils/   # Crop DB & weather API
│   ├── models/      # Trained model artifacts
│   ├── data/
│   ├── crop_recommendation.py
│   ├── inference.py
│   ├── test_integration.py
│   ├── test_preprocess.py
│   └── requirements.txt
├── frontend/        # User interface (React)
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── README.md
├── SETUP.md
├── CONTRIBUTING.md
├── ... (other docs)
```

---

## 4. Key Features

- Accepts soil parameters (N, P, K, pH) and location (lat/lon)
- Fetches weather data internally (temperature, humidity, rainfall)
- Assembles features in strict order for inference
- Returns predicted crop and confidence
- No weather endpoint or client-side weather fetching

---

## 5. Development & Collaboration

- Git branching: `main`, `feature/*`, `bugfix/*`, etc.
- Pre-push checklist and GitHub push guide
- All dependencies and environment variables documented
- Code review, commit message, and PR guidelines

---

## 6. Deployment & GitHub

- `.gitignore` excludes `.env`, models, cache
- `requirements.txt` lists all dependencies
- `.env.example` provided (never commit real API keys)
- Step-by-step GitHub push instructions included

---

## 7. Crop Cycle & Data Sources

- 22 crops with duration, season, water needs, temperature (see `src/utils/crop_database.py`)
- Data sourced from FAO, ICAR, ICRISAT, and official agri ministries

---

## 8. Checklists & Verification

- MASTER_CHECKLIST.md: All items verified, ready for production
- PROJECT_READY_SUMMARY.md: Executive summary, team quick start, model performance
- REACT_CHECKLIST.md: Frontend implementation status

---

## 9. Full Stack Guide

- Backend: Flask REST API (Python)
- Frontend: React + Vite
- End-to-end setup, development, and deployment instructions

---

## 10. Additional Resources

- Troubleshooting, FAQ, and team onboarding in SETUP.md and 00_START_HERE.md
- Crop cycle and weather integration details in CROP_CYCLE_GUIDE.md
- Contribution and collaboration rules in CONTRIBUTING.md

---

For detailed instructions, see the original markdown files in the project root.
