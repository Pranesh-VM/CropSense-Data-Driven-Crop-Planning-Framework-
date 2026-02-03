# React Frontend Setup Guide

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Backend running on port 5000

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── RecommendationForm.jsx      # Soil parameter input form
│   │   ├── RecommendationForm.css
│   │   ├── RecommendationResult.jsx    # Results display
│   │   └── RecommendationResult.css
│   ├── services/
│   │   └── api.js                      # API client & endpoints
│   ├── App.jsx                         # Main app component
│   ├── App.css
│   ├── main.jsx                        # React entry point
│   ├── index.css                       # Global styles
│   └── public/                         # Static assets
├── index.html                          # HTML template
├── vite.config.js                      # Vite configuration
├── package.json                        # Dependencies
├── .env.example                        # Environment template
└── .env                                # Environment variables (not in git)
```

---

## 🔧 Available Scripts

### Development
```bash
npm run dev
```
Starts the Vite development server with hot module replacement (HMR).

### Production Build
```bash
npm run build
```
Creates an optimized production build in the `dist/` directory.

### Preview Build
```bash
npm run preview
```
Previews the production build locally.

---

## 🌐 API Integration

### API Endpoints

The frontend communicates with the backend Flask API at `http://localhost:5000`:

#### 1. **Health Check**
```
GET /health
```
Response:
```json
{
  "status": "ok",
  "message": "CropSense API is running"
}
```

#### 2. **Get Crop Recommendation**
```
POST /recommend
Content-Type: application/json

{
  "nitrogen": 90,
  "phosphorus": 42,
  "potassium": 43,
  "ph": 6.5,
  "rainfall": 200,
  "temperature": 25,
  "humidity": 60,
  "location": "Delhi"
}
```

Response:
```json
{
  "recommended_crop": "Rice",
  "confidence": 0.9955,
  "alternative_crops": ["Wheat", "Corn"],
  "crop_info": {
    "growing_season": "June-October",
    "optimal_temp": "25-30°C",
    "rainfall_needed": "1000-1500 mm",
    "soil_type": "Loamy"
  },
  "weather_info": {
    "temperature": 25,
    "humidity": 60,
    "description": "Clear Sky"
  }
}
```

#### 3. **Get Crop Information**
```
GET /crop-info/<crop_name>
```
Response:
```json
{
  "name": "Rice",
  "growing_season": "June-October",
  "optimal_temp": "25-30°C",
  "rainfall_needed": "1000-1500 mm",
  "soil_type": "Loamy"
}
```

#### 4. **Get Weather Data**
```
GET /weather?location=Delhi
GET /weather?latitude=28.7041&longitude=77.1025
```

---

## 🎨 UI Components

### RecommendationForm
Collects soil and environmental parameters:
- **Nitrogen (N)**: mg/kg
- **Phosphorus (P)**: mg/kg
- **Potassium (K)**: mg/kg
- **pH Level**: 0-14
- **Rainfall**: mm
- **Temperature**: °C
- **Humidity**: 0-100%
- **Location**: Optional city name

### RecommendationResult
Displays recommendation results:
- **Recommended Crop**: With confidence percentage
- **Crop Information**: Growing season, optimal temp, rainfall, soil type
- **Alternative Options**: Other suitable crops
- **Weather Data**: Current location weather (if available)

---

## 🔐 Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_URL=http://localhost:5000
```

**Production:**
```env
VITE_API_URL=https://api.yourdomain.com
```

---

## 🎯 Key Features

✅ **Modern React 18** with Vite bundler  
✅ **Responsive Design** - Works on desktop, tablet, mobile  
✅ **Real-time API Integration** - Communicates with backend  
✅ **Beautiful UI** - Gradient backgrounds, smooth animations  
✅ **Form Validation** - Numeric input validation  
✅ **Error Handling** - Displays API errors gracefully  
✅ **Loading States** - Shows spinner during processing  
✅ **Accessibility** - Semantic HTML, proper labels  

---

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

This creates a `dist/` folder ready for deployment.

### Deploy to Vercel (Recommended)
```bash
npm install -g vercel
vercel
```

### Deploy to Netlify
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

### Deploy to AWS S3 + CloudFront
```bash
npm run build
aws s3 sync dist/ s3://your-bucket-name/
```

---

## 🔗 Connecting Frontend & Backend

### Option 1: Local Development
Start both in development mode:

```bash
# Terminal 1 - Backend
cd backend
python app.py
# Runs on http://localhost:5000

# Terminal 2 - Frontend
cd frontend
npm run dev
# Runs on http://localhost:3000
```

### Option 2: Production
Deploy both to servers and update `.env`:
```env
VITE_API_URL=https://api.yourdomain.com
```

---

## 🐛 Troubleshooting

### CORS Errors
If you see CORS errors, ensure:
1. Backend has `flask-cors` installed
2. Backend is running on port 5000
3. `.env` has correct `VITE_API_URL`

### API Not Found (404)
Check that:
1. Backend `app.py` is running
2. Endpoints match the routes defined in `app.py`
3. Request format matches API specification

### Build Errors
```bash
# Clear node modules and reinstall
rm -r node_modules package-lock.json
npm install
npm run build
```

---

## 📚 Technologies Used

- **React 18** - UI library
- **Vite** - Build tool & dev server
- **Axios** - HTTP client
- **CSS3** - Styling with gradients & animations
- **ES6+** - Modern JavaScript

---

## 📖 Resources

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [Axios Documentation](https://axios-http.com)
- [MDN Web Docs](https://developer.mozilla.org)

---

## 🤝 Contributing

When adding new features:
1. Create a new component in `src/components/`
2. Add corresponding styles in `.css` file
3. Update API calls in `src/services/api.js` if needed
4. Test thoroughly before committing

---

## 📝 License

This project is part of the CropSense AI recommendation system.

---

**Last Updated:** February 3, 2026  
**Version:** 1.0.0
