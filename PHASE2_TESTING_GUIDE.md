# CropSense Phase 2 - Testing & Integration Guide

## 🎯 Overview

Phase 2 of the CropSense frontend is now fully implemented with all major features. This guide will help you test the application and integrate it with your backend.

---

## 📋 Prerequisites

### Backend Requirements
1. ✅ Backend API running on `http://localhost:5000`
2. ✅ PostgreSQL database with schema_v2.sql applied
3. ✅ All crop data seeded in `crop_nutrient_requirements` table
4. ✅ Farmers table simplified (username, email, password, phone only)

### Frontend Setup
```bash
cd frontend
npm run dev
```
- App runs on `http://localhost:5173`
- Hot reload enabled for development
- All 298 packages installed

---

## 🧪 Testing Workflow

### 1. Welcome Page - `/welcome`
**What to expect:**
- Landing page with CropSense logo (🌱)
- Feature highlights
- "Login" and "Sign up" CTA buttons
- Descriptive subtitle about the application

**Test Steps:**
1. Navigate to `http://localhost:5173`
2. Should redirect to `/welcome`
3. Click "Login to Your Account" → navigates to `/login`
4. Click "Create New Account" → navigates to `/signup`

**Expected Behavior:**
- Clean, professional landing page
- Responsive on mobile/tablet/desktop
- No API calls needed

---

### 2. Signup Page - `/signup`
**What to expect:**
- Form with 5 fields: Username, Email, Phone, Password, Confirm Password
- Real-time form validation
- "Create Account" button
- Link to Login page

**Test Steps:**
1. Fill form with test data:
   ```
   Username: testfarmer123
   Email: testfarmer@example.com
   Phone: 9876543210
   Password: TestPass123!
   Confirm Password: TestPass123!
   ```
2. Click "Create Account"

**Expected Behavior:**
- Loading state on button during submission
- Success toast: "Signup successful! Welcome to CropSense!"
- Auto-redirect to `/dashboard`
- Token saved to localStorage (check DevTools → Application → localStorage)
- User data persisted to localStorage

**Error Cases:**
- Empty fields: Shows validation error
- Invalid email: Shows validation error
- Password mismatch: Shows "Passwords do not match"
- Existing user: Backend returns 409 Conflict → Shows toast error
- Server error: Shows appropriate error message

---

### 3. Login Page - `/login`
**What to expect:**
- Form with Username and Password fields
- "Login" button
- Link to Signup page
- Link to Welcome page

**Test Steps:**
1. Fill form:
   ```
   Username: testfarmer123
   Password: TestPass123!
   ```
2. Click "Login"

**Expected Behavior:**
- Loading state on button
- Success toast: "Login successful!"
- Auto-redirect to `/dashboard`
- Token and user data saved to localStorage

**Error Cases:**
- Invalid credentials: Backend returns 401 → Shows "Invalid username or password"
- Non-existent user: Backend returns 404 → Shows error message
- Server error: Shows appropriate error message

---

### 4. Dashboard Page - `/dashboard`
**What to expect** (First time after signup):
- Welcome greeting with username
- "No Active Cycle" card with CTA to start new cycle
- Quick stats showing Total Cycles (0), Completed (0)
- Recent Cycles empty list
- Info cards with helpful tips

**What to expect** (After starting a cycle):
- Active Cycle card showing:
  - Crop name
  - Soil type
  - Status badge
  - N, P, K levels with status colors
  - "View Details" and "End Cycle" buttons
- Statistics updated
- Recent cycles list showing latest cycle

**Test Steps:**
1. Login → redirects to dashboard
2. Click "Start New Cycle" → navigates to `/cycle/new`
3. Complete new cycle (see step 5)
4. Dashboard updates automatically

**Expected Behavior:**
- Page loads with user greeting
- Recent cycles list scrolls if content overflows
- Nutrient badges show correct status colors:
  - 🔴 Red: Critical (< 40 N, < 15 P, < 40 K)
  - 🟠 Orange/Red: Low (below optimal)
  - 🟢 Green: Optimal
  - 🟡 Yellow: High (above max)
- Sidebar stays sticky on scroll
- Header dropdown menu works (click username)

**API Calls**:
- `GET /api/rindm/active-cycle` - Fetch active cycle
- `GET /api/rindm/cycle-history` - Fetch past cycles

