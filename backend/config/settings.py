"""
Configuration settings for the Kelantan Flood Prediction API
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Configuration
    api_title: str = "Kelantan Flood Prediction API"
    api_version: str = "1.0.0"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///./flood_prediction.db"
    
    # External API Keys
    openweather_api_key: Optional[str] = None
    google_earth_engine_key: Optional[str] = None
    
    # Malaysian Data Sources
    met_malaysia_api_url: str = "https://api.met.gov.my"
    nahrim_api_url: str = "https://publicinfobanjir.water.gov.my"
    did_malaysia_api_url: str = "https://publicinfobanjir.water.gov.my"
    
    # Kelantan Specific Configuration
    kelantan_bounds: dict = {
        "north": 6.2,
        "south": 4.5,
        "east": 102.5,
        "west": 101.2
    }
    
    # Model Configuration
    model_update_interval: int = 3600  # seconds
    prediction_cache_ttl: int = 1800   # seconds
    
    # CLIMADA Configuration
    climada_data_dir: str = "./data/climada"
    climada_results_dir: str = "./data/results"
    
    # Flood Risk Thresholds
    flood_risk_thresholds: dict = {
        "low": 0.2,
        "medium": 0.5,
        "high": 0.8,
        "extreme": 0.95
    }
    
    # Asset Categories
    asset_damage_multipliers: dict = {
        "residential": {
            "low": 0.05,
            "medium": 0.15,
            "high": 0.35,
            "extreme": 0.75
        },
        "commercial": {
            "low": 0.08,
            "medium": 0.25,
            "high": 0.50,
            "extreme": 0.85
        },
        "industrial": {
            "low": 0.10,
            "medium": 0.30,
            "high": 0.60,
            "extreme": 0.90
        }
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()