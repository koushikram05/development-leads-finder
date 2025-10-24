"""
GIS Enrichment module for Newton, MA property data
Fetches parcel, zoning, and assessment data from public sources
"""

import time
import re
from typing import Dict, Any, Optional, List
import requests
from app.utils import setup_logging, clean_sqft


class GISEnrichment:
    """
    Enrich property listings with GIS and public record data
    """
    
    def __init__(self):
        self.logger = setup_logging('gis_enrichment')
        
        # Newton GIS endpoints
        self.newton_gis_base = "https://gis.newtonma.gov/arcgis/rest/services"
        self.newton_assessor_url = "https://data.newtonma.gov/resource/assessor-data"
        
        # Backup: MassGIS for statewide data
        self.mass_gis_base = "https://gis.massgis.state.ma.us/arcgis/rest/services"
        
        self.session = requests.Session()
    
    def enrich_listing(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a single listing with GIS data
        
        Args:
            listing: Property listing dictionary
            
        Returns:
            Enriched listing with additional fields
        """
        address = listing.get('address', '')
        if not address or address == "N/A":
            self.logger.warning("No valid address for enrichment")
            return listing
        
        self.logger.info(f"Enriching: {address}")
        
        # Try to get parcel data
        parcel_data = self._get_parcel_data(address)
        if parcel_data:
            listing.update(parcel_data)
        
        # Try to get assessment data
        assessment_data = self._get_assessment_data(address)
        if assessment_data:
            listing.update(assessment_data)
        
        # Get coordinates if not present
        if 'latitude' not in listing or 'longitude' not in listing:
            coords = self._geocode_address(address)
            if coords:
                listing.update(coords)
        
        # Calculate derived metrics
        listing = self._calculate_metrics(listing)
        
        return listing
    
    def enrich_listings_batch(self, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich multiple listings with rate limiting
        
        Args:
            listings: List of property listings
            
        Returns:
            List of enriched listings
        """
        enriched = []
        
        for i, listing in enumerate(listings):
            try:
                enriched_listing = self.enrich_listing(listing)
                enriched.append(enriched_listing)
                
                # Rate limiting
                if i > 0 and i % 10 == 0:
                    self.logger.info(f"Enriched {i}/{len(listings)} listings")
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Error enriching listing: {e}")
                enriched.append(listing)  # Add original if enrichment fails
        
        self.logger.info(f"Completed enrichment: {len(enriched)} listings")
        return enriched
    
    def _get_parcel_data(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Get parcel data from Newton GIS
        
        Args:
            address: Property address
            
        Returns:
            Dictionary with parcel data
        """
        try:
            # Newton Parcels API endpoint
            url = f"{self.newton_gis_base}/Public/Parcels/MapServer/0/query"
            
            params = {
                'where': f"SITE_ADDR LIKE '%{self._clean_address_for_query(address)}%'",
                'outFields': '*',
                'f': 'json',
                'returnGeometry': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('features'):
                feature = data['features'][0]
                attrs = feature.get('attributes', {})
                
                parcel_data = {
                    'parcel_id': attrs.get('PARCEL_ID'),
                    'lot_size': clean_sqft(str(attrs.get('LOT_SIZE', ''))),
                    'zoning': attrs.get('ZONING'),
                    'land_use': attrs.get('LAND_USE'),
                    'frontage': attrs.get('FRONTAGE'),
                    'owner_name': attrs.get('OWNER_NAME'),
                    'owner_address': attrs.get('OWNER_ADDR')
                }
                
                # Extract coordinates from geometry
                if 'geometry' in feature:
                    geom = feature['geometry']
                    if 'x' in geom and 'y' in geom:
                        parcel_data['longitude'] = geom['x']
                        parcel_data['latitude'] = geom['y']
                
                self.logger.info(f"Found parcel data for {address}")
                return parcel_data
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching parcel data: {e}")
            return None
    
    def _get_assessment_data(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Get assessment data from Newton assessor database
        
        Args:
            address: Property address
            
        Returns:
            Dictionary with assessment data
        """
        try:
            # This is a placeholder - actual API may vary
            # Newton may have a public assessor database or API
            
            url = "https://data.newtonma.gov/resource/assessor.json"
            
            params = {
                'address': address,
                '$limit': 1
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data:
                    record = data[0]
                    
                    assessment_data = {
                        'assessed_value': record.get('total_value'),
                        'land_value': record.get('land_value'),
                        'building_value': record.get('building_value'),
                        'year_built': record.get('year_built'),
                        'building_area': clean_sqft(str(record.get('building_area', '')))
                    }
                    
                    self.logger.info(f"Found assessment data for {address}")
                    return assessment_data
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Assessment data not available: {e}")
            return None
    
    def _geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """
        Geocode an address to get coordinates
        Uses a free geocoding service
        
        Args:
            address: Property address
            
        Returns:
            Dictionary with latitude and longitude
        """
        try:
            # Using Nominatim (OpenStreetMap) - free geocoding
            url = "https://nominatim.openstreetmap.org/search"
            
            params = {
                'q': address,
                'format': 'json',
                'limit': 1
            }
            
            headers = {
                'User-Agent': 'Anil_Project_Real_Estate/1.0'
            }
            
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data:
                result = data[0]
                coords = {
                    'latitude': float(result['lat']),
                    'longitude': float(result['lon'])
                }
                
                self.logger.info(f"Geocoded: {address}")
                return coords
            
            return None
            
        except Exception as e:
            self.logger.error(f"Geocoding failed: {e}")
            return None
    
    def _calculate_metrics(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate derived metrics from available data
        
        Args:
            listing: Property listing
            
        Returns:
            Listing with additional calculated fields
        """
        # Price per square foot
        if listing.get('price') and listing.get('sqft'):
            if listing['sqft'] > 0:
                listing['price_per_sqft'] = round(listing['price'] / listing['sqft'], 2)
        
        # Land value ratio (if we have building and land values)
        if listing.get('land_value') and listing.get('assessed_value'):
            if listing['assessed_value'] > 0:
                listing['land_value_ratio'] = round(
                    listing['land_value'] / listing['assessed_value'], 2
                )
        
        # Lot size to building area ratio
        if listing.get('lot_size') and listing.get('sqft'):
            if listing['sqft'] > 0:
                listing['lot_to_building_ratio'] = round(
                    listing['lot_size'] / listing['sqft'], 2
                )
        
        # Building age
        if listing.get('year_built'):
            from datetime import datetime
            current_year = datetime.now().year
            listing['building_age'] = current_year - listing['year_built']
        
        return listing
    
    def _clean_address_for_query(self, address: str) -> str:
        """
        Clean address for SQL/API query
        
        Args:
            address: Raw address string
            
        Returns:
            Cleaned address
        """
        # Extract street address (before city)
        parts = address.split(',')
        if parts:
            street = parts[0].strip()
            # Remove apartment numbers, etc.
            street = re.sub(r'\s+(Unit|Apt|#).*', '', street, flags=re.IGNORECASE)
            return street
        return address
    
    def get_zoning_info(self, zoning_code: str) -> Dict[str, Any]:
        """
        Get zoning information and regulations
        
        Args:
            zoning_code: Zoning code (e.g., 'SR-2', 'S-10')
            
        Returns:
            Dictionary with zoning details
        """
        # Newton zoning districts (example data - should be loaded from actual regulations)
        zoning_info = {
            'SR-1': {'type': 'Single Residence', 'min_lot_size': 15000, 'max_far': 0.30},
            'SR-2': {'type': 'Single Residence', 'min_lot_size': 10000, 'max_far': 0.35},
            'SR-3': {'type': 'Single Residence', 'min_lot_size': 7500, 'max_far': 0.40},
            'S-10': {'type': 'Single Family', 'min_lot_size': 10000, 'max_far': 0.35},
            'S-15': {'type': 'Single Family', 'min_lot_size': 15000, 'max_far': 0.30},
            'S-40': {'type': 'Single Family', 'min_lot_size': 40000, 'max_far': 0.25}
        }
        
        return zoning_info.get(zoning_code, {
            'type': 'Unknown',
            'min_lot_size': None,
            'max_far': None
        })
    
    def calculate_buildable_area(self, listing: Dict[str, Any]) -> Optional[float]:
        """
        Calculate maximum buildable area based on lot size and FAR
        
        Args:
            listing: Property listing with lot_size and zoning
            
        Returns:
            Maximum buildable square footage
        """
        lot_size = listing.get('lot_size')
        zoning = listing.get('zoning')
        
        if not lot_size or not zoning:
            return None
        
        zoning_info = self.get_zoning_info(zoning)
        max_far = zoning_info.get('max_far')
        
        if max_far:
            return round(lot_size * max_far, 2)
        
        return None


# Example usage
if __name__ == "__main__":
    enricher = GISEnrichment()
    
    # Test with sample listing
    test_listing = {
        'address': '68 Vernon St, Newton, MA 02458',
        'price': 975000,
        'sqft': 2500
    }
    
    enriched = enricher.enrich_listing(test_listing)
    
    print("\nEnriched Listing:")
    for key, value in enriched.items():
        print(f"  {key}: {value}")
        