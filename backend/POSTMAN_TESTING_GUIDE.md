# 📬 POSTMAN TESTING GUIDE - CropSense API

Complete guide to test all endpoints in Postman.

---

## 🔧 SETUP

### Base URL
```
http://localhost:5000
```

### Server Must Be Running
```bash
cd backend
python app_v2.py
```

Look for:
```
✓ Weather monitor started (checking every 60 minutes)
* Running on http://0.0.0.0:5000
```

---

## 📝 TESTING SEQUENCE

Follow this order to test the complete workflow:

1. ✅ Health Check
2. ✅ Signup
3. ✅ Login (get token)
4. ✅ Get Profile (test auth)
5. ✅ Get Recommendations
6. ✅ Start Cycle
7. ✅ Check Cycle Status
8. ✅ Manual Weather Check
9. ✅ Get History
10. ✅ Complete Cycle

---

## 🧪 ENDPOINT TESTS

### 1️⃣ HEALTH CHECK

**Purpose:** Verify server is running

**Request:**
```
GET http://localhost:5000/health
```

**Headers:** None needed

**Expected Response (200 OK):**
```json
{
  "status": "ok",
  "message": "CropSense API is running",
  "services": {
    "authentication": "enabled",
    "single_prediction": "enabled",
    "rindm_cycles": "enabled",
    "weather_monitor": "enabled"
  }
}
```

---

### 2️⃣ SIGNUP

**Purpose:** Create new farmer account

**Request:**
```
POST http://localhost:5000/api/auth/signup
```

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "username": "ramesh_farmer",
  "email": "ramesh@example.com",
  "password": "test123456",
  "name": "Ramesh Kumar",
  "phone": "+919876543210",
  "location": "Chennai, Tamil Nadu",
  "latitude": 13.0827,
  "longitude": 80.2707
}
```

**Expected Response (201 Created):**
```json
{
  "success": true,
  "farmer": {
    "farmer_id": 1,
    "username": "ramesh_farmer",
    "email": "ramesh@example.com",
    "name": "Ramesh Kumar"
  },
  "field_id": 1,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmYXJtZXJfaWQiOjEsInVzZXJuYW1lIjoicmFtZXNoX2Zhcm1lciIsImVtYWlsIjoicmFtZXNoQGV4YW1wbGUuY29tIiwiZXhwIjoxNzM5Mzc2MDAwLCJpYXQiOjE3Mzg3NzEyMDB9.abc123...",
  "message": "Registration successful"
}
```

**⚠️ IMPORTANT:** Copy the `token` value - you'll need it for all subsequent requests!

**Possible Errors:**
- 400: "Username already exists" - Change username
- 400: "Email already registered" - Change email
- 400: "Missing required fields" - Check all fields present

---

### 3️⃣ LOGIN

**Purpose:** Login existing farmer

**Request:**
```
POST http://localhost:5000/api/auth/login
```

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "username": "ramesh_farmer",
  "password": "test123456"
}
```

**Alternative (login with email):**
```json
{
  "username": "ramesh@example.com",
  "password": "test123456"
}
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "farmer": {
    "farmer_id": 1,
    "username": "ramesh_farmer",
    "email": "ramesh@example.com",
    "name": "Ramesh Kumar"
  },
  "field_id": 1,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "Login successful"
}
```

**⚠️ SAVE THE TOKEN:** Create a Postman environment variable:
1. Click "Environments" in Postman
2. Create new environment "CropSense"
3. Add variable: `auth_token` = `<paste token here>`
4. Select "CropSense" environment

**Possible Errors:**
- 401: "Invalid credentials" - Wrong username/password

---

### 4️⃣ GET PROFILE (Test Authentication)

**Purpose:** Verify token works