---

### 5. New Cycle Page - `/cycle/new`
**3-Step Wizard for Starting a Cycle**

#### Step 1: Soil Analysis Input
**What to expect:**
- Form with fields: N, P, K, pH, Latitude, Longitude
- Progress indicator showing "Step 1 of 3"
- Nutrient status badges showing real-time status
- "Get Recommendations" button (disabled until valid)
- "Cancel" button

**Test Steps:**
1. Fill form with test data:
   ```
   Nitrogen: 60
   Phosphorus: 25
   Potassium: 70
   pH: 7.0
   Latitude: 28.6139
   Longitude: 77.2090
   ```
2. Watch nutrient badges update in real-time
3. Click "Get Recommendations" button

**Expected Behavior:**
- Form validates each field
- Error messages appear for invalid inputs
- Nutrient badges show status colors based on values:
  - 60 N → Yellow (below optimal 80)
  - 25 P → Yellow (below optimal 40)
  - 70 K → Yellow (below optimal 100)
- Button disables during API call (shows "Getting Recommendations...")
- Success → moves to Step 2

**Error Cases:**
- Invalid latitude (< -90 or > 90): Shows validation error
- Invalid longitude (< -180 or > 180): Shows validation error
- pH out of range: Shows validation error
- Backend error: Shows toast error
- Recommendation fetch fails: Error toast with retry option

#### Step 2: Crop Recommendations
**What to expect:**
- List of recommended crops (from backend)
- Each crop shows name and confidence percentage
- Radio buttons for selection
- After crop selection, soil type buttons appear (clay, sandy, loamy, silt, peaty, chalky)
- "Back" and "Continue" buttons

**Test Steps:**
1. Wait for recommendations to load
2. Select a crop (e.g., "rice")
3. Select soil type (e.g., "loamy")
4. Click "Continue"

**Expected Behavior:**
- Recommendations display after API call
- Selected crop shows green border and background
- Soil type buttons change to active state when clicked
- "Continue" button enabled only when both selections made
- Progress moves to Step 3

**Backend Requirement**:
Response format must be:
```json
{
  "id": 1,
  "recommendations": [
    {
      "name": "rice",
      "confidence": 85,
      "notes": "Suitable for high rainfall..."
    }
  ]
}
```

#### Step 3: Confirmation
**What to expect:**
- Review cards showing:
  - Selected crop
  - Selected soil type
  - Input nutrient values
- Success message: "Everything looks good! Click Start Cycle..."
- "Back" and "Start Cycle" buttons

**Test Steps:**
1. Review the displayed information
2. Click "Start Cycle"

**Expected Behavior:**
- Loading state on button (shows "Starting Cycle...")
- Success toast: "Cycle started successfully!"
- Auto-redirect to `/cycle/active`
- New cycle data visible in dashboard

**API Calls**:
- `POST /api/rindm/get-recommendations` with body:
```json
{
  "n": 60,
  "p": 25,
  "k": 70,
  "ph": 7.0,
  "latitude": 28.6139,
  "longitude": 77.2090
}
```

- `POST /api/rindm/start-cycle` with body:
```json
{
  "recommendation_id": 1,
  "selected_crop": "rice",
  "soil_type": "loamy"
}
```

---

### 6. Active Cycle Page - `/cycle/active`
**What to expect:**
- Cycle Overview section showing:
  - Crop name, soil type, pH, status
  - Start date and duration in days
- Nutrient Status section with progress bars:
  - Nitrogen bar
  - Phosphorus bar
  - Potassium bar
  - Each showing value, unit, and status
- Sidebar with:
  - "Check Weather" button
  - "End Cycle" button
  - Weather widget (if available)
  - Location coordinates

**Test Steps:**
1. From Dashboard, click "View Details" on active cycle
   OR navigate directly: `http://localhost:5173/cycle/active`
2. Click "Check Weather" button
3. Observe nutrient progress bars
4. Check location coordinates displayed

**Expected Behavior:**
- Page loads active cycle data from backend
- Uses `GET /api/rindm/active-cycle` endpoint
- Nutrient bars animate and show correct colors:
  - Green: Optimal
  - Yellow: Low (below optimal)
  - Red: Critical
  - Orange: High (above max)
- Weather button shows loading state
- Sidebar sticks to viewport while scrolling
- Duration shows correct day count

