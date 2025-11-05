"""
Data Service for accessing various data sources
Integrates meteorological, hydrological, and geographical data
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import random
from config.settings import settings

class DataService:
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
    
    async def get_geographical_data(self, latitude: float, longitude: float) -> Dict:
        """Get geographical data for a location"""
        cache_key = f"geo_{latitude}_{longitude}"
        
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # In a real implementation, this would call actual APIs
            # For now, we'll simulate based on Kelantan geography
            
            geo_data = await self._simulate_geographical_data(latitude, longitude)
            
            self._cache_data(cache_key, geo_data)
            return geo_data
            
        except Exception as e:
            print(f"Error fetching geographical data: {e}")
            return self._get_default_geo_data()
    
    async def _simulate_geographical_data(self, lat: float, lng: float) -> Dict:
        """Simulate geographical data based on Kelantan characteristics"""
        
        # Kelantan elevation patterns (simplified)
        # Coastal areas: 0-20m, Inland: 20-200m, Mountainous: 200m+
        if lng > 102.3:  # Eastern coastal areas
            elevation = random.uniform(0, 30)
            distance_to_river = random.uniform(500, 3000)
        elif lng > 102.0:  # Central areas
            elevation = random.uniform(20, 100)
            distance_to_river = random.uniform(200, 2000)
        else:  # Western mountainous areas
            elevation = random.uniform(100, 500)
            distance_to_river = random.uniform(1000, 5000)
        
        # Calculate slope (simplified)
        slope = max(0.1, elevation / 100)
        
        # Land cover type (encoded)
        # 1=urban, 2=forest, 3=agriculture, 4=water
        if elevation < 20:
            land_cover = random.choice([1, 3])  # Urban or agriculture in low areas
        elif elevation < 100:
            land_cover = random.choice([2, 3])  # Forest or agriculture
        else:
            land_cover = 2  # Mostly forest in mountains
        
        # Soil saturation (0-1 scale)
        base_saturation = 0.3
        if elevation < 20:
            base_saturation += 0.2  # Higher saturation in low areas
        
        # Drainage density (km/km²)
        drainage_density = random.uniform(0.3, 1.2)
        
        return {
            'elevation': elevation,
            'slope': slope,
            'distance_to_river': distance_to_river,
            'land_cover_type': land_cover,
            'soil_saturation': base_saturation,
            'drainage_density': drainage_density,
            'coordinates': {'latitude': lat, 'longitude': lng}
        }
    
    def _get_default_geo_data(self) -> Dict:
        """Return default geographical data"""
        return {
            'elevation': 50,
            'slope': 2,
            'distance_to_river': 1000,
            'land_cover_type': 2,
            'soil_saturation': 0.3,
            'drainage_density': 0.5
        }
    
    async def get_historical_floods(self, latitude: float, longitude: float, 
                                   radius_km: float = 10) -> Dict:
        """Get historical flood data for a location"""
        cache_key = f"hist_floods_{latitude}_{longitude}_{radius_km}"
        
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # Simulate historical flood data
            historical_data = await self._simulate_historical_floods(latitude, longitude)
            
            self._cache_data(cache_key, historical_data)
            return historical_data
            
        except Exception as e:
            print(f"Error fetching historical flood data: {e}")
            return {'flood_frequency': 0, 'last_flood': None, 'max_severity': 0}
    
    async def _simulate_historical_floods(self, lat: float, lng: float) -> Dict:
        """Simulate historical flood data based on known Kelantan flood patterns"""
        
        # Major flood years in Kelantan: 2014, 2017, 2019, 2021
        flood_years = [2014, 2017, 2019, 2021]
        
        # Determine flood frequency based on location
        # Areas closer to rivers and lower elevation have higher frequency
        base_frequency = 0.1  # 10% annual probability
        
        # Adjust based on coordinates (simplified)
        if lng > 102.2:  # Eastern areas (more flood-prone)
            base_frequency *= 1.5
        if lat > 5.8:  # Northern areas
            base_frequency *= 1.2
        
        # Generate flood events
        flood_events = []
        for year in flood_years:
            if random.random() < base_frequency * 2:  # Higher chance in known flood years
                severity = random.uniform(0.3, 0.9)
                flood_events.append({
                    'year': year,
                    'severity': severity,
                    'duration_days': random.randint(3, 21),
                    'estimated_depth': severity * 2.5  # meters
                })
        
        # Add some random events
        for year in range(2010, 2024):
            if year not in flood_years and random.random() < base_frequency:
                severity = random.uniform(0.1, 0.5)
                flood_events.append({
                    'year': year,
                    'severity': severity,
                    'duration_days': random.randint(1, 7),
                    'estimated_depth': severity * 1.5
                })
        
        # Calculate statistics
        flood_frequency = len(flood_events) / 14  # 14 years of data
        last_flood = max(flood_events, key=lambda x: x['year']) if flood_events else None
        max_severity = max([f['severity'] for f in flood_events]) if flood_events else 0
        
        return {
            'flood_frequency': flood_frequency,
            'flood_events': flood_events,
            'last_flood': last_flood,
            'max_severity': max_severity,
            'total_events': len(flood_events)
        }
    
    async def get_kelantan_districts(self) -> List[Dict]:
        """Get Kelantan districts with boundaries"""
        districts = [
            {
                'name': 'Kota Bharu',
                'code': 'KB',
                'center': {'lat': 6.1254, 'lng': 102.2386},
                'bounds': {
                    'north': 6.2, 'south': 6.0,
                    'east': 102.3, 'west': 102.1
                },
                'population': 491237,
                'area_km2': 394.4,
                'flood_risk': 'high'
            },
            {
                'name': 'Kuala Krai',
                'code': 'KK',
                'center': {'lat': 5.5333, 'lng': 102.2000},
                'bounds': {
                    'north': 5.7, 'south': 5.3,
                    'east': 102.4, 'west': 102.0
                },
                'population': 103404,
                'area_km2': 2329.1,
                'flood_risk': 'extreme'
            },
            {
                'name': 'Machang',
                'code': 'MC',
                'center': {'lat': 5.7667, 'lng': 102.2167},
                'bounds': {
                    'north': 5.9, 'south': 5.6,
                    'east': 102.4, 'west': 102.0
                },
                'population': 95639,
                'area_km2': 547.5,
                'flood_risk': 'medium'
            },
            {
                'name': 'Pasir Mas',
                'code': 'PM',
                'center': {'lat': 6.0500, 'lng': 102.1333},
                'bounds': {
                    'north': 6.2, 'south': 5.9,
                    'east': 102.3, 'west': 101.9
                },
                'population': 188741,
                'area_km2': 577.5,
                'flood_risk': 'high'
            },
            {
                'name': 'Tanah Merah',
                'code': 'TM',
                'center': {'lat': 5.8000, 'lng': 102.1500},
                'bounds': {
                    'north': 6.0, 'south': 5.6,
                    'east': 102.3, 'west': 101.9
                },
                'population': 121319,
                'area_km2': 865.3,
                'flood_risk': 'medium'
            },
            {
                'name': 'Bachok',
                'code': 'BC',
                'center': {'lat': 6.0167, 'lng': 102.4167},
                'bounds': {
                    'north': 6.2, 'south': 5.8,
                    'east': 102.6, 'west': 102.2
                },
                'population': 140202,
                'area_km2': 379.3,
                'flood_risk': 'low'
            },
            {
                'name': 'Tumpat',
                'code': 'TP',
                'center': {'lat': 6.2000, 'lng': 102.1667},
                'bounds': {
                    'north': 6.3, 'south': 6.1,
                    'east': 102.3, 'west': 102.0
                },
                'population': 156629,
                'area_km2': 169.5,
                'flood_risk': 'medium'
            },
            {
                'name': 'Pasir Puteh',
                'code': 'PP',
                'center': {'lat': 5.8333, 'lng': 102.4000},
                'bounds': {
                    'north': 6.0, 'south': 5.6,
                    'east': 102.6, 'west': 102.2
                },
                'population': 119056,
                'area_km2': 433.1,
                'flood_risk': 'low'
            },
            {
                'name': 'Gua Musang',
                'code': 'GM',
                'center': {'lat': 4.8833, 'lng': 101.9667},
                'bounds': {
                    'north': 5.5, 'south': 4.2,
                    'east': 102.2, 'west': 101.7
                },
                'population': 90057,
                'area_km2': 8611.0,
                'flood_risk': 'medium'
            },
            {
                'name': 'Jeli',
                'code': 'JL',
                'center': {'lat': 5.7000, 'lng': 101.8500},
                'bounds': {
                    'north': 6.0, 'south': 5.4,
                    'east': 102.0, 'west': 101.7
                },
                'population': 42882,
                'area_km2': 1330.6,
                'flood_risk': 'low'
            }
        ]
        
        return districts
    
    async def get_historical_floods_data(self, start_date: Optional[str] = None,
                                        end_date: Optional[str] = None,
                                        district: Optional[str] = None) -> List[Dict]:
        """Get historical flood events data"""
        
        # Generate sample historical flood data
        flood_events = []
        
        # Major flood events in Kelantan
        major_events = [
            {
                'date': '2014-12-15',
                'district': 'Kuala Krai',
                'severity': 'extreme',
                'affected_area_km2': 500,
                'displaced_people': 15000,
                'economic_loss_myr': 500000000,
                'max_depth_m': 3.5,
                'duration_days': 14
            },
            {
                'date': '2014-12-20',
                'district': 'Kota Bharu',
                'severity': 'high',
                'affected_area_km2': 200,
                'displaced_people': 8000,
                'economic_loss_myr': 200000000,
                'max_depth_m': 2.1,
                'duration_days': 10
            },
            {
                'date': '2017-01-03',
                'district': 'Pasir Mas',
                'severity': 'high',
                'affected_area_km2': 150,
                'displaced_people': 5000,
                'economic_loss_myr': 150000000,
                'max_depth_m': 1.8,
                'duration_days': 7
            },
            {
                'date': '2019-12-28',
                'district': 'Machang',
                'severity': 'medium',
                'affected_area_km2': 80,
                'displaced_people': 2000,
                'economic_loss_myr': 50000000,
                'max_depth_m': 1.2,
                'duration_days': 5
            },
            {
                'date': '2021-01-15',
                'district': 'Tanah Merah',
                'severity': 'medium',
                'affected_area_km2': 100,
                'displaced_people': 3000,
                'economic_loss_myr': 75000000,
                'max_depth_m': 1.5,
                'duration_days': 6
            }
        ]
        
        # Filter by district if specified
        if district:
            major_events = [e for e in major_events if e['district'] == district]
        
        # Filter by date range if specified
        if start_date or end_date:
            filtered_events = []
            for event in major_events:
                event_date = datetime.strptime(event['date'], '%Y-%m-%d')
                
                include = True
                if start_date:
                    start = datetime.strptime(start_date, '%Y-%m-%d')
                    if event_date < start:
                        include = False
                
                if end_date:
                    end = datetime.strptime(end_date, '%Y-%m-%d')
                    if event_date > end:
                        include = False
                
                if include:
                    filtered_events.append(event)
            
            major_events = filtered_events
        
        return major_events
    
    async def get_current_alerts(self) -> List[Dict]:
        """Get current flood alerts and warnings"""
        
        # Simulate current alerts based on time of year
        current_month = datetime.now().month
        alerts = []
        
        # Higher alert probability during monsoon seasons
        if current_month in [11, 12, 1, 2]:  # Northeast monsoon
            alert_probability = 0.7
        elif current_month in [6, 7, 8]:  # Southwest monsoon
            alert_probability = 0.4
        else:
            alert_probability = 0.2
        
        if random.random() < alert_probability:
            districts = ['Kota Bharu', 'Kuala Krai', 'Pasir Mas']
            for district in districts:
                if random.random() < 0.5:
                    alert_level = random.choice(['yellow', 'orange', 'red'])
                    alerts.append({
                        'district': district,
                        'alert_level': alert_level,
                        'type': 'flood_warning',
                        'issued_at': datetime.now().isoformat(),
                        'valid_until': (datetime.now() + timedelta(hours=24)).isoformat(),
                        'description': f"{alert_level.title()} flood warning for {district}"
                    })
        
        return alerts
    
    async def get_recent_predictions(self) -> List[Dict]:
        """Get recent flood predictions"""
        
        predictions = []
        districts = await self.get_kelantan_districts()
        
        for district in districts[:5]:  # Get predictions for first 5 districts
            prediction = {
                'district': district['name'],
                'coordinates': district['center'],
                'flood_probability': random.uniform(0.1, 0.8),
                'risk_level': random.choice(['low', 'medium', 'high']),
                'predicted_at': (datetime.now() - timedelta(hours=random.randint(1, 12))).isoformat(),
                'valid_for_hours': 24
            }
            predictions.append(prediction)
        
        return predictions
    
    async def check_data_sources(self) -> Dict:
        """Check status of various data sources"""
        
        # Simulate data source status
        sources = {
            'met_malaysia': {
                'status': 'online',
                'last_update': datetime.now().isoformat(),
                'data_quality': 'good'
            },
            'nahrim': {
                'status': 'online',
                'last_update': (datetime.now() - timedelta(minutes=30)).isoformat(),
                'data_quality': 'good'
            },
            'did_malaysia': {
                'status': 'online',
                'last_update': (datetime.now() - timedelta(hours=1)).isoformat(),
                'data_quality': 'fair'
            },
            'satellite_data': {
                'status': 'online',
                'last_update': (datetime.now() - timedelta(hours=2)).isoformat(),
                'data_quality': 'excellent'
            }
        }
        
        return sources
    
    async def generate_stress_scenario(self, scenario: str, region: str) -> Dict:
        """Generate stress test scenario data"""
        
        scenarios = {
            '100_year_flood': {
                'description': '100-year return period flood event',
                'severity': 'extreme',
                'affected_districts': ['Kota Bharu', 'Kuala Krai', 'Pasir Mas', 'Machang'],
                'duration_days': 21,
                'max_depth_m': 4.0,
                'affected_population_pct': 0.4,
                'economic_impact_multiplier': 3.0
            },
            'river_overflow': {
                'description': 'Major river overflow event',
                'severity': 'high',
                'affected_districts': ['Kuala Krai', 'Pasir Mas', 'Tanah Merah'],
                'duration_days': 14,
                'max_depth_m': 2.5,
                'affected_population_pct': 0.25,
                'economic_impact_multiplier': 2.0
            },
            'coastal_surge': {
                'description': 'Coastal storm surge',
                'severity': 'moderate',
                'affected_districts': ['Kota Bharu', 'Bachok', 'Tumpat'],
                'duration_days': 7,
                'max_depth_m': 1.5,
                'affected_population_pct': 0.15,
                'economic_impact_multiplier': 1.5
            },
            'prolonged_monsoon': {
                'description': 'Extended monsoon season flooding',
                'severity': 'high',
                'affected_districts': ['Kota Bharu', 'Kuala Krai', 'Pasir Mas', 'Machang', 'Tanah Merah'],
                'duration_days': 30,
                'max_depth_m': 2.0,
                'affected_population_pct': 0.35,
                'economic_impact_multiplier': 2.5
            }
        }
        
        scenario_data = scenarios.get(scenario, scenarios['river_overflow'])
        scenario_data['scenario'] = scenario
        scenario_data['region'] = region
        scenario_data['generated_at'] = datetime.now().isoformat()
        
        return scenario_data
    
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