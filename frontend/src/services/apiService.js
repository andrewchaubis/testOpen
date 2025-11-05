import axios from 'axios'

const API_BASE_URL = 'http://localhost:12001/api'

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        return response.data
      },
      (error) => {
        console.error('API Error:', error.response?.data || error.message)
        return Promise.reject(error)
      }
    )
  }

  // Dashboard endpoints
  async getDashboardOverview() {
    return this.client.get('/dashboard/overview')
  }

  // Flood prediction endpoints
  async predictFlood(data) {
    return this.client.post('/predict/flood', data)
  }

  async predictAssetImpact(data) {
    return this.client.post('/predict/asset-impact', data)
  }

  async runStressTest(data) {
    return this.client.post('/stress-test', data)
  }

  // Data endpoints
  async getKelantanDistricts() {
    return this.client.get('/data/districts')
  }

  async getHistoricalFloods(params = {}) {
    return this.client.get('/data/historical-floods', { params })
  }

  // Weather and geographical data (mock implementations for demo)
  async getWeatherForecast(lat, lng, days = 7) {
    // Mock weather data for demo
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          location: { latitude: lat, longitude: lng },
          forecast_period_days: days,
          daily_forecasts: Array.from({ length: days }, (_, i) => ({
            date: new Date(Date.now() + i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            temperature: 25 + Math.random() * 8,
            humidity: 70 + Math.random() * 20,
            wind_speed: 5 + Math.random() * 15,
            rainfall_24h: Math.random() * 50,
            condition: ['sunny', 'cloudy', 'rain'][Math.floor(Math.random() * 3)]
          })),
          summary: {
            total_rainfall: Math.random() * 200,
            avg_temperature: 28,
            avg_humidity: 80,
            max_wind_speed: 20,
            rainy_days: Math.floor(Math.random() * days)
          }
        })
      }, 1000)
    })
  }

  async getLocationRisk(lat, lng) {
    // Mock location risk data
    return new Promise((resolve) => {
      setTimeout(() => {
        const risk = Math.random()
        resolve({
          location: { latitude: lat, longitude: lng },
          flood_probability: risk,
          risk_level: risk > 0.7 ? 'high' : risk > 0.4 ? 'medium' : 'low',
          confidence: 0.8,
          factors: {
            elevation: Math.random() * 100,
            distance_to_river: Math.random() * 5000,
            historical_frequency: Math.random() * 0.3
          }
        })
      }, 800)
    })
  }

  // Utility methods
  formatCurrency(amount, currency = 'MYR') {
    return new Intl.NumberFormat('en-MY', {
      style: 'currency',
      currency: currency,
    }).format(amount)
  }

  formatPercentage(value) {
    return `${(value * 100).toFixed(1)}%`
  }

  formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-MY')
  }

  formatDateTime(dateString) {
    return new Date(dateString).toLocaleString('en-MY')
  }
}

export const apiService = new ApiService()
export default apiService