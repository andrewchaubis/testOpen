"""
Kelantan Flood Prediction API
Main FastAPI application for flood likelihood and asset impact prediction
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from datetime import datetime, timedelta

from models.flood_predictor import FloodPredictor
from models.asset_impact import AssetImpactModel
from services.data_service import DataService
from services.weather_service import WeatherService
from config.settings import Settings

# Initialize FastAPI app
app = FastAPI(
    title="Kelantan Flood Prediction API",
    description="API for predicting flood likelihood and asset impact in Kelantan, Malaysia",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
settings = Settings()
data_service = DataService()
weather_service = WeatherService()
flood_predictor = FloodPredictor()
asset_impact_model = AssetImpactModel()

# Pydantic models
class FloodPredictionRequest(BaseModel):
    latitude: float
    longitude: float
    forecast_days: int = 7
    include_historical: bool = True

class AssetImpactRequest(BaseModel):
    asset_location: Dict[str, float]  # {"lat": float, "lng": float}
    asset_type: str  # "residential", "commercial", "industrial"
    asset_value: float
    loan_amount: Optional[float] = None
    insurance_coverage: Optional[float] = None

class StressTestRequest(BaseModel):
    scenario: str  # "100_year_flood", "river_overflow", "coastal_surge"
    region: str = "kelantan"
    portfolio_size: int = 1000

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Kelantan Flood Prediction API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/predict/flood")
async def predict_flood(request: FloodPredictionRequest):
    """
    Predict flood likelihood for a specific location
    """
    try:
        # Get weather data
        weather_data = await weather_service.get_forecast(
            request.latitude, 
            request.longitude, 
            request.forecast_days
        )
        
        # Get geographical data
        geo_data = await data_service.get_geographical_data(
            request.latitude, 
            request.longitude
        )
        
        # Get historical flood data if requested
        historical_data = None
        if request.include_historical:
            historical_data = await data_service.get_historical_floods(
                request.latitude, 
                request.longitude
            )
        
        # Make prediction
        prediction = flood_predictor.predict(
            weather_data=weather_data,
            geo_data=geo_data,
            historical_data=historical_data
        )
        
        return {
            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            "prediction": prediction,
            "forecast_period": request.forecast_days,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict/asset-impact")
async def predict_asset_impact(request: AssetImpactRequest):
    """
    Predict asset impact and financial risk from flooding
    """
    try:
        # Get flood risk for asset location
        flood_risk = await flood_predictor.get_location_risk(
            request.asset_location["lat"],
            request.asset_location["lng"]
        )
        
        # Calculate asset impact
        impact_assessment = asset_impact_model.assess_impact(
            flood_risk=flood_risk,
            asset_type=request.asset_type,
            asset_value=request.asset_value,
            loan_amount=request.loan_amount,
            insurance_coverage=request.insurance_coverage
        )
        
        return {
            "asset_location": request.asset_location,
            "flood_risk": flood_risk,
            "impact_assessment": impact_assessment,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stress-test")
async def run_stress_test(request: StressTestRequest):
    """
    Run systemic climate stress test
    """
    try:
        # Generate scenario data
        scenario_data = await data_service.generate_stress_scenario(
            request.scenario,
            request.region
        )
        
        # Run stress test
        stress_results = asset_impact_model.run_stress_test(
            scenario_data=scenario_data,
            portfolio_size=request.portfolio_size
        )
        
        return {
            "scenario": request.scenario,
            "region": request.region,
            "portfolio_size": request.portfolio_size,
            "results": stress_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/districts")
async def get_kelantan_districts():
    """
    Get list of districts in Kelantan with geographical boundaries
    """
    try:
        districts = await data_service.get_kelantan_districts()
        return {"districts": districts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/historical-floods")
async def get_historical_floods(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    district: Optional[str] = None
):
    """
    Get historical flood data for Kelantan
    """
    try:
        floods = await data_service.get_historical_floods_data(
            start_date=start_date,
            end_date=end_date,
            district=district
        )
        return {"historical_floods": floods}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/overview")
async def get_dashboard_overview():
    """
    Get overview data for the main dashboard
    """
    try:
        overview = {
            "current_alerts": await data_service.get_current_alerts(),
            "risk_summary": await flood_predictor.get_regional_risk_summary(),
            "recent_predictions": await data_service.get_recent_predictions(),
            "system_status": {
                "models_loaded": flood_predictor.is_loaded(),
                "data_sources": await data_service.check_data_sources(),
                "last_update": datetime.now().isoformat()
            }
        }
        return overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files (React frontend)
if os.path.exists("../dist"):
    app.mount("/", StaticFiles(directory="../dist", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=12001,
        reload=True,
        log_level="info"
    )