**If No Active Cycle**:
- Shows friendly message
- "Start New Cycle" button navigates to `/cycle/new`

**API Calls**:
- `GET /api/rindm/active-cycle` - Fetch cycle details
- `GET /api/rindm/check-weather/{cycle_id}` - Optional weather update

**Complete Cycle Test**:
1. Click "End Cycle" button
2. Confirm modal appears
3. Click "Yes, End Cycle"
4. Loading state shows
5. Success toast: "Cycle completed successfully!"
6. Redirects to `/cycle/history`

---

### 7. Cycle History Page - `/cycle/history`
**What to expect:**
- List of all past cycles (clickable cards)
- Each cycle card shows:
  - Crop name
  - Soil type
  - pH level
  - Start date
  - Status badge (completed/active)
- Sidebar with statistics:
  - Total Cycles count
  - Completed Cycles count
  - Average Duration
  - Top 3 Crops

**Test Steps:**
1. Navigate to `/cycle/history`
   OR from Active Cycle page after ending cycle
2. Click on a cycle card to expand
3. Observe detailed information

**Expected Behavior:**
- All past cycles load from backend
- Click expands to show:
  - Nutrient values (N, P, K) with color boxes
  - Cycle dates and duration
  - Any notes (if available)
- Sidebar statistics calculate correctly:
  - Total = count of all cycles
  - Average duration = sum of days / completed cycles
  - Top crops = most frequently grown

**Empty History**:
- Shows friendly message with crop icon
- No cycles available yet

**API Calls**:
- `GET /api/rindm/cycle-history` - Fetch all cycles

---

### 8. Profile Page - `/profile`
**What to expect:**
- User avatar with initials
- Username, email display
- Status badges (Active, Verified)
- "Edit" button
- Account Information section
- Account Settings section with toggles
- Danger Zone with Logout button

**Test Steps:**
1. Navigate to `/profile` or click username → Profile
2. Click "Edit" button
3. Modify email or phone fields
4. Click "Save Changes"
5. Verify changes display in view mode
6. Test logout: Click "Logout" button

**Expected Behavior:**
- Edit mode shows form with current values pre-filled
- Form validates email and phone format
- Save button shows success message (demo - not saved to backend yet)
- Toggle switches work smoothly
- Logout clears localStorage and redirects to `/welcome`

**Note**: Profile update is UI-only. Backend endpoint needed for persistence.

---

## 🔐 Authentication Testing

### Session Management
1. **Token Storage**:
   - Open DevTools → Application → localStorage
   - Should see `cropsense_auth_token` and `cropsense_user_data`

2. **Protected Routes**:
   - Logout by clicking Logout button
   - Try to access `/dashboard` directly
   - Should redirect to `/login`

3. **Token Persistence**:
   - Login successfully
   - Refresh page (Ctrl+R)
   - Should stay logged in
   - User data should load from localStorage

4. **Auto-Logout on 401**:
   - Delete the token from localStorage manually
   - Try any action that calls API
   - Should redirect to `/login`

---

## 🌐 API Endpoint Testing

### Using Postman/Insomnia

**1. Signup**
```
POST http://localhost:5000/api/auth/signup
Body (JSON):
{
  "username": "testfarmer1",
  "email": "test@example.com",
  "password": "TestPass123!",
  "phone": "9876543210"
}

Expected Response (201):
{
  "token": "eyJ...",
  "user": {
    "farmer_id": 1,
    "username": "testfarmer1",
    "email": "test@example.com",
    "phone": "9876543210"
  }
}
```

**2. Login**
```
POST http://localhost:5000/api/auth/login
Body (JSON):
{
  "username": "testfarmer1",
  "password": "TestPass123!"
}

Expected Response (200):
{
  "token": "eyJ...",
  "user": {...}
}
```

**3. Get Recommendations**
```
POST http://localhost:5000/api/rindm/get-recommendations
Headers: Authorization: Bearer <token>
Body (JSON):
{
  "n": 60,
  "p": 25,
  "k": 70,
  "ph": 7.0,
  "latitude": 28.6139,
  "longitude": 77.2090
}

Expected Response (200):
{
  "id": 1,
  "recommendations": [
    {
      "name": "rice",
      "confidence": 85,
      "notes": "..."
    }
  ]
}
```

