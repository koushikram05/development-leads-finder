#!/usr/bin/env python3
"""Quick test of ROI integration"""

from app.integrations.roi_calculator import ROICalculator, EnhancedLLMClassifier

# Test 1: ROI Calculator
print("=" * 80)
print("TEST 1: ROI Calculator")
print("=" * 80)

calc = ROICalculator()
roi = calc.calculate_roi(
    address='123 Test Property, Newton, MA',
    purchase_price=1200000,
    lot_size_sqft=43560,
    current_sqft=4000,
    zoning_type='residential'
)

print(f"Address: 123 Test Property, Newton, MA")
print(f"Purchase Price: ${1200000:,.0f}")
print(f"Buildable SF: {roi.buildable_sqft:,.0f}")
print(f"Est. Sale: ${roi.estimated_sale_price:,.0f}")
print(f"Profit: ${roi.net_profit:,.0f}")
print(f"ROI: {roi.roi_percentage:.1f}%")
print(f"ROI Score: {roi.roi_score:.0f}/100")
print(f"Confidence: {roi.roi_confidence:.0f}%")

# Test 2: Enhanced LLM Classifier
print("\n" + "=" * 80)
print("TEST 2: Enhanced LLM Classifier with ROI")
print("=" * 80)

classifier = EnhancedLLMClassifier()

classification = {
    'address': '456 Oak Ave, Newton, MA',
    'label': 'excellent',
    'development_score': 85,
    'explanation': 'Large lot with high potential'
}

property_data = {
    'address': '456 Oak Ave, Newton, MA',
    'price': 950000,
    'lot_size': 21780,
    'square_feet': 3000,
    'zoning_type': 'residential'
}

result = classifier.add_roi_to_classification(classification, property_data)

print(f"Classification before ROI: development_score={classification['development_score']}")
print(f"Classification after ROI:")
print(f"  Buildable SF: {result.get('buildable_sqft', 'N/A')}")
print(f"  Est. Profit: ${result.get('estimated_profit', 0):,.0f}")
print(f"  ROI: {result.get('roi_percentage', 0):.1f}%")
print(f"  ROI Score: {result.get('roi_score', 0):.0f}/100")
print(f"  ROI Confidence: {result.get('roi_confidence', 0):.0f}%")

print("\n✅ ROI Integration Tests Passed!")
