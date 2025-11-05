#!/usr/bin/env python3
"""
Test script to verify the application works in other cities
Tests basic functionality without GIS enrichment
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.dev_pipeline import DevelopmentPipeline
from app.utils import setup_logging

def test_different_cities():
    """Test pipeline with different cities"""
    
    logger = setup_logging('city_test')
    pipeline = DevelopmentPipeline()
    
    # Test cities
    test_cities = [
        ("Boston, MA", "Boston MA teardown single family home large lot"),
        ("Cambridge, MA", "Cambridge MA development opportunity large lot"),
        ("Brookline, MA", "Brookline MA builder special teardown"),
        ("Somerville, MA", "Somerville MA single family renovation opportunity")
    ]
    
    for location, search_query in test_cities:
        logger.info(f"\n{'='*60}")
        logger.info(f"TESTING: {location}")
        logger.info(f"{'='*60}")
        
        try:
            # Run pipeline with minimal features to test core functionality
            results = pipeline.run(
                search_query=search_query,
                location=location,
                use_scrapers=False,  # Skip scrapers for speed
                max_pages=1,         # Minimal pages
                enrich_data=False,   # Skip GIS enrichment (Newton-specific)
                classify_data=True,  # Keep classification
                min_dev_score=40.0
            )
            
            logger.info(f"✅ SUCCESS: {location}")
            logger.info(f"   Found {results['total_listings']} listings")
            logger.info(f"   Classified {results['classified_listings']} listings")
            logger.info(f"   Development opportunities: {results['development_opportunities']}")
            
        except Exception as e:
            logger.error(f"❌ FAILED: {location} - {str(e)}")
    
    logger.info(f"\n{'='*60}")
    logger.info("CITY TESTING COMPLETE")
    logger.info("='*60}")

if __name__ == "__main__":
    test_different_cities()