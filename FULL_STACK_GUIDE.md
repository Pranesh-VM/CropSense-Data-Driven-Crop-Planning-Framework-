# Full Stack Setup: Backend + React Frontend

## 📋 Overview

This document explains how to run the complete CropSense system with:
- **Backend**: Flask REST API (Python) on port 5000
- **Frontend**: React + Vite on port 3000

---

## ✅ Prerequisites

### System Requirements
- **Python**: 3.8+
- **Node.js**: 16+ 
- **npm**: 7+
- **Git**: For version control

### Verify Installation
```bash
python --version          # Should be 3.8+
node --version           # Should be 16+
npm --version            # Should be 7+
```

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Clone & Setup Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OpenWeatherMap API key
```

### Step 2: Run Backend

```bash
# Make sure you're in backend directory with venv activated
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
```

### Step 3: Setup Frontend (New Terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm run dev
```

Expected output:
```
  ➜  Local:   http://localhost:3000/
```

### Step 4: Access Application

Open browser and go to: **http://localhost:3000**

---

## 🔄 Development Workflow

### Terminal 1 - Backend
```bash
cd g:\sem-8\Project\implementation\backend
venv\Scripts\activate
python app.py
```

### Terminal 2 - Frontend
```bash
cd g:\sem-8\Project\implementation\frontend
npm run dev
```

### Terminal 3 - Optional (Testing/Debugging)
```bash
cd g:\sem-8\Project\implementation\backend
python test_integration.py
```

---

## 📡 API Communication Flow

```
User (Browser)
    ↓
    ↓ HTTP Request
    ↓
React Frontend (localhost:3000)
    ↓
    ↓ JSON POST/GET
    ↓
Flask Backend (localhost:5000)
    ↓
    ↓ Process
    ↓
ML Models + Crop Database
    ↓
    ↓ JSON Response
    ↓
React Frontend
    ↓
Display Results
```

---

## 🔌 Backend Endpoints

### Health Check
```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "ok",
  "message": "CropSense API is running"
}
```

### Get Recommendation
```bash
curl -X POST http://localhost:5000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "nitrogen": 90,
    "phosphorus": 42,
    "potassium": 43,
    "ph": 6.5,
    "rainfall": 200,
    "temperature": 25,
    "humidity": 60,
    "location": "Delhi"
  }'
```

### Get Crop Info
```bash
curl http://localhost:5000/crop-info/Rice
```

### Get Weather
```bash
curl "http://localhost:5000/weather?location=Delhi"
```

---

## 🎯 Testing the System

### Test Backend Only
```bash
cd backend
python test_integration.py
```

### Test Frontend Only
```bash
cd frontend
npm run build  # Test production build
npm run preview
```

### Test Full Integration
1. Start backend: `python app.py`
2. Start frontend: `npm run dev`
3. Open http://localhost:3000
4. Enter soil parameters
5. Click "Get Recommendation"
6. Verify results display

---

## 🔧 Configuration Files

### Backend (.env)
```env
OPENWEATHER_API_KEY=your_api_key_here
FLASK_PORT=5000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000
```

---

## 📦 Deployment

### Production Backend (Flask)
```bash
# Install production WSGI server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Production Frontend (React)
```bash
# Build optimized bundle
npm run build

# Deploy 'dist' folder to static hosting:
# - AWS S3
# - Netlify
# - Vercel
# - GitHub Pages
# - etc.
```

---

## 🐛 Common Issues & Solutions

### Issue: Backend won't start
```
Error: Address already in use
```
**Solution**: Change port in `backend/app.py` and `frontend/.env`

```python
# In app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

```env
# In frontend/.env
VITE_API_URL=http://localhost:5001
```

### Issue: CORS errors in browser console
```
Access to XMLHttpRequest blocked by CORS policy
```
**Solution**: Ensure `flask-cors` is installed
```bash
pip install flask-cors
```

