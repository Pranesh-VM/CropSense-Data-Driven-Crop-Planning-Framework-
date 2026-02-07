"""
Database Utility Module for CropSense

Provides easy-to-use functions for database operations:
- Connection management
- CRUD operations for nutrients, crops, rainfall
- Threshold checking
- Nutrient calculations

Usage:
    from database.db_utils import DatabaseManager
    
    db = DatabaseManager()
    crop_cycle = db.start_crop_cycle(...)
    db.add_rainfall_event(...)
    status = db.check_nutrient_status(...)
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Dict, List, Optional, Tuple
import os
from dotenv import load_dotenv
from datetime import date, datetime

# Load environment variables
load_dotenv()


class DatabaseManager:
    """
    Manages all database operations for CropSense nutrient tracking.
    """
    
    def __init__(
        self,
        host: str = None,
        port: str = None,
        database: str = None,
        user: str = None,
        password: str = None
    ):
        """
        Initialize database connection parameters.
        
        Args:
            host, port, database, user, password: Connection parameters
            If not provided, reads from environment variables
        """
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or os.getenv('DB_PORT', '5432')
        self.database = database or os.getenv('DB_NAME', 'cropsense_db')
        self.user = user or os.getenv('DB_USER', 'postgres')
        self.password = password or os.getenv('DB_PASSWORD', '')
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        Automatically handles connection and cursor cleanup.
        
        Usage:
            with db.get_connection() as (conn, cursor):
                cursor.execute("SELECT ...")
        """
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            yield conn, cursor
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    # =========================================================================
    # FARMER OPERATIONS
    # =========================================================================
    
    def create_farmer(
        self,
        farmer_id: str,
        name: str,
        phone: str = None,
        email: str = None,
        location: str = None,
        latitude: float = None,
        longitude: float = None
    ) -> Dict:
        """Create a new farmer profile."""
        with self.get_connection() as (conn, cursor):
            cursor.execute("""
                INSERT INTO farmers (farmer_id, name, phone, email, location, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (farmer_id, name, phone, email, location, latitude, longitude))
            return dict(cursor.fetchone())
    
    def get_farmer(self, farmer_id: str) -> Optional[Dict]:
        """Get farmer by ID."""
        with self.get_connection() as (conn, cursor):
            cursor.execute("SELECT * FROM farmers WHERE farmer_id = %s", (farmer_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
    
    # =========================================================================
    # FIELD OPERATIONS
    # =========================================================================
    
    def create_field(
        self,
        farmer_id: str,
        field_name: str,
        area_hectares: float,
        soil_type: str = None,
        soil_ph: float = None,
        **kwargs
    ) -> Dict:
        """Create a new field."""
        with self.get_connection() as (conn, cursor):
            cursor.execute("""
                INSERT INTO fields (
                    farmer_id, field_name, area_hectares, soil_type, soil_ph,
                    sand_percentage, silt_percentage, clay_percentage,
                    latitude, longitude, slope_degrees, drainage_quality
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                farmer_id, field_name, area_hectares, soil_type, soil_ph,
                kwargs.get('sand_pct'), kwargs.get('silt_pct'), kwargs.get('clay_pct'),
                kwargs.get('latitude'), kwargs.get('longitude'),
                kwargs.get('slope_degrees', 3.0),
                kwargs.get('drainage_quality')
            ))
            return dict(cursor.fetchone())
    
    def get_field(self, field_id: int) -> Optional[Dict]:
        """Get field by ID."""
        with self.get_connection() as (conn, cursor):
            cursor.execute("SELECT * FROM fields WHERE field_id = %s", (field_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
    
    # =========================================================================
    # CROP CYCLE OPERATIONS
    # =========================================================================
    
    def start_crop_cycle(
        self,
        field_id: int,
        crop_name: str,
        planting_date: date,
        initial_n: float,
        initial_p: float,
        initial_k: float,
        expected_harvest_date: date = None
    ) -> Dict:
        """
        Start a new crop growing cycle.
        
        Returns:
            Dictionary with cycle_id and cycle details
        """
        with self.get_connection() as (conn, cursor):
            cursor.execute("""
                INSERT INTO crop_cycles (
                    field_id, crop_name, planting_date, expected_harvest_date,
                    initial_n_kg_ha, initial_p_kg_ha, initial_k_kg_ha,
                    cycle_status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'active')
                RETURNING *
            """, (
                field_id, crop_name, planting_date, expected_harvest_date,
                initial_n, initial_p, initial_k
            ))
            return dict(cursor.fetchone())
    
    def get_active_crop_cycle(self, field_id: int) -> Optional[Dict]:
        """Get active crop cycle for a field."""
        with self.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT * FROM crop_cycles 
                WHERE field_id = %s AND cycle_status = 'active'
                ORDER BY planting_date DESC
                LIMIT 1
            """, (field_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def complete_crop_cycle(
        self,
        cycle_id: int,
        harvest_date: date,
        actual_yield: float = None
    ) -> Dict:
        """
        Complete a crop cycle at harvest.
        Calculates final nutrients automatically.
        """
        with self.get_connection() as (conn, cursor):
            # Calculate final nutrients
            cursor.execute("""
                SELECT * FROM calculate_final_nutrients(%s)
            """, (cycle_id,))
            result = cursor.fetchone()
            final_n, final_p, final_k = result['final_n'], result['final_p'], result['final_k']
            
            # Update crop cycle
            cursor.execute("""
                UPDATE crop_cycles 
                SET actual_harvest_date = %s,
                    cycle_status = 'completed',
                    final_n_kg_ha = %s,
                    final_p_kg_ha = %s,
                    final_k_kg_ha = %s,
                    actual_yield_tonnes_ha = %s
                WHERE cycle_id = %s
                RETURNING *
            """, (harvest_date, final_n, final_p, final_k, actual_yield, cycle_id))
            
            return dict(cursor.fetchone())
    
    # =========================================================================
    # RAINFALL EVENT OPERATIONS
    # =========================================================================
    
    def add_rainfall_event(
        self,
        cycle_id: int,
        event_date: date,
        rainfall_mm: float,
        duration_hours: float,
        n_loss: float,
        p_loss: float,
        k_loss: float,
        n_before: float,
        p_before: float,
        k_before: float,
        data_source: str = 'weather_api'
    ) -> Dict:
        """
        Record a rainfall event and its nutrient impact.
        
        Also updates the cumulative loss in crop_cycles table.
        """
        with self.get_connection() as (conn, cursor):
            # Insert rainfall event
            cursor.execute("""
                INSERT INTO rainfall_events (
                    cycle_id, event_date, rainfall_mm, duration_hours,
                    intensity_mm_per_hour, nutrient_loss_n, nutrient_loss_p, nutrient_loss_k,
                    n_before_event, p_before_event, k_before_event, data_source
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                cycle_id, event_date, rainfall_mm, duration_hours,
                rainfall_mm / duration_hours if duration_hours > 0 else 0,
                n_loss, p_loss, k_loss,
                n_before, p_before, k_before,
                data_source
            ))
            event = dict(cursor.fetchone())
            
            # Update cumulative losses in crop_cycles
            cursor.execute("""
                UPDATE crop_cycles 
                SET total_rainfall_loss_n = COALESCE(total_rainfall_loss_n, 0) + %s,
                    total_rainfall_loss_p = COALESCE(total_rainfall_loss_p, 0) + %s,
                    total_rainfall_loss_k = COALESCE(total_rainfall_loss_k, 0) + %s
                WHERE cycle_id = %s
            """, (n_loss, p_loss, k_loss, cycle_id))
            
            return event
    
    def get_rainfall_events(self, cycle_id: int) -> List[Dict]:
        """Get all rainfall events for a crop cycle."""
        with self.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT * FROM rainfall_events 
                WHERE cycle_id = %s 
                ORDER BY event_date
            """, (cycle_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    # =========================================================================
    # NUTRIENT MEASUREMENT OPERATIONS
    # =========================================================================
    
    def record_nutrient_measurement(
        self,
        cycle_id: int,
        measurement_date: date,
        n_kg_ha: float,
        p_kg_ha: float,
        k_kg_ha: float,
        measurement_type: str = 'calculated',
        measurement_source: str = 'calculated'
    ) -> Dict:
        """Record a nutrient measurement."""
        # Determine status
        n_status = self._get_nutrient_status(n_kg_ha, 'N')
        p_status = self._get_nutrient_status(p_kg_ha, 'P')
        k_status = self._get_nutrient_status(k_kg_ha, 'K')
        needs_test = any(s in ['CRITICAL', 'LOW'] for s in [n_status, p_status, k_status])
        
        with self.get_connection() as (conn, cursor):
            cursor.execute("""
                INSERT INTO nutrient_measurements (
                    cycle_id, measurement_date, measurement_type,
                    n_kg_ha, p_kg_ha, k_kg_ha,
                    n_status, p_status, k_status, needs_soil_test,
                    measurement_source
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                cycle_id, measurement_date, measurement_type,
                n_kg_ha, p_kg_ha, k_kg_ha,
                n_status, p_status, k_status, needs_test,
                measurement_source
            ))
            return dict(cursor.fetchone())
    
    def _get_nutrient_status(self, value: float, nutrient: str) -> str:
        """Determine status level for a nutrient."""
        thresholds = {
            'N': {'critical': 30, 'low': 60, 'moderate': 100},
            'P': {'critical': 10, 'low': 20, 'moderate': 30},
            'K': {'critical': 40, 'low': 80, 'moderate': 120}
        }
        t = thresholds[nutrient]
        
        if value < t['critical']:
            return 'CRITICAL'
        elif value < t['low']:
            return 'LOW'
        elif value < t['moderate']:
            return 'MODERATE'
        else:
            return 'GOOD'
    
    # =========================================================================
    # SOIL TEST RECOMMENDATIONS
    # =========================================================================
    
    def create_soil_test_recommendation(
        self,
        cycle_id: int,
        reason: str,
        current_n: float,
        current_p: float,
        current_k: float,
        message: str = None
    ) -> Dict:
        """Create a soil test recommendation alert."""
        critical_n = current_n < 30
        critical_p = current_p < 10
        critical_k = current_k < 40
        
        with self.get_connection() as (conn, cursor):
            cursor.execute("""
                INSERT INTO soil_test_recommendations (
                    cycle_id, recommendation_date, reason,
                    critical_n, critical_p, critical_k,
                    current_n_kg_ha, current_p_kg_ha, current_k_kg_ha,
                    message, recommendation_status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
                RETURNING *
            """, (
                cycle_id, date.today(), reason,
                critical_n, critical_p, critical_k,
                current_n, current_p, current_k,
                message
            ))
            return dict(cursor.fetchone())
    
    def get_pending_recommendations(self, cycle_id: int) -> List[Dict]:
        """Get pending soil test recommendations for a cycle."""
        with self.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT * FROM soil_test_recommendations 
                WHERE cycle_id = %s AND recommendation_status = 'pending'
                ORDER BY recommendation_date DESC
            """, (cycle_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    # =========================================================================
    # CROP REQUIREMENTS
    # =========================================================================
    
    def get_crop_nutrient_requirement(self, crop_name: str) -> Optional[Dict]:
        """Get nutrient requirements for a crop."""
        with self.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT * FROM crop_nutrient_requirements 
                WHERE crop_name = %s
            """, (crop_name.lower(),))
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def get_all_crops(self) -> List[Dict]:
        """Get all available crops."""
        with self.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT * FROM crop_nutrient_requirements 
                ORDER BY crop_name
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    # =========================================================================
    # UTILITY FUNCTIONS
    # =========================================================================
    
    def get_current_nutrients(self, cycle_id: int) -> Dict[str, float]:
        """
        Calculate current nutrient levels for an active crop cycle.
        
        Returns:
            {'N': float, 'P': float, 'K': float}
        """
        with self.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT 
                    initial_n_kg_ha,
                    initial_p_kg_ha,
                    initial_k_kg_ha,
                    COALESCE(total_rainfall_loss_n, 0) AS rainfall_loss_n,
                    COALESCE(total_rainfall_loss_p, 0) AS rainfall_loss_p,
                    COALESCE(total_rainfall_loss_k, 0) AS rainfall_loss_k,
                    COALESCE(fertilizer_applied_n, 0) AS fertilizer_n,
                    COALESCE(fertilizer_applied_p, 0) AS fertilizer_p,
                    COALESCE(fertilizer_applied_k, 0) AS fertilizer_k
                FROM crop_cycles
                WHERE cycle_id = %s
            """, (cycle_id,))
            row = cursor.fetchone()
            
            if not row:
                raise ValueError(f"Crop cycle {cycle_id} not found")
            
            return {
                'N': row['initial_n_kg_ha'] + row['fertilizer_n'] - row['rainfall_loss_n'],
                'P': row['initial_p_kg_ha'] + row['fertilizer_p'] - row['rainfall_loss_p'],
                'K': row['initial_k_kg_ha'] + row['fertilizer_k'] - row['rainfall_loss_k']
            }
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_connection() as (conn, cursor):
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False


# Convenience functions for quick operations
def quick_connect() -> DatabaseManager:
    """Quick database connection with default parameters."""
    return DatabaseManager()


if __name__ == "__main__":
    """Test database operations."""
    print("=" * 80)
    print("Database Utility Test")
    print("=" * 80)
    
    db = DatabaseManager()
    
    # Test connection
    print("\n1. Testing connection...")
    if db.test_connection():
        print("✓ Connection successful")
    else:
        print("✗ Connection failed")
        exit(1)
    
    # Test get all crops
    print("\n2. Getting all crops...")
    crops = db.get_all_crops()
    print(f"✓ Found {len(crops)} crops")
    print(f"  Sample: {crops[0]['crop_name']} (N={crops[0]['n_uptake_kg_ha']})")
    
    # Test get specific crop
    print("\n3. Getting rice nutrient requirements...")
    rice = db.get_crop_nutrient_requirement('rice')
    if rice:
        print(f"✓ Rice: N={rice['n_uptake_kg_ha']}, P={rice['p_uptake_kg_ha']}, K={rice['k_uptake_kg_ha']} kg/ha")
    
    print("\n" + "=" * 80)
    print("Database Utility Tests Complete ✓")
    print("=" * 80)
