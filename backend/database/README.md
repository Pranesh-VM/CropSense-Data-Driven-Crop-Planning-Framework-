# 🗄️ CropSense Database Setup Guide

**PostgreSQL Database for Nutrient Tracking System**

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Setup](#quick-setup)
3. [Manual Setup](#manual-setup)
4. [Database Structure](#database-structure)
5. [Import/Export](#importexport)
6. [Connection Setup](#connection-setup)
7. [Verification](#verification)

---

## 🔧 Prerequisites

### Required Software

- **PostgreSQL** 12+ 
  - Download: https://www.postgresql.org/download/
  - Or install via package manager:
    ```bash
    # Ubuntu/Debian
    sudo apt-get install postgresql postgresql-contrib
    
    # macOS (Homebrew)
    brew install postgresql
    
    # Windows
    # Download installer from postgresql.org
    ```

- **Python psycopg2** (for Python connection)
  ```bash
  pip install psycopg2-binary
  ```

---

## 🚀 Quick Setup (Recommended)

### Option 1: Using provided script (Linux/Mac)

```bash
cd backend/database
chmod +x setup_database.sh
./setup_database.sh
```

### Option 2: Using Python script

```bash
cd backend/database
python setup_database.py
```

This will:
1. Create database `cropsense_db`
2. Create all tables
3. Import crop nutrient data
4. Run verification tests

---

## 📝 Manual Setup (Step-by-Step)

### Step 1: Start PostgreSQL

```bash
# Linux/Mac
sudo service postgresql start

# Or
pg_ctl start

# Check status
sudo service postgresql status
```

### Step 2: Access PostgreSQL

```bash
# Login as postgres user
sudo -u postgres psql
```

### Step 3: Create Database

```sql
-- Create database
CREATE DATABASE cropsense_db;

-- Create user (optional - for security)
CREATE USER cropsense_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE cropsense_db TO cropsense_user;

-- Exit
\q
```

### Step 4: Import Schema

```bash
# Connect to database and run schema
psql -U postgres -d cropsense_db -f schema.sql

# If you created a user:
psql -U cropsense_user -d cropsense_db -f schema.sql
```

### Step 5: Import Seed Data

```bash
# Import crop nutrient requirements
psql -U postgres -d cropsense_db -f seed_data.sql
```

### Step 6: Verify Installation

```bash
# Connect to database
psql -U postgres -d cropsense_db

# Check tables
\dt

# Check crop data
SELECT COUNT(*) FROM crop_nutrient_requirements;

# Should show 22 crops
```

---

## 🗂️ Database Structure

### Tables Overview

| Table | Purpose | Records |
|-------|---------|---------|
| **farmers** | Farmer profiles | Variable |
| **fields** | Field information with soil properties | Variable |
| **crop_nutrient_requirements** | Crop nutrient uptake data | 22 crops |
| **crop_cycles** | Track growing seasons | Variable |
| **rainfall_events** | Rainfall during crop cycles | Variable |
| **nutrient_measurements** | Nutrient tracking over time | Variable |
| **soil_test_recommendations** | Alerts and recommendations | Variable |

### Key Relationships

```
farmers (1) ─────► (N) fields
fields (1) ──────► (N) crop_cycles
crop_cycles (1) ─► (N) rainfall_events
crop_cycles (1) ─► (N) nutrient_measurements
crop_cycles (1) ─► (N) soil_test_recommendations
crop_cycles (N) ─► (1) crop_nutrient_requirements
```

### Normalization Level

- **3NF (Third Normal Form)** - Optimized for data integrity
- **No redundancy** - Crop data stored once in reference table
- **Cascading deletes** - Removing farmer removes all related data

---

## 📥 Import/Export

### Export Database

```bash
# Full database dump
pg_dump -U postgres cropsense_db > cropsense_backup.sql

# Data only (no schema)
pg_dump -U postgres --data-only cropsense_db > cropsense_data.sql

# Specific table
pg_dump -U postgres -t crop_nutrient_requirements cropsense_db > crops.sql
```

### Import Database

```bash
# Full restore
psql -U postgres -d cropsense_db < cropsense_backup.sql

# Data only
psql -U postgres -d cropsense_db < cropsense_data.sql
```

### Copy to Another Server

```bash
# Dump and compress
pg_dump -U postgres cropsense_db | gzip > cropsense.sql.gz

# Transfer to another server (scp, rsync, etc.)

# Restore on new server
gunzip < cropsense.sql.gz | psql -U postgres cropsense_db
```

---

## 🔌 Connection Setup

### Python Connection (psycopg2)

Create `.env` file:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cropsense_db
DB_USER=postgres
DB_PASSWORD=your_password
```

Python code:

```python
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# Connection parameters
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'cropsense_db'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD')
)

# Use dictionary cursor for easier data handling
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Example query
cursor.execute("SELECT * FROM crop_nutrient_requirements LIMIT 5")
crops = cursor.fetchall()

for crop in crops:
    print(f"{crop['crop_name']}: N={crop['n_uptake_kg_ha']}")

cursor.close()
conn.close()
```

### Using SQLAlchemy (ORM)

```python
from sqlalchemy import create_engine
import os

# Create engine
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)

# Test connection
with engine.connect() as conn:
    result = conn.execute("SELECT COUNT(*) FROM crop_nutrient_requirements")
    print(f"Total crops: {result.scalar()}")
```

---

## ✅ Verification

### Check Installation

Run these queries to verify everything is set up correctly:

```sql
-- 1. Check all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Expected: 7 tables


-- 2. Verify crop data
SELECT 
    COUNT(*) as total_crops,
    MIN(cycle_days) as shortest_cycle,
    MAX(cycle_days) as longest_cycle,
    ROUND(AVG(n_uptake_kg_ha), 2) as avg_n_uptake
FROM crop_nutrient_requirements;

-- Expected: 22 crops


-- 3. Check views
SELECT table_name 
FROM information_schema.views 
WHERE table_schema = 'public';

-- Expected: active_crop_cycles, nutrient_status_summary


-- 4. Test foreign keys
SELECT
    tc.table_name, 
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';

-- Should show all relationships


-- 5. Sample data check
SELECT * FROM farmers;
SELECT * FROM fields;

-- Should show sample farmer and field
```

### Test Crop Data

```sql
-- High nitrogen crops
SELECT crop_name, n_uptake_kg_ha 
FROM crop_nutrient_requirements 
ORDER BY n_uptake_kg_ha DESC 
LIMIT 5;

-- Fast growing crops
SELECT crop_name, cycle_days 
FROM crop_nutrient_requirements 
ORDER BY cycle_days ASC 
LIMIT 5;

-- High potassium crops (fruits)
SELECT crop_name, k_uptake_kg_ha 
FROM crop_nutrient_requirements 
ORDER BY k_uptake_kg_ha DESC 
LIMIT 5;
```

---

## 🔍 Common Issues

### Issue 1: Permission Denied

```bash
# Fix: Grant permissions
sudo -u postgres psql
GRANT ALL PRIVILEGES ON DATABASE cropsense_db TO your_username;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_username;
```

### Issue 2: Database Already Exists

```bash
# Drop and recreate
sudo -u postgres psql
DROP DATABASE cropsense_db;
CREATE DATABASE cropsense_db;
\q
# Then re-run setup
```

### Issue 3: Cannot Connect

```bash
# Check PostgreSQL is running
sudo service postgresql status

# Check port
sudo netstat -plnt | grep 5432

# Check pg_hba.conf for authentication settings
sudo nano /etc/postgresql/[version]/main/pg_hba.conf
```

### Issue 4: psycopg2 Installation Error

```bash
# Install development headers
sudo apt-get install libpq-dev python3-dev

# Then reinstall
pip install psycopg2-binary
```

---

## 📊 Database Statistics

After setup, you should have:

- **7 tables** (normalized structure)
- **2 views** (for easy querying)
- **22 crop records** (all supported crops)
- **2 sample farmers** (for testing)
- **2 sample fields** (for testing)
- **4 triggers** (auto-update timestamps)
- **1 stored function** (calculate nutrients)

---

## 🔐 Security Recommendations

### Production Setup

1. **Create dedicated user** (don't use 'postgres')
   ```sql
   CREATE USER cropsense_app WITH PASSWORD 'strong_random_password';
   GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO cropsense_app;
   ```

2. **Use environment variables** (never commit passwords)
   ```bash
   # .env file (add to .gitignore!)
   DB_PASSWORD=your_secure_password
   ```

3. **Enable SSL** for remote connections

4. **Regular backups**
   ```bash
   # Automated daily backup
   pg_dump cropsense_db > /backups/cropsense_$(date +%Y%m%d).sql
   ```

5. **Restrict network access** (pg_hba.conf)

---

## 📚 Next Steps

After database setup:

1. **Configure Flask app** to connect to database
2. **Create database models** (SQLAlchemy ORM)
3. **Build API endpoints** for CRUD operations
4. **Test with sample data**
5. **Integrate with RINDM model**

---

## 🆘 Support

### Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- psycopg2 Documentation: https://www.psycopg.org/docs/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/

### Getting Help

1. Check error logs: `/var/log/postgresql/`
2. Run verification queries above
3. Check connection parameters in `.env`
4. Verify PostgreSQL is running

---

**Setup Complete! 🎉**

Your CropSense database is ready for use.
