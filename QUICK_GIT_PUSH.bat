@echo off
REM ============================================================
REM 🚀 QUICK GIT PUSH SCRIPT FOR WINDOWS
REM Copy and paste these commands in order in PowerShell/CMD
REM ============================================================

REM STEP 1: Navigate to project
cd g:\sem-8\Project\implementation

REM STEP 2: Initialize Git (run once)
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"

REM STEP 3: Stage all files
git add .

REM STEP 4: Create first commit
git commit -m "Initial commit: React frontend + ML backend + documentation"

REM STEP 5: (Manual step - do on GitHub)
REM Go to: https://github.com/new
REM 1. Name: cropsense
REM 2. Description: AI-powered crop recommendation system
REM 3. Choose Public/Private
REM 4. Do NOT initialize with README
REM 5. Click Create repository
REM 6. Copy the HTTPS URL

REM STEP 6: Add remote (replace with YOUR URL)
git remote add origin https://github.com/YOUR_USERNAME/cropsense.git

REM STEP 7: Push to GitHub
git branch -M main
git push -u origin main

echo.
echo ============================================================
echo ✅ COMPLETE! Your code is now on GitHub
echo ============================================================
echo View at: https://github.com/YOUR_USERNAME/cropsense
echo.
