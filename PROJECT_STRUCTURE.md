# Project Structure - Backend/Frontend Separation

## Overview
This project has been reorganized with **backend** (ML/data) and **frontend** (user interface) separation for better scalability and maintainability.

## Directory Layout

```
implementation/
├── 📂 backend/                           # ML Core & Data Processing
│   ├── 📂 src/
│   │   ├── data/                        # Data preprocessing
│   │   ├── models/                      # Model training scripts
│   │   └── utils/                       # Crop DB & Weather API
│   ├── 📂 models/                       # Trained model artifacts
│   │   ├── ensemble.pkl                 # Final ensemble model
│   │   ├── random_forest.pkl
│   │   ├── xgboost.pkl
│   │   ├── catboost.pkl
│   │   ├── svm.pkl
│   │   ├── scaler.pkl
│   │   └── label_encoder.pkl
│   ├── 📂 data/
│   │   └── raw/
│   │       └── Crop_recommendation.csv  # Raw training dataset
│   ├── crop_recommendation.py           # Main integrated system (338 lines)
│   ├── inference.py                     # Standalone inference engine
│   ├── test_integration.py              # Integration tests
│   ├── test_preprocess.py               # Preprocessing tests
│   └── requirements.txt                 # Backend dependencies
│
├── 📂 frontend/                         # User Interface Layer
│   └── interactive_test.py              # CLI interface (106 lines)
│
├── 📋 Documentation (Root)
│   ├── README.md                        # Project overview (350+ lines)
│   ├── SETUP.md                         # Installation & setup (400+ lines)
│   ├── CONTRIBUTING.md                  # Contribution guidelines
│   ├── 00_START_HERE.md                 # Quick start guide
│   ├── GITHUB_PUSH_GUIDE.md             # GitHub integration steps
│   ├── MASTER_CHECKLIST.md              # Pre-deployment checklist
│   ├── PROJECT_READY_SUMMARY.md         # Current status summary
│   ├── CROP_CYCLE_GUIDE.md              # Crop information reference
│   └── PROJECT_STRUCTURE.md             # This file
│
├── 🔐 Configuration (Root)
│   ├── .env                             # API keys (NEVER COMMIT)
│   ├── .env.example                     # Template for .env
│   └── .gitignore                       # Excludes .env, *.pkl, __pycache__
│
└── 📋 Initialization (Root)
    └── SETUP.md, README.md              # Instructions for team members
```

## Key Features of This Structure

### ✅ Backend (`backend/`)
- **Contains:** All ML models, data preprocessing, and core recommendation logic
- **Responsible for:** 
  - Model training (Random Forest, XGBoost, CatBoost, SVM)
  - Soft voting ensemble (99.55% accuracy)
  - Weather data fetching (OpenWeatherMap API)
  - Crop information database
  - Data preprocessing and inference
- **Dependencies:** scikit-learn, xgboost, catboost, requests, python-dotenv
- **Entry points:**
  - `crop_recommendation.py` - Main integrated system
  - `inference.py` - Standalone inference

### ✅ Frontend (`frontend/`)
- **Contains:** User-facing interfaces
- **Current:** CLI test interface (`interactive_test.py`)
- **Future:** Flask web app, React/Vue UI, mobile app
- **Imports from:** `backend.crop_recommendation`

### ✅ Root Level (Documentation & Config)
- Configuration files (`.env`, `.gitignore`)
- Setup instructions (SETUP.md, README.md)
- GitHub workflow guides
- Project status documents

## Import Paths After Restructuring

### In `backend/crop_recommendation.py`
```python
sys.path.insert(0, str(Path(__file__).parent))
from src.models.ensemble import EnsemblePredictor
from src.data.preprocess import DataPreprocessor
```

### In `frontend/interactive_test.py`
```python
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from crop_recommendation import FarmerCropRecommender
```

## Files Removed in Cleanup
- ❌ `output.txt` - debug output
- ❌ `instruction.md` - old spec (superseded by README.md)
- ❌ `app/` - old Flask structure
- ❌ `notebooks/` - exploratory code (not in production)
- ❌ `catboost_info/` - CatBoost temp files
- ❌ `__pycache__/` - Python cache
- ❌ Root-level `data/` directory (data moved to `backend/data/`)

## Running the System

### Test Backend
```bash
cd backend
python test_integration.py
```

### Run Frontend CLI
```bash
cd frontend
python interactive_test.py
```

### Run Specific Components
```bash
# Backend inference only
cd backend
python -c "from crop_recommendation import FarmerCropRecommender; r = FarmerCropRecommender()"

# Training a new model
cd backend
python src/models/train_rf.py
```

## Next Steps

1. **Frontend Expansion:** Add Flask REST API or web interface
2. **Backend Optimization:** Model performance improvements, caching
3. **Containerization:** Docker setup for consistent deployment
4. **CI/CD:** GitHub Actions for automated testing
5. **Database:** PostgreSQL for crop metadata (replaces in-memory DB)

## Team Collaboration

- Clone the repo: `git clone <repo-url>`
- Install backend deps: `pip install -r backend/requirements.txt`
- Read: [00_START_HERE.md](00_START_HERE.md) and [SETUP.md](SETUP.md)
- Create `.env` file from `.env.example`
- Run: `python frontend/interactive_test.py`

---
**Last Updated:** 2024  
**Structure Version:** 2.0 (Backend/Frontend Separation)
