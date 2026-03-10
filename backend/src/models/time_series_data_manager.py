"""
Time Series Data Manager for CropSense Phase 3

Data access layer for LSTM and Prophet models.
- Reads from database if data exists
- Generates synthetic training data using StateTransitionSimulator if empty
- Logs daily nutrient measurements to nutrient_timeseries_log table

Usage:
    mgr = TimeSeriesDataManager()
    
    # Get training data (auto-generates synthetic if DB empty)
    df = mgr.get_timeseries_for_training(farmer_id=5, days_back=365)
    
    # Get market prices for Prophet
    prices = mgr.get_market_price_history('rice', days_back=365)
    
    # Log daily measurement
    mgr.log_daily_nutrient(cycle_id=10, farmer_id=5, n=85.5, p=38.2, k=40.1, ...)
"""

import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np

# Import database manager (optional - works in standalone mode without DB)
try:
    from database.db_utils import DatabaseManager
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Import state transition simulator
from src.models.state_transition_simulator import (
    StateTransitionSimulator,
    EnvironmentState,
    DEFAULT_MARKET_PRICES,
    SEASONS
)


class TimeSeriesDataManager:
    """
    Data access layer for LSTM and Prophet time-series models.
    
    Provides:
    1. get_timeseries_for_training() - Daily NPK/weather data for LSTM
    2. get_market_price_history() - Crop prices for Prophet market forecasting
    3. log_daily_nutrient() - Write daily logs to DB
    
    Falls back to synthetic data generation when DB is empty or unavailable.
    """
    
    def __init__(self, db_manager: Optional['DatabaseManager'] = None):
        """
        Initialize the data manager.
        
        Args:
            db_manager: Optional DatabaseManager instance. 
                        If None and DB_AVAILABLE, creates new instance.
                        If None and not DB_AVAILABLE, works in synthetic-only mode.
        """
        self.db = db_manager
        if self.db is None and DB_AVAILABLE:
            try:
                self.db = DatabaseManager()
            except Exception as e:
                print(f"⚠ Could not connect to database: {e}")
                self.db = None
        
        self.simulator = StateTransitionSimulator()
    
    # =========================================================================
    # TRAINING DATA FOR LSTM
    # =========================================================================
    
    def get_timeseries_for_training(
        self,
        farmer_id: Optional[int] = None,
        crop_name: Optional[str] = None,
        days_back: int = 365,
        use_synthetic_if_empty: bool = True
    ) -> pd.DataFrame:
        """
        Get time-series data for LSTM training.
        
        Column output: [log_date, n_kg_ha, p_kg_ha, k_kg_ha,
                        rainfall_mm, temperature_avg, humidity_avg]
        
        Args:
            farmer_id: Filter to one farmer (or None for all)
            crop_name: Filter to one crop type (or None for all)
            days_back: How many days of history to fetch
            use_synthetic_if_empty: Generate synthetic data if DB is empty
        
        Returns:
            DataFrame with columns suitable for LSTM training
        """
        df = pd.DataFrame()
        
        # Try to read from database first
        if self.db is not None:
            df = self._read_timeseries_from_db(farmer_id, crop_name, days_back)
        
        # If empty and synthetic fallback enabled, generate synthetic data
        if df.empty and use_synthetic_if_empty:
            print("ℹ No DB records found. Generating synthetic training data...")
            num_seasons = max(4, days_back // 90)  # ~90 days per season
            df = self._generate_synthetic_dataframe(num_seasons=num_seasons)
        
        return df
    
    def _read_timeseries_from_db(
        self,
        farmer_id: Optional[int],
        crop_name: Optional[str],
        days_back: int
    ) -> pd.DataFrame:
        """Read time-series data from nutrient_timeseries_log table."""
        if self.db is None:
            return pd.DataFrame()
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            query = """
                SELECT 
                    ntl.log_date,
                    ntl.n_kg_ha,
                    ntl.p_kg_ha,
                    ntl.k_kg_ha,
                    ntl.rainfall_mm,
                    ntl.temperature_avg,
                    ntl.humidity_avg,
                    ntl.days_into_cycle,
                    cc.crop_name
                FROM nutrient_timeseries_log ntl
                LEFT JOIN crop_cycles cc ON ntl.cycle_id = cc.cycle_id
                WHERE ntl.log_date >= %s
            """
            params = [cutoff_date]
            
            if farmer_id is not None:
                query += " AND ntl.farmer_id = %s"
                params.append(farmer_id)
            
            if crop_name is not None:
                query += " AND cc.crop_name = %s"
                params.append(crop_name.lower())
            
            query += " ORDER BY ntl.log_date ASC"
            
            with self.db.get_connection() as (conn, cursor):
                cursor.execute(query, params)
                rows = cursor.fetchall()
            
            if rows:
                df = pd.DataFrame(rows)
                return df
            
        except Exception as e:
            print(f"⚠ Error reading from DB: {e}")
        
        return pd.DataFrame()
    
    def _generate_synthetic_dataframe(self, num_seasons: int = 8) -> pd.DataFrame:
        """
        Generate synthetic LSTM training data using StateTransitionSimulator.
        
        Args:
            num_seasons: Number of crop cycles to simulate
        
        Returns:
            DataFrame with columns: log_date, n_kg_ha, p_kg_ha, k_kg_ha,
                                    rainfall_mm, temperature_avg, humidity_avg
        """
        # Random initial state
        initial_state = EnvironmentState(
            n=random.uniform(60, 120),
            p=random.uniform(25, 55),
            k=random.uniform(35, 80),
            season_index=random.randint(0, 3),
            expected_rainfall_mm=random.uniform(400, 900),
            soil_type=random.choice(['sandy', 'loamy', 'clay']),
            temperature=random.uniform(20, 35),
            humidity=random.uniform(50, 80)
        )
        
        # Generate sequence
        daily_data = self.simulator.generate_lstm_training_sequence(
            initial_state=initial_state,
            num_seasons=num_seasons
        )
        
        df = pd.DataFrame(daily_data)
        
        # Ensure correct column types
        df['log_date'] = pd.to_datetime(df['log_date'])
        for col in ['n_kg_ha', 'p_kg_ha', 'k_kg_ha', 'rainfall_mm', 
                    'temperature_avg', 'humidity_avg']:
            df[col] = df[col].astype(float)
        
        return df
    
    # =========================================================================
    # MARKET PRICE DATA FOR PROPHET
    # =========================================================================
    
    def get_market_price_history(
        self,
        crop_name: str,
        days_back: int = 365
    ) -> pd.DataFrame:
        """
        Get market price history for Prophet forecasting.
        
        Column output: [price_date, price_per_kg]
        
        Args:
            crop_name: Crop name (e.g., 'rice', 'wheat')
            days_back: How many days of history to fetch
        
        Returns:
            DataFrame with price_date and price_per_kg columns
        """
        df = pd.DataFrame()
        
        # Try to read from database first
        if self.db is not None:
            df = self._read_market_prices_from_db(crop_name, days_back)
        
        # If empty, generate synthetic
        if df.empty:
            print(f"ℹ No market price records for {crop_name}. Generating synthetic...")
            df = self._generate_synthetic_price_series(crop_name, days_back)
        
        return df
    
    def _read_market_prices_from_db(
        self,
        crop_name: str,
        days_back: int
    ) -> pd.DataFrame:
        """Read market prices from market_prices table."""
        if self.db is None:
            return pd.DataFrame()
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            query = """
                SELECT price_date, price_per_kg
                FROM market_prices
                WHERE crop_name = %s AND price_date >= %s
                ORDER BY price_date ASC
            """
            
            with self.db.get_connection() as (conn, cursor):
                cursor.execute(query, (crop_name.lower(), cutoff_date))
                rows = cursor.fetchall()
            
            if rows:
                return pd.DataFrame(rows)
        
        except Exception as e:
            print(f"⚠ Error reading market prices: {e}")
        
        return pd.DataFrame()
    
    def _generate_synthetic_price_series(
        self,
        crop_name: str,
        days: int = 365
    ) -> pd.DataFrame:
        """
        Generate synthetic price series with seasonal variation.
        
        Uses: base_price * (1 + 0.15 * sin(2π * day / 365))
        Plus random noise ±5%
        
        Args:
            crop_name: Crop name
            days: Number of days to generate
        
        Returns:
            DataFrame with price_date and price_per_kg
        """
        base_price = DEFAULT_MARKET_PRICES.get(crop_name.lower(), 25.0)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        data = []
        current_date = start_date
        
        for day_num in range(days):
            # Seasonal variation: ±15%
            seasonal_factor = 1 + 0.15 * math.sin(2 * math.pi * day_num / 365)
            
            # Random noise: ±5%
            noise = random.uniform(-0.05, 0.05)
            
            price = base_price * seasonal_factor * (1 + noise)
            price = round(max(1.0, price), 2)
            
            data.append({
                'price_date': current_date.strftime('%Y-%m-%d'),
                'price_per_kg': price
            })
            
            current_date += timedelta(days=1)
        
        df = pd.DataFrame(data)
        df['price_date'] = pd.to_datetime(df['price_date'])
        
        return df
    
    # =========================================================================
    # LOGGING DAILY NUTRIENTS
    # =========================================================================
    
    def log_daily_nutrient(
        self,
        cycle_id: int,
        farmer_id: int,
        n: float,
        p: float,
        k: float,
        rainfall_mm: float = 0.0,
        temperature: float = None,
        humidity: float = None,
        days_into_cycle: int = None,
        log_date: datetime = None
    ) -> bool:
        """
        Write a daily nutrient log entry to nutrient_timeseries_log.
        
        Called by RINDM weather monitor after processing rainfall events.
        
        Args:
            cycle_id: Active crop cycle ID
            farmer_id: Farmer ID
            n, p, k: Current nutrient levels (kg/ha)
            rainfall_mm: Rainfall on this day
            temperature: Average temperature (°C)
            humidity: Average humidity (%)
            days_into_cycle: Day number within current crop cycle
            log_date: Date of log entry (defaults to today)
        
        Returns:
            True if successfully logged, False otherwise
        """
        if self.db is None:
            print("⚠ Database not available. Cannot log nutrient data.")
            return False
        
        log_date = log_date or datetime.now().date()
        
        try:
            with self.db.get_connection() as (conn, cursor):
                cursor.execute("""
                    INSERT INTO nutrient_timeseries_log (
                        cycle_id, farmer_id, log_date,
                        n_kg_ha, p_kg_ha, k_kg_ha,
                        rainfall_mm, temperature_avg, humidity_avg,
                        days_into_cycle
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (cycle_id, log_date) DO UPDATE SET
                        n_kg_ha = EXCLUDED.n_kg_ha,
                        p_kg_ha = EXCLUDED.p_kg_ha,
                        k_kg_ha = EXCLUDED.k_kg_ha,
                        rainfall_mm = EXCLUDED.rainfall_mm,
                        temperature_avg = EXCLUDED.temperature_avg,
                        humidity_avg = EXCLUDED.humidity_avg,
                        days_into_cycle = EXCLUDED.days_into_cycle
                """, (
                    cycle_id, farmer_id, log_date,
                    round(n, 2), round(p, 2), round(k, 2),
                    round(rainfall_mm, 2),
                    round(temperature, 2) if temperature else None,
                    round(humidity, 2) if humidity else None,
                    days_into_cycle
                ))
            
            return True
        
        except Exception as e:
            print(f"⚠ Error logging nutrient data: {e}")
            return False
    
    def log_market_price(
        self,
        crop_name: str,
        price_per_kg: float,
        price_date: datetime = None,
        market_name: str = None,
        state_name: str = None
    ) -> bool:
        """
        Log a market price entry.
        
        Args:
            crop_name: Crop name
            price_per_kg: Price in ₹/kg
            price_date: Date of price (defaults to today)
            market_name: Name of market/mandi
            state_name: State name
        
        Returns:
            True if successfully logged
        """
        if self.db is None:
            print("⚠ Database not available. Cannot log market price.")
            return False
        
        price_date = price_date or datetime.now().date()
        
        try:
            with self.db.get_connection() as (conn, cursor):
                cursor.execute("""
                    INSERT INTO market_prices (
                        crop_name, price_date, price_per_kg,
                        market_name, state_name
                    ) VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (crop_name, price_date, market_name) DO UPDATE SET
                        price_per_kg = EXCLUDED.price_per_kg
                """, (
                    crop_name.lower(), price_date, round(price_per_kg, 2),
                    market_name, state_name
                ))
            
            return True
        
        except Exception as e:
            print(f"⚠ Error logging market price: {e}")
            return False
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_cycle_data(self, cycle_id: int) -> Optional[Dict]:
        """
        Get all time-series data for a specific crop cycle.
        
        Args:
            cycle_id: Crop cycle ID
        
        Returns:
            Dict with cycle info and daily data, or None
        """
        if self.db is None:
            return None
        
        try:
            with self.db.get_connection() as (conn, cursor):
                # Get cycle info
                cursor.execute("""
                    SELECT * FROM crop_cycles WHERE cycle_id = %s
                """, (cycle_id,))
                cycle_info = cursor.fetchone()
                
                if not cycle_info:
                    return None
                
                # Get daily logs
                cursor.execute("""
                    SELECT * FROM nutrient_timeseries_log
                    WHERE cycle_id = %s
                    ORDER BY log_date ASC
                """, (cycle_id,))
                daily_logs = cursor.fetchall()
                
                return {
                    'cycle_info': dict(cycle_info),
                    'daily_data': [dict(row) for row in daily_logs],
                    'num_days': len(daily_logs)
                }
        
        except Exception as e:
            print(f"⚠ Error getting cycle data: {e}")
            return None
    
    def get_training_stats(self) -> Dict:
        """
        Get statistics about available training data.
        
        Returns:
            Dict with counts and date ranges
        """
        stats = {
            'nutrient_logs': 0,
            'market_prices': 0,
            'date_range': None,
            'crops_with_prices': [],
            'db_connected': self.db is not None
        }
        
        if self.db is None:
            return stats
        
        try:
            with self.db.get_connection() as (conn, cursor):
                # Count nutrient logs
                cursor.execute("SELECT COUNT(*) as cnt FROM nutrient_timeseries_log")
                stats['nutrient_logs'] = cursor.fetchone()['cnt']
                
                # Count market prices
                cursor.execute("SELECT COUNT(*) as cnt FROM market_prices")
                stats['market_prices'] = cursor.fetchone()['cnt']
                
                # Date range
                cursor.execute("""
                    SELECT MIN(log_date) as min_date, MAX(log_date) as max_date
                    FROM nutrient_timeseries_log
                """)
                row = cursor.fetchone()
                if row['min_date']:
                    stats['date_range'] = {
                        'from': str(row['min_date']),
                        'to': str(row['max_date'])
                    }
                
                # Crops with prices
                cursor.execute("""
                    SELECT DISTINCT crop_name FROM market_prices ORDER BY crop_name
                """)
                stats['crops_with_prices'] = [r['crop_name'] for r in cursor.fetchall()]
        
        except Exception as e:
            print(f"⚠ Error getting training stats: {e}")
        
        return stats


# ============================================================================
# TEST / DEMO
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Time Series Data Manager Test")
    print("=" * 60)
    
    mgr = TimeSeriesDataManager()
    
    # Test 1: Get training data (synthetic fallback)
    print("\n--- Test 1: Get Training Data ---")
    df = mgr.get_timeseries_for_training(days_back=365)
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Date range: {df['log_date'].min()} to {df['log_date'].max()}")
    print(df.head(3))
    
    # Test 2: Get market prices (synthetic)
    print("\n--- Test 2: Get Market Prices ---")
    prices = mgr.get_market_price_history('rice', days_back=365)
    print(f"Shape: {prices.shape}")
    print(f"Columns: {prices.columns.tolist()}")
    print(f"Price range: ₹{prices['price_per_kg'].min():.2f} - ₹{prices['price_per_kg'].max():.2f}")
    print(prices.head(3))
    
    # Test 3: Training stats
    print("\n--- Test 3: Training Stats ---")
    stats = mgr.get_training_stats()
    print(f"DB Connected: {stats['db_connected']}")
    print(f"Nutrient logs: {stats['nutrient_logs']}")
    print(f"Market price records: {stats['market_prices']}")
    
    print("\n✓ All tests passed!")