**Request:**
```
GET http://localhost:5000/api/auth/profile
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**⚠️ In Postman:**
- In Headers tab, add:
  - Key: `Authorization`
  - Value: `Bearer {{auth_token}}` (if using environment variable)
  - OR Value: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (paste full token)

**Expected Response (200 OK):**
```json
{
  "success": true,
  "profile": {
    "farmer_id": 1,
    "username": "ramesh_farmer",
    "email": "ramesh@example.com",
    "name": "Ramesh Kumar",
    "phone": "+919876543210",
    "location": "Chennai, Tamil Nadu",
    "latitude": "13.08270000",
    "longitude": "80.27070000",
    "created_at": "2026-02-07T10:30:00",
    "last_login": "2026-02-07T10:35:00"
  }
}
```

**Possible Errors:**
- 401: "No token provided" - Add Authorization header
- 401: "Invalid or expired token" - Login again to get new token

---

### 5️⃣ GET CROP RECOMMENDATIONS (RINDM)

**Purpose:** Get top 3 crop recommendations for RINDM cycle

**Request:**
```
POST http://localhost:5000/api/rindm/get-recommendations
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "N": 90,
  "P": 42,
  "K": 43,
  "ph": 6.5,
  "latitude": 13.0827,
  "longitude": 80.2707
}
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "recommendation_id": 1,
  "recommendations": {
    "predicted_crop": "rice",
    "confidence": 0.9545,
    "crop_1": "rice",
    "confidence_1": 0.9545,
    "crop_2": "unknown",
    "confidence_2": 0.0,
    "crop_3": "unknown",
    "confidence_3": 0.0
  },
  "nutrients": {
    "N": 90,
    "P": 42,
    "K": 43,
    "ph": 6.5
  },
  "weather": {
    "temperature": 28.5,
    "humidity": 75.2,
    "rainfall": 0
  }
}
```

**⚠️ SAVE:** Copy the `recommendation_id` value (e.g., 1)

**Possible Errors:**
- 401: Missing/invalid token
- 400: Missing required fields

---

### 6️⃣ START RINDM CYCLE

**Purpose:** Start monitoring cycle with selected crop

**Request:**
```
POST http://localhost:5000/api/rindm/start-cycle
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "recommendation_id": 1,
  "selected_crop": "rice",
  "N": 90,
  "P": 42,
  "K": 43,
  "ph": 6.5,
  "soil_type": "loamy"
}
```

**Alternative (with soil texture):**
```json
{
  "recommendation_id": 1,
  "selected_crop": "rice",
  "N": 90,
  "P": 42,
  "K": 43,
  "ph": 6.5,
  "soil_type": "loamy",
  "sand_pct": 40,
  "silt_pct": 40,
  "clay_pct": 20
}
```

**Expected Response (201 Created):**
```json
{
  "success": true,
  "cycle_id": 1,
  "cycle_number": 1,
  "crop": "rice",
  "start_date": "2026-02-07",
  "expected_end_date": "2026-06-07",
  "duration_days": 120,
  "current_nutrients": {
    "N": 90,
    "P": 42,
    "K": 43
  },
  "crop_requirements": {
    "N": 120,
    "P": 40,
    "K": 140
  }
}
```

**⚠️ SAVE:** Copy the `cycle_id` value (e.g., 1)

**✅ CYCLE NOW ACTIVE!** Background monitor will check weather every 60 minutes automatically.

**Possible Errors:**
- 401: Missing/invalid token
- 400: Invalid crop name
- 404: No field found for farmer

---

### 7️⃣ GET ACTIVE CYCLE

**Purpose:** Check if farmer has active cycle

**Request:**
```
GET http://localhost:5000/api/rindm/active-cycle
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Expected Response (200 OK) - With active cycle:**
```json
{
  "success": true,
  "has_active_cycle": true,
  "cycle": {
    "success": true,
    "cycle_id": 1,
    "status": "active",
    "crop": "rice",
    "cycle_number": 1,
    "progress": {
      "days_elapsed": 0,
      "days_remaining": 120,
      "total_days": 120,
      "percent_complete": 0.0
    },
    "current_nutrients": {
      "N": 90,
      "P": 42,
      "K": 43
    },
    "nutrient_status": {
      "N": {
        "level": "MODERATE",
        "status": "moderate",
        "color": "yellow",
        "message": "✓ MODERATE: N is adequate but monitor levels.",
        "action": "Monitor: Consider soil test if planning heavy-feeding crops"
      },
      "P": {
        "level": "GOOD",
        "status": "good",
        "color": "lightgreen",
        "message": "✓ GOOD: P levels are good for crop production.",
        "action": "No action needed"
      },
      "K": {
        "level": "MODERATE",
        "status": "moderate",
        "color": "yellow",
        "message": "✓ MODERATE: K is adequate but monitor levels.",
        "action": "Monitor: Consider soil test if planning heavy-feeding crops"
      },
      "overall_status": "MODERATE",
      "overall_color": "yellow",
      "needs_soil_test": false,
      "soil_test_message": "✓ Nutrient levels are adequate. Soil testing not urgently needed.",
      "nutrient_values": {
        "N": 90,
        "P": 42,
        "K": 43
      }
    },
    "rainfall_events": 0,
    "last_weather_check": "2026-02-07 10:40:00"
  }
}
```

