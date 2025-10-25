"""
ROI Scoring & Calculator for Development Opportunities
Estimates buildable square footage, development costs, profit potential, and ROI for properties
"""

import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math

logger = logging.getLogger(__name__)


class ZoningType(Enum):
    """Boston area zoning classifications"""
    RESIDENTIAL = "residential"
    RESIDENTIAL_DENSE = "residential_dense"
    MIXED_USE = "mixed_use"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    UNKNOWN = "unknown"


@dataclass
class ROIEstimate:
    """Container for ROI calculation results"""
    buildable_sqft: float                    # Estimated buildable square footage
    construction_cost_per_sqft: float        # Cost per square foot ($)
    total_construction_cost: float           # Total construction cost ($)
    estimated_sale_price: float              # Estimated sale price after development ($)
    estimated_profit: float                  # Gross profit (sale price - purchase - construction)
    net_profit: float                        # Net profit after taxes/fees (~70% of gross)
    roi_percentage: float                    # ROI percentage (100+ is excellent)
    roi_score: float                         # Normalized ROI score (0-100)
    roi_confidence: float                    # Confidence level (0-100)
    reasoning: str                           # Explanation of calculations


class ROICalculator:
    """
    Calculates ROI potential for development opportunities
    
    Boston Area Assumptions:
    - Newton area mid-market construction: $250-350/sqft
    - Single-family residential: $300/sqft
    - Multi-unit development: $350/sqft
    - Construction markup/profit: 20-30%
    - Sale timeframe: 18-24 months
    - Tax/fees: 25-30% of gross profit
    """
    
    # Newton, MA market data
    NEWTON_CONSTRUCTION_COSTS = {
        ZoningType.RESIDENTIAL: 300,              # $/sqft
        ZoningType.RESIDENTIAL_DENSE: 350,        # $/sqft (multi-unit)
        ZoningType.MIXED_USE: 325,                # $/sqft
        ZoningType.COMMERCIAL: 280,               # $/sqft
        ZoningType.INDUSTRIAL: 200,               # $/sqft
    }
    
    # Newton zoning lot coverage & density rules (approximate)
    ZONING_MULTIPLIERS = {
        ZoningType.RESIDENTIAL: {
            'lot_coverage_percent': 0.30,          # Max 30% lot coverage
            'buildable_ratio': 0.40,               # Can build ~40% of lot (conservative)
        },
        ZoningType.RESIDENTIAL_DENSE: {
            'lot_coverage_percent': 0.45,
            'buildable_ratio': 0.60,
        },
        ZoningType.MIXED_USE: {
            'lot_coverage_percent': 0.50,
            'buildable_ratio': 0.80,
        },
        ZoningType.COMMERCIAL: {
            'lot_coverage_percent': 0.60,
            'buildable_ratio': 1.0,
        },
    }
    
    # Market price per sqft in Newton, MA (2024 estimates)
    # These are retail prices for newly built/renovated homes
    MARKET_PRICE_PER_SQFT = {
        ZoningType.RESIDENTIAL: 450,           # $/sqft for new single-family homes
        ZoningType.RESIDENTIAL_DENSE: 475,     # $/sqft for multi-unit condos
        ZoningType.MIXED_USE: 420,
        ZoningType.COMMERCIAL: 350,
    }
    
    def __init__(self, location: str = "Newton, MA"):
        """
        Initialize ROI Calculator
        
        Args:
            location: Target location for market assumptions
        """
        self.location = location
        self.logger = logging.getLogger(__name__)
    
    def calculate_roi(
        self,
        address: str,
        purchase_price: float,
        lot_size_sqft: Optional[float] = None,
        current_sqft: Optional[float] = None,
        zoning_type: Optional[str] = None,
        confidence_adjustment: float = 1.0
    ) -> ROIEstimate:
        """
        Calculate ROI potential for a property
        
        Args:
            address: Property address
            purchase_price: Current market price ($)
            lot_size_sqft: Lot size in square feet (if available)
            current_sqft: Current building square footage
            zoning_type: Zoning classification
            confidence_adjustment: Multiplier for confidence (0.5-1.5)
        
        Returns:
            ROIEstimate object with all calculations
        """
        
        # Validate inputs
        if not purchase_price or purchase_price <= 0:
            return self._create_low_confidence_estimate(
                address, "Invalid purchase price"
            )
        
        # Determine zoning type
        zoning = self._get_zoning_type(zoning_type)
        
        # Estimate buildable square footage
        buildable_sqft = self._estimate_buildable_sqft(
            lot_size_sqft,
            current_sqft,
            zoning
        )
        
        # If no buildable potential detected, return low confidence
        if buildable_sqft <= 0:
            return self._create_low_confidence_estimate(
                address, "No buildable potential detected"
            )
        
        # Get construction cost per sqft
        construction_cost_per_sqft = self.NEWTON_CONSTRUCTION_COSTS.get(
            zoning, 300
        )
        
        # Calculate total construction cost
        total_construction_cost = buildable_sqft * construction_cost_per_sqft
        
        # Estimate sale price (based on market rate)
        market_price_per_sqft = self.MARKET_PRICE_PER_SQFT.get(
            zoning, 300
        )
        estimated_sale_price = buildable_sqft * market_price_per_sqft
        
        # Calculate profit before taxes/fees
        # Gross profit = Sale price - (Purchase price + Construction costs)
        # This reflects selling developed property for market price
        gross_profit = estimated_sale_price - purchase_price - total_construction_cost
        
        # Apply tax/fees (25% of gross profit as conservative estimate)
        tax_rate = 0.25
        net_profit = gross_profit * (1 - tax_rate) if gross_profit > 0 else gross_profit
        
        # Calculate ROI percentage
        # ROI = (Net Profit) / (Purchase Price + Construction Investment) * 100
        total_investment = purchase_price + total_construction_cost
        if total_investment > 0:
            roi_percentage = (net_profit / total_investment) * 100
        else:
            roi_percentage = 0
        
        # Calculate confidence score
        confidence = self._calculate_confidence(
            lot_size_sqft,
            current_sqft,
            zoning,
            confidence_adjustment
        )
        
        # Calculate ROI score (0-100 scale)
        roi_score = self._calculate_roi_score(roi_percentage)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            address,
            lot_size_sqft,
            buildable_sqft,
            purchase_price,
            estimated_sale_price,
            roi_percentage,
            confidence
        )
        
        return ROIEstimate(
            buildable_sqft=buildable_sqft,
            construction_cost_per_sqft=construction_cost_per_sqft,
            total_construction_cost=total_construction_cost,
            estimated_sale_price=estimated_sale_price,
            estimated_profit=gross_profit,
            net_profit=net_profit,
            roi_percentage=roi_percentage,
            roi_score=roi_score,
            roi_confidence=confidence,
            reasoning=reasoning
        )
    
    def _estimate_buildable_sqft(
        self,
        lot_size: Optional[float],
        current_sqft: Optional[float],
        zoning: ZoningType
    ) -> float:
        """
        Estimate buildable square footage based on lot size and zoning
        
        Newton zoning rules (realistic):
        - Residential: 40% of lot (accounting for setbacks, easements, density limits)
        - Dense Residential: 60% of lot
        - Mixed Use: 80% of lot
        - Commercial: 100% of lot
        
        For teardown scenarios:
            Existing building removal → build up to zoning limit
        
        Args:
            lot_size: Lot size in square feet
            current_sqft: Current building square footage
            zoning: Zoning type
        
        Returns:
            Estimated buildable square footage
        """
        
        if lot_size is None or lot_size <= 0:
            # Use current sqft as proxy if lot size unavailable
            if current_sqft and current_sqft > 0:
                return current_sqft * 1.2  # Conservative estimate
            return 0
        
        # Get zoning multiplier/ratio
        multiplier = self.ZONING_MULTIPLIERS.get(
            zoning, {'buildable_ratio': 0.40}
        )['buildable_ratio']
        
        # Calculate buildable sqft
        buildable_sqft = lot_size * multiplier
        
        return max(0, buildable_sqft)
    
    def _get_zoning_type(self, zoning_str: Optional[str]) -> ZoningType:
        """
        Parse zoning string to ZoningType enum
        
        Args:
            zoning_str: Zoning type string
        
        Returns:
            ZoningType enum value
        """
        if not zoning_str:
            return ZoningType.RESIDENTIAL
        
        zoning_lower = zoning_str.lower()
        
        if 'dense' in zoning_lower or 'multi' in zoning_lower:
            return ZoningType.RESIDENTIAL_DENSE
        elif 'mixed' in zoning_lower or 'commercial' in zoning_lower:
            return ZoningType.MIXED_USE
        elif 'commercial' in zoning_lower:
            return ZoningType.COMMERCIAL
        elif 'industrial' in zoning_lower:
            return ZoningType.INDUSTRIAL
        else:
            return ZoningType.RESIDENTIAL
    
    def _calculate_confidence(
        self,
        lot_size: Optional[float],
        current_sqft: Optional[float],
        zoning: ZoningType,
        adjustment: float
    ) -> float:
        """
        Calculate confidence level (0-100) based on available data
        
        Args:
            lot_size: Whether lot size is available
            current_sqft: Whether building sqft is available
            zoning: Zoning type (affects estimate reliability)
            adjustment: User-provided adjustment factor
        
        Returns:
            Confidence score (0-100)
        """
        confidence = 50  # Base confidence
        
        # Add points for available data
        if lot_size and lot_size > 0:
            confidence += 20
        if current_sqft and current_sqft > 0:
            confidence += 15
        if zoning not in [ZoningType.UNKNOWN, None]:
            confidence += 15
        
        # Apply adjustment
        confidence = confidence * adjustment
        
        # Cap at 0-100
        return max(0, min(100, confidence))
    
    def _calculate_roi_score(self, roi_percentage: float) -> float:
        """
        Convert ROI percentage to normalized score (0-100)
        
        ROI Scale:
        - 0% ROI = 0 points
        - 20% ROI = 25 points
        - 50% ROI = 50 points
        - 100% ROI = 75 points
        - 200%+ ROI = 100 points
        
        Args:
            roi_percentage: ROI percentage
        
        Returns:
            Score 0-100
        """
        if roi_percentage < 0:
            return 0  # Negative ROI
        elif roi_percentage < 20:
            return (roi_percentage / 20) * 25
        elif roi_percentage < 50:
            return 25 + ((roi_percentage - 20) / 30) * 25
        elif roi_percentage < 100:
            return 50 + ((roi_percentage - 50) / 50) * 25
        else:
            return 75 + (min(roi_percentage - 100, 100) / 100) * 25
    
    def _create_low_confidence_estimate(
        self,
        address: str,
        reason: str
    ) -> ROIEstimate:
        """
        Create a low-confidence ROI estimate
        
        Args:
            address: Property address
            reason: Reason for low confidence
        
        Returns:
            Low-confidence ROIEstimate
        """
        return ROIEstimate(
            buildable_sqft=0,
            construction_cost_per_sqft=0,
            total_construction_cost=0,
            estimated_sale_price=0,
            estimated_profit=0,
            net_profit=0,
            roi_percentage=0,
            roi_score=0,
            roi_confidence=0,
            reasoning=f"Cannot estimate ROI: {reason}"
        )
    
    def _generate_reasoning(
        self,
        address: str,
        lot_size: Optional[float],
        buildable_sqft: float,
        purchase_price: float,
        sale_price: float,
        roi_percentage: float,
        confidence: float
    ) -> str:
        """
        Generate human-readable reasoning for ROI calculation
        
        Args:
            address: Property address
            lot_size: Lot size
            buildable_sqft: Buildable square footage
            purchase_price: Purchase price
            sale_price: Estimated sale price
            roi_percentage: ROI percentage
            confidence: Confidence score
        
        Returns:
            Reasoning string
        """
        reasoning = f"Buildable: {buildable_sqft:,.0f} SF | "
        
        if lot_size:
            ratio = buildable_sqft / lot_size if lot_size > 0 else 0
            reasoning += f"Lot: {lot_size:,.0f} SF ({ratio:.1f}x) | "
        
        reasoning += f"Est. Sale: ${sale_price:,.0f} | "
        reasoning += f"ROI: {roi_percentage:.1f}% | "
        reasoning += f"Confidence: {confidence:.0f}%"
        
        return reasoning


