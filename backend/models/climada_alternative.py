"""
Alternative CLIMADA-like implementation for Python 3.12.3 compatibility
Provides climate risk modeling functionality without requiring the full CLIMADA package
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json
from datetime import datetime, timedelta

@dataclass
class ClimateEvent:
    """Represents a climate event (flood) with intensity and location"""
    event_id: str
    intensity: float  # 0-1 scale
    location: Tuple[float, float]  # (lat, lon)
    timestamp: datetime
    duration_hours: int
    affected_area_km2: float

@dataclass
class Asset:
    """Represents an asset (property) with value and location"""
    asset_id: str
    value: float
    location: Tuple[float, float]  # (lat, lon)
    asset_type: str  # residential, commercial, industrial
    vulnerability: float  # 0-1 scale

@dataclass
class ImpactResult:
    """Results of impact assessment"""
    total_damage: float
    affected_assets: int
    damage_by_asset_type: Dict[str, float]
    damage_distribution: List[float]

class ClimateRiskModel:
    """
    Alternative implementation of climate risk modeling
    Provides similar functionality to CLIMADA for flood risk assessment
    """
    
    def __init__(self):
        self.hazard_data = {}
        self.exposure_data = {}
        self.vulnerability_functions = self._initialize_vulnerability_functions()
        
    def _initialize_vulnerability_functions(self) -> Dict[str, Dict]:
        """Initialize vulnerability functions for different asset types"""
        return {
            "residential": {
                "threshold": 0.1,  # Minimum intensity to cause damage
                "slope": 0.8,      # Damage increase rate
                "max_damage": 0.75 # Maximum damage ratio
            },
            "commercial": {
                "threshold": 0.08,
                "slope": 0.9,
                "max_damage": 0.85
            },
            "industrial": {
                "threshold": 0.12,
                "slope": 0.7,
                "max_damage": 0.9
            }
        }
    
    def load_hazard_data(self, flood_events: List[ClimateEvent]):
        """Load flood hazard data"""
        self.hazard_data = {
            event.event_id: event for event in flood_events
        }
    
    def load_exposure_data(self, assets: List[Asset]):
        """Load asset exposure data"""
        self.exposure_data = {
            asset.asset_id: asset for asset in assets
        }
    
    def calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate distance between two points using Haversine formula"""
        lat1, lon1 = np.radians(point1)
        lat2, lon2 = np.radians(point2)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        r = 6371  # Earth's radius in kilometers
        
        return c * r
    
    def calculate_flood_intensity_at_location(self, event: ClimateEvent, location: Tuple[float, float]) -> float:
        """Calculate flood intensity at a specific location based on distance from event center"""
        distance = self.calculate_distance(event.location, location)
        
        # Intensity decreases with distance (exponential decay)
        max_range = np.sqrt(event.affected_area_km2 / np.pi)  # Approximate radius
        if distance > max_range:
            return 0.0
        
        # Exponential decay with distance
        intensity_factor = np.exp(-distance / (max_range * 0.3))
        return event.intensity * intensity_factor
    
    def calculate_vulnerability_damage(self, asset: Asset, flood_intensity: float) -> float:
        """Calculate damage to an asset based on flood intensity and vulnerability"""
        if asset.asset_type not in self.vulnerability_functions:
            asset_type = "residential"  # Default
        else:
            asset_type = asset.asset_type
        
        vuln_func = self.vulnerability_functions[asset_type]
        
        if flood_intensity < vuln_func["threshold"]:
            return 0.0
        
        # Calculate damage ratio
        damage_ratio = min(
            vuln_func["slope"] * (flood_intensity - vuln_func["threshold"]) * asset.vulnerability,
            vuln_func["max_damage"]
        )
        
        return asset.value * damage_ratio
    
    def run_impact_assessment(self, event_id: str) -> ImpactResult:
        """Run impact assessment for a specific flood event"""
        if event_id not in self.hazard_data:
            raise ValueError(f"Event {event_id} not found in hazard data")
        
        event = self.hazard_data[event_id]
        total_damage = 0.0
        affected_assets = 0
        damage_by_type = {"residential": 0.0, "commercial": 0.0, "industrial": 0.0}
        damage_distribution = []
        
        for asset in self.exposure_data.values():
            # Calculate flood intensity at asset location
            intensity = self.calculate_flood_intensity_at_location(event, asset.location)
            
            if intensity > 0:
                # Calculate damage
                damage = self.calculate_vulnerability_damage(asset, intensity)
                
                if damage > 0:
                    total_damage += damage
                    affected_assets += 1
                    damage_distribution.append(damage)
                    
                    if asset.asset_type in damage_by_type:
                        damage_by_type[asset.asset_type] += damage
                    else:
                        damage_by_type["residential"] += damage  # Default category
        
        return ImpactResult(
            total_damage=total_damage,
            affected_assets=affected_assets,
            damage_by_asset_type=damage_by_type,
            damage_distribution=damage_distribution
        )
    
    def run_probabilistic_assessment(self, return_periods: List[int] = [10, 25, 50, 100]) -> Dict[int, ImpactResult]:
        """Run probabilistic impact assessment for different return periods"""
        results = {}
        
        for return_period in return_periods:
            # Generate synthetic event based on return period
            synthetic_event = self._generate_synthetic_event(return_period)
            
            # Add to hazard data temporarily
            temp_event_id = f"synthetic_{return_period}yr"
            self.hazard_data[temp_event_id] = synthetic_event
            
            # Run assessment
            results[return_period] = self.run_impact_assessment(temp_event_id)
            
            # Clean up
            del self.hazard_data[temp_event_id]
        
        return results
    
    def _generate_synthetic_event(self, return_period: int) -> ClimateEvent:
        """Generate a synthetic flood event based on return period"""
        # Kelantan center coordinates
        center_lat, center_lon = 5.8, 102.0
        
        # Intensity increases with return period
        intensity_map = {10: 0.4, 25: 0.6, 50: 0.8, 100: 0.95}
        intensity = intensity_map.get(return_period, 0.5)
        
        # Affected area increases with return period
        area_map = {10: 500, 25: 1000, 50: 2000, 100: 4000}  # km²
        affected_area = area_map.get(return_period, 1000)
        
        return ClimateEvent(
            event_id=f"synthetic_{return_period}yr",
            intensity=intensity,
            location=(center_lat, center_lon),
            timestamp=datetime.now(),
            duration_hours=24 + (return_period // 10),  # Longer events for higher return periods
            affected_area_km2=affected_area
        )
    
    def export_results(self, results: Dict, filename: str):
        """Export results to JSON file"""
        serializable_results = {}
        
        for key, result in results.items():
            if isinstance(result, ImpactResult):
                serializable_results[str(key)] = {
                    "total_damage": result.total_damage,
                    "affected_assets": result.affected_assets,
                    "damage_by_asset_type": result.damage_by_asset_type,
                    "damage_statistics": {
                        "mean": np.mean(result.damage_distribution) if result.damage_distribution else 0,
                        "std": np.std(result.damage_distribution) if result.damage_distribution else 0,
                        "max": max(result.damage_distribution) if result.damage_distribution else 0
                    }
                }
        
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2)

