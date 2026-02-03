import React, { useState } from 'react'
import './RecommendationForm.css'

export default function RecommendationForm({ onSubmit, loading }) {
  const [formData, setFormData] = useState({
    nitrogen: 90,
    phosphorus: 42,
    potassium: 43,
    ph: 6.5,
    rainfall: 200,
    temperature: 25,
    humidity: 60,
    location: ''
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'location' ? value : parseFloat(value)
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="form">
      <h2>📊 Soil & Environmental Parameters</h2>
      
      <div className="form-grid">
        <div className="form-group">
          <label>Nitrogen (N) - mg/kg</label>
          <input
            type="number"
            name="nitrogen"
            value={formData.nitrogen}
            onChange={handleChange}
            min="0"
            step="0.1"
          />
        </div>

        <div className="form-group">
          <label>Phosphorus (P) - mg/kg</label>
          <input
            type="number"
            name="phosphorus"
            value={formData.phosphorus}
            onChange={handleChange}
            min="0"
            step="0.1"
          />
        </div>

        <div className="form-group">
          <label>Potassium (K) - mg/kg</label>
          <input
            type="number"
            name="potassium"
            value={formData.potassium}
            onChange={handleChange}
            min="0"
            step="0.1"
          />
        </div>

        <div className="form-group">
          <label>pH Level</label>
          <input
            type="number"
            name="ph"
            value={formData.ph}
            onChange={handleChange}
            min="0"
            max="14"
            step="0.1"
          />
        </div>

        <div className="form-group">
          <label>Rainfall (mm)</label>
          <input
            type="number"
            name="rainfall"
            value={formData.rainfall}
            onChange={handleChange}
            min="0"
            step="0.1"
          />
        </div>

        <div className="form-group">
          <label>Temperature (°C)</label>
          <input
            type="number"
            name="temperature"
            value={formData.temperature}
            onChange={handleChange}
            step="0.1"
          />
        </div>

        <div className="form-group">
          <label>Humidity (%)</label>
          <input
            type="number"
            name="humidity"
            value={formData.humidity}
            onChange={handleChange}
            min="0"
            max="100"
            step="0.1"
          />
        </div>

        <div className="form-group">
          <label>Location</label>
          <input
            type="text"
            name="location"
            value={formData.location}
            onChange={handleChange}
            placeholder="e.g., Delhi, Mumbai"
          />
        </div>
      </div>

      <button type="submit" disabled={loading} className="btn-submit">
        {loading ? '⏳ Analyzing...' : '🚀 Get Recommendation'}
      </button>
    </form>
  )
}
