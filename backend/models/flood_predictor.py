"""
Flood Prediction Model using CLIMADA framework and machine learning
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import joblib
import os
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

class FloodPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            'rainfall_24h', 'rainfall_7d', 'humidity', 'temperature',
            'wind_speed', 'river_level', 'soil_saturation', 'elevation',
            'slope', 'distance_to_river', 'land_cover_type', 'drainage_density',
            'historical_flood_frequency', 'season', 'monsoon_intensity'
        ]
        
    def load_model(self, model_path: str = "./models/flood_predictor.joblib"):
        """Load pre-trained model"""
        try:
            if os.path.exists(model_path):
                model_data = joblib.load(model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.is_trained = True
                return True
        except Exception as e:
            print(f"Error loading model: {e}")
        return False
    
    def save_model(self, model_path: str = "./models/flood_predictor.joblib"):
        """Save trained model"""
        try:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_columns': self.feature_columns,
                'trained_at': datetime.now().isoformat()
            }
            joblib.dump(model_data, model_path)
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def prepare_features(self, weather_data: Dict, geo_data: Dict, 
                        historical_data: Optional[Dict] = None) -> np.ndarray:
        """Prepare features for prediction"""
        features = []
        
        # Weather features
        features.extend([
            weather_data.get('rainfall_24h', 0),
            weather_data.get('rainfall_7d', 0),
            weather_data.get('humidity', 50),
            weather_data.get('temperature', 25),
            weather_data.get('wind_speed', 5)
        ])
        
        # Hydrological features
        features.extend([
            geo_data.get('river_level', 0),
            geo_data.get('soil_saturation', 0.3)
        ])
        
        # Geographical features
        features.extend([
            geo_data.get('elevation', 50),
            geo_data.get('slope', 2),
            geo_data.get('distance_to_river', 1000),
            geo_data.get('land_cover_type', 1),  # Encoded: 1=urban, 2=forest, 3=agriculture
            geo_data.get('drainage_density', 0.5)
        ])
        
        # Historical features
        if historical_data:
            features.append(historical_data.get('flood_frequency', 0))
        else:
            features.append(0)
        
        # Temporal features
        current_date = datetime.now()
        season = self._get_season(current_date)
        monsoon_intensity = self._get_monsoon_intensity(current_date)
        
        features.extend([season, monsoon_intensity])
        
        return np.array(features).reshape(1, -1)
    
    def _get_season(self, date: datetime) -> int:
        """Get season encoding (1=dry, 2=wet, 3=transition)"""
        month = date.month
        if month in [12, 1, 2]:  # Northeast monsoon
            return 2
        elif month in [6, 7, 8]:  # Southwest monsoon
            return 2
        elif month in [3, 4, 5, 9, 10, 11]:  # Inter-monsoon
            return 3
        return 1
    
    def _get_monsoon_intensity(self, date: datetime) -> float:
        """Get monsoon intensity (0-1 scale)"""
        month = date.month
        # Peak monsoon months have higher intensity
        if month in [11, 12, 1]:  # Northeast monsoon peak
            return 0.9
        elif month in [6, 7]:  # Southwest monsoon peak
            return 0.7
        elif month in [2, 3, 9, 10]:  # Moderate
            return 0.5
        return 0.3  # Low intensity
    
    def train_model(self, training_data: pd.DataFrame):
        """Train the flood prediction model"""
        try:
            # Prepare features and target
            X = training_data[self.feature_columns]
            y = training_data['flood_probability']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train ensemble model
            self.model = GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            self.is_trained = True
            
            return {
                'mse': mse,
                'r2': r2,
                'feature_importance': dict(zip(
                    self.feature_columns, 
                    self.model.feature_importances_
                ))
            }
            
        except Exception as e:
            print(f"Error training model: {e}")
            return None
    
    def predict(self, weather_data: Dict, geo_data: Dict, 
                historical_data: Optional[Dict] = None) -> Dict:
        """Predict flood probability and risk level"""
        try:
            if not self.is_trained and not self.load_model():
                # Use rule-based prediction if no trained model
                return self._rule_based_prediction(weather_data, geo_data, historical_data)
            
            # Prepare features
            features = self.prepare_features(weather_data, geo_data, historical_data)
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            flood_probability = self.model.predict(features_scaled)[0]
            flood_probability = max(0, min(1, flood_probability))  # Clamp to [0,1]
            
            # Determine risk level
            risk_level = self._get_risk_level(flood_probability)
            
            # Calculate confidence based on feature consistency
            confidence = self._calculate_confidence(weather_data, geo_data)
            
            return {
                'flood_probability': float(flood_probability),
                'risk_level': risk_level,
                'confidence': confidence,
                'factors': self._analyze_risk_factors(weather_data, geo_data),
                'recommendations': self._get_recommendations(risk_level, flood_probability)
            }
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            return self._rule_based_prediction(weather_data, geo_data, historical_data)
    
    def _rule_based_prediction(self, weather_data: Dict, geo_data: Dict, 
                              historical_data: Optional[Dict] = None) -> Dict:
        """Fallback rule-based prediction when ML model is not available"""
        
        # Weather risk factors
        rainfall_24h = weather_data.get('rainfall_24h', 0)
        rainfall_7d = weather_data.get('rainfall_7d', 0)
        
        weather_risk = 0
        if rainfall_24h > 100:  # Heavy rain
            weather_risk += 0.4
        elif rainfall_24h > 50:  # Moderate rain
            weather_risk += 0.2
        
        if rainfall_7d > 300:  # Prolonged rain
            weather_risk += 0.3
        elif rainfall_7d > 150:
            weather_risk += 0.15
        
        # Geographical risk factors
        elevation = geo_data.get('elevation', 50)
        distance_to_river = geo_data.get('distance_to_river', 1000)
        
        geo_risk = 0
        if elevation < 10:  # Low-lying area
            geo_risk += 0.3
        elif elevation < 30:
            geo_risk += 0.15
        
        if distance_to_river < 500:  # Close to river
            geo_risk += 0.2
        elif distance_to_river < 1000:
            geo_risk += 0.1
        
        # Historical risk
        hist_risk = 0
        if historical_data:
            flood_freq = historical_data.get('flood_frequency', 0)
            hist_risk = min(0.2, flood_freq * 0.1)
        
        # Combine risks
        total_risk = min(1.0, weather_risk + geo_risk + hist_risk)
        
        risk_level = self._get_risk_level(total_risk)
        
        return {
            'flood_probability': float(total_risk),
            'risk_level': risk_level,
            'confidence': 0.7,  # Lower confidence for rule-based
            'factors': {
                'weather_risk': weather_risk,
                'geographical_risk': geo_risk,
                'historical_risk': hist_risk
            },
            'recommendations': self._get_recommendations(risk_level, total_risk)
        }
    
    def _get_risk_level(self, probability: float) -> str:
        """Convert probability to risk level"""
        if probability >= 0.8:
            return "extreme"
        elif probability >= 0.5:
            return "high"
        elif probability >= 0.2:
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence(self, weather_data: Dict, geo_data: Dict) -> float:
        """Calculate prediction confidence based on data quality"""
        confidence = 1.0
        
        # Reduce confidence for missing data
        required_weather = ['rainfall_24h', 'humidity', 'temperature']
        missing_weather = sum(1 for key in required_weather if key not in weather_data)
        confidence -= missing_weather * 0.1
        
        required_geo = ['elevation', 'distance_to_river']
        missing_geo = sum(1 for key in required_geo if key not in geo_data)
        confidence -= missing_geo * 0.15
        
        return max(0.3, confidence)
    
    def _analyze_risk_factors(self, weather_data: Dict, geo_data: Dict) -> Dict:
        """Analyze individual risk factors"""
        factors = {}
        
        # Weather factors
        rainfall_24h = weather_data.get('rainfall_24h', 0)
        if rainfall_24h > 100:
            factors['heavy_rainfall'] = "Critical rainfall levels detected"
        elif rainfall_24h > 50:
            factors['moderate_rainfall'] = "Elevated rainfall levels"
        
        # Geographical factors
        elevation = geo_data.get('elevation', 50)
        if elevation < 10:
            factors['low_elevation'] = "Location in flood-prone low-lying area"
        
        distance_to_river = geo_data.get('distance_to_river', 1000)
        if distance_to_river < 500:
            factors['river_proximity'] = "Close proximity to water bodies"
        
        return factors
    
    def _get_recommendations(self, risk_level: str, probability: float) -> List[str]:
        """Get recommendations based on risk level"""
        recommendations = []
        
        if risk_level == "extreme":
            recommendations.extend([
                "Immediate evacuation may be necessary",
                "Avoid all non-essential travel",
                "Monitor official emergency channels",
                "Prepare emergency supplies and evacuation plan"
            ])
        elif risk_level == "high":
            recommendations.extend([
                "Stay alert and monitor weather conditions",
                "Avoid low-lying areas and river crossings",
                "Prepare emergency kit and evacuation plan",
                "Consider postponing outdoor activities"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "Monitor weather updates regularly",
                "Avoid unnecessary travel to flood-prone areas",
                "Keep emergency contacts readily available"
            ])
        else:
            recommendations.extend([
                "Normal precautions sufficient",
                "Stay informed about weather conditions"
            ])
        
        return recommendations
    
    async def get_location_risk(self, latitude: float, longitude: float) -> Dict:
        """Get flood risk assessment for a specific location"""
        # This would integrate with real data sources
        # For now, return mock data based on location
        
        # Simulate risk based on proximity to known flood-prone areas
        # Kelantan flood-prone coordinates (approximate)
        flood_prone_areas = [
            (6.1254, 102.2386),  # Kota Bharu
            (5.4141, 102.0882),  # Kuala Krai
            (4.9667, 101.8833),  # Gua Musang
        ]
        
        min_distance = min([
            ((latitude - lat) ** 2 + (longitude - lng) ** 2) ** 0.5
            for lat, lng in flood_prone_areas
        ])
        
        # Convert distance to risk (closer = higher risk)
        base_risk = max(0.1, 1.0 - min_distance * 10)
        
        return {
            'base_risk': base_risk,
            'location': {'latitude': latitude, 'longitude': longitude},
            'nearest_flood_zone': min_distance < 0.1
        }
    
    async def get_regional_risk_summary(self) -> Dict:
        """Get risk summary for Kelantan region"""
        # Mock regional risk data
        districts = [
            {"name": "Kota Bharu", "risk_level": "high", "probability": 0.7},
            {"name": "Kuala Krai", "risk_level": "extreme", "probability": 0.85},
            {"name": "Machang", "risk_level": "medium", "probability": 0.4},
            {"name": "Pasir Mas", "risk_level": "high", "probability": 0.65},
            {"name": "Tanah Merah", "risk_level": "medium", "probability": 0.35},
            {"name": "Bachok", "risk_level": "low", "probability": 0.15},
            {"name": "Tumpat", "risk_level": "medium", "probability": 0.3},
            {"name": "Pasir Puteh", "risk_level": "low", "probability": 0.2},
            {"name": "Gua Musang", "risk_level": "medium", "probability": 0.45},
            {"name": "Jeli", "risk_level": "low", "probability": 0.25}
        ]
        
        return {
            'districts': districts,
            'overall_risk': 'medium',
            'high_risk_districts': [d['name'] for d in districts if d['risk_level'] in ['high', 'extreme']],
            'last_updated': datetime.now().isoformat()
        }
    
    def is_loaded(self) -> bool:
        """Check if model is loaded and ready"""
        return self.is_trained or self.model is not None