**4. Start Cycle**
```
POST http://localhost:5000/api/rindm/start-cycle
Headers: Authorization: Bearer <token>
Body (JSON):
{
  "recommendation_id": 1,
  "selected_crop": "rice",
  "soil_type": "loamy"
}

Expected Response (201):
{
  "cycle_id": 1,
  "crop": "rice",
  "soil_type": "loamy",
  "status": "active"
}
```

**5. Get Active Cycle**
```
GET http://localhost:5000/api/rindm/active-cycle
Headers: Authorization: Bearer <token>

Expected Response (200):
{
  "id": 1,
  "crop": "rice",
  "soil_type": "loamy",
  "nitrogen_kg_ha": 60,
  "phosphorus_kg_ha": 25,
  "potassium_kg_ha": 70,
  "ph": 7.0,
  "status": "active",
  "start_date": "2026-02-10T...",
  "latitude": 28.6139,
  "longitude": 77.2090
}
```

**6. Get Cycle History**
```
GET http://localhost:5000/api/rindm/cycle-history
Headers: Authorization: Bearer <token>

Expected Response (200):
{
  "cycles": [
    {
      "id": 1,
      "crop": "rice",
      ...
    }
  ]
}
```

**7. Check Weather**
```
GET http://localhost:5000/api/rindm/check-weather/1
Headers: Authorization: Bearer <token>

Expected Response (200):
{
  "temperature": 28.5,
  "humidity": 65,
  "rainfall": 5.2
}
```

**8. Complete Cycle**
```
POST http://localhost:5000/api/rindm/complete-cycle/1
Headers: Authorization: Bearer <token>
Body: {}

Expected Response (200):
{
  "status": "completed",
  "end_date": "2026-02-15T..."
}
```

---

## 🐛 Common Issues & Fixes

### Issue: "Failed to fetch recommendations"
**Cause**: Backend API not running or endpoint not returning correct format

**Fix**:
1. Check backend is running: `python app_v2.py`
2. Verify endpoint returns: `{"id": ..., "recommendations": [...]}`
3. Check API URI in constants.js

### Issue: "Page blank after login"
**Cause**: Dashboard page failing to load

**Fix**:
1. Open DevTools → Console
2. Check for JavaScript errors
3. Verify `GET /api/rindm/active-cycle` endpoint works in Postman
4. Check backend response format

### Issue: "Nutrient values show 'NaN'"
**Cause**: Backend returning null or missing fields

**Fix**:
1. Verify active cycle response includes: `nitrogen_kg_ha`, `phosphorus_kg_ha`, `potassium_kg_ha`
2. Check database has correct data in `crop_cycles` table

### Issue: "Logout doesn't work"
**Cause**: localStorage not being cleared properly

**Fix**:
1. Check DevTools → Console for errors
2. Verify logout function in AuthContext.jsx
3. Clear localStorage manually and test again

### Issue: "Mobile sidebar not opening"
**Cause**: CSS classes not applied correctly

**Fix**:
1. Ensure Tailwind CSS is compiled (HMR should handle this)
2. Restart dev server: `npm run dev`
3. Clear browser cache (Ctrl+Shift+Delete)

---

## ✅ Final Verification Checklist

- [ ] Welcome page displays correctly
- [ ] Can signup with new user
- [ ] Can login with credentials
- [ ] Dashboard shows greeting and stats
- [ ] Can start new cycle (3-step wizard)
- [ ] Recommendations fetch from backend
- [ ] Can select crop and soil type
- [ ] Active cycle page shows nutrient data
- [ ] Weather check button works
- [ ] Can end/complete cycle
- [ ] Cycle history displays past cycles
- [ ] Profile page shows user info
- [ ] Can logout and redirect to login
- [ ] Protected routes work (redirect when not authenticated)
- [ ] All forms validate correctly
- [ ] Error messages display as toasts
- [ ] Loading states show spinners
- [ ] Responsive on mobile/tablet/desktop

---

## 📞 Support

If you encounter issues:
1. Check browser console (F12) for JavaScript errors
2. Check Network tab for failed API requests
3. Verify backend is running on `localhost:5000`
4. Check response format in Postman
5. Review backend logs for errors

---

**Document Created**: February 10, 2026  
**Frontend Version**: Phase 2 Complete  
**Status**: Ready for Testing ✅
