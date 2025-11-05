"""
LLM-powered search using SerpAPI for real estate listings
Alternative to direct scraping, more reliable and faster
"""

import os
import time
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv
from app.utils import setup_logging, get_env_variable, clean_price, clean_sqft

load_dotenv()


class LLMSearch:
    """
    Search for real estate listings using SerpAPI
    Provides structured data from Google search results
    """
    
    def __init__(self):
        self.api_key = get_env_variable('SERPAPI_KEY')
        self.base_url = "https://serpapi.com/search"
        self.logger = setup_logging('llm_search')
        
    def search_properties(
        self, 
        query: str, 
        location: str = "Newton, MA",
        num_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for properties using SerpAPI Google Search
        
        Args:
            query: Search query (e.g., "teardown single family home")
            location: Location to search
            num_results: Number of results to fetch
            
        Returns:
            List of property dictionaries
        """
        self.logger.info(f"Searching: '{query}' in {location}")
        
        # Construct full search query
        full_query = f"{query} {location} site:zillow.com OR site:redfin.com OR site:realtor.com"
        
        params = {
            "q": full_query,
            "api_key": self.api_key,
            "engine": "google",
            "num": num_results,
            "gl": "us",
            "hl": "en"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            listings = self._parse_search_results(data)
            self.logger.info(f"Found {len(listings)} listings from search")
            
            return listings
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"SerpAPI request failed: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error processing search results: {e}")
            return []
    
    def _parse_search_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse SerpAPI search results into structured listings
        
        Args:
            data: Raw SerpAPI response
            
        Returns:
            List of parsed listings
        """
        listings = []
        
        organic_results = data.get('organic_results', [])
        
        for result in organic_results:
            listing = {
                'title': result.get('title', ''),
                'link': result.get('link', ''),
                'snippet': result.get('snippet', ''),
                'source': self._identify_source(result.get('link', '')),
                'search_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Try to extract price from title or snippet
            listing['price'] = self._extract_price(result)
            
            # Extract address from title
            listing['address'] = self._extract_address(result)
            
            # Only add if we have meaningful data
            if listing['address'] or listing['link']:
                listings.append(listing)
        
        return listings
    
    def _identify_source(self, url: str) -> str:
        """Identify the real estate source from URL"""
        url_lower = url.lower()
        if 'zillow.com' in url_lower:
            return 'zillow'
        elif 'redfin.com' in url_lower:
            return 'redfin'
        elif 'realtor.com' in url_lower:
            return 'realtor'
        else:
            return 'other'
    
    def _extract_price(self, result: Dict[str, Any]) -> Optional[float]:
        """Extract price from search result"""
        text = f"{result.get('title', '')} {result.get('snippet', '')}"
        
        # Look for price patterns like $1,200,000 or $1.2M
        import re
        
        # Match formats like $1,200,000
        price_match = re.search(r'\$[\d,]+', text)
        if price_match:
            return clean_price(price_match.group())
        
        # Match formats like $1.2M
        million_match = re.search(r'\$([\d.]+)M', text, re.IGNORECASE)
        if million_match:
            return float(million_match.group(1)) * 1_000_000
        
        return None
    
    def _extract_address(self, result: Dict[str, Any]) -> str:
        """Extract address from search result - only real property addresses"""
        title = result.get('title', '')
        
        # Address is typically at the start of the title
        # Example: "68 Vernon St, Newton, MA 02458 | MLS# ..."
        import re
        
        # FIRST: Check if this is a real address or category page
        if not self._is_real_address(title):
            return ""
        
        # Extract the address part before pipe or colon
        address_match = re.match(r'^([^|:]+)', title)
        
        if address_match:
            return address_match.group(1).strip()
        
        return ""
    
    def _is_real_address(self, text: str) -> bool:
        """
        Determine if text is a real property address vs category page
        
        Real address pattern: "123 Main St, City, State 12345"
        Category pages: "Homes for Sale in...", "Land & Lots For Sale", etc
        """
        import re
        
        # Real address must start with a number (street number)
        if not re.match(r'^\d+\s+', text):
            return False
        
        # Check for street type indicators after number
        street_types = ['St', 'Rd', 'Ave', 'Ln', 'Blvd', 'Way', 'Ct', 'Dr', 'Pl', 'Terr', 'Tr', 'Pkwy', 'Circle', 'Cove']
        has_street_type = any(st in text for st in street_types)
        
        if not has_street_type:
            return False
        
        # Exclude category page keywords
        exclude_keywords = [
            'for sale in',
            'homes for sale',
            'properties for sale',
            'listings',
            'browse',
            'search homes',
            'land & lots',
            'new construction homes',
        ]
        
        text_lower = text.lower()
        for keyword in exclude_keywords:
            if keyword in text_lower:
                return False
        
        # Must have location info (city, state, zip)
        has_state = re.search(r',\s*[A-Z]{2}\s*\d{5}', text)
        if not has_state:
            return False
        
        return True
    
    def search_google_maps(
        self, 
        query: str, 
        location: str = "Newton, MA"
    ) -> List[Dict[str, Any]]:
        """
        Search Google Maps for properties (alternative method)
        
        Args:
            query: Search query
            location: Location to search
            
        Returns:
            List of properties with location data
        """
        self.logger.info(f"Searching Google Maps: '{query}' in {location}")
        
        params = {
            "q": f"{query} {location}",
            "api_key": self.api_key,
            "engine": "google_maps",
            "type": "search",
            "hl": "en"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('local_results', [])
            
            listings = []
            for result in results:
                listing = {
                    'title': result.get('title', ''),
                    'address': result.get('address', ''),
                    'gps_coordinates': result.get('gps_coordinates', {}),
                    'rating': result.get('rating'),
                    'phone': result.get('phone'),
                    'source': 'google_maps'
                }
                listings.append(listing)
            
            self.logger.info(f"Found {len(listings)} results from Google Maps")
            return listings
            
        except Exception as e:
            self.logger.error(f"Google Maps search failed: {e}")
            return []
    
    def search_multiple_queries(
        self, 
        queries: List[str], 
        location: str = "Newton, MA"
    ) -> List[Dict[str, Any]]:
        """
        Run multiple search queries and combine results
        
        Args:
            queries: List of search queries
            location: Location to search
            
        Returns:
            Combined list of all results
        """
        all_listings = []
        
        for query in queries:
            listings = self.search_properties(query, location)
            all_listings.extend(listings)
            time.sleep(1)  # Rate limiting
        
        # Deduplicate by link
        seen_links = set()
        unique_listings = []
        
        for listing in all_listings:
            link = listing.get('link', '')
            if link and link not in seen_links:
                seen_links.add(link)
                unique_listings.append(listing)
        
        self.logger.info(f"Total unique listings: {len(unique_listings)}")
        return unique_listings


# Example usage
if __name__ == "__main__":
    searcher = LLMSearch()
    
    # Example queries
    queries = [
        "teardown opportunity single family home",
        "builder special Newton MA",
        "large lot development opportunity"
    ]
    
    results = searcher.search_multiple_queries(queries, "Newton, MA")
    
    print(f"\nFound {len(results)} total listings")
    for i, listing in enumerate(results[:5], 1):
        print(f"\n{i}. {listing['title']}")
        print(f"   Address: {listing['address']}")
        print(f"   Price: ${listing['price']:,.0f}" if listing['price'] else "   Price: N/A")
        print(f"   Source: {listing['source']}")
        print(f"   Link: {listing['link']}")