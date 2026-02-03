import React, { useState } from 'react'
import RecommendationForm from './components/RecommendationForm'
import RecommendationResult from './components/RecommendationResult'
import { recommendCrop } from './services/api'
import './App.css'

export default function App() {
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (formData) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await recommendCrop(formData)
      setResult(response)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header className="header">
        <h1>🌾 CropSense</h1>
        <p>AI-Powered Crop Recommendation System</p>
      </header>

      <main className="main">
        <RecommendationForm onSubmit={handleSubmit} loading={loading} />
        <RecommendationResult result={result} error={error} loading={loading} />
      </main>

      <footer className="footer">
        <p>💡 Powered by Machine Learning | Accuracy: 99.55%</p>
      </footer>
    </div>
  )
}