class EnhancedLLMClassifier:
    """
    Wrapper to add ROI calculations to LLM classification results
    """
    
    def __init__(self, roi_calculator: Optional[ROICalculator] = None):
        """
        Initialize enhanced classifier
        
        Args:
            roi_calculator: ROI calculator instance (creates new if None)
        """
        self.roi_calc = roi_calculator or ROICalculator()
        self.logger = logging.getLogger(__name__)
    
    def add_roi_to_classification(
        self,
        classification: Dict[str, Any],
        property_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add ROI calculations to classification results
        
        Args:
            classification: Classification dict from LLM
            property_data: Property data dict with lot_size, price, etc.
        
        Returns:
            Updated classification with ROI fields
        """
        try:
            # Extract relevant fields
            address = property_data.get('address', 'Unknown')
            purchase_price = property_data.get('price') or property_data.get('last_price')
            lot_size = property_data.get('lot_size')
            current_sqft = property_data.get('square_feet')
            zoning = property_data.get('zoning_type')
            
            # Calculate ROI
            roi_estimate = self.roi_calc.calculate_roi(
                address=address,
                purchase_price=purchase_price,
                lot_size_sqft=lot_size,
                current_sqft=current_sqft,
                zoning_type=zoning
            )
            
            # Add to classification
            classification['buildable_sqft'] = roi_estimate.buildable_sqft
            classification['estimated_profit'] = roi_estimate.net_profit
            classification['roi_percentage'] = roi_estimate.roi_percentage
            classification['roi_score'] = roi_estimate.roi_score
            classification['roi_confidence'] = roi_estimate.roi_confidence
            classification['roi_reasoning'] = roi_estimate.reasoning
            
            # Log
            if roi_estimate.roi_score >= 70:
                self.logger.info(
                    f"High ROI opportunity: {address} "
                    f"({roi_estimate.roi_percentage:.1f}% ROI, "
                    f"Score: {roi_estimate.roi_score:.0f}/100)"
                )
            
            return classification
            
        except Exception as e:
            self.logger.error(f"Error calculating ROI for {property_data.get('address')}: {e}")
            # Return classification with None values
            classification['buildable_sqft'] = None
            classification['estimated_profit'] = None
            classification['roi_percentage'] = None
            classification['roi_score'] = None
            classification['roi_confidence'] = None
            classification['roi_reasoning'] = f"ROI calculation failed: {e}"
            return classification


def main():
    """Test the ROI calculator"""
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    calc = ROICalculator(location="Newton, MA")
    
    # Test scenarios
    test_properties = [
        {
            'address': '42 Lindbergh Ave, Newton, MA',
            'purchase_price': 950000,
            'lot_size_sqft': 21780,  # 0.5 acres
            'current_sqft': 3000,
            'zoning_type': 'residential',
            'scenario': 'Large lot, good potential'
        },
        {
            'address': '123 Main St, Newton, MA',
            'purchase_price': 1200000,
            'lot_size_sqft': 43560,  # 1.0 acres
            'current_sqft': 4000,
            'zoning_type': 'residential',
            'scenario': 'Very large lot, developer dream'
        },
        {
            'address': '456 Oak Ave, Newton, MA',
            'purchase_price': 650000,
            'lot_size_sqft': 10890,  # 0.25 acres
            'current_sqft': 2000,
            'zoning_type': 'residential',
            'scenario': 'Small lot, limited potential'
        },
        {
            'address': '789 Park St, Newton, MA',
            'purchase_price': 800000,
            'lot_size_sqft': None,  # Missing lot size
            'current_sqft': 3500,
            'zoning_type': 'residential_dense',
            'scenario': 'Missing lot size data'
        },
    ]
    
    print("\n" + "=" * 80)
    print("ROI CALCULATOR TEST RESULTS")
    print("=" * 80)
    
    for prop in test_properties:
        print(f"\n{prop['address']}")
        print(f"Scenario: {prop['scenario']}")
        print(f"Purchase Price: ${prop['purchase_price']:,.0f}")
        
        roi = calc.calculate_roi(
            address=prop['address'],
            purchase_price=prop['purchase_price'],
            lot_size_sqft=prop['lot_size_sqft'],
            current_sqft=prop['current_sqft'],
            zoning_type=prop['zoning_type']
        )
        
        print(f"\nROI Estimate:")
        print(f"  Buildable SF: {roi.buildable_sqft:,.0f}")
        print(f"  Construction Cost: ${roi.total_construction_cost:,.0f} "
              f"(${roi.construction_cost_per_sqft:.0f}/SF)")
        print(f"  Est. Sale Price: ${roi.estimated_sale_price:,.0f}")
        print(f"  Est. Profit: ${roi.estimated_profit:,.0f} (gross) / "
              f"${roi.net_profit:,.0f} (net)")
        print(f"  ROI: {roi.roi_percentage:.1f}%")
        print(f"  ROI Score: {roi.roi_score:.1f}/100")
        print(f"  Confidence: {roi.roi_confidence:.0f}%")
        print(f"  Reasoning: {roi.reasoning}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
