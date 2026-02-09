#!/bin/bash

# ============================================================================
# CropSense Database Setup Script
# Run this to recreate the database with the updated schema
# ============================================================================

echo "=========================================="
echo "CropSense Database Setup"
echo "=========================================="

# Configuration
DB_NAME="cropsense_db"
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_HOST="localhost"
DB_PORT="5432"

echo ""
echo "1. Dropping existing database (if exists)..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -tc "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "   ✓ Database dropped successfully"
else
    echo "   ⚠ Database not found (this is OK if fresh install)"
fi

echo ""
echo "2. Creating new database..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -tc "CREATE DATABASE $DB_NAME;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "   ✓ Database created successfully"
else
    echo "   ✗ Failed to create database"
    exit 1
fi

echo ""
echo "3. Importing schema..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f schema_v2.sql 2>/dev/null

if [ $? -eq 0 ]; then
    echo "   ✓ Schema imported successfully"
else
    echo "   ✗ Failed to import schema"
    exit 1
fi

echo ""
echo "4. Seeding initial data (optional)..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f seed_data.sql 2>/dev/null

if [ $? -eq 0 ]; then
    echo "   ✓ Seed data imported successfully"
else
    echo "   ⚠ Failed to import seed data (this is optional)"
fi

echo ""
echo "=========================================="
echo "✓ Database setup complete!"
echo "=========================================="
echo ""
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Host: $DB_HOST:$DB_PORT"
echo ""
