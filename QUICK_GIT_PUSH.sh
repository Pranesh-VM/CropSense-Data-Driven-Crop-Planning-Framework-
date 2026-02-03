#!/bin/bash
# 🚀 QUICK GIT PUSH SCRIPT
# Copy and paste these commands in order

# ============================================================
# STEP 1: Initialize Git (run once)
# ============================================================
cd g:\sem-8\Project\implementation
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"

# ============================================================
# STEP 2: Stage all files
# ============================================================
git add .

# ============================================================
# STEP 3: Create first commit
# ============================================================
git commit -m "Initial commit: React frontend + ML backend + documentation

Added:
- React 18 frontend with Vite bundler
- Flask REST API with CORS
- 4 reusable React components
- Axios HTTP client
- Beautiful responsive UI with animations
- ML models (99.55% accuracy ensemble)
- Weather API integration
- Comprehensive documentation (2000+ lines)
- Backend/Frontend separation
- Production-ready configuration"

# ============================================================
# STEP 4: Create GitHub repository
# ============================================================
# Go to: https://github.com/new
# 1. Name: cropsense
# 2. Description: AI-powered crop recommendation system
# 3. Public/Private: Choose preference
# 4. Do NOT initialize with README
# 5. Click "Create repository"
# 6. Copy the HTTPS or SSH URL

# ============================================================
# STEP 5: Add remote repository
# ============================================================
# Replace with your actual GitHub URL
git remote add origin https://github.com/YOUR_USERNAME/cropsense.git

# ============================================================
# STEP 6: Push to GitHub
# ============================================================
git branch -M main
git push -u origin main

# ============================================================
# DONE! Your code is now on GitHub
# ============================================================
# View at: https://github.com/YOUR_USERNAME/cropsense

# ============================================================
# FUTURE COMMITS (after making changes)
# ============================================================
git add .
git commit -m "Your commit message"
git push
