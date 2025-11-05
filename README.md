# 🌊 Kelantan Flood Prediction Webapp

A comprehensive web application for predicting flood likelihood and assessing climate risk impact on assets in Kelantan, Malaysia. Built with CLIMADA framework integration for advanced climate risk modeling.

## 🎯 Overview

This application addresses Malaysia's key climate risks by modeling the chain of impact:
**Flood → Property Damage → Loan Defaults → Bank Balance Sheets → National & Cross-Border Financial Stability**

### Key Features

- **🌦️ Real-time Flood Prediction**: ML-based flood probability assessment using meteorological, hydrological, and geographic data
- **🏡 Asset Impact Modeling**: Financial impact assessment on property portfolios and mortgage loans
- **📊 Interactive Dashboard**: GIS mapping with heat zones for loan exposure vs flood incidents
- **🧪 Climate Stress Testing**: Systemic risk analysis for extreme flood scenarios
- **📈 Risk Analytics**: Comprehensive risk scoring by district and postal code

## 🏗️ Architecture

### Data Sources Integration
- **🌦️ Meteorological**: Rainfall, humidity, windspeed, temperature (MET Malaysia, ECMWF)
- **🏞️ Hydrological**: River water level, soil saturation, drainage (NAHRIM, DID Malaysia)
- **🗺️ Geographic**: Elevation, slope, land cover, flood plain data (SRTM DEM, Google Earth Engine)
- **🏡 Asset & Mortgage**: Property geo-location, type, loan value, insurance
- **🧭 Historical Floods**: Flood polygons, severity level, damage estimates (NADMA)

### Technology Stack
- **Backend**: FastAPI, Python 3.12.3, scikit-learn, pandas, numpy
- **Frontend**: React, Vite, Ant Design, Leaflet maps
- **Climate Modeling**: Custom CLIMADA-compatible implementation
- **Database**: SQLAlchemy (configurable)
- **APIs**: RESTful with OpenAPI documentation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (optimized for Python 3.12.3)
- Node.js 16+ and npm
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/andrewchaubis/testOpen.git
   cd testOpen
   git checkout flood-prediction-webapp
   ```

2. **Automated Installation** (Recommended)
   ```bash
   python install_dependencies.py
   ```

3. **Manual Installation**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Install Node.js dependencies
   npm install
   ```

### Running the Application

1. **Start Backend Server**
   ```bash
   cd backend
   python main.py
   ```
   Backend will be available at: http://localhost:12001

2. **Start Frontend Development Server**
   ```bash
   npm run dev
   ```
   Frontend will be available at: http://localhost:12000 (or next available port)

3. **Access the Application**
   - **Web App**: http://localhost:12000 (or check console for actual port)
   - **API Documentation**: http://localhost:12001/docs
   - **Health Check**: http://localhost:12001/health

## 📋 API Endpoints

### Core Prediction APIs

#### Flood Prediction
```bash
POST /api/predict/flood
Content-Type: application/json

{
  "latitude": 6.1254,
  "longitude": 102.2386,
  "weather_data": {
    "rainfall_24h": 50,
    "rainfall_7d": 200,
    "humidity": 80,
    "temperature": 28,
    "wind_speed": 15
  },
  "geo_data": {
    "elevation": 25,
    "slope": 2,
    "distance_to_river": 800,
    "land_cover_type": "urban",
    "drainage_density": 0.5
  }
}
```

#### Asset Impact Assessment
```bash
POST /api/predict/asset-impact
Content-Type: application/json

{
  "flood_probability": 0.7,
  "asset_data": {
    "property_type": "residential",
    "property_value": 500000,
    "loan_amount": 400000,
    "insurance_coverage": 0.8,
    "location": {
      "latitude": 6.1254,
      "longitude": 102.2386
    }
  }
}
```

#### Climate Stress Testing
```bash
POST /api/stress-test
Content-Type: application/json

{
  "scenario": "100_year_flood",
  "return_periods": [10, 25, 50, 100],
  "portfolio_size": 1000
}
```

### Dashboard APIs

#### Dashboard Overview
```bash
GET /api/dashboard/overview
```

#### District Risk Assessment
```bash
GET /api/dashboard/districts
```

## 🧪 CLIMADA Integration

The application includes a custom CLIMADA-compatible implementation optimized for Python 3.12.3:

