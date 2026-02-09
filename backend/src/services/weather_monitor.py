"""
Weather Monitor Background Service

Continuously monitors weather for all active RINDM cycles.
Checks for rainfall and processes nutrient depletion automatically.

Usage:
    # Start in background thread
    from src/services/weather_monitor import WeatherMonitor
    
    monitor = WeatherMonitor()
    monitor.start()  # Runs in background
    
    # Or run once manually
    monitor.check_all_active_cycles()
"""

import threading
import time
import schedule
from datetime import datetime
from typing import List, Dict
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.db_utils import DatabaseManager
from src.services.rindm_cycle_manager import RINDMCycleManager


class WeatherMonitor:
    """
    Background service to monitor weather for active cycles.
    """
    
    def __init__(self, check_interval_minutes: int = 60):
        """
        Initialize weather monitor.
        
        Args:
            check_interval_minutes: How often to check weather (default: 60 minutes)
        """
        self.db = DatabaseManager()
        self.cycle_manager = RINDMCycleManager(self.db)
        self.check_interval = check_interval_minutes
        self.is_running = False
        self.thread = None
    
    def get_active_cycles(self) -> List[Dict]:
        """
        Get all active cycles that need weather monitoring.
        
        Returns:
            List of active cycle dictionaries
        """
        with self.db.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT 
                    cc.cycle_id,
                    cc.farmer_id,
                    cc.crop_name,
                    cc.start_date,
                    cc.expected_end_date,
                    cc.current_n_kg_ha,
                    cc.current_p_kg_ha,
                    cc.current_k_kg_ha,
                    cc.last_weather_check,
                    f.latitude,
                    f.longitude
                FROM crop_cycles cc
                JOIN fields f ON cc.field_id = f.field_id
                WHERE cc.status = 'active'
                ORDER BY cc.last_weather_check ASC
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def check_all_active_cycles(self) -> Dict:
        """
        Check weather for all active cycles and process any rainfall.
        
        Returns:
            Summary of checks performed
        """
        start_time = datetime.now()
        active_cycles = self.get_active_cycles()
        
        if not active_cycles:
            return {
                'timestamp': str(start_time),
                'cycles_checked': 0,
                'rainfall_detected': 0,
                'warnings_generated': 0,
                'message': 'No active cycles to monitor'
            }
        
        print(f"\n[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] Checking {len(active_cycles)} active cycles...")
        
        rainfall_count = 0
        warning_count = 0
        results = []
        
        for cycle in active_cycles:
            try:
                # Check and process rainfall for this cycle
                result = self.cycle_manager.check_and_process_rainfall(cycle['cycle_id'])
                
                if result.get('rainfall_detected'):
                    rainfall_count += 1
                    print(f"  ✓ Cycle {cycle['cycle_id']} ({cycle['crop_name']}): "
                          f"Rainfall {result['rainfall_mm']}mm detected")
                    
                    if result.get('warning'):
                        warning_count += 1
                        print(f"    ⚠️  Warning: {result['message']}")
                
                results.append({
                    'cycle_id': cycle['cycle_id'],
                    'crop': cycle['crop_name'],
                    'rainfall_detected': result.get('rainfall_detected', False),
                    'warning': result.get('warning', False)
                })
                
            except Exception as e:
                print(f"  ✗ Error checking cycle {cycle['cycle_id']}: {e}")
                results.append({
                    'cycle_id': cycle['cycle_id'],
                    'error': str(e)
                })
        
        duration = (datetime.now() - start_time).total_seconds()
        
        summary = {
            'timestamp': str(start_time),
            'duration_seconds': round(duration, 2),
            'cycles_checked': len(active_cycles),
            'rainfall_detected': rainfall_count,
            'warnings_generated': warning_count,
            'results': results,
            'message': f'Checked {len(active_cycles)} cycles, {rainfall_count} rainfall events, {warning_count} warnings'
        }
        
        print(f"  Completed in {duration:.2f}s\n")
        
        return summary
    
    def check_and_complete_cycles(self) -> Dict:
        """
        Check if any active cycles have reached their end date and complete them.
        
        Returns:
            Summary of completed cycles
        """
        with self.db.get_connection() as (conn, cursor):
            # Find cycles that have reached end date
            cursor.execute("""
                SELECT cycle_id, crop_name, farmer_id, expected_end_date
                FROM crop_cycles
                WHERE status = 'active' 
                  AND expected_end_date <= CURRENT_DATE
            """)
            
            cycles_to_complete = [dict(row) for row in cursor.fetchall()]
        
        if not cycles_to_complete:
            return {
                'cycles_completed': 0,
                'message': 'No cycles ready to complete'
            }
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Completing {len(cycles_to_complete)} mature cycles...")
        
        completed = []
        for cycle in cycles_to_complete:
            try:
                result = self.cycle_manager.complete_cycle(cycle['cycle_id'])
                
                if result['success']:
                    print(f"  ✓ Completed cycle {cycle['cycle_id']} ({cycle['crop_name']})")
                    print(f"    Final nutrients: N={result['final_nutrients']['N']:.1f}, "
                          f"P={result['final_nutrients']['P']:.1f}, "
                          f"K={result['final_nutrients']['K']:.1f}")
                    
                    if result['below_threshold']:
                        print(f"    ⚠️  Nutrients below threshold - stopping cycles")
                    else:
                        print(f"    ✓ Can continue to next cycle")
                    
                    completed.append(result)
                
            except Exception as e:
                print(f"  ✗ Error completing cycle {cycle['cycle_id']}: {e}")
        
        return {
            'cycles_completed': len(completed),
            'completed_details': completed,
            'message': f'Completed {len(completed)} cycles'
        }
    
    def run_scheduled_checks(self):
        """
        Run scheduled weather checks in a loop.
        This method runs in a background thread.
        """
        print(f"\n{'='*80}")
        print(f"Weather Monitor Started")
        print(f"{'='*80}")
        print(f"Check interval: {self.check_interval} minutes")
        print(f"Monitoring all active RINDM cycles...")
        print(f"{'='*80}\n")
        
        # Schedule tasks
        schedule.every(self.check_interval).minutes.do(self.check_all_active_cycles)
        schedule.every(6).hours.do(self.check_and_complete_cycles)  # Check completion every 6 hours
        
        # Run immediately on start
        self.check_all_active_cycles()
        self.check_and_complete_cycles()
        
        # Keep running
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute if any jobs are due
        
        print(f"\n{'='*80}")
        print(f"Weather Monitor Stopped")
        print(f"{'='*80}\n")
    
    def start(self):
        """
        Start weather monitoring in a background thread.
        """
        if self.is_running:
            print("Weather monitor is already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self.run_scheduled_checks, daemon=True)
        self.thread.start()
        
        print(f"✓ Weather monitor started (background thread)")
    
    def stop(self):
        """
        Stop weather monitoring.
        """
        if not self.is_running:
            print("Weather monitor is not running")
            return
        
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        print(f"✓ Weather monitor stopped")
    
    def is_active(self) -> bool:
        """Check if monitor is running."""
        return self.is_running


# Global instance
_monitor_instance = None


def get_monitor_instance(check_interval_minutes: int = 60) -> WeatherMonitor:
    """
    Get or create the global weather monitor instance.
    
    Args:
        check_interval_minutes: Check interval (default: 60)
        
    Returns:
        WeatherMonitor instance
    """
    global _monitor_instance
    
    if _monitor_instance is None:
        _monitor_instance = WeatherMonitor(check_interval_minutes)
    
    return _monitor_instance


def start_monitor(check_interval_minutes: int = 60):
    """
    Start the global weather monitor.
    
    Args:
        check_interval_minutes: Check interval (default: 60)
    """
    monitor = get_monitor_instance(check_interval_minutes)
    monitor.start()
    return monitor


def stop_monitor():
    """Stop the global weather monitor."""
    global _monitor_instance
    
    if _monitor_instance:
        _monitor_instance.stop()


if __name__ == "__main__":
    """
    Run weather monitor as standalone service.
    
    Usage:
        python weather_monitor.py [interval_minutes]
    """
    import sys
    
    # Get interval from command line or use default
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    
    print(f"\n{'='*80}")
    print(f"CropSense Weather Monitor - Standalone Mode")
    print(f"{'='*80}\n")
    
    try:
        monitor = WeatherMonitor(check_interval_minutes=interval)
        monitor.start()
        
        print(f"\nMonitor running... Press Ctrl+C to stop\n")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n\nShutting down...")
        monitor.stop()
        print(f"Goodbye!\n")
