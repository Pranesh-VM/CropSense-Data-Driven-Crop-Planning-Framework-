# 🚀 QUICK START GUIDE - 15 MINUTES TO RUNNING SYSTEM

## Step 1: Copy Files (2 minutes)

```bash
cd your-project/implementation/backend

# 1. Copy database schema
cp schema_v2.sql database/schema_v2.sql

# 2. Copy authentication
mkdir -p src/auth
cp auth.py src/auth/auth.py

# 3. Copy services
mkdir -p src/services
cp rindm_cycle_manager.py src/services/
cp weather_monitor.py src/services/

# 4. Copy app
cp app_v2.py app_v2.py

# 5. Update requirements
cp requirements_v2.txt requirements_v2.txt
```

## Step 2: Install Dependencies (3 minutes)

```bash
pip install -r requirements_v2.txt
```

## Step 3: Setup Database (5 minutes)

```bash
# Create database
psql -U postgres -c "CREATE DATABASE cropsense_db"

# Import schema
psql -U postgres -d cropsense_db -f database/schema_v2.sql

# Import crop data
psql -U postgres -d cropsense_db -f database/seed_data.sql
```

## Step 4: Configure Environment (2 minutes)

Create/update `.env`:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cropsense_db
DB_USER=postgres
DB_PASSWORD=your_password

# API
OPENWEATHERMAP_API_KEY=your_api_key

# Flask
FLASK_PORT=5000
FLASK_ENV=development

# JWT
JWT_SECRET=change-this-to-random-secret-key

# Weather Monitor
ENABLE_WEATHER_MONITOR=true
WEATHER_CHECK_INTERVAL_MINUTES=60
```

## Step 5: Start Server (1 minute)

```bash
python app_v2.py
```

## Step 6: Test (2 minutes)

```bash
# Test signup
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testfarmer",
    "email": "test@example.com",
    "password": "test123",
    "name": "Test Farmer"
  }'

# Copy the token from response, then test RINDM
TOKEN="paste-token-here"

curl -X POST http://localhost:5000/api/rindm/get-recommendations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "N": 90,
    "P": 42,
    "K": 43,
    "ph": 6.5,
    "latitude": 13.0827,
    "longitude": 80.2707
  }'
```

## ✅ You're Done!

Your system is now:
- ✅ Running on port 5000
- ✅ Background monitor checking weather every 60 minutes
- ✅ Ready to accept farmer signups
- ✅ Ready to manage RINDM cycles

## 📁 File Structure After Setup

```
backend/
├── app_v2.py ⭐ NEW - Main application
├── requirements_v2.txt ⭐ NEW
├── src/
│   ├── auth/
│   │   └── auth.py ⭐ NEW - Authentication
│   ├── services/
│   │   ├── rindm_cycle_manager.py ⭐ NEW - Cycle management
│   │   └── weather_monitor.py ⭐ NEW - Background monitor
│   ├── models/
│   │   └── rindm.py ✅ (already created)
│   └── utils/
│       └── crop_nutrient_database.py ✅ (already created)
└── database/
    ├── schema_v2.sql ⭐ NEW - Updated schema
    ├── seed_data.sql ✅ (already created)
    └── db_utils.py ✅ (already created)
```

## 🎯 What Works Now

### 1. Authentication ✅
- Farmer signup/login
- JWT token authentication
- Protected routes

### 2. Single Prediction ✅
- One-time crop recommendation (existing)

### 3. RINDM Cycle ✅
- Get top 3 crop recommendations
- Start cycle with selected crop
- **Automatic background monitoring**
- Real-time nutrient updates from rainfall
- Threshold warnings
- Cycle completion
- History tracking

### 4. Background Monitor ✅
- Checks weather every 60 minutes
- Processes rainfall automatically
- Updates nutrients in real-time
- Generates warnings when critical

## 🔧 Troubleshooting

### Database Error?
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Restart if needed
sudo service postgresql restart
```

### Import Error?
```bash
# Make sure you're in backend directory
cd implementation/backend

# Activate virtual environment if using one
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Weather Monitor Not Starting?
```bash
# Check .env file
ENABLE_WEATHER_MONITOR=true  # Make sure it's 'true' not 'True'
```

## 📞 Next Steps

1. ✅ Test all API endpoints
2. 🔄 Build React frontend
3. 🔄 Deploy LSTM model (optional)
4. 🔄 Deploy to production

---

**Need help?** Read COMPLETE_IMPLEMENTATION_GUIDE.md for detailed documentation!
