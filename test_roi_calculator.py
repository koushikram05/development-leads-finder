"""
Unit tests for ROI Calculator
Tests buildable SF estimation, construction costs, profit calculations, and ROI scoring
"""

import unittest
from app.integrations.roi_calculator import (
    ROICalculator, 
    EnhancedLLMClassifier,
    ZoningType,
    ROIEstimate
)


class TestROICalculator(unittest.TestCase):
    """Test cases for ROI calculator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.calc = ROICalculator(location="Newton, MA")
    
    def test_large_lot_residential_good_roi(self):
        """
        Test Case 1: Large lot with residential zoning should have positive ROI
        - 1 acre lot @ $1.2M
        - Should estimate ~0.4x lot = 17,424 SF buildable
        - At $450/SF market rate = strong ROI potential
        """
        roi = self.calc.calculate_roi(
            address='123 Main St, Newton, MA',
            purchase_price=1200000,
            lot_size_sqft=43560,  # 1 acre
            current_sqft=4000,
            zoning_type='residential'
        )
        
        # Assertions
        self.assertGreater(roi.buildable_sqft, 0)
        self.assertGreater(roi.roi_percentage, 10)  # > 10% ROI
        self.assertGreater(roi.roi_score, 15)  # > 15/100 score
        self.assertGreater(roi.roi_confidence, 90)  # High confidence
        self.assertIn('Buildable', roi.reasoning)
    
    def test_small_lot_residential_low_roi(self):
        """
        Test Case 2: Small lot with limited development potential
        - 0.25 acre @ $650K
        - Should estimate ~0.4x lot = 4,356 SF buildable
        - Close to break-even ROI
        """
        roi = self.calc.calculate_roi(
            address='456 Oak Ave, Newton, MA',
            purchase_price=650000,
            lot_size_sqft=10890,  # 0.25 acres
            current_sqft=2000,
            zoning_type='residential'
        )
        
        # Assertions
        self.assertGreater(roi.buildable_sqft, 0)
        self.assertLess(roi.roi_percentage, 5)  # < 5% ROI
        self.assertLess(roi.roi_score, 10)  # Low score
        self.assertGreater(roi.roi_confidence, 90)  # Still high confidence (data available)
    
    def test_dense_residential_zoning_boost(self):
        """
        Test Case 3: Dense residential zoning should increase buildable SF and ROI
        - Same lot as test 2, but dense zoning
        - Should be 60% of lot instead of 40%
        - Should have better ROI
        """
        roi_dense = self.calc.calculate_roi(
            address='789 Oak Ave, Newton, MA',
            purchase_price=650000,
            lot_size_sqft=10890,
            current_sqft=2000,
            zoning_type='residential_dense'
        )
        
        roi_standard = self.calc.calculate_roi(
            address='789 Oak Ave, Newton, MA',
            purchase_price=650000,
            lot_size_sqft=10890,
            current_sqft=2000,
            zoning_type='residential'
        )
        
        # Dense should have more buildable and better ROI
        self.assertGreater(roi_dense.buildable_sqft, roi_standard.buildable_sqft)
        self.assertGreater(roi_dense.roi_percentage, roi_standard.roi_percentage)
        self.assertGreater(roi_dense.roi_score, roi_standard.roi_score)
    
    def test_missing_lot_size_fallback(self):
        """
        Test Case 4: When lot size is missing, calculator should fallback to current SF
        - No lot size provided
        - Should use current SF as estimate
        - Should have lower confidence
        """
        roi = self.calc.calculate_roi(
            address='999 Unknown St, Newton, MA',
            purchase_price=750000,
            lot_size_sqft=None,  # Missing
            current_sqft=3500,
            zoning_type='residential'
        )
        
        # Should still calculate something
        self.assertGreater(roi.buildable_sqft, 0)
        # Confidence should be lower (missing data)
        self.assertLess(roi.roi_confidence, 100)
        self.assertIn('SF', roi.reasoning)
    
    def test_zero_price_handling(self):
        """
        Test Case 5: Zero or invalid price should return low-confidence estimate
        - Price = 0 (invalid)
        - Should return zero ROI and low confidence
        """
        roi = self.calc.calculate_roi(
            address='Invalid Property, Newton, MA',
            purchase_price=0,
            lot_size_sqft=10000,
            current_sqft=2000,
            zoning_type='residential'
        )
        
        # Should be low confidence
        self.assertEqual(roi.roi_score, 0)
        self.assertEqual(roi.roi_confidence, 0)
        self.assertIn('Invalid', roi.reasoning)
    
    def test_roi_score_scaling(self):
        """
        Test Case 6: ROI score should scale properly from 0-100
        - 0% ROI → 0 points
        - 20% ROI → 25 points
        - 50% ROI → 50 points
        - 100% ROI → 75 points
        - 200%+ ROI → 100 points
        """
        test_rois = [
            (0, 0),           # 0% → 0 points
            (20, 25),         # 20% → ~25 points
            (50, 50),         # 50% → ~50 points
            (100, 75),        # 100% → ~75 points
            (200, 100),       # 200% → 100 points
        ]
        
        for roi_pct, expected_score in test_rois:
            score = self.calc._calculate_roi_score(roi_pct)
            # Allow some tolerance for the 20% and 50% cases
            if roi_pct == 0 or roi_pct >= 100:
                self.assertEqual(score, expected_score)
            else:
                # Within ±5 points
                self.assertAlmostEqual(score, expected_score, delta=5)
    
    def test_confidence_calculation(self):
        """
        Test Case 7: Confidence should increase with more available data
        - No data → low confidence (~50%)
        - Only lot size → medium confidence
        - Lot size + current SF + zoning → high confidence (~90%+)
        """
        # No lot size, no current SF
        conf_low = self.calc._calculate_confidence(
            lot_size=None,
            current_sqft=None,
            zoning=ZoningType.UNKNOWN,
            adjustment=1.0
        )
        
        # Has lot size and current SF
        conf_high = self.calc._calculate_confidence(
            lot_size=10000,
            current_sqft=3000,
            zoning=ZoningType.RESIDENTIAL,
            adjustment=1.0
        )
        
        # High should be significantly greater than low
        self.assertGreater(conf_high, conf_low + 30)


class TestEnhancedLLMClassifier(unittest.TestCase):
    """Test cases for LLM classifier with ROI enhancement"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.classifier = EnhancedLLMClassifier()
    
    def test_add_roi_to_classification_complete_data(self):
        """
        Test Case 1: ROI should be added to classification when all data available
        """
        classification = {
            'address': '42 Lindbergh Ave, Newton, MA',
            'label': 'excellent',
            'development_score': 85,
            'confidence_score': 0.95
        }
        
        property_data = {
            'address': '42 Lindbergh Ave, Newton, MA',
            'price': 950000,
            'lot_size': 21780,
            'square_feet': 3000,
            'zoning_type': 'residential'
        }
        
        result = self.classifier.add_roi_to_classification(classification, property_data)
        
        # Check ROI fields were added
        self.assertIn('buildable_sqft', result)
        self.assertIn('estimated_profit', result)
        self.assertIn('roi_percentage', result)
        self.assertIn('roi_score', result)
        self.assertIn('roi_confidence', result)
        
        # ROI values should be non-None
        self.assertIsNotNone(result['roi_score'])
        self.assertGreater(result['buildable_sqft'], 0)
    
    def test_add_roi_to_classification_missing_price(self):
        """
        Test Case 2: ROI should still be calculated with missing price
        """
        classification = {
            'label': 'good',
            'development_score': 72
        }
        
        property_data = {
            'address': '123 Main St, Newton, MA',
            'price': None,
            'last_price': 800000,  # Fallback
            'lot_size': 15000,
            'square_feet': 2500,
            'zoning_type': 'residential'
        }
        
        result = self.classifier.add_roi_to_classification(classification, property_data)
        
        # Should still have ROI fields
        self.assertIn('roi_score', result)
        self.assertIsNotNone(result['roi_score'])


class TestROIEstimate(unittest.TestCase):
    """Test the ROIEstimate dataclass"""
    
    def test_estimate_creation(self):
        """Test that ROIEstimate can be created with all fields"""
        estimate = ROIEstimate(
            buildable_sqft=10000,
            construction_cost_per_sqft=300,
            total_construction_cost=3000000,
            estimated_sale_price=4500000,
            estimated_profit=1000000,
            net_profit=750000,
            roi_percentage=50,
            roi_score=50,
            roi_confidence=90,
            reasoning="Test estimation"
        )
        
        self.assertEqual(estimate.buildable_sqft, 10000)
        self.assertEqual(estimate.roi_percentage, 50)
        self.assertEqual(estimate.roi_confidence, 90)


def run_tests():
    """Run all tests with verbose output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestROICalculator))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedLLMClassifier))
    suite.addTests(loader.loadTestsFromTestCase(TestROIEstimate))
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
