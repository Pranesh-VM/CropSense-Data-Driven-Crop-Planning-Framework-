import React from 'react'
import './RecommendationResult.css'

export default function RecommendationResult({ result, error, loading }) {
  if (loading) {
    return (
      <div className="result result-loading">
        <div className="spinner"></div>
        <p>🔍 Analyzing soil conditions with AI...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="result result-error">
        <h3>❌ Error</h3>
        <p>{typeof error === 'string' ? error : error.message || 'Failed to get recommendation'}</p>
      </div>
    )
  }

  if (!result) {
    return null
  }

  return (
    <div className="result result-success">
      <h2>🎯 Recommended Crop</h2>
      
      <div className="crop-card">
        <div className="crop-name">{result.recommended_crop}</div>
        <div className="confidence">
          Confidence: <span className="confidence-value">{(result.confidence * 100).toFixed(1)}%</span>
        </div>
      </div>

      {result.crop_info && (
        <div className="crop-info">
          <h3>📋 Crop Information</h3>
          <div className="info-grid">
            {result.crop_info.growing_season && (
              <div className="info-item">
                <label>Growing Season:</label>
                <value>{result.crop_info.growing_season}</value>
              </div>
            )}
            {result.crop_info.optimal_temp && (
              <div className="info-item">
                <label>Optimal Temperature:</label>
                <value>{result.crop_info.optimal_temp}°C</value>
              </div>
            )}
            {result.crop_info.rainfall_needed && (
              <div className="info-item">
                <label>Required Rainfall:</label>
                <value>{result.crop_info.rainfall_needed} mm</value>
              </div>
            )}
            {result.crop_info.soil_type && (
              <div className="info-item">
                <label>Soil Type:</label>
                <value>{result.crop_info.soil_type}</value>
              </div>
            )}
          </div>
        </div>
      )}

      {result.alternative_crops && result.alternative_crops.length > 0 && (
        <div className="alternatives">
          <h3>🌾 Alternative Options</h3>
          <div className="alternatives-list">
            {result.alternative_crops.map((crop, index) => (
              <div key={index} className="alternative-item">
                <span className="crop-name-alt">{crop}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.weather_info && (
        <div className="weather-info">
          <h3>🌤️ Current Weather</h3>
          <div className="weather-grid">
            {result.weather_info.temperature && (
              <div className="weather-item">
                <label>Temperature:</label>
                <value>{result.weather_info.temperature}°C</value>
              </div>
            )}
            {result.weather_info.humidity && (
              <div className="weather-item">
                <label>Humidity:</label>
                <value>{result.weather_info.humidity}%</value>
              </div>
            )}
            {result.weather_info.description && (
              <div className="weather-item">
                <label>Condition:</label>
                <value>{result.weather_info.description}</value>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