class KelantanFloodModel(ClimateRiskModel):
    """
    Specialized flood model for Kelantan, Malaysia
    """
    
    def __init__(self):
        super().__init__()
        self.kelantan_districts = [
            "Kota Bharu", "Pasir Mas", "Tumpat", "Pasir Puteh", 
            "Bachok", "Kuala Krai", "Machang", "Tanah Merah", 
            "Jeli", "Gua Musang"
        ]
        self.district_coordinates = {
            "Kota Bharu": (6.1254, 102.2386),
            "Pasir Mas": (6.0469, 102.1394),
            "Tumpat": (6.2000, 102.1667),
            "Pasir Puteh": (5.8269, 102.4061),
            "Bachok": (6.0167, 102.4167),
            "Kuala Krai": (5.5333, 102.2000),
            "Machang": (5.7667, 102.2167),
            "Tanah Merah": (5.8000, 102.1500),
            "Jeli": (5.7000, 101.8333),
            "Gua Musang": (4.8833, 101.9667)
        }
    
    def generate_kelantan_assets(self, num_assets: int = 1000) -> List[Asset]:
        """Generate synthetic assets distributed across Kelantan districts"""
        assets = []
        
        for i in range(num_assets):
            # Randomly select a district
            district = np.random.choice(self.kelantan_districts)
            base_lat, base_lon = self.district_coordinates[district]
            
            # Add some random variation around district center
            lat = base_lat + np.random.normal(0, 0.05)  # ~5km variation
            lon = base_lon + np.random.normal(0, 0.05)
            
            # Random asset properties
            asset_types = ["residential", "commercial", "industrial"]
            asset_type = np.random.choice(asset_types, p=[0.7, 0.25, 0.05])
            
            # Value based on asset type
            if asset_type == "residential":
                value = np.random.lognormal(12, 0.5)  # ~200k-500k MYR
            elif asset_type == "commercial":
                value = np.random.lognormal(14, 0.7)  # ~1M-3M MYR
            else:  # industrial
                value = np.random.lognormal(15, 0.8)  # ~3M-10M MYR
            
            vulnerability = np.random.beta(2, 3)  # Skewed towards lower vulnerability
            
            assets.append(Asset(
                asset_id=f"asset_{i:04d}",
                value=value,
                location=(lat, lon),
                asset_type=asset_type,
                vulnerability=vulnerability
            ))
        
        return assets
    
    def generate_historical_floods(self, num_events: int = 50) -> List[ClimateEvent]:
        """Generate synthetic historical flood events for Kelantan"""
        events = []
        
        # High-risk areas (based on historical data)
        high_risk_areas = [
            (6.0469, 102.1394),  # Pasir Mas
            (5.5333, 102.2000),  # Kuala Krai
            (6.1254, 102.2386),  # Kota Bharu
            (6.2000, 102.1667),  # Tumpat
        ]
        
        for i in range(num_events):
            # Select event center (bias towards high-risk areas)
            if np.random.random() < 0.6:  # 60% chance in high-risk area
                center = high_risk_areas[np.random.randint(len(high_risk_areas))]
                lat, lon = center[0] + np.random.normal(0, 0.02), center[1] + np.random.normal(0, 0.02)
            else:
                # Random location in Kelantan
                lat = np.random.uniform(4.5, 6.2)
                lon = np.random.uniform(101.2, 102.5)
            
            # Event properties
            intensity = np.random.beta(2, 5)  # Skewed towards lower intensities
            affected_area = np.random.lognormal(6, 1)  # 100-2000 km²
            duration = np.random.randint(6, 72)  # 6-72 hours
            
            # Random timestamp in the past 10 years
            days_ago = np.random.randint(0, 3650)
            timestamp = datetime.now() - timedelta(days=days_ago)
            
            events.append(ClimateEvent(
                event_id=f"flood_{i:03d}",
                intensity=intensity,
                location=(lat, lon),
                timestamp=timestamp,
                duration_hours=duration,
                affected_area_km2=affected_area
            ))
        
        return events