**Expected Response - No active cycle:**
```json
{
  "success": true,
  "has_active_cycle": false,
  "message": "No active cycle"
}
```

---

### 8️⃣ CHECK CYCLE STATUS

**Purpose:** Get detailed status of a specific cycle

**Request:**
```
GET http://localhost:5000/api/rindm/cycle-status/1
```
*(Replace `1` with your cycle_id)*

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "cycle_id": 1,
  "status": "active",
  "crop": "rice",
  "cycle_number": 1,
  "progress": {
    "days_elapsed": 0,
    "days_remaining": 120,
    "total_days": 120,
    "percent_complete": 0.0
  },
  "current_nutrients": {
    "N": 90,
    "P": 42,
    "K": 43
  },
  "nutrient_status": { ... },
  "rainfall_events": 0,
  "last_weather_check": "2026-02-07 10:40:00"
}
```

**Possible Errors:**
- 403: Unauthorized (not your cycle)
- 404: Cycle not found

---

### 9️⃣ MANUAL WEATHER CHECK (Simulate Rainfall)

**Purpose:** Manually trigger weather check (normally automatic)

**Request:**
```
POST http://localhost:5000/api/rindm/check-weather/1
```
*(Replace `1` with your cycle_id)*

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Body:** None needed

**Expected Response (200 OK) - No rainfall:**
```json
{
  "success": true,
  "rainfall_detected": false,
  "message": "No rainfall detected"
}
```

**Expected Response - Rainfall detected:**
```json
{
  "success": true,
  "rainfall_detected": true,
  "rainfall_mm": 25.5,
  "event_id": 1,
  "nutrient_loss": {
    "N": 11.25,
    "P": 4.78,
    "K": 5.83
  },
  "updated_nutrients": {
    "N": 78.75,
    "P": 37.22,
    "K": 37.17
  },
  "status": {
    "N": { "level": "MODERATE", ... },
    "P": { "level": "GOOD", ... },
    "K": { "level": "LOW", ... },
    "needs_soil_test": true
  },
  "warning": true,
  "message": "🔬 SOIL TEST RECOMMENDED: One or more nutrients are below optimal levels..."
}
```

**✅ THIS SIMULATES WHAT HAPPENS AUTOMATICALLY!**

---

### 🔟 GET CYCLE HISTORY

**Purpose:** View all past cycles

**Request:**
```
GET http://localhost:5000/api/rindm/history
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "cycles": [
    {
      "cycle_id": 1,
      "cycle_number": 1,
      "crop_name": "rice",
      "status": "active",
      "start_date": "2026-02-07",
      "actual_end_date": null,
      "initial_n_kg_ha": "90.00",
      "initial_p_kg_ha": "42.00",
      "initial_k_kg_ha": "43.00",
      "final_n_kg_ha": null,
      "final_p_kg_ha": null,
      "final_k_kg_ha": null,
      "rainfall_event_count": 0,
      "total_rainfall_loss_n": "0.00",
      "total_rainfall_loss_p": "0.00",
      "total_rainfall_loss_k": "0.00"
    }
  ],
  "total": 1
}
```

---

### 1️⃣1️⃣ COMPLETE CYCLE (Manual)

**Purpose:** Manually complete a cycle (normally automatic after duration)

**Request:**
```
POST http://localhost:5000/api/rindm/complete-cycle/1
```
*(Replace `1` with your cycle_id)*

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Body:** None needed

**Expected Response (200 OK):**
```json
{
  "success": true,
  "cycle_id": 1,
  "completed": true,
  "final_nutrients": {
    "N": 0,
    "P": 2,
    "K": 0
  },
  "depletion_summary": {
    "crop_uptake": {
      "N": 120,
      "P": 40,
      "K": 140
    },
    "rainfall_loss": {
      "N": 0,
      "P": 0,
      "K": 0
    },
    "total_depletion": {
      "N": 90,
      "P": 40,
      "K": 43
    }
  },
  "below_threshold": true,
  "can_continue": false,
  "message": "Nutrients below threshold - cycle must stop"
}
```

**If nutrients >= threshold:**
```json
{
  ...
  "below_threshold": false,
  "can_continue": true,
  "message": "Cycle complete - ready for next crop"
}
```

**Then farmer can start next cycle (go back to step 5)!**

---

### 1️⃣2️⃣ SINGLE PREDICTION (Existing - Untouched)

**Purpose:** One-time crop prediction (no auth needed)

**Request:**
```
POST http://localhost:5000/api/predict
```

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "N": 90,
  "P": 42,
  "K": 43,
  "ph": 6.5,
  "latitude": 13.0827,
  "longitude": 80.2707
}
```

