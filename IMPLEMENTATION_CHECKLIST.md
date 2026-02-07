# Implementation Checklist - Post-Harvest Nutrient Management

## Phase 2: Post-Harvest Nutrient Tracking Implementation

### [ ] STEP 1: Enhance Crop Database with Nutrient Data
**File**: `backend/src/utils/crop_database.py`

- [ ] Add `CROP_NUTRIENT_UPTAKE` dictionary with N, P, K values per crop
  - Example structure:
    ```python
    CROP_NUTRIENT_UPTAKE = {
        'rice': {'N': 60, 'P': 20, 'K': 40},          # kg/hectare avg
        'maize': {'N': 120, 'P': 30, 'K': 100},
        'wheat': {'N': 100, 'P': 25, 'K': 50},
        # ... all other crops
    }
    ```

- [ ] Add `SOIL_LEACHING_COEFFICIENTS` dictionary for different soil types
  - Example structure:
    ```python
    SOIL_LEACHING_COEFFICIENTS = {
        'sandy': {'N': 0.80, 'P': 0.30, 'K': 0.60},    # High leaching
        'loamy': {'N': 0.50, 'P': 0.20, 'K': 0.40},    # Medium
        'clay': {'N': 0.20, 'P': 0.10, 'K': 0.15},     # Low leaching
    }
    ```

- [ ] Add helper functions:
  ```python
  def get_crop_nutrient_uptake(crop_name)
  def get_soil_leaching_coefficient(soil_type)
  def get_all_crop_nutrient_info(crop_name)
  ```

---

### [ ] STEP 2: Create RINDM (Rainfall Induced Nutrient Depletion Model)
**New File**: `backend/src/models/rindm.py`

**Research Required**:
- [ ] Define the mathematical formula for nutrient loss due to rainfall
- [ ] Consider factors:
  - Rainfall amount (mm)
  - Rainfall intensity
  - Soil texture/type
  - Depth of nutrient presence in soil
  - Crop growth stage

**Implementation**:
```python
class RainfallInducedNutrientDepletionModel:
    """
    RINDM: Rainfall Induced Nutrient Depletion Model
    
    Calculates nutrient losses from rain leaching during crop growing season
    Formula basis: Nutrient Loss = Rainfall × Leaching Coefficient × Soil Factor
    """
    
    def __init__(self):
        pass
    
    def calculate_single_rainfall_loss(self, 
                                      rainfall_mm, 
                                      soil_type, 
                                      nutrient_type):
        """Calculate N, P, K loss for a single rainfall event"""
        pass
    
    def calculate_season_nutrient_loss(self, 
                                      rainfall_events, 
                                      soil_type, 
                                      crop):
        """Aggregate total nutrient loss for entire growing season"""
        pass
    
    def get_rainfall_nutrient_impact(self, 
                                    rainfall_mm, 
                                    soil_type):
        """Returns nutrient loss percentages for N, P, K"""
        pass
```

---

### [ ] STEP 3: Create Nutrient Calculation Module
**New File**: `backend/src/utils/nutrient_calculator.py`

```python
class PostHarvestNutrientCalculator:
    """
    Calculate remaining nutrients after harvest
    Formula: Final Nutrients = Initial - Uptake - Rainfall Loss
    """
    
    def calculate_remaining_nutrients(self,
                                     crop_name,
                                     initial_nutrients,  # {'N': x, 'P': y, 'K': z}
                                     rainfall_data,      # [{'date': '...', 'rainfall_mm': x}, ...]
                                     soil_type,
                                     harvest_date):
        """
        Returns:
        {
            'initial': {'N': ..., 'P': ..., 'K': ...},
            'uptake': {'N': ..., 'P': ..., 'K': ...},
            'rainfall_loss': {'N': ..., 'P': ..., 'K': ...},
            'final': {'N': ..., 'P': ..., 'K': ...},
            'balance_sheet': {...},
            'nutrient_status': 'Low/Medium/High'
        }
        """
        pass
    
    def generate_nutrient_balance_sheet(self):
        """Create detailed report of nutrient changes"""
        pass
    
    def get_nutrient_health_status(self, final_nutrients):
        """Classify nutrient levels: Low/Medium/High"""
        pass
```

---

### [ ] STEP 4: Add Post-Harvest Endpoint to Flask API
**File**: `backend/app.py`

