"""
Asset Impact Assessment Model
Calculates financial impact of floods on assets and loan portfolios
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import random
from config.settings import settings

class AssetImpactModel:
    def __init__(self):
        self.damage_curves = self._initialize_damage_curves()
        self.default_probability_model = self._initialize_default_model()
        
    def _initialize_damage_curves(self) -> Dict:
        """Initialize damage curves for different asset types"""
        return {
            'residential': {
                'depth_damage': {
                    0.0: 0.0,    # No flood
                    0.3: 0.05,   # 30cm - minor damage
                    0.6: 0.15,   # 60cm - moderate damage
                    1.0: 0.35,   # 1m - significant damage
                    1.5: 0.55,   # 1.5m - major damage
                    2.0: 0.75,   # 2m+ - severe damage
                    3.0: 0.90    # 3m+ - near total loss
                },
                'duration_multiplier': {
                    1: 1.0,      # 1 day
                    3: 1.2,      # 3 days
                    7: 1.5,      # 1 week
                    14: 1.8,     # 2 weeks
                    30: 2.0      # 1 month+
                }
            },
            'commercial': {
                'depth_damage': {
                    0.0: 0.0,
                    0.3: 0.08,
                    0.6: 0.25,
                    1.0: 0.50,
                    1.5: 0.70,
                    2.0: 0.85,
                    3.0: 0.95
                },
                'duration_multiplier': {
                    1: 1.0,
                    3: 1.3,
                    7: 1.7,
                    14: 2.2,
                    30: 2.5
                }
            },
            'industrial': {
                'depth_damage': {
                    0.0: 0.0,
                    0.3: 0.10,
                    0.6: 0.30,
                    1.0: 0.60,
                    1.5: 0.80,
                    2.0: 0.90,
                    3.0: 0.98
                },
                'duration_multiplier': {
                    1: 1.0,
                    3: 1.4,
                    7: 2.0,
                    14: 2.8,
                    30: 3.0
                }
            }
        }
    
    def _initialize_default_model(self) -> Dict:
        """Initialize loan default probability model parameters"""
        return {
            'base_default_rate': 0.02,  # 2% base default rate
            'damage_elasticity': 2.5,   # How damage affects default probability
            'ltv_factor': 1.5,          # Loan-to-value impact factor
            'insurance_protection': 0.7, # Insurance reduces default risk by 70%
            'recovery_time_factor': 0.1  # Recovery time impact
        }
    
    def assess_impact(self, flood_risk: Dict, asset_type: str, asset_value: float,
                     loan_amount: Optional[float] = None, 
                     insurance_coverage: Optional[float] = None) -> Dict:
        """Assess flood impact on a specific asset"""
        
        # Calculate physical damage
        physical_damage = self._calculate_physical_damage(
            flood_risk, asset_type, asset_value
        )
        
        # Calculate financial impact
        financial_impact = self._calculate_financial_impact(
            physical_damage, asset_value, loan_amount, insurance_coverage
        )
        
        # Calculate loan default probability if loan exists
        default_probability = None
        if loan_amount:
            default_probability = self._calculate_default_probability(
                physical_damage, asset_value, loan_amount, insurance_coverage
            )
        
        return {
            'asset_type': asset_type,
            'asset_value': asset_value,
            'flood_risk_level': flood_risk.get('risk_level', 'unknown'),
            'physical_damage': physical_damage,
            'financial_impact': financial_impact,
            'default_probability': default_probability,
            'recommendations': self._get_impact_recommendations(
                physical_damage, financial_impact, default_probability
            ),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_physical_damage(self, flood_risk: Dict, asset_type: str, 
                                  asset_value: float) -> Dict:
        """Calculate physical damage to asset"""
        
        risk_probability = flood_risk.get('base_risk', 0.1)
        
        # Estimate flood depth based on risk probability
        # Higher risk = potentially deeper flooding
        estimated_depth = self._estimate_flood_depth(risk_probability)
        estimated_duration = self._estimate_flood_duration(risk_probability)
        
        # Get damage curve for asset type
        damage_curve = self.damage_curves.get(asset_type, self.damage_curves['residential'])
        
        # Calculate base damage from depth
        base_damage_ratio = self._interpolate_damage(estimated_depth, damage_curve['depth_damage'])
        
        # Apply duration multiplier
        duration_multiplier = self._interpolate_damage(
            estimated_duration, damage_curve['duration_multiplier']
        )
        
        # Final damage ratio
        total_damage_ratio = min(0.95, base_damage_ratio * duration_multiplier)
        
        # Calculate monetary damage
        damage_amount = asset_value * total_damage_ratio
        
        return {
            'estimated_flood_depth': estimated_depth,
            'estimated_duration_days': estimated_duration,
            'damage_ratio': total_damage_ratio,
            'damage_amount': damage_amount,
            'salvage_value': asset_value - damage_amount
        }
    
    def _estimate_flood_depth(self, risk_probability: float) -> float:
        """Estimate flood depth based on risk probability"""
        # Simple model: higher probability = deeper potential flooding
        if risk_probability >= 0.8:
            return random.uniform(1.5, 3.0)  # Extreme: 1.5-3m
        elif risk_probability >= 0.5:
            return random.uniform(0.8, 2.0)  # High: 0.8-2m
        elif risk_probability >= 0.2:
            return random.uniform(0.3, 1.0)  # Medium: 0.3-1m
        else:
            return random.uniform(0.0, 0.5)  # Low: 0-0.5m
    
    def _estimate_flood_duration(self, risk_probability: float) -> int:
        """Estimate flood duration based on risk probability"""
        if risk_probability >= 0.8:
            return random.randint(7, 30)     # Extreme: 1-4 weeks
        elif risk_probability >= 0.5:
            return random.randint(3, 14)     # High: 3-14 days
        elif risk_probability >= 0.2:
            return random.randint(1, 7)      # Medium: 1-7 days
        else:
            return random.randint(1, 3)      # Low: 1-3 days
    
    def _interpolate_damage(self, value: float, damage_dict: Dict) -> float:
        """Interpolate damage ratio from damage curve"""
        keys = sorted(damage_dict.keys())
        
        if value <= keys[0]:
            return damage_dict[keys[0]]
        if value >= keys[-1]:
            return damage_dict[keys[-1]]
        
        # Find surrounding points
        for i in range(len(keys) - 1):
            if keys[i] <= value <= keys[i + 1]:
                # Linear interpolation
                x1, x2 = keys[i], keys[i + 1]
                y1, y2 = damage_dict[x1], damage_dict[x2]
                return y1 + (y2 - y1) * (value - x1) / (x2 - x1)
        
        return 0.0
    
    def _calculate_financial_impact(self, physical_damage: Dict, asset_value: float,
                                   loan_amount: Optional[float], 
                                   insurance_coverage: Optional[float]) -> Dict:
        """Calculate financial impact including insurance and loan considerations"""
        
        damage_amount = physical_damage['damage_amount']
        
        # Calculate insurance payout
        insurance_payout = 0
        if insurance_coverage:
            insurance_payout = min(insurance_coverage, damage_amount)
        
        # Net loss after insurance
        net_loss = damage_amount - insurance_payout
        
        # Calculate impact on loan if exists
        loan_impact = {}
        if loan_amount:
            remaining_asset_value = asset_value - damage_amount
            ltv_after_damage = loan_amount / max(remaining_asset_value, 1)
            
            loan_impact = {
                'original_ltv': loan_amount / asset_value,
                'ltv_after_damage': ltv_after_damage,
                'underwater_amount': max(0, loan_amount - remaining_asset_value),
                'equity_loss': min(asset_value - loan_amount, damage_amount)
            }
        
        return {
            'gross_damage': damage_amount,
            'insurance_payout': insurance_payout,
            'net_loss': net_loss,
            'loss_ratio': net_loss / asset_value,
            'loan_impact': loan_impact
        }
    
    def _calculate_default_probability(self, physical_damage: Dict, asset_value: float,
                                      loan_amount: float, 
                                      insurance_coverage: Optional[float]) -> Dict:
        """Calculate probability of loan default due to flood damage"""
        
        model = self.default_probability_model
        base_rate = model['base_default_rate']
        
        # Damage impact
        damage_ratio = physical_damage['damage_ratio']
        damage_impact = (damage_ratio ** model['damage_elasticity']) * 0.5
        
        # LTV impact
        original_ltv = loan_amount / asset_value
        ltv_impact = max(0, (original_ltv - 0.8) * model['ltv_factor'])
        
        # Insurance protection
        insurance_protection = 0
        if insurance_coverage:
            coverage_ratio = insurance_coverage / asset_value
            insurance_protection = coverage_ratio * model['insurance_protection'] * damage_ratio
        
        # Recovery time impact
        recovery_days = physical_damage.get('estimated_duration_days', 7)
        recovery_impact = (recovery_days / 30) * model['recovery_time_factor']
        
        # Calculate total default probability
        default_prob = base_rate + damage_impact + ltv_impact + recovery_impact - insurance_protection
        default_prob = max(0.001, min(0.95, default_prob))  # Clamp between 0.1% and 95%
        
        return {
            'default_probability': default_prob,
            'base_rate': base_rate,
            'damage_impact': damage_impact,
            'ltv_impact': ltv_impact,
            'insurance_protection': insurance_protection,
            'recovery_impact': recovery_impact,
            'risk_category': self._categorize_default_risk(default_prob)
        }
    
    def _categorize_default_risk(self, probability: float) -> str:
        """Categorize default risk level"""
        if probability >= 0.5:
            return "extreme"
        elif probability >= 0.2:
            return "high"
        elif probability >= 0.05:
            return "medium"
        else:
            return "low"
    
    def _get_impact_recommendations(self, physical_damage: Dict, 
                                   financial_impact: Dict,
                                   default_probability: Optional[Dict]) -> List[str]:
        """Generate recommendations based on impact assessment"""
        recommendations = []
        
        damage_ratio = physical_damage['damage_ratio']
        net_loss_ratio = financial_impact['loss_ratio']
        
        # Physical damage recommendations
        if damage_ratio > 0.7:
            recommendations.append("Consider total loss claim and replacement")
        elif damage_ratio > 0.3:
            recommendations.append("Significant repairs required - obtain professional assessment")
        elif damage_ratio > 0.1:
            recommendations.append("Minor to moderate repairs needed")
        
        # Financial recommendations
        if net_loss_ratio > 0.5:
            recommendations.append("Severe financial impact - consider emergency funding options")
        elif net_loss_ratio > 0.2:
            recommendations.append("Substantial financial impact - review insurance coverage")
        
        # Default risk recommendations
        if default_probability:
            default_risk = default_probability['risk_category']
            if default_risk in ['high', 'extreme']:
                recommendations.extend([
                    "High default risk - contact lender immediately",
                    "Consider loan modification or forbearance options",
                    "Explore disaster relief programs"
                ])
            elif default_risk == 'medium':
                recommendations.append("Monitor financial situation closely")
        
        # Insurance recommendations
        insurance_payout = financial_impact.get('insurance_payout', 0)
        gross_damage = financial_impact.get('gross_damage', 0)
        
        if insurance_payout < gross_damage * 0.5:
            recommendations.append("Consider increasing insurance coverage for future protection")
        
        return recommendations
    
    def run_stress_test(self, scenario_data: Dict, portfolio_size: int) -> Dict:
        """Run systemic stress test on a loan portfolio"""
        
        scenario = scenario_data['scenario']
        severity = scenario_data.get('severity', 'moderate')
        
        # Generate synthetic portfolio
        portfolio = self._generate_synthetic_portfolio(portfolio_size)
        
        # Apply stress scenario
        stressed_portfolio = self._apply_stress_scenario(portfolio, scenario_data)
        
        # Calculate aggregate impacts
        results = self._calculate_portfolio_impact(stressed_portfolio)
        
        return {
            'scenario': scenario,
            'severity': severity,
            'portfolio_size': portfolio_size,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_synthetic_portfolio(self, size: int) -> List[Dict]:
        """Generate synthetic loan portfolio for stress testing"""
        portfolio = []
        
        asset_types = ['residential', 'commercial', 'industrial']
        districts = ['Kota Bharu', 'Kuala Krai', 'Machang', 'Pasir Mas', 'Tanah Merah']
        
        for i in range(size):
            asset_type = random.choice(asset_types)
            district = random.choice(districts)
            
            # Generate realistic asset values
            if asset_type == 'residential':
                asset_value = random.uniform(150000, 800000)
                ltv = random.uniform(0.7, 0.9)
            elif asset_type == 'commercial':
                asset_value = random.uniform(500000, 5000000)
                ltv = random.uniform(0.6, 0.8)
            else:  # industrial
                asset_value = random.uniform(1000000, 10000000)
                ltv = random.uniform(0.5, 0.75)
            
            loan_amount = asset_value * ltv
            insurance_coverage = asset_value * random.uniform(0.8, 1.0)
            
            portfolio.append({
                'id': f'loan_{i+1}',
                'asset_type': asset_type,
                'district': district,
                'asset_value': asset_value,
                'loan_amount': loan_amount,
                'insurance_coverage': insurance_coverage,
                'current_ltv': ltv
            })
        
        return portfolio
    
    def _apply_stress_scenario(self, portfolio: List[Dict], scenario_data: Dict) -> List[Dict]:
        """Apply stress scenario to portfolio"""
        
        scenario = scenario_data['scenario']
        severity_multiplier = {
            'mild': 0.5,
            'moderate': 1.0,
            'severe': 1.5,
            'extreme': 2.0
        }.get(scenario_data.get('severity', 'moderate'), 1.0)
        
        # Define base risk by scenario
        base_risks = {
            '100_year_flood': 0.8,
            'river_overflow': 0.6,
            'coastal_surge': 0.4,
            'prolonged_monsoon': 0.7
        }
        
        base_risk = base_risks.get(scenario, 0.5) * severity_multiplier
        
        stressed_portfolio = []
        
        for loan in portfolio:
            # Adjust risk by district (some areas more vulnerable)
            district_multiplier = {
                'Kota Bharu': 1.2,
                'Kuala Krai': 1.5,
                'Machang': 0.8,
                'Pasir Mas': 1.3,
                'Tanah Merah': 0.9
            }.get(loan['district'], 1.0)
            
            adjusted_risk = min(0.95, base_risk * district_multiplier)
            
            # Calculate impact
            flood_risk = {'base_risk': adjusted_risk, 'risk_level': 'high'}
            
            impact = self.assess_impact(
                flood_risk=flood_risk,
                asset_type=loan['asset_type'],
                asset_value=loan['asset_value'],
                loan_amount=loan['loan_amount'],
                insurance_coverage=loan['insurance_coverage']
            )
            
            stressed_loan = loan.copy()
            stressed_loan['stress_impact'] = impact
            stressed_portfolio.append(stressed_loan)
        
        return stressed_portfolio
    
    def _calculate_portfolio_impact(self, stressed_portfolio: List[Dict]) -> Dict:
        """Calculate aggregate portfolio impact"""
        
        total_loans = len(stressed_portfolio)
        total_exposure = sum(loan['loan_amount'] for loan in stressed_portfolio)
        
        # Calculate losses and defaults
        total_damage = 0
        total_defaults = 0
        default_exposure = 0
        
        risk_distribution = {'low': 0, 'medium': 0, 'high': 0, 'extreme': 0}
        
        for loan in stressed_portfolio:
            impact = loan['stress_impact']
            
            # Physical damage
            damage = impact['physical_damage']['damage_amount']
            total_damage += damage
            
            # Default probability
            if impact['default_probability']:
                default_prob = impact['default_probability']['default_probability']
                risk_cat = impact['default_probability']['risk_category']
                risk_distribution[risk_cat] += 1
                
                # Expected default (probability weighted)
                if default_prob > 0.5:  # Assume default if >50% probability
                    total_defaults += 1
                    default_exposure += loan['loan_amount']
        
        # Calculate ratios
        default_rate = total_defaults / total_loans
        loss_rate = default_exposure / total_exposure
        damage_rate = total_damage / sum(loan['asset_value'] for loan in stressed_portfolio)
        
        # Capital impact (simplified)
        risk_weighted_assets = total_exposure * 1.0  # 100% risk weight for simplicity
        expected_loss = total_exposure * loss_rate
        capital_impact = expected_loss * 8.0  # Assume 8% capital ratio requirement
        
        return {
            'portfolio_summary': {
                'total_loans': total_loans,
                'total_exposure': total_exposure,
                'total_asset_value': sum(loan['asset_value'] for loan in stressed_portfolio)
            },
            'impact_metrics': {
                'total_defaults': total_defaults,
                'default_rate': default_rate,
                'default_exposure': default_exposure,
                'loss_rate': loss_rate,
                'total_damage': total_damage,
                'damage_rate': damage_rate
            },
            'risk_distribution': risk_distribution,
            'capital_impact': {
                'expected_loss': expected_loss,
                'capital_requirement': capital_impact,
                'capital_ratio_impact': capital_impact / risk_weighted_assets
            },
            'recommendations': self._get_portfolio_recommendations(
                default_rate, loss_rate, damage_rate
            )
        }
    
    def _get_portfolio_recommendations(self, default_rate: float, 
                                      loss_rate: float, damage_rate: float) -> List[str]:
        """Generate portfolio-level recommendations"""
        recommendations = []
        
        if default_rate > 0.2:
            recommendations.extend([
                "Critical portfolio risk - implement immediate risk mitigation",
                "Consider portfolio restructuring or divestment",
                "Increase capital reserves significantly"
            ])
        elif default_rate > 0.1:
            recommendations.extend([
                "Elevated portfolio risk - enhance monitoring",
                "Review and tighten lending criteria",
                "Increase provisioning for expected losses"
            ])
        
        if loss_rate > 0.15:
            recommendations.append("Severe financial impact - consider reinsurance options")
        
        if damage_rate > 0.3:
            recommendations.append("High physical damage exposure - review geographic concentration")
        
        recommendations.extend([
            "Enhance flood risk assessment in underwriting",
            "Consider climate-adjusted pricing models",
            "Develop early warning systems for portfolio monitoring"
        ])
        
        return recommendations