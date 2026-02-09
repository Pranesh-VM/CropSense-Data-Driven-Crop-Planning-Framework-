# 🚀 QUICK START - Database Setup

## **FASTEST WAY (Windows Users)**

### Just Run This:
```bash
cd G:\sem-8\Project\implementation\backend
.\SETUP_DATABASE.bat
```

Done! ✓

---

## **For pgAdmin Users - Copy & Paste Method**

### Step 1: Drop Old Database
Open pgAdmin → Tools → Query Tool
```sql
DROP DATABASE IF EXISTS cropsense_db;
```
Execute (F5)

### Step 2: Create Fresh Database
```sql
CREATE DATABASE cropsense_db;
```
Execute (F5)

### Step 3: Right-Click Database → Query Tool
Open the entire schema_v2.sql file:
- Location: `backend/database/schema_v2.sql`
- Copy ALL content
- Paste into pgAdmin Query Tool
- Execute (F5)

Wait for "Commands completed successfully"

---

## **Command Line Users - Copy & Paste These Commands**

### Windows PowerShell / Command Prompt:

```bash
# Step 1: Navigate to backend folder
cd G:\sem-8\Project\implementation\backend\database

# Step 2: Drop old database
psql -U postgres -c "DROP DATABASE IF EXISTS cropsense_db;"

# Step 3: Create fresh database
psql -U postgres -c "CREATE DATABASE cropsense_db;"

# Step 4: Import schema
psql -U postgres -d cropsense_db -f schema_v2.sql

# Step 5: Import seed data (optional)
psql -U postgres -d cropsense_db -f seed_data.sql
```

---

## **Or Run All At Once (One-Liner)**

```bash
psql -U postgres -c "DROP DATABASE IF EXISTS cropsense_db; CREATE DATABASE cropsense_db;" && psql -U postgres -d cropsense_db -f schema_v2.sql
```

---

## **Verify It Worked**

### In PostgreSQL / pgAdmin, run:
```sql
-- Should return 7 tables
\dt

-- Should show farmers table structure
\d farmers
```

Expected output for `\d farmers`:
```
farmer_id        | integer
username         | character varying(50)
email            | character varying(100)
password_hash    | character varying(255)
phone            | character varying(20)
is_active        | boolean
email_verified   | boolean
created_at       | timestamp
last_login       | timestamp
updated_at       | timestamp
```

---

## **Troubleshooting**

| Error | Solution |
|-------|----------|
| "psql is not recognized" | Use full path: `"C:\Program Files\PostgreSQL\14\bin\psql"` |
| "Password authentication failed" | Add `--password` flag or set `PGPASSWORD` environment variable |
| "Database is being accessed by others" | Close pgAdmin and try again |
| "Schema import failed" | Make sure schema_v2.sql is in `backend/database/` folder |

---

## **Test Your Setup**

```bash
# Go to backend folder
cd G:\sem-8\Project\implementation\backend

# Start the server
python app_v2.py

# Should see:
# ✓ Database connected successfully
# ✓ Weather monitor started
# Running on http://0.0.0.0:5000
```

---

## **3 Files Provided:**

1. **SETUP_DATABASE.bat** - Run on Windows (easiest)
2. **SETUP_DATABASE.sh** - Run on Linux/Mac
3. **schema_v2.sql** - The database schema (already updated)

All in `backend/` folder

