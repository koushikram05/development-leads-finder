#!/usr/bin/env python3
"""
Test script for Map Generator
Tests map creation with real data from database
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.integrations.map_generator import MapGenerator, create_opportunity_map
from app.integrations.database_manager import HistoricalDatabaseManager
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_map_generation():
    """Test basic map generation with database data"""
    print("\n" + "=" * 70)
    print("TEST 1: Map Generation with Database Data")
    print("=" * 70)
    
    try:
        # Get data from database
        db = HistoricalDatabaseManager()
        properties = db.get_recent_opportunities(days=30, min_score=0)
        
        print(f"✓ Retrieved {len(properties)} properties from database")
        
        if not properties:
            print("⚠ No properties found in database")
            return False
        
        # Create map
        map_gen = MapGenerator()
        stats = map_gen.add_properties(properties)
        
        print(f"✓ Properties added to map:")
        print(f"  - Excellent (🔴): {stats['excellent']}")
        print(f"  - Good (🟠): {stats['good']}")
        print(f"  - Fair (🟡): {stats['fair']}")
        print(f"  - Low (🟢): {stats['low']}")
        
        # Add heatmap
        map_gen.add_heatmap()
        print("✓ Heatmap layer added")
        
        # Add layer controls
        map_gen.add_layer_control()
        print("✓ Layer controls added")
        
        # Generate stats
        map_stats = map_gen.generate_stats()
        print(f"\nMap Statistics:")
        print(f"  Total properties: {map_stats['total_properties']}")
        print(f"  Average score: {map_stats['average_score']:.1f}/100")
        print(f"  Score range: {map_stats['min_score']:.1f} - {map_stats['max_score']:.1f}")
        
        # Save map
        output_dir = Path("data/maps")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "latest_map.html"
        map_path = map_gen.save_map(str(output_file))
        print(f"\n✓ Map saved: {map_path}")
        
        # Check file exists
        if Path(map_path).exists():
            file_size = Path(map_path).stat().st_size
            print(f"  File size: {file_size / 1024:.1f} KB")
            print(f"  ✓ TEST PASSED")
            return True
        else:
            print(f"  ✗ Map file not found")
            return False
            
    except Exception as e:
        print(f"✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_high_value_map():
    """Test creating filtered map with only high-value properties"""
    print("\n" + "=" * 70)
    print("TEST 2: High-Value Properties Map (Score ≥ 70)")
    print("=" * 70)
    
    try:
        db = HistoricalDatabaseManager()
        properties = db.get_recent_opportunities(days=30, min_score=70)
        
        print(f"✓ Retrieved {len(properties)} high-value properties")
        
        if not properties:
            print("⚠ No high-value properties found")
            return True  # Not a failure
        
        # Create high-value map
        output_dir = Path("data/maps")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        map_gen = MapGenerator()
        map_gen.add_properties(properties)
        map_gen.add_heatmap()
        map_gen.add_layer_control()
        
        output_file = output_dir / "high_value_map.html"
        map_path = map_gen.save_map(str(output_file))
        
        print(f"✓ High-value map saved: {map_path}")
        print(f"  ✓ TEST PASSED")
        return True
        
    except Exception as e:
        print(f"✗ TEST FAILED: {e}")
        return False


def test_excellent_map():
    """Test creating map with only excellent properties"""
    print("\n" + "=" * 70)
    print("TEST 3: Excellent Properties Map (Score ≥ 80)")
    print("=" * 70)
    
    try:
        db = HistoricalDatabaseManager()
        properties = db.get_recent_opportunities(days=30, min_score=80)
        
        print(f"✓ Retrieved {len(properties)} excellent properties")
        
        if not properties:
            print("⚠ No excellent properties found")
            return True  # Not a failure
        
        # Create excellent map
        output_dir = Path("data/maps")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        map_gen = MapGenerator()
        map_gen.add_properties(properties)
        map_gen.add_heatmap()
        map_gen.add_layer_control()
        
        output_file = output_dir / "excellent_map.html"
        map_path = map_gen.save_map(str(output_file))
        
        print(f"✓ Excellent map saved: {map_path}")
        print(f"  ✓ TEST PASSED")
        return True
        
    except Exception as e:
        print(f"✗ TEST FAILED: {e}")
        return False


def test_sample_data():
    """Test map generation with sample data (no database needed)"""
    print("\n" + "=" * 70)
    print("TEST 4: Map Generation with Sample Data")
    print("=" * 70)
    
    try:
        # Create sample properties
        sample_properties = [
            {
                'address': '42 Lindbergh Avenue, Newton, MA',
                'latitude': 42.3314,
                'longitude': -71.2045,
                'development_score': 88.5,
                'price': 750000,
                'lot_size': 12000,
                'year_built': 1985,
                'explanation': 'Large lot, prime location, development potential'
            },
            {
                'address': '156 Gould Street, Newton, MA',
                'latitude': 42.3325,
                'longitude': -71.2055,
                'development_score': 75.2,
                'price': 680000,
                'lot_size': 10000,
                'year_built': 1978,
                'explanation': 'Decent lot size, good area'
            },
            {
                'address': '89 Winchester Street, Newton, MA',
                'latitude': 42.3305,
                'longitude': -71.2035,
                'development_score': 65.0,
                'price': 620000,
                'lot_size': 8000,
                'year_built': 1990,
                'explanation': 'Fair location, some development potential'
            },
            {
                'address': '123 Main Street, Newton, MA',
                'latitude': 42.3335,
                'longitude': -71.2065,
                'development_score': 45.3,
                'price': 500000,
                'lot_size': 5000,
                'year_built': 2005,
                'explanation': 'Small lot, limited potential'
            },
        ]
        
        print(f"✓ Created {len(sample_properties)} sample properties")
        
        # Create map
        map_gen = MapGenerator()
        stats = map_gen.add_properties(sample_properties)
        map_gen.add_heatmap()
        map_gen.add_layer_control()
        
        print(f"✓ Map created with sample data:")
        print(f"  - Excellent: {stats['excellent']}")
        print(f"  - Good: {stats['good']}")
        print(f"  - Fair: {stats['fair']}")
        print(f"  - Low: {stats['low']}")
        
        # Save map
        output_dir = Path("data/maps")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "sample_map.html"
        map_path = map_gen.save_map(str(output_file))
        
        print(f"✓ Sample map saved: {map_path}")
        
        if Path(map_path).exists():
            print(f"  ✓ TEST PASSED")
            return True
        else:
            print(f"  ✗ Map file not found")
            return False
            
    except Exception as e:
        print(f"✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("MAP GENERATOR TEST SUITE")
    print("=" * 70)
    
    results = {
        'test_1': test_map_generation(),
        'test_2': test_high_value_map(),
        'test_3': test_excellent_map(),
        'test_4': test_sample_data(),
    }
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED - Map generator ready!")
        return 0
    else:
        print(f"\n✗ {total - passed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
