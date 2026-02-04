# COMMENTS.md

## Refactoring Notes — Single Endpoint Crop Recommendation Service

This file documents required architectural changes to refactor the current implementation into a **single API endpoint** for crop recommendation.

**Scope is LIMITED to:**
- Weather data fetching
- Model inference
- Input orchestration

*Frontend implementation details are OUT OF SCOPE.*

---

## 1. Target Architecture (MANDATORY)

The system must expose **ONE single API endpoint**: 
`POST /recommend-crop`

This endpoint must internally:
1. Accept soil parameters (N, P, K, pH) and location (Lat/Long) from the user.
2. Fetch real-time weather data using a weather API.
3. Construct the full feature vector.
4. Run preprocessing (Scaling/Encoding).
5. Perform ensemble inference using all models.
6. Return the predicted crop.

**No separate `/weather` endpoint should be exposed to the client.**

---

## 2. Input Contract

### Expected Request Payload
```json
{
  "N": number,
  "P": number,
  "K": number,
  "ph": number,
  "latitude": number,
  "longitude": number
}
Important Rules
User provides ONLY soil parameters and location.

Internal Derivation: Temperature, humidity, and rainfall MUST be derived internally.

No Client-Side Weather: The frontend should not handle weather API calls.

3. Weather Data Handling (Internal)
Behavior: Fetch weather data INSIDE the /recommend-crop handler.

Required Fields: Temperature, humidity, and rainfall.

Error Handling: If the Weather API fails, use a safe fallback (e.g., historical averages or cached values) to prevent the inference from crashing.

Isolation: Keep weather fetching logic in a dedicated utility function.

4. Feature Assembly (CRITICAL)
The final feature vector passed to the model MUST follow this exact order:

FEATURE_ORDER = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

Rule: Never rely on dictionary ordering or raw arrays from the request.

Mapping: Explicitly map named inputs to the ordered array before inference.

5. Preprocessing & Inference Rules
Preprocessing
StandardScaler & LabelEncoder: Must be loaded from disk at application startup.

No Refitting: Do not fit/train anything inside the API endpoint.

Ensemble Logic
Models: Random Forest, XGBoost, SVM, and CatBoost.

Method: Soft voting (averaging probabilities).

Consistency: All models must share the exact same preprocessed input.

6. Output Contract
Minimum Response
JSON
{
  "predicted_crop": "rice",
  "confidence": 0.87
}
7. What Must Be Removed / Avoided
NO separate /weather endpoint.

NO frontend-side weather fetching logic.

NO passing of environmental data (Temp/Rain) from the client.

NO silent failures if weather data is missing.

8. Design Goal Summary
The system must guarantee: One request → One response.
The frontend sends soil/location; the backend orchestrates the rest and returns the answer.