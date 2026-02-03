import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const recommendCrop = async (soilData) => {
  try {
    const response = await api.post('/recommend', soilData)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export const getWeather = async (latitude, longitude) => {
  try {
    const response = await api.get('/weather', {
      params: { latitude, longitude }
    })
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export const getCropInfo = async (cropName) => {
  try {
    const response = await api.get(`/crop-info/${cropName}`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export default api
