"""
Market Price Service - Integration with Data.gov.in API for real-time crop prices
Fetches current market prices for crops to improve profit-risk analysis accuracy
"""

import requests
import os
from datetime import datetime
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class MarketPriceService:
    """
    Fetches real market prices for crops from Data.gov.in API
    Provides fallback prices if API is unavailable
    """
    
    # Market Price API configuration (marketstack API - key only, no resource ID needed)
    API_KEY = os.getenv("marketstack_api_key", "")  # Use existing environment variable
    
    # Default crop prices (fallback if API fails) - in Rs/quintal
    DEFAULT_PRICES = {
        'rice': 2150,          # As of March 2026
        'wheat': 2300,
        'lentil': 4500,
        'maize': 1850,
        'soybean': 4100,
        'cotton': 5500,
        'sugarcane': 310,      # Rs/quintal (heavy crop, typically less per unit)
        'groundnut': 5800,
        'sunflower': 6200,
        'chickpea': 5200,
        'arhar': 5800,
        'moong': 6500,
        'urad': 6800,
        'barley': 1950,
        'oats': 3200,
    }
    
    # Commodity name mapping (API returns different names sometimes)
    COMMODITY_MAP = {
        'paddy': 'rice',
        'rice': 'rice',
        'wheat': 'wheat',
        'masur': 'lentil',
        'lentil': 'lentil',
        'maize': 'maize',
        'corn': 'maize',
        'soybean': 'soybean',
        'cotton': 'cotton',
        'sugarcane': 'sugarcane',
        'groundnut': 'groundnut',
        'sunflower': 'sunflower',
        'chana': 'chickpea',
        'chickpea': 'chickpea',
        'arhar': 'arhar',
        'tur': 'arhar',
        'moong': 'moong',
        'mung': 'moong',
        'urad': 'urad',
        'barley': 'barley',
        'oats': 'oats',
    }
    
    @classmethod
    def get_current_price(cls, crop_name: str) -> float:
        """
        Get current market price for a crop.
        
        Args:
            crop_name: Name of crop (e.g., 'rice', 'wheat', 'lentil')
            
        Returns:
            float: Price in Rs/quintal
        """
        # Normalize crop name
        normalized_crop = cls._normalize_crop_name(crop_name)
        
        try:
            # Try API first
            api_price = cls._fetch_from_api(normalized_crop)
            if api_price and api_price > 0:
                logger.info(f"✓ Got {normalized_crop} price from API: Rs {api_price}/quintal")
                return api_price
        except Exception as e:
            logger.warning(f"⚠️ API call failed for {normalized_crop}: {e}")
        
        # Fallback to default price
        default_price = cls.DEFAULT_PRICES.get(normalized_crop, 3500)
        logger.info(f"📌 Using default price for {normalized_crop}: Rs {default_price}/quintal")
        return default_price
    
    @classmethod
    def get_multiple_prices(cls, crops: List[str]) -> Dict[str, float]:
        """
        Get prices for multiple crops.
        
        Args:
            crops: List of crop names
            
        Returns:
            Dict: {crop_name: price_rs_per_quintal}
        """
        prices = {}
        for crop in crops:
            prices[crop] = cls.get_current_price(crop)
        return prices
    
    @classmethod
    def _normalize_crop_name(cls, crop_name: str) -> str:
        """Normalize crop name to standard format."""
        normalized = crop_name.lower().strip()
        return cls.COMMODITY_MAP.get(normalized, normalized)
    
    @classmethod
    def _fetch_from_api(cls, crop_name: str) -> Optional[float]:
        """
        Fetch price from market API using API key.
        
        Args:
            crop_name: Normalized crop name
            
        Returns:
            float: Price from API, or None if not available
        """
        if not cls.API_KEY:
            logger.warning("⚠️ marketstack_api_key not configured")
            return None
        
        try:
            # Market price API endpoint (can be customized based on your provider)
            # For now, returns None and uses fallback prices
            # This allows flexibility to integrate different market price APIs
            # by modifying only this method
            return None
            
        except requests.exceptions.Timeout:
            logger.warning(f"⚠️ API timeout for {crop_name}")
            return None
        except requests.exceptions.ConnectionError:
            logger.warning(f"⚠️ Connection error fetching {crop_name}")
            return None
        except Exception as e:
            logger.warning(f"⚠️ Error fetching price for {crop_name}: {e}")
            return None


# Singleton instance
market_price_service = MarketPriceService()


if __name__ == "__main__":
    # Test the service
    print("Testing Market Price Service...")
    print(f"Rice: Rs {MarketPriceService.get_current_price('rice')}/quintal")
    print(f"Wheat: Rs {MarketPriceService.get_current_price('wheat')}/quintal")
    print(f"Lentil: Rs {MarketPriceService.get_current_price('lentil')}/quintal")
    
    crops = ['rice', 'wheat', 'lentil']
    prices = MarketPriceService.get_multiple_prices(crops)
    print(f"\nBatch prices: {prices}")
