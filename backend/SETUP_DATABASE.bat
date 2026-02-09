@echo off
REM ============================================================================
REM CropSense Database Setup Script for Windows
REM Run this to recreate the database with the updated schema
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo CropSense Database Setup
echo ==========================================
echo.

REM Configuration
set DB_NAME=cropsense_db
set DB_USER=postgres
set DB_PASSWORD=postgres
set DB_HOST=localhost
set DB_PORT=5432
set PGPASSWORD=%DB_PASSWORD%

echo 1. Dropping existing database (if exists)...
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -tc "DROP DATABASE IF EXISTS %DB_NAME%;" >nul 2>&1

if %ERRORLEVEL% equ 0 (
    echo    ✓ Database dropped successfully
) else (
    echo    ⚠ Database not found (this is OK if fresh install^)
)

echo.
echo 2. Creating new database...
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -tc "CREATE DATABASE %DB_NAME%;" >nul 2>&1

if %ERRORLEVEL% equ 0 (
    echo    ✓ Database created successfully
) else (
    echo    ✗ Failed to create database
    pause
    exit /b 1
)

echo.
echo 3. Importing schema...
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f schema_v2.sql >nul 2>&1

if %ERRORLEVEL% equ 0 (
    echo    ✓ Schema imported successfully
) else (
    echo    ✗ Failed to import schema
    pause
    exit /b 1
)

echo.
echo 4. Seeding initial data (optional^)...
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f seed_data.sql >nul 2>&1

if %ERRORLEVEL% equ 0 (
    echo    ✓ Seed data imported successfully
) else (
    echo    ⚠ Failed to import seed data (this is optional^)
)

echo.
echo ==========================================
echo ✓ Database setup complete!
echo ==========================================
echo.
echo Database: %DB_NAME%
echo User: %DB_USER%
echo Host: %DB_HOST%:%DB_PORT%
echo.

pause
