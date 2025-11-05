"""
Weather Service for fetching meteorological data
Integrates with Malaysian Meteorological Department and other weather APIs
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random
import math
from config.settings import settings

class WeatherService:
    def __init__(self):
        self.session = None
        self.cache = {}
        self.cache_ttl = 1800  # 30 minutes
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_forecast(self, latitude: float, longitude: float, 
                          days: int = 7) -> Dict:
        """Get weather forecast for location"""
        cache_key = f"forecast_{latitude}_{longitude}_{days}"
        
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # In production, this would call actual weather APIs
            # For now, simulate realistic weather data for Kelantan
            forecast_data = await self._simulate_weather_forecast(
                latitude, longitude, days
            )
            
            self._cache_data(cache_key, forecast_data)
            return forecast_data
            
        except Exception as e:
            print(f"Error fetching weather forecast: {e}")
            return self._get_default_weather_data()
    
    async def _simulate_weather_forecast(self, lat: float, lng: float, 
                                        days: int) -> Dict:
        """Simulate realistic weather forecast for Kelantan"""
        
        current_date = datetime.now()
        current_month = current_date.month
        
        # Kelantan climate patterns
        # Wet season: Nov-Mar (Northeast monsoon), May-Sep (Southwest monsoon)
        # Dry season: Apr, Oct
        
        base_temp = self._get_base_temperature(current_month)
        base_humidity = self._get_base_humidity(current_month)
        base_rainfall_prob = self._get_rainfall_probability(current_month)
        
        # Generate daily forecasts
        daily_forecasts = []
        cumulative_rainfall_7d = 0
        
        for day in range(days):
            forecast_date = current_date + timedelta(days=day)
            
            # Temperature (°C)
            temp_variation = random.uniform(-3, 3)
            temperature = base_temp + temp_variation
            
            # Humidity (%)
            humidity_variation = random.uniform(-10, 10)
            humidity = max(60, min(95, base_humidity + humidity_variation))
            
            # Wind speed (km/h)
            wind_speed = random.uniform(5, 25)
            if current_month in [11, 12, 1, 2]:  # Monsoon season
                wind_speed += random.uniform(5, 15)
            
            # Rainfall
            will_rain = random.random() < base_rainfall_prob
            rainfall_24h = 0
            if will_rain:
                # Rainfall intensity based on season
                if current_month in [11, 12, 1]:  # Peak monsoon
                    rainfall_24h = random.uniform(10, 150)
                    if random.random() < 0.1:  # 10% chance of heavy rain
                        rainfall_24h = random.uniform(100, 300)
                elif current_month in [6, 7, 8]:  # Southwest monsoon
                    rainfall_24h = random.uniform(5, 80)
                else:  # Other months
                    rainfall_24h = random.uniform(2, 40)
            
            cumulative_rainfall_7d += rainfall_24h
            
            # Weather condition
            if rainfall_24h > 50:
                condition = "heavy_rain"
            elif rainfall_24h > 10:
                condition = "rain"
            elif humidity > 85:
                condition = "cloudy"
            else:
                condition = "partly_cloudy"
            
            daily_forecast = {
                'date': forecast_date.strftime('%Y-%m-%d'),
                'temperature': round(temperature, 1),
                'humidity': round(humidity, 1),
                'wind_speed': round(wind_speed, 1),
                'rainfall_24h': round(rainfall_24h, 1),
                'condition': condition,
                'pressure': random.uniform(1008, 1018)  # hPa
            }
            
            daily_forecasts.append(daily_forecast)
        
        # Calculate summary statistics
        total_rainfall = sum(day['rainfall_24h'] for day in daily_forecasts)
        avg_temperature = sum(day['temperature'] for day in daily_forecasts) / len(daily_forecasts)
        avg_humidity = sum(day['humidity'] for day in daily_forecasts) / len(daily_forecasts)
        max_wind_speed = max(day['wind_speed'] for day in daily_forecasts)
        
        return {
            'location': {'latitude': lat, 'longitude': lng},
            'forecast_period_days': days,
            'generated_at': datetime.now().isoformat(),
            'daily_forecasts': daily_forecasts,
            'summary': {
                'total_rainfall': round(total_rainfall, 1),
                'rainfall_7d': round(cumulative_rainfall_7d, 1),
                'avg_temperature': round(avg_temperature, 1),
                'avg_humidity': round(avg_humidity, 1),
                'max_wind_speed': round(max_wind_speed, 1),
                'rainy_days': len([d for d in daily_forecasts if d['rainfall_24h'] > 1])
            },
            'alerts': self._generate_weather_alerts(daily_forecasts)
        }
    
    def _get_base_temperature(self, month: int) -> float:
        """Get base temperature for month in Kelantan"""
        # Kelantan temperature patterns (°C)
        temp_by_month = {
            1: 26, 2: 27, 3: 28, 4: 29, 5: 29,
            6: 28, 7: 28, 8: 28, 9: 28, 10: 28,
            11: 27, 12: 26
        }
        return temp_by_month.get(month, 28)
    
    def _get_base_humidity(self, month: int) -> float:
        """Get base humidity for month in Kelantan"""
        # Kelantan humidity patterns (%)
        humidity_by_month = {
            1: 85, 2: 82, 3: 80, 4: 78, 5: 80,
            6: 82, 7: 83, 8: 83, 9: 84, 10: 85,
            11: 87, 12: 88
        }
        return humidity_by_month.get(month, 82)
    
    def _get_rainfall_probability(self, month: int) -> float:
        """Get rainfall probability for month in Kelantan"""
        # Kelantan rainfall probability by month
        rainfall_prob_by_month = {
            1: 0.7,   # Northeast monsoon peak
            2: 0.6,   # Northeast monsoon
            3: 0.4,   # Transition
            4: 0.3,   # Dry season
            5: 0.5,   # Pre-southwest monsoon
            6: 0.6,   # Southwest monsoon
            7: 0.6,   # Southwest monsoon
            8: 0.5,   # Southwest monsoon
            9: 0.4,   # Post-southwest monsoon
            10: 0.3,  # Dry season
            11: 0.8,  # Northeast monsoon starts
            12: 0.9   # Northeast monsoon peak
        }
        return rainfall_prob_by_month.get(month, 0.5)
    
    def _generate_weather_alerts(self, daily_forecasts: List[Dict]) -> List[Dict]:
        """Generate weather alerts based on forecast"""
        alerts = []
        
        # Check for heavy rainfall
        for day in daily_forecasts:
            if day['rainfall_24h'] > 100:
                alerts.append({
                    'type': 'heavy_rain',
                    'severity': 'high',
                    'date': day['date'],
                    'message': f"Heavy rainfall expected: {day['rainfall_24h']:.1f}mm"
                })
            elif day['rainfall_24h'] > 50:
                alerts.append({
                    'type': 'moderate_rain',
                    'severity': 'medium',
                    'date': day['date'],
                    'message': f"Moderate rainfall expected: {day['rainfall_24h']:.1f}mm"
                })
        
        # Check for prolonged rainfall
        consecutive_rainy_days = 0
        for day in daily_forecasts:
            if day['rainfall_24h'] > 10:
                consecutive_rainy_days += 1
            else:
                if consecutive_rainy_days >= 3:
                    alerts.append({
                        'type': 'prolonged_rain',
                        'severity': 'medium',
                        'message': f"Prolonged rainfall period: {consecutive_rainy_days} consecutive days"
                    })
                consecutive_rainy_days = 0
        
        # Check for strong winds
        for day in daily_forecasts:
            if day['wind_speed'] > 40:
                alerts.append({
                    'type': 'strong_wind',
                    'severity': 'medium',
                    'date': day['date'],
                    'message': f"Strong winds expected: {day['wind_speed']:.1f} km/h"
                })
        
        return alerts
    
    def _get_default_weather_data(self) -> Dict:
        """Return default weather data when API fails"""
        return {
            'location': {'latitude': 0, 'longitude': 0},
            'forecast_period_days': 7,
            'generated_at': datetime.now().isoformat(),
            'daily_forecasts': [{
                'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                'temperature': 28,
                'humidity': 80,
                'wind_speed': 10,
                'rainfall_24h': 0,
                'condition': 'partly_cloudy',
                'pressure': 1013
            } for i in range(7)],
            'summary': {
                'total_rainfall': 0,
                'rainfall_7d': 0,
                'avg_temperature': 28,
                'avg_humidity': 80,
                'max_wind_speed': 10,
                'rainy_days': 0
            },
            'alerts': []
        }
    
    async def get_current_conditions(self, latitude: float, longitude: float) -> Dict:
        """Get current weather conditions"""
        cache_key = f"current_{latitude}_{longitude}"
        
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # Simulate current conditions
            current_month = datetime.now().month
            
            conditions = {
                'location': {'latitude': latitude, 'longitude': longitude},
                'timestamp': datetime.now().isoformat(),
                'temperature': self._get_base_temperature(current_month) + random.uniform(-2, 2),
                'humidity': self._get_base_humidity(current_month) + random.uniform(-5, 5),
                'wind_speed': random.uniform(5, 20),
                'pressure': random.uniform(1010, 1016),
                'visibility': random.uniform(8, 15),  # km
                'condition': random.choice(['clear', 'partly_cloudy', 'cloudy', 'rain']),
                'rainfall_1h': random.uniform(0, 10) if random.random() < 0.3 else 0
            }
            
            self._cache_data(cache_key, conditions)
            return conditions
            
        except Exception as e:
            print(f"Error fetching current conditions: {e}")
            return {
                'location': {'latitude': latitude, 'longitude': longitude},
                'timestamp': datetime.now().isoformat(),
                'temperature': 28,
                'humidity': 80,
                'wind_speed': 10,
                'pressure': 1013,
                'visibility': 10,
                'condition': 'partly_cloudy',
                'rainfall_1h': 0
            }
    
    async def get_historical_weather(self, latitude: float, longitude: float,
                                    start_date: str, end_date: str) -> Dict:
        """Get historical weather data"""
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            historical_data = []
            current_date = start
            
            while current_date <= end:
                month = current_date.month
                
                # Simulate historical data
                daily_data = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'temperature_max': self._get_base_temperature(month) + random.uniform(0, 4),
                    'temperature_min': self._get_base_temperature(month) + random.uniform(-4, 0),
                    'humidity': self._get_base_humidity(month) + random.uniform(-10, 10),
                    'rainfall': random.uniform(0, 50) if random.random() < self._get_rainfall_probability(month) else 0,
                    'wind_speed': random.uniform(5, 25)
                }
                
                historical_data.append(daily_data)
                current_date += timedelta(days=1)
            
            # Calculate statistics
            total_rainfall = sum(day['rainfall'] for day in historical_data)
            avg_temp = sum((day['temperature_max'] + day['temperature_min']) / 2 for day in historical_data) / len(historical_data)
            rainy_days = len([day for day in historical_data if day['rainfall'] > 1])
            
            return {
                'location': {'latitude': latitude, 'longitude': longitude},
                'period': {'start': start_date, 'end': end_date},
                'daily_data': historical_data,
                'statistics': {
                    'total_rainfall': round(total_rainfall, 1),
                    'average_temperature': round(avg_temp, 1),
                    'rainy_days': rainy_days,
                    'max_daily_rainfall': max(day['rainfall'] for day in historical_data)
                }
            }
            
        except Exception as e:
            print(f"Error fetching historical weather: {e}")
            return {'error': str(e)}
    
    async def get_monsoon_status(self) -> Dict:
        """Get current monsoon status for Malaysia"""
        
        current_date = datetime.now()
        month = current_date.month
        
        # Determine monsoon season
        if month in [11, 12, 1, 2]:
            monsoon_type = "Northeast Monsoon"
            intensity = "high" if month in [12, 1] else "moderate"
            description = "Wet season with heavy rainfall expected"
        elif month in [6, 7, 8]:
            monsoon_type = "Southwest Monsoon"
            intensity = "moderate"
            description = "Moderate rainfall with occasional heavy showers"
        elif month in [3, 4, 5]:
            monsoon_type = "Inter-monsoon"
            intensity = "low"
            description = "Transition period with scattered showers"
        else:  # 9, 10
            monsoon_type = "Inter-monsoon"
            intensity = "low"
            description = "Generally dry with occasional showers"
        
        return {
            'current_monsoon': monsoon_type,
            'intensity': intensity,
            'description': description,
            'peak_months': self._get_peak_months(monsoon_type),
            'rainfall_expectation': self._get_rainfall_expectation(intensity),
            'flood_risk_level': self._get_flood_risk_from_monsoon(intensity),
            'last_updated': current_date.isoformat()
        }
    
    def _get_peak_months(self, monsoon_type: str) -> List[str]:
        """Get peak months for monsoon type"""
        if "Northeast" in monsoon_type:
            return ["December", "January"]
        elif "Southwest" in monsoon_type:
            return ["June", "July"]
        else:
            return []
    
    def _get_rainfall_expectation(self, intensity: str) -> str:
        """Get rainfall expectation based on intensity"""
        expectations = {
            "high": "200-400mm per month",
            "moderate": "100-200mm per month",
            "low": "50-100mm per month"
        }
        return expectations.get(intensity, "Variable")
    
    def _get_flood_risk_from_monsoon(self, intensity: str) -> str:
        """Get flood risk level from monsoon intensity"""
        risk_levels = {
            "high": "elevated",
            "moderate": "moderate",
            "low": "low"
        }
        return risk_levels.get(intensity, "low")
    
    def _is_cached(self, key: str) -> bool:
        """Check if data is cached and still valid"""
        if key not in self.cache:
            return False
        
        cached_time = self.cache[key]['timestamp']
        return (datetime.now() - cached_time).seconds < self.cache_ttl
    
    def _cache_data(self, key: str, data: Any):
        """Cache data with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }