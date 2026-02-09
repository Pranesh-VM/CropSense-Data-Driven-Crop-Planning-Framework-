"""
RINDM Cycle Manager

Manages the complete RINDM cycle workflow:
1. Start new cycle with crop selection
2. Monitor weather continuously
3. Calculate nutrient depletion from rainfall
4. Track nutrients in real-time
5. Check thresholds and generate recommendations
6. Complete cycle and suggest next crop
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import time

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.rindm import RainfallNutrientDepletionModel
from src.utils.crop_nutrient_database import (
    get_crop_nutrient_uptake,
    check_nutrient_status,
    calculate_remaining_nutrients
)
from src.utils.weather_fetcher import WeatherAPIFetcher
from database.db_utils import DatabaseManager


class RINDMCycleManager:
    """
    Manages RINDM cycles with real-time nutrient tracking.
    """
    
    def __init__(self, db_manager: DatabaseManager = None):
        """Initialize cycle manager."""
        self.db = db_manager or DatabaseManager()
        self.rindm = RainfallNutrientDepletionModel()
        self.weather = WeatherAPIFetcher()
        
        # Thresholds for stopping cycles
        self.CRITICAL_THRESHOLDS = {
            'N': 30,
            'P': 10,
            'K': 40
        }
    
    def start_new_cycle(
        self,
        farmer_id: int,
        field_id: int,
        selected_crop: str,
        initial_n: float,
        initial_p: float,
        initial_k: float,
        initial_ph: float,
        soil_type: str,
        recommendation_id: int = None
    ) -> Dict:
        """
        Start a new RINDM crop cycle.
        
        Args:
            farmer_id: Farmer ID
            field_id: Field ID
            selected_crop: Chosen crop name
            initial_n, initial_p, initial_k: Initial nutrient levels
            initial_ph: Soil pH
            soil_type: sandy, loamy, or clay
            recommendation_id: ID of the recommendation that led to this cycle
            
        Returns:
            Dictionary with cycle info
        """
        # Get crop data
        crop_data = get_crop_nutrient_uptake(selected_crop)
        if not crop_data:
            return {'success': False, 'error': f'Crop {selected_crop} not found'}
        
        # Get current cycle number for this farmer
        with self.db.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT COALESCE(MAX(cycle_number), 0) + 1 as next_cycle
                FROM crop_cycles
                WHERE farmer_id = %s
            """, (farmer_id,))
            cycle_number = cursor.fetchone()['next_cycle']
        
        # Calculate expected end date
        start_date = date.today()
        expected_end_date = start_date + timedelta(days=crop_data['cycle_days'])
        
        # Create crop cycle
        with self.db.get_connection() as (conn, cursor):
            cursor.execute("""
                INSERT INTO crop_cycles (
                    farmer_id, field_id, cycle_number, crop_name,
                    start_date, expected_end_date, status,
                    initial_n_kg_ha, initial_p_kg_ha, initial_k_kg_ha, initial_ph,
                    current_n_kg_ha, current_p_kg_ha, current_k_kg_ha,
                    soil_type, soil_ph,
                    total_crop_uptake_n, total_crop_uptake_p, total_crop_uptake_k,
                    last_weather_check
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s, 'active',
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    CURRENT_TIMESTAMP
                )
                RETURNING cycle_id
            """, (
                farmer_id, field_id, cycle_number, selected_crop,
                start_date, expected_end_date,
                initial_n, initial_p, initial_k, initial_ph,
                initial_n, initial_p, initial_k,  # current = initial at start
                soil_type, initial_ph,
                crop_data['N_uptake_kg_ha'], crop_data['P_uptake_kg_ha'], crop_data['K_uptake_kg_ha']
            ))
            
            cycle_id = cursor.fetchone()['cycle_id']
            
            # Update recommendation if provided
            if recommendation_id:
                cursor.execute("""
                    UPDATE cycle_recommendations
                    SET selected_crop = %s, selected_at = CURRENT_TIMESTAMP
                    WHERE recommendation_id = %s
                """, (selected_crop, recommendation_id))
            
            # Record initial measurement
            cursor.execute("""
                INSERT INTO nutrient_measurements (
                    cycle_id, measurement_type, n_kg_ha, p_kg_ha, k_kg_ha,
                    below_threshold, notes
                )
                VALUES (%s, 'cycle_start', %s, %s, %s, FALSE, 'Cycle started')
            """, (cycle_id, initial_n, initial_p, initial_k))
        
        return {
            'success': True,
            'cycle_id': cycle_id,
            'cycle_number': cycle_number,
            'crop': selected_crop,
            'start_date': str(start_date),
            'expected_end_date': str(expected_end_date),
            'duration_days': crop_data['cycle_days'],
            'current_nutrients': {
                'N': initial_n,
                'P': initial_p,
                'K': initial_k
            },
            'crop_requirements': {
                'N': crop_data['N_uptake_kg_ha'],
                'P': crop_data['P_uptake_kg_ha'],
                'K': crop_data['K_uptake_kg_ha']
            }
        }
    
    def check_and_process_rainfall(self, cycle_id: int) -> Dict:
        """
        Check weather API for rainfall and process if detected.
        
        This should be called periodically (e.g., every hour) for active cycles.
        
        Args:
            cycle_id: Active cycle ID
            
        Returns:
            Dictionary with rainfall status and nutrient updates
        """
        # Get cycle info
        with self.db.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT 
                    cc.*,
                    f.latitude, f.longitude
                FROM crop_cycles cc
                JOIN fields f ON cc.field_id = f.field_id
                WHERE cc.cycle_id = %s AND cc.status = 'active'
            """, (cycle_id,))
            
            cycle = cursor.fetchone()
            if not cycle:
                return {'success': False, 'error': 'Cycle not found or not active'}
            
            cycle = dict(cycle)
        
        # Get current weather
        weather_data = self.weather.get_current_weather(
            cycle['latitude'],
            cycle['longitude']
        )
        
        if not weather_data:
            return {'success': False, 'error': 'Could not fetch weather data'}
        
        # Check for rainfall
        rainfall_mm = weather_data.get('rainfall', 0)
        
        if rainfall_mm <= 0:
            # No rainfall, just update check time
            with self.db.get_connection() as (conn, cursor):
                cursor.execute("""
                    UPDATE crop_cycles 
                    SET last_weather_check = CURRENT_TIMESTAMP
                    WHERE cycle_id = %s
                """, (cycle_id,))
            
            return {
                'success': True,
                'rainfall_detected': False,
                'message': 'No rainfall detected'
            }
        
        # Rainfall detected! Process it
        return self.process_rainfall_event(
            cycle_id=cycle_id,
            rainfall_mm=rainfall_mm,
            current_n=cycle['current_n_kg_ha'],
            current_p=cycle['current_p_kg_ha'],
            current_k=cycle['current_k_kg_ha'],
            soil_type=cycle['soil_type']
        )
    
    def process_rainfall_event(
        self,
        cycle_id: int,
        rainfall_mm: float,
        current_n: float,
        current_p: float,
        current_k: float,
        soil_type: str,
        duration_hours: float = 2.0
    ) -> Dict:
        """
        Process a rainfall event and update nutrients.
        
        Args:
            cycle_id: Cycle ID
            rainfall_mm: Rainfall amount
            current_n, current_p, current_k: Current nutrient levels
            soil_type: Soil type
            duration_hours: Estimated duration (default 2 hours)
            
        Returns:
            Dictionary with updated nutrients
        """
        # Calculate nutrient loss using RINDM
        loss_result = self.rindm.calculate_nutrient_loss(
            rainfall_mm=rainfall_mm,
            duration_hours=duration_hours,
            N_current=current_n,
            P_current=current_p,
            K_current=current_k,
            soil_type=soil_type
        )
        
        # Calculate new nutrient levels
        new_n = loss_result['N_remaining']
        new_p = loss_result['P_remaining']
        new_k = loss_result['K_remaining']
        
        # Check status
        status = check_nutrient_status(new_n, new_p, new_k)
        
        # Update database
        with self.db.get_connection() as (conn, cursor):
            # Record rainfall event
            cursor.execute("""
                INSERT INTO rainfall_events (
                    cycle_id, event_start, rainfall_mm, duration_hours,
                    intensity_mm_per_hour,
                    n_before_event, p_before_event, k_before_event,
                    nutrient_loss_n, nutrient_loss_p, nutrient_loss_k,
                    n_after_event, p_after_event, k_after_event,
                    processed, processed_at
                )
                VALUES (
                    %s, CURRENT_TIMESTAMP, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    TRUE, CURRENT_TIMESTAMP
                )
                RETURNING event_id
            """, (
                cycle_id, rainfall_mm, duration_hours,
                rainfall_mm / duration_hours,
                current_n, current_p, current_k,
                loss_result['N_loss'], loss_result['P_loss'], loss_result['K_loss'],
                new_n, new_p, new_k
            ))
            
            event_id = cursor.fetchone()['event_id']
            
            # Update cycle with new nutrient levels
            cursor.execute("""
                UPDATE crop_cycles
                SET current_n_kg_ha = %s,
                    current_p_kg_ha = %s,
                    current_k_kg_ha = %s,
                    total_rainfall_loss_n = COALESCE(total_rainfall_loss_n, 0) + %s,
                    total_rainfall_loss_p = COALESCE(total_rainfall_loss_p, 0) + %s,
                    total_rainfall_loss_k = COALESCE(total_rainfall_loss_k, 0) + %s,
                    rainfall_event_count = COALESCE(rainfall_event_count, 0) + 1,
                    last_weather_check = CURRENT_TIMESTAMP
                WHERE cycle_id = %s
            """, (
                new_n, new_p, new_k,
                loss_result['N_loss'], loss_result['P_loss'], loss_result['K_loss'],
                cycle_id
            ))
            
            # Record measurement
            cursor.execute("""
                INSERT INTO nutrient_measurements (
                    cycle_id, measurement_type, n_kg_ha, p_kg_ha, k_kg_ha,
                    below_threshold, notes
                )
                VALUES (
                    %s, 'rainfall_update', %s, %s, %s,
                    %s,
                    %s
                )
            """, (
                cycle_id, new_n, new_p, new_k,
                status['needs_soil_test'],
                f'Rainfall: {rainfall_mm}mm, Losses: N={loss_result["N_loss"]}, P={loss_result["P_loss"]}, K={loss_result["K_loss"]}'
            ))
            
            # Create warning if threshold reached
            if status['needs_soil_test']:
                cursor.execute("""
                    SELECT farmer_id FROM crop_cycles WHERE cycle_id = %s
                """, (cycle_id,))
                farmer_id = cursor.fetchone()['farmer_id']
                
                cursor.execute("""
                    INSERT INTO soil_test_recommendations (
                        cycle_id, farmer_id, reason,
                        current_n_kg_ha, current_p_kg_ha, current_k_kg_ha,
                        message, status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
                """, (
                    cycle_id, farmer_id, 'low_nutrients',
                    new_n, new_p, new_k,
                    status['soil_test_message']
                ))
        
        return {
            'success': True,
            'rainfall_detected': True,
            'rainfall_mm': rainfall_mm,
            'event_id': event_id,
            'nutrient_loss': {
                'N': loss_result['N_loss'],
                'P': loss_result['P_loss'],
                'K': loss_result['K_loss']
            },
            'updated_nutrients': {
                'N': new_n,
                'P': new_p,
                'K': new_k
            },
            'status': status,
            'warning': status['needs_soil_test'],
            'message': status['soil_test_message'] if status['needs_soil_test'] else 'Nutrients updated'
        }
    
    def complete_cycle(self, cycle_id: int) -> Dict:
        """
        Complete a cycle at harvest and calculate final nutrients.
        
        Args:
            cycle_id: Cycle ID to complete
            
        Returns:
            Dictionary with final nutrients and next crop recommendations
        """
        # Get cycle info
        with self.db.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT * FROM crop_cycles WHERE cycle_id = %s
            """, (cycle_id,))
            
            cycle = cursor.fetchone()
            if not cycle:
                return {'success': False, 'error': 'Cycle not found'}
            
            cycle = dict(cycle)
        
        # Calculate final nutrients after crop uptake
        final_n = max(0, cycle['current_n_kg_ha'] - cycle['total_crop_uptake_n'])
        final_p = max(0, cycle['current_p_kg_ha'] - cycle['total_crop_uptake_p'])
        final_k = max(0, cycle['current_k_kg_ha'] - cycle['total_crop_uptake_k'])
        
        # Check if below threshold
        below_threshold = (
            final_n < self.CRITICAL_THRESHOLDS['N'] or
            final_p < self.CRITICAL_THRESHOLDS['P'] or
            final_k < self.CRITICAL_THRESHOLDS['K']
        )
        
        # Update cycle
        with self.db.get_connection() as (conn, cursor):
            cursor.execute("""
                UPDATE crop_cycles
                SET status = 'completed',
                    actual_end_date = CURRENT_DATE,
                    final_n_kg_ha = %s,
                    final_p_kg_ha = %s,
                    final_k_kg_ha = %s
                WHERE cycle_id = %s
            """, (final_n, final_p, final_k, cycle_id))
            
            # Record final measurement
            cursor.execute("""
                INSERT INTO nutrient_measurements (
                    cycle_id, measurement_type, n_kg_ha, p_kg_ha, k_kg_ha,
                    below_threshold, notes
                )
                VALUES (%s, 'cycle_end', %s, %s, %s, %s, %s)
            """, (
                cycle_id, final_n, final_p, final_k, below_threshold,
                f'Cycle completed. Crop uptake: N={cycle["total_crop_uptake_n"]}, P={cycle["total_crop_uptake_p"]}, K={cycle["total_crop_uptake_k"]}'
            ))
        
        return {
            'success': True,
            'cycle_id': cycle_id,
            'completed': True,
            'final_nutrients': {
                'N': final_n,
                'P': final_p,
                'K': final_k
            },
            'depletion_summary': {
                'crop_uptake': {
                    'N': cycle['total_crop_uptake_n'],
                    'P': cycle['total_crop_uptake_p'],
                    'K': cycle['total_crop_uptake_k']
                },
                'rainfall_loss': {
                    'N': cycle['total_rainfall_loss_n'],
                    'P': cycle['total_rainfall_loss_p'],
                    'K': cycle['total_rainfall_loss_k']
                },
                'total_depletion': {
                    'N': cycle['initial_n_kg_ha'] - final_n,
                    'P': cycle['initial_p_kg_ha'] - final_p,
                    'K': cycle['initial_k_kg_ha'] - final_k
                }
            },
            'below_threshold': below_threshold,
            'can_continue': not below_threshold,
            'message': 'Nutrients below threshold - cycle must stop' if below_threshold else 'Cycle complete - ready for next crop'
        }
    
    def get_cycle_status(self, cycle_id: int) -> Dict:
        """Get current status of a cycle."""
        with self.db.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT 
                    cc.*,
                    cnr.cycle_days,
                    (CURRENT_DATE - cc.start_date) as days_elapsed,
                    (cc.expected_end_date - CURRENT_DATE) as days_remaining
                FROM crop_cycles cc
                JOIN crop_nutrient_requirements cnr ON cc.crop_name = cnr.crop_name
                WHERE cc.cycle_id = %s
            """, (cycle_id,))
            
            cycle = cursor.fetchone()
            if not cycle:
                return {'success': False, 'error': 'Cycle not found'}
            
            cycle = dict(cycle)
            
            # Check current status
            status = check_nutrient_status(
                cycle['current_n_kg_ha'],
                cycle['current_p_kg_ha'],
                cycle['current_k_kg_ha']
            )
            
            return {
                'success': True,
                'cycle_id': cycle_id,
                'status': cycle['status'],
                'crop': cycle['crop_name'],
                'cycle_number': cycle['cycle_number'],
                'progress': {
                    'days_elapsed': cycle['days_elapsed'],
                    'days_remaining': cycle['days_remaining'],
                    'total_days': cycle['cycle_days'],
                    'percent_complete': round((cycle['days_elapsed'] / cycle['cycle_days']) * 100, 1)
                },
                'current_nutrients': {
                    'N': cycle['current_n_kg_ha'],
                    'P': cycle['current_p_kg_ha'],
                    'K': cycle['current_k_kg_ha']
                },
                'nutrient_status': status,
                'rainfall_events': cycle['rainfall_event_count'],
                'last_weather_check': str(cycle['last_weather_check'])
            }


if __name__ == "__main__":
    """Test RINDM Cycle Manager."""
    print("=" * 80)
    print("RINDM Cycle Manager Test")
    print("=" * 80)
    
    # Note: This requires database to be set up
    print("\nThis module requires database connection.")
    print("Run the following to test:")
    print("  1. Setup database: python database/setup_database.py")
    print("  2. Start cycle via API: POST /api/rindm/start-cycle")
    print("  3. Monitor via API: GET /api/rindm/cycle-status/{cycle_id}")
    
    print("\n" + "=" * 80)
