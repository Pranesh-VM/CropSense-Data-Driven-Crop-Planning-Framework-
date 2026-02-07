#!/usr/bin/env python3
"""
CropSense Database Setup Script

Automated setup for PostgreSQL database:
1. Creates database
2. Imports schema
3. Imports seed data
4. Verifies installation

Usage:
    python setup_database.py
    
    With custom parameters:
    python setup_database.py --host localhost --user postgres --password mypass
"""

import subprocess
import sys
import os
import argparse
import shutil
import platform
from pathlib import Path


class DatabaseSetup:
    """Automated database setup for CropSense."""
    
    def __init__(self, host='localhost', port='5432', user='postgres', password='', db_name='cropsense_db'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name
        self.script_dir = Path(__file__).parent
    
    def run_command(self, command, description, ignore_error=False):
        """Run a shell command and handle errors."""
        print(f"\n{'='*80}")
        print(f"{description}")
        print(f"{'='*80}")
        
        try:
            # Set password environment variable if provided
            env = os.environ.copy()
            if self.password:
                env['PGPASSWORD'] = self.password
            
            result = subprocess.run(
                command,
                shell=True,
                check=not ignore_error,
                capture_output=True,
                text=True,
                env=env
            )
            
            if result.stdout:
                print(result.stdout)
            
            if result.returncode == 0:
                print(f"✓ {description} completed successfully")
                return True
            else:
                if not ignore_error:
                    print(f"✗ {description} failed")
                    if result.stderr:
                        print(f"Error: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"✗ {description} failed")
            print(f"Error: {e}")
            if not ignore_error:
                sys.exit(1)
            return False
    
    def check_postgresql(self):
        """Check if PostgreSQL is installed and running (cross-platform compatible)."""
        print("\n" + "="*80)
        print("STEP 1: Checking PostgreSQL Installation")
        print("="*80)
        
        # Check if psql is available - Cross-platform compatible
        psql_path = shutil.which('psql')
        if not psql_path:
            print("✗ PostgreSQL (psql) not found in PATH")
            print("\nPlease install PostgreSQL:")
            if platform.system() == 'Windows':
                print("  Windows: https://www.postgresql.org/download/windows/")
            elif platform.system() == 'Darwin':
                print("  macOS: brew install postgresql")
            else:
                print("  Linux (Ubuntu/Debian): sudo apt-get install postgresql")
                print("  Linux (Fedora/RHEL): sudo dnf install postgresql")
            sys.exit(1)
        
        print(f"✓ PostgreSQL is installed at: {psql_path}")
        
        # Check if server is running (optional check)
        result = subprocess.run(
            f"psql -h {self.host} -p {self.port} -U {self.user} -c 'SELECT 1' ",
            shell=True,
            capture_output=True,
            text=True,
            env={**os.environ.copy(), 'PGPASSWORD': self.password}
        )
        if result.returncode == 0:
            print(f"✓ PostgreSQL server is running on {self.host}:{self.port}")
        else:
            print(f"⚠ PostgreSQL server may not be running on {self.host}:{self.port}")
            if platform.system() == 'Windows':
                print("  Start it in Services (services.msc) or using:\n  net start postgresql-x64-xxx")
            else:
                print("  Start it with: sudo service postgresql start")
    
    def create_database(self):
        """Create the database."""
        print("\n" + "="*80)
        print("STEP 2: Creating Database")
        print("="*80)
        
        # Drop if exists (optional - comment out for safety)
        drop_cmd = f'psql -h {self.host} -p {self.port} -U {self.user} -c "DROP DATABASE IF EXISTS {self.db_name}"'
        self.run_command(drop_cmd, f"Dropping existing database '{self.db_name}' if exists", ignore_error=True)
        
        # Create database
        create_cmd = f'psql -h {self.host} -p {self.port} -U {self.user} -c "CREATE DATABASE {self.db_name}"'
        return self.run_command(create_cmd, f"Creating database '{self.db_name}'")
    
    def import_schema(self):
        """Import database schema."""
        print("\n" + "="*80)
        print("STEP 3: Importing Database Schema")
        print("="*80)
        
        schema_file = self.script_dir / 'schema.sql'
        
        if not schema_file.exists():
            print(f"✗ Schema file not found: {schema_file}")
            print("⚠ Continuing anyway - you can import schema manually later")
            return True  # Don't fail, just warn
        
        # On Windows, use double quotes instead of single quotes
        if platform.system() == 'Windows':
            cmd = f'psql -h {self.host} -p {self.port} -U {self.user} -d {self.db_name} -f "{schema_file}"'
        else:
            cmd = f'psql -h {self.host} -p {self.port} -U {self.user} -d {self.db_name} -f {schema_file}'
        
        return self.run_command(cmd, "Importing schema (tables, views, functions)")
    
    def import_seed_data(self):
        """Import seed data (crop nutrient requirements)."""
        print("\n" + "="*80)
        print("STEP 4: Importing Seed Data (22 Crops)")
        print("="*80)
        
        seed_file = self.script_dir / 'seed_data.sql'
        
        if not seed_file.exists():
            print(f"✗ Seed data file not found: {seed_file}")
            print("⚠ Continuing anyway - you can import data manually later")
            return True  # Don't fail, just warn
        
        # On Windows, use double quotes instead of single quotes
        if platform.system() == 'Windows':
            cmd = f'psql -h {self.host} -p {self.port} -U {self.user} -d {self.db_name} -f "{seed_file}"'
        else:
            cmd = f'psql -h {self.host} -p {self.port} -U {self.user} -d {self.db_name} -f {seed_file}'
        
        return self.run_command(cmd, "Importing crop nutrient data")
    
    def verify_installation(self):
        """Verify database setup."""
        print("\n" + "="*80)
        print("STEP 5: Verifying Installation")
        print("="*80)
        
        # Check tables
        cmd = f'psql -h {self.host} -p {self.port} -U {self.user} -d {self.db_name} -c "\\\\dt"'
        self.run_command(cmd, "Checking tables", ignore_error=True)
        
        # Count crops (ignore if table doesn't exist yet)
        cmd = f'psql -h {self.host} -p {self.port} -U {self.user} -d {self.db_name} -c "SELECT COUNT(*) as total_crops FROM crop_nutrient_requirements;"'
        self.run_command(cmd, "Counting crops in database", ignore_error=True)
        
        # Show sample crops (ignore if table doesn't exist yet)
        cmd = f'psql -h {self.host} -p {self.port} -U {self.user} -d {self.db_name} -c "SELECT crop_name, n_uptake_kg_ha, p_uptake_kg_ha, k_uptake_kg_ha FROM crop_nutrient_requirements LIMIT 5;"'
        self.run_command(cmd, "Sample crops", ignore_error=True)
    
    def create_env_file(self):
        """Create .env file template."""
        print("\n" + "="*80)
        print("STEP 6: Creating .env File Template")
        print("="*80)
        
        env_file = self.script_dir.parent / '.env'
        
        if env_file.exists():
            print(f"⚠ .env file already exists at {env_file}")
            return
        
        env_content = f"""# CropSense Database Configuration
# Generated by setup_database.py

# Database Connection
DB_HOST={self.host}
DB_PORT={self.port}
DB_NAME={self.db_name}
DB_USER={self.user}
DB_PASSWORD={self.password if self.password else 'your_password_here'}

# API Keys (add your keys)
OPENWEATHERMAP_API_KEY=your_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_PORT=5000
"""
        
        try:
            with open(env_file, 'w') as f:
                f.write(env_content)
            print(f"✓ Created .env file at {env_file}")
            print("⚠ Remember to add your actual passwords and API keys!")
        except Exception as e:
            print(f"✗ Failed to create .env file: {e}")
    
    def run_full_setup(self):
        """Run complete database setup."""
        print("\n" + "🚀" * 40)
        print("CropSense Database Setup")
        print("🚀" * 40)
        
        print(f"\nConfiguration:")
        print(f"  Host: {self.host}")
        print(f"  Port: {self.port}")
        print(f"  User: {self.user}")
        print(f"  Database: {self.db_name}")
        print(f"  OS: {platform.system()}")
        
        # Step 1: Check PostgreSQL
        self.check_postgresql()
        
        # Step 2: Create database
        if not self.create_database():
            print("\n✗ Database creation failed. Exiting.")
            sys.exit(1)
        
        # Step 3: Import schema
        if not self.import_schema():
            print("\n⚠ Schema import warning - continuing with setup")
        
        # Step 4: Import seed data
        if not self.import_seed_data():
            print("\n⚠ Seed data import warning - continuing with setup")
        
        # Step 5: Verify
        self.verify_installation()
        
        # Step 6: Create .env
        self.create_env_file()
        
        # Final message
        print("\n" + "🎉" * 40)
        print("DATABASE SETUP COMPLETE!")
        print("🎉" * 40)
        
        print("\n✅ Summary:")
        print(f"   • Database '{self.db_name}' created")
        print(f"   • Schema and seed data imported (if files exist)")
        print(f"   • Ready for use!")
        
        print("\n📚 Next Steps:")
        print("   1. Update .env file with your actual credentials")
        print("   2. Test connection: python database/db_utils.py")
        print("   3. Start Flask backend: python app.py")
        
        print("\n🔗 Connection String:")
        print(f"   postgresql://{self.user}@{self.host}:{self.port}/{self.db_name}")
        
        print("\n" + "="*80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='CropSense Database Setup')
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--port', default='5432', help='Database port')
    parser.add_argument('--user', default='postgres', help='Database user')
    parser.add_argument('--password', default='', help='Database password')
    parser.add_argument('--dbname', default='cropsense_db', help='Database name')
    
    args = parser.parse_args()
    
    # If no password provided, ask for it
    if not args.password:
        import getpass
        print(f"Connecting as user '{args.user}' to '{args.host}'")
        args.password = getpass.getpass(f"Enter password for {args.user} (press Enter for no password): ")
    
    setup = DatabaseSetup(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        db_name=args.dbname
    )
    
    setup.run_full_setup()


if __name__ == "__main__":
    main()