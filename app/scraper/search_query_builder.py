"""
Enhanced search query builder for more specific property results
Focuses on getting actual property addresses instead of category pages
"""

import os
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()


class SearchQueryBuilder:
    """
    Builds targeted search queries to get specific property addresses
    instead of generic listing category pages
    """
    
    # Query templates that return actual properties with addresses
    SPECIFIC_PROPERTY_QUERIES = [
        # Site-specific searches for individual listings
        "site:zillow.com {location} \"single family\" \"lot\" home address",
        "site:redfin.com {location} \"single family\" property address",
        "site:realtor.com {location} MLS property \"address\"",
        
        # Address pattern searches
        "\"{street}\" {location} real estate for sale",
        "{location} homes for sale by owner address",
        
        # Development-specific with address patterns
        "{location} teardown opportunity address zip",
        "{location} development property street address",
    ]
    
    # Filters to improve result quality
    INCLUDE_FILTERS = [
        "address",
        "MLS",
        "property for sale",
        "single family home",
        "lot size",
        "zip code"
    ]
    
    # Exclude filters to remove category pages
    EXCLUDE_FILTERS = [
        "-site:pinterest.com",
        "-site:instagram.com",
        "-\"homes for sale in\"",  # Generic category pages
        "-\"search homes\"",
        "-\"browse listings\"",
        "-\"view all\"",
    ]
    
    def __init__(self):
        pass
    
    @staticmethod
    def build_address_focused_queries(location: str) -> List[str]:
        """
        Build search queries specifically designed to return individual properties with addresses
        
        Args:
            location: Location string (e.g., "Newton, MA")
            
        Returns:
            List of targeted search queries
        """
        city, state = location.split(',') if ',' in location else (location, '')
        city = city.strip()
        state = state.strip()
        
        queries = [
            # Direct address searches
            f"site:zillow.com {city} {state} single family home \"$\" address MLS",
            f"site:redfin.com {city} {state} property address zip code",
            f"site:realtor.com {city} {state} \"for sale\" MLS# address",
            
            # Specific development targets
            f"{city} {state} teardown property street address sold",
            f"{city} {state} fixer upper single family home address",
            f"{city} {state} large lot development ready property",
            
            # Alternative format searches
            f"\"{city},\" {state} home address \"for sale\" MLS",
            f"{city} MA real estate listing \"St\" OR \"Rd\" OR \"Ave\" OR \"Ln\"",
            
            # Specific neighborhood/address pattern searches
            f"site:zillow.com {city} {state} \"Road\" OR \"Street\" OR \"Avenue\" OR \"Lane\" for sale",
            f"site:redfin.com {city} {state} homes \"#\" address",
        ]
        
        return queries
    
    @staticmethod
    def build_optimized_query(
        base_query: str,
        location: str,
        exclude_generic: bool = True
    ) -> str:
        """
        Build an optimized search query with filters
        
        Args:
            base_query: Base search query
            location: Location string
            exclude_generic: Whether to exclude generic category pages
            
        Returns:
            Optimized search query string
        """
        query_parts = [base_query, location]
        
        # Add required terms
        query_parts.extend([
            "address",
            "(zillow.com OR redfin.com OR realtor.com)"
        ])
        
        # Add exclusions to remove category pages
        if exclude_generic:
            query_parts.extend([
                "-\"homes for sale in\"",
                "-\"browse\"",
                "-\"search\"",
                "-\"view all\"",
                "-\"map search\"",
            ])
        
        return " ".join(query_parts)
    
    @staticmethod
    def validate_address(address: str) -> bool:
        """
        Check if a string looks like a real address
        (not a generic category page title)
        
        Args:
            address: String to validate
            
        Returns:
            True if it looks like a real address
        """
        # Real addresses typically have:
        # - A number at the start
        # - Street type indicators
        # - Not category keywords
        
        import re
        
        # Real address pattern: "123 Main St, Newton, MA 02459"
        address_pattern = r'^\d+\s+[A-Za-z\s]+(?:St|Rd|Ave|Ln|Blvd|Way|Ct|Dr|Pl|Terr|Tr).*'
        
        # Category page patterns to exclude
        category_patterns = [
            r'for sale in',
            r'homes for sale',
            r'properties for sale',
            r'listings in',
            r'real estate in',
            r'browse',
            r'search',
            r'view all',
        ]
        
        # Check if it looks like a real address
        if re.match(address_pattern, address, re.IGNORECASE):
            return True
        
        # Check if it matches category patterns
        address_lower = address.lower()
        for pattern in category_patterns:
            if re.search(pattern, address_lower):
                return False
        
        return False
    
    @staticmethod
    def extract_real_addresses(listings: List[dict]) -> List[dict]:
        """
        Filter listings to keep only those with real addresses
        
        Args:
            listings: List of listing dictionaries
            
        Returns:
            Filtered list with only real property addresses
        """
        filtered = []
        
        for listing in listings:
            address = listing.get('address', '') or listing.get('title', '')
            
            if SearchQueryBuilder.validate_address(address):
                filtered.append(listing)
        
        return filtered


# Example usage
if __name__ == "__main__":
    builder = SearchQueryBuilder()
    
    # Generate address-focused queries
    location = "Newton, MA"
    queries = builder.build_address_focused_queries(location)
    
    print(f"Generated {len(queries)} address-focused queries for {location}:\n")
    for i, query in enumerate(queries, 1):
        print(f"{i}. {query}")
    
    # Test address validation
    print("\n\nTesting address validation:\n")
    test_addresses = [
        "136 Dudley Rd, Newton Center, MA 02459",
        "66 Rockland Pl, Newton Upper Falls, MA 02464",
        "Homes for Sale in Newton, MA with a Large Lot",
        "Newton MA Land & Lots For Sale - 11 Listings",
        "42 Lindbergh Ave, Newton, MA 02465",
    ]
    
    for addr in test_addresses:
        is_valid = SearchQueryBuilder.validate_address(addr)
        status = "✅ REAL ADDRESS" if is_valid else "❌ CATEGORY PAGE"
        print(f"{status}: {addr}")