### Features
- **KelantanFloodModel**: Specialized flood modeling for Kelantan region
- **ClimateEvent**: Historical and synthetic flood event modeling
- **Asset**: Property and infrastructure asset modeling
- **Probabilistic Assessment**: Multi-return period risk analysis

### Usage Example
```python
from backend.models.climada_alternative import KelantanFloodModel

# Initialize model
model = KelantanFloodModel()

# Generate synthetic assets
assets = model.generate_kelantan_assets(1000)
model.load_exposure_data(assets)

# Run stress test
results = model.run_probabilistic_assessment([10, 25, 50, 100])
```

## 🗺️ Prototype Implementations

### 1. Flood–Mortgage Exposure Dashboard
- **Goal**: Visualize overlap of floods and mortgage portfolios in real time
- **Features**: GIS heat zones, risk scoring by district, NPL correlation trends

### 2. Predictive Model (Machine Learning)
- **Goal**: Predict default probability given flood exposure
- **Approach**: Gradient Boosted Trees with satellite + loan data
- **Output**: Default risk index per loan/region

### 3. Systemic Climate Stress Test
- **Goal**: Understand macro-financial impact of extreme floods
- **Features**: Scenario generation, propagation modeling, capital impact analysis

## 📊 Data Models

### Weather Data
```python
{
  "rainfall_24h": float,      # mm in last 24 hours
  "rainfall_7d": float,       # mm in last 7 days
  "humidity": float,          # percentage
  "temperature": float,       # celsius
  "wind_speed": float,        # km/h
  "river_level": float,       # meters
  "soil_saturation": float    # percentage
}
```

### Geographic Data
```python
{
  "elevation": float,         # meters above sea level
  "slope": float,            # degrees
  "distance_to_river": float, # meters
  "land_cover_type": str,    # urban/rural/forest/agricultural
  "drainage_density": float   # km/km²
}
```

### Asset Data
```python
{
  "property_type": str,       # residential/commercial/industrial
  "property_value": float,    # MYR
  "loan_amount": float,       # MYR
  "insurance_coverage": float, # ratio (0-1)
  "location": {
    "latitude": float,
    "longitude": float
  }
}
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=12001
DEBUG=true

# Database Configuration (optional)
DATABASE_URL=sqlite:///./flood_prediction.db

# External API Keys (optional)
WEATHER_API_KEY=your_weather_api_key
MAPS_API_KEY=your_maps_api_key

# CLIMADA Configuration
CLIMADA_DATA_DIR=./data/climada
CLIMADA_RESULTS_DIR=./data/results
```

### Settings
Modify `backend/config/settings.py` for:
- Data source URLs
- Model parameters
- Regional configurations
- API rate limits

## 🧪 Testing

### API Testing
```bash
# Health check
curl http://localhost:12001/health

# Test flood prediction
curl -X POST "http://localhost:12001/api/predict/flood" \
  -H "Content-Type: application/json" \
  -d @test_data/flood_request.json

# Test stress testing
curl -X POST "http://localhost:12001/api/stress-test" \
  -H "Content-Type: application/json" \
  -d @test_data/stress_test_request.json
```

### Frontend Testing
```bash
npm test
```

## 📈 Performance Optimization

### Backend
- Async/await for I/O operations
- Connection pooling for database
- Caching for frequently accessed data
- Batch processing for large datasets

### Frontend
- Code splitting with React.lazy()
- Memoization for expensive calculations
- Virtual scrolling for large lists
- Progressive loading for maps

## 🔒 Security

### API Security
- CORS configuration
- Rate limiting
- Input validation with Pydantic
- SQL injection prevention

### Data Privacy
- Anonymized mortgage data
- Encrypted sensitive information
- GDPR compliance considerations

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Production Deployment
1. Set environment variables
2. Configure reverse proxy (nginx)
3. Set up SSL certificates
4. Configure monitoring and logging
5. Set up backup procedures

## 📚 Documentation

### API Documentation
- **Interactive Docs**: http://localhost:12001/docs
- **OpenAPI Spec**: http://localhost:12001/openapi.json

### Code Documentation
- Comprehensive docstrings
- Type hints throughout
- Architecture decision records

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for new frontend components
- Write tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **CLIMADA**: Climate risk modeling framework
- **MET Malaysia**: Meteorological data
- **NAHRIM**: Hydrological research
- **NADMA**: Disaster management data
- **Bank Negara Malaysia**: Financial stability insights

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation at `/docs`
- Review API examples in `/examples`

---

**Built with ❤️ for climate resilience in Malaysia** 🇲🇾