**Expected Response (200 OK):**
```json
{
  "predicted_crop": "rice",
  "confidence": 0.9545
}
```

---

## 🎯 QUICK TEST WORKFLOW

**Copy-paste this sequence in Postman:**

### 1. Signup
```
POST http://localhost:5000/api/auth/signup
Headers: Content-Type: application/json
Body:
{
  "username": "test_farmer",
  "email": "test@example.com",
  "password": "test123",
  "name": "Test Farmer"
}
```

### 2. Copy token → Create environment variable `auth_token`

### 3. Get Recommendations
```
POST http://localhost:5000/api/rindm/get-recommendations
Headers: 
  Authorization: Bearer {{auth_token}}
  Content-Type: application/json
Body:
{
  "N": 90,
  "P": 42,
  "K": 43,
  "ph": 6.5,
  "latitude": 13.0827,
  "longitude": 80.2707
}
```

### 4. Start Cycle (use crop from step 3)
```
POST http://localhost:5000/api/rindm/start-cycle
Headers: 
  Authorization: Bearer {{auth_token}}
  Content-Type: application/json
Body:
{
  "selected_crop": "rice",
  "N": 90,
  "P": 42,
  "K": 43,
  "ph": 6.5,
  "soil_type": "loamy"
}
```

### 5. Check Status
```
GET http://localhost:5000/api/rindm/active-cycle
Headers: Authorization: Bearer {{auth_token}}
```

### 6. Simulate Rainfall (optional)
```
POST http://localhost:5000/api/rindm/check-weather/1
Headers: Authorization: Bearer {{auth_token}}
```

---

## 🐛 COMMON ISSUES

### 1. "Connection refused"
**Fix:** Make sure server is running
```bash
python app_v2.py
```

### 2. "401 Unauthorized"
**Fix:** Add Authorization header with token
```
Authorization: Bearer <your-token-here>
```

### 3. "Invalid or expired token"
**Fix:** Login again to get new token (tokens expire after 7 days)

### 4. "No active cycle"
**Fix:** Start a cycle first (step 6)

### 5. Database errors
**Fix:** Make sure database is set up:
```bash
psql -U postgres -d cropsense_db -f database/schema_v2.sql
```

---

## 📊 MONITORING BACKGROUND SERVICE

**Check server console for weather monitor logs:**

```
[2026-02-07 14:00:00] Checking 1 active cycles...
  ✓ Cycle 1 (rice): No rainfall detected
  Completed in 0.35s

[2026-02-07 15:00:00] Checking 1 active cycles...
  ✓ Cycle 1 (rice): Rainfall 25mm detected
    ⚠️  Warning: Nutrients approaching threshold
  Completed in 0.42s
```

---

## 🎉 SUCCESS INDICATORS

**You know everything works when:**

✅ Signup creates account  
✅ Login returns token  
✅ Profile shows farmer info  
✅ Recommendations return 3 crops  
✅ Start cycle creates active cycle  
✅ Status shows progress  
✅ Weather check updates nutrients (if rainfall)  
✅ Console shows background monitor running  
✅ History shows all cycles  
✅ Complete cycle calculates final nutrients  

---

**Need help?** Check the server console for error messages!
