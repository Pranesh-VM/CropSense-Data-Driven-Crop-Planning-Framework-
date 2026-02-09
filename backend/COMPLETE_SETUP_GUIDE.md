# 🎯 Complete Database Setup - Choose Your Method

---

## **📍 YOUR STATUS**
- ✅ Schema updated (removed name, location, latitude, longitude from signup)
- ✅ Code updated (app_v2.py, auth.py, POSTMAN_TESTING_GUIDE.md)
- ✅ Seed data fixed (matches new schema)
- ⏳ **NEXT:** Run database setup

---

## **METHOD 1: Windows Batch Script (Easiest) ⭐**

### Step 1: Open Command Prompt or PowerShell
Press `Win + R`, type `cmd` or `powershell`

### Step 2: Run this command:
```bash
cd G:\sem-8\Project\implementation\backend && SETUP_DATABASE.bat
```

### Step 3: Wait for completion
You should see:
```
✓ Database dropped successfully
✓ Database created successfully
✓ Schema imported successfully
✓ Seed data imported successfully
✓ Database setup complete!
```

Done! ✓ Skip to [Verification](#verification) section

---

## **METHOD 2: Command Line (psql) - One Command**

### Prerequisites:
- PostgreSQL installed and in PATH
- Open Command Prompt or PowerShell

### Navigate to backend/database folder:
```bash
cd G:\sem-8\Project\implementation\backend\database
```

### Run all setup in one command:
```bash
psql -U postgres -c "DROP DATABASE IF EXISTS cropsense_db; CREATE DATABASE cropsense_db;" && psql -U postgres -d cropsense_db -f schema_v2.sql
```

### Expected output:
```
CREATE DATABASE
CREATE TABLE
CREATE TABLE
... (many lines)
INSERT 0 1
INSERT 0 1
```

Done! ✓ Skip to [Verification](#verification) section

---

## **METHOD 3: pgAdmin 4 GUI (Step-by-Step)**

### Step 1: Open pgAdmin 4
- Open browser
- Go to http://localhost:5050 or open pgAdmin application

### Step 2: Connect to PostgreSQL
- Expand "Servers" on left
- Click "PostgreSQL" (or your server name)
- Enter password if prompted

### Step 3: Drop Old Database
- Right-click "Databases"
- Select "Query Tool"
- Copy and paste:
```sql
DROP DATABASE IF EXISTS cropsense_db;
```
- Press F5 or click "Execute"
- You should see: `DROP DATABASE completed`

### Step 4: Create New Database
```sql
CREATE DATABASE cropsense_db;
```
- Press F5 to execute
- Should see: `CREATE DATABASE completed`

### Step 5: Import Schema
- Close this query tab
- Right-click "Databases" → Refresh
- Click on the new `cropsense_db` database
- Right-click → "Query Tool"
- Open file: `G:\sem-8\Project\implementation\backend\database\schema_v2.sql`
- Copy entire content
- Paste into pgAdmin Query Tool
- Press F5 to execute
- Wait for: `Commands completed successfully`

### Step 6: (Optional) Verify
- Close query tab
- Expand `cropsense_db` → `Schemas` → `public` → `Tables`
- Should see 7 tables:
  - crop_cycles
  - crop_nutrient_requirements
  - cycle_recommendations
  - farmers ✓
  - fields
  - nutrient_measurements
  - rainfall_events

Done! ✓ Skip to [Verification](#verification) section

---

## **Verification**

### Option A: Using pgAdmin
1. Open pgAdmin
2. Expand cropsense_db → Schemas → public → Tables
3. Right-click "farmers" → "View/Edit Data" → "All Rows"
4. Should see 1 sample farmer row

### Option B: Using psql
Open Command Prompt and run:
```bash
psql -U postgres -d cropsense_db -c "SELECT * FROM farmers;"
```

Should see:
```
 farmer_id | username   | email                | password_hash | phone
-----------+------------+----------------------+---------------+--
         1 | testfarmer | test@example.com     | $2b$12$...    | +919876543210
```

### Option C: Using Python
```bash
cd G:\sem-8\Project\implementation\backend
python -c "from database.db_utils import DatabaseManager; db = DatabaseManager(); conn, cur = db.get_connection().__enter__(); cur.execute('SELECT COUNT(*) FROM farmers'); print(f'Total farmers: {cur.fetchone()[0]}')"
```

Should print: `Total farmers: 1`

---

## **Test Your Setup**

### Start the API:
```bash
cd G:\sem-8\Project\implementation\backend
python app_v2.py
```

### Look for these messages:
```
✓ Database connected successfully
✓ Weather monitor started (checking every 60 minutes)
* Running on http://0.0.0.0:5000
```

### In another terminal, test:
```bash
curl http://localhost:5000/health
```

Should return:
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

## **Troubleshooting**

### Problem: "psql is not recognized"
**Solution:**
- Add PostgreSQL bin folder to PATH, OR
- Use full path:
```bash
"C:\Program Files\PostgreSQL\15\bin\psql" -U postgres -d cropsense_db
```

### Problem: "FATAL: Ident authentication failed"
**Solution:**
```bash
psql -U postgres --password -d cropsense_db
```
Then enter your PostgreSQL password

### Problem: "Database already exists"
**Solution:** Drop it first
```bash
psql -U postgres -c "DROP DATABASE IF EXISTS cropsense_db;"
```

### Problem: "Cannot drop database"
**Solution:** Close all connections
1. In pgAdmin, close all Query Tool tabs
2. Disconnect from the database
3. Try again

### Problem: Schema import fails
**Solution:**
1. Make sure schema_v2.sql is in `backend/database/` folder
2. Check entire file is copied (should be ~450 lines)
3. Try pasting into pgAdmin instead of command line
4. Check for syntax errors in schema file

### Problem: "Column 'name' does not exist"
**Solution:** This means old schema is still active
- Verify you dropped the database completely
- Run DROP DATABASE command again
- Create fresh database

---

## **Files You Have**

| File | Purpose | Location |
|------|---------|----------|
| `SETUP_DATABASE.bat` | Windows setup script | `backend/` |
| `SETUP_DATABASE.sh` | Linux/Mac setup script | `backend/` |
| `schema_v2.sql` | Database schema (UPDATED) | `backend/database/` |
| `QUICK_SETUP.md` | Quick reference | `backend/` |
| `DATABASE_SETUP_GUIDE.md` | Detailed guide | `backend/` |
| `MIGRATION_SUMMARY.md` | Summary of changes | `backend/` |

---

## **What Was Changed**

### Database Side:
- ✅ Farmers table: Removed `name, location, latitude, longitude` columns
- ✅ Removed `idx_farmers_location` index
- ✅ Updated seed data to match new schema

### Code Side:
- ✅ Signup endpoint: Only accepts `username, email, password, phone`
- ✅ Auth service: Updated `register_farmer()` method
- ✅ Profile endpoint: Returns only `username, email, phone` (not name/location/lat/lon)

### Documentation:
- ✅ Updated POSTMAN_TESTING_GUIDE.md with new examples

---

## **Data Collection Timeline**

```
Farmer Register → Farmer Login → Get Recommendations → Start Cycle
username, email,        ✓           N, P, K, pH,        crop,
password, phone                    latitude, longitude   soil_type
```

---

## **Next Steps After Setup**

1. ✅ Run database setup (you are here)
2. ✅ Test signup: POST /api/auth/signup (new simplified body)
3. ✅ Test login: POST /api/auth/login
4. ✅ Test recommendations: POST /api/rindm/get-recommendations
5. ✅ Test cycle start: POST /api/rindm/start-cycle

---

**Choose a method above and run it. The schema_v2.sql is already updated!**

Need help? Check the error messages above or files in this folder.