- [ ] Add new endpoint: `POST /calculate-post-harvest-nutrients`
  ```python
  @app.route('/calculate-post-harvest-nutrients', methods=['POST'])
  def post_harvest_nutrients():
      """
      Calculate remaining nutrients after harvest
      Input: {
          'crop': 'rice',
          'initial_nutrients': {'N': 100, 'P': 50, 'K': 80},
          'rainfall_data': [{...}, ...],
          'soil_type': 'loamy',
          'harvest_date': '2024-10-15'
      }
      Output: Nutrient balance sheet with final values
      """
  ```

- [ ] Error handling for:
  - Missing rainfall data
  - Invalid crop name
  - Invalid soil type
  - Invalid nutrient values

---

### [ ] STEP 5: Historical Rainfall Data Fetching
**Enhancement**: `backend/src/utils/weather_fetcher.py`

- [ ] Add method to fetch historical rainfall:
  ```python
  def get_historical_rainfall(self, 
                             latitude, 
                             longitude, 
                             start_date, 
                             end_date):
      """Fetch actual rainfall data for past period"""
      pass
  ```

- [ ] Consider data sources:
  - OpenWeatherMap historical API
  - NOAA weather stations
  - Weather Underground
  - Local meteorological stations

---

### [ ] STEP 6: Testing & Validation
**Files**: `backend/test_post_harvest.py`

- [ ] Unit tests for RINDM calculations
- [ ] Unit tests for nutrient calculator
- [ ] Integration tests for post-harvest endpoint
- [ ] Example test cases:
  ```python
  def test_rice_harvest_nutrients():
      # Rice with 100mm rainfall during season
      # Should show specific N, P, K losses
      pass
  
  def test_different_soil_types():
      # Same rainfall, different soil types
      # Should show varying losses (sandy > loamy > clay)
      pass
  
  def test_nutrient_balance_edge_cases():
      # What if rainfall loss > available nutrients?
      pass
  ```

---

## Data Collection Requirements

### Nutrient Uptake Data Needed:
- [ ] Standard N, P, K uptake per crop (kg/ha)
- [ ] Source: Agricultural research papers, FAO guidelines
- [ ] Example sources:
  - ICRISAT (International Crops Research Institute)
  - National Agricultural Extension Services
  - University crop science departments
  - FAO Crop databases

### RINDM Parameters Needed:
- [ ] Nutrient leaching coefficients per soil type
- [ ] Saturation water content per soil type
- [ ] Nutrient availability depths
- [ ] Rainfall-runoff vs infiltration ratios

### Soil Type Classification:
- [ ] Sand percentage
- [ ] Silt percentage
- [ ] Clay percentage
- [ ] Reference: USDA Soil Texture Classification

---

## Success Criteria

✅ Phase 2 is complete when:
- [ ] Post-harvest endpoint returns correct nutrient calculations
- [ ] RINDM model accurately predicts nutrient loss based on rainfall
- [ ] Nutrient balance sheet matches manual calculations
- [ ] All soil types handled correctly (sandy, loamy, clay)
- [ ] Historical rainfall data can be fetched for past seasons
- [ ] Comprehensive test suite passes
- [ ] Documentation updated with formulas and assumptions

---

## Example Scenario to Test

**Input**:
```json
{
  "crop": "rice",
  "initial_nutrients": {"N": 100, "P": 50, "K": 80},
  "rainfall_data": [
    {"date": "2024-06-15", "rainfall_mm": 45},
    {"date": "2024-06-20", "rainfall_mm": 60},
    {"date": "2024-07-10", "rainfall_mm": 55},
    {"date": "2024-07-25", "rainfall_mm": 40},
    {"date": "2024-08-15", "rainfall_mm": 75}
  ],
  "soil_type": "loamy",
  "harvest_date": "2024-10-15"
}
```

**Expected Output**:
```json
{
  "initial_nutrients": {"N": 100, "P": 50, "K": 80},
  "uptake": {"N": 60, "P": 20, "K": 40},
  "rainfall_loss_loamy": {"N": 12, "P": 8, "K": 14},
  "final_nutrients": {"N": 28, "P": 22, "K": 26},
  "nutrient_status": "Medium",
  "recommendations": [
    "N level is moderate for next crop",
    "P is sufficient",
    "K is moderate"
  ]
}
```