### Issue: npm install fails
```bash
# Clear cache and reinstall
npm cache clean --force
rm -r node_modules package-lock.json
npm install
```

### Issue: React can't find backend
```
Network Error: connect ECONNREFUSED
```
**Solution**:
1. Check backend is running: `curl http://localhost:5000/health`
2. Verify `.env` has correct URL
3. Check firewall settings

---

## 🔒 Security Notes

⚠️ **Important for Production:**
- Never commit `.env` files
- Use environment variables for secrets
- Enable HTTPS/TLS
- Implement authentication
- Rate limiting on API
- Input validation
- CORS restrictions

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│           User's Web Browser                            │
│         http://localhost:3000                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │  React UI                                         │  │
│  │  - Soil Parameter Form                           │  │
│  │  - Result Display                                │  │
│  │  - Weather Integration                           │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                    HTTP/JSON Requests
                           │
┌─────────────────────────────────────────────────────────┐
│        Backend Flask API                                │
│      http://localhost:5000                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Flask REST API (app.py)                         │  │
│  │  - /recommend          (POST)                    │  │
│  │  - /crop-info/<name>   (GET)                     │  │
│  │  - /weather            (GET)                     │  │
│  │  - /health             (GET)                     │  │
│  └───────────────────────────────────────────────────┘  │
│                           │                              │
│  ┌────────────────────────┴────────────────────────┐    │
│  │                                                 │    │
│  ▼                                                 ▼    │
│  Crop Recommendation System              Weather API    │
│  - ML Models (RF, XGB, CAT, SVM)         (OpenWeather)  │
│  - Ensemble Voting                                      │
│  - Data Preprocessing                                   │
│  - Crop Database                                        │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 📚 File Structure Reference

```
implementation/
├── backend/
│   ├── venv/                    # Python virtual environment
│   ├── src/                     # Source code
│   ├── models/                  # Trained models (*.pkl)
│   ├── data/                    # Dataset
│   ├── app.py                   # Flask API
│   ├── crop_recommendation.py   # ML system
│   ├── inference.py             # Inference engine
│   ├── test_integration.py      # Tests
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # Environment (NOT in git)
│   └── .env.example             # Environment template
│
├── frontend/
│   ├── node_modules/            # JavaScript dependencies
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── services/            # API client
│   │   ├── App.jsx              # Main component
│   │   └── main.jsx             # Entry point
│   ├── public/                  # Static assets
│   ├── index.html               # HTML template
│   ├── vite.config.js           # Vite config
│   ├── package.json             # JavaScript dependencies
│   ├── .env                     # Environment (NOT in git)
│   └── .env.example             # Environment template
│
└── Documentation/
    ├── README.md
    ├── SETUP.md
    ├── REACT_FRONTEND_SETUP.md  # This file
    └── ...
```

---

## ✅ Checklist: Ready to Run

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Backend `requirements.txt` dependencies installed
- [ ] Backend `.env` file with API key
- [ ] Frontend `node_modules` installed
- [ ] Frontend `.env` file with correct API URL
- [ ] Backend runs without errors
- [ ] Frontend runs without errors
- [ ] Can access http://localhost:3000
- [ ] Can submit recommendation form
- [ ] Results display correctly

---

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev)
- [REST API Best Practices](https://restfulapi.net/)
- [Frontend Performance](https://web.dev/performance/)

---

## 🆘 Getting Help

If you encounter issues:
1. Check the [Troubleshooting](#-common-issues--solutions) section
2. Review error messages in terminal
3. Check browser console (F12)
4. Look at API response in Network tab (F12)
5. Read backend logs

---

## 📝 Next Steps

1. ✅ Run both backend and frontend
2. ✅ Test with sample data
3. ✅ Explore API endpoints
4. ✅ Customize frontend styling
5. ✅ Deploy to production

---

**Last Updated:** February 3, 2026  
**Version:** 1.0.0  
**Status:** ✅ Ready for Development
