"""
Zillow scraper for real estate listings
Uses requests + BeautifulSoup with anti-bot measures
"""

import time
import re
import json
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from app.utils import setup_logging, clean_price, clean_sqft, clean_year


class ZillowScraper:
    """
    Scraper for Zillow.com real estate listings
    Note: Zillow has strong anti-scraping measures, may require additional handling
    """
    
    def __init__(self):
        self.base_url = "https://www.zillow.com"
        self.logger = setup_logging('zillow_scraper')
        self.ua = UserAgent()
        self.session = requests.Session()
        
    def _get_headers(self) -> Dict[str, str]:
        """Generate request headers with random user agent"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.zillow.com',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def search_location(
        self, 
        city: str = "Newton",
        state: str = "MA",
        property_type: str = "houses",
        max_pages: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search Zillow for properties in a specific location
        
        Args:
            city: City name
            state: State abbreviation
            property_type: Type of property
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of property listings
        """
        self.logger.info(f"Scraping Zillow: {city}, {state}")
        
        # Construct Zillow search URL
        city_formatted = city.replace(' ', '-').lower()
        search_url = f"{self.base_url}/{city_formatted}-{state.lower()}"
        
        all_listings = []
        
        for page in range(1, max_pages + 1):
            page_url = f"{search_url}/{page}_p" if page > 1 else search_url
            
            try:
                listings = self._scrape_search_page(page_url)
                if not listings:
                    self.logger.info(f"No more listings found on page {page}")
                    break
                
                all_listings.extend(listings)
                self.logger.info(f"Page {page}: Found {len(listings)} listings")
                
                time.sleep(3)  # Longer delay for Zillow
                
            except Exception as e:
                self.logger.error(f"Error scraping page {page}: {e}")
                continue
        
        self.logger.info(f"Total Zillow listings scraped: {len(all_listings)}")
        return all_listings
    
    def _scrape_search_page(self, url: str) -> List[Dict[str, Any]]:
        """
        Scrape a single Zillow search results page
        
        Args:
            url: Page URL
            
        Returns:
            List of listings from the page
        """
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=15)
            response.raise_for_status()
            
            # Check if we hit a CAPTCHA or block
            if 'captcha' in response.text.lower() or response.status_code == 403:
                self.logger.warning("Zillow CAPTCHA or block detected")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to extract JSON data (Zillow often embeds data in scripts)
            script_data = self._extract_json_data(soup)
            if script_data:
                return self._parse_json_listings(script_data)
            
            # Fallback to HTML parsing
            property_cards = soup.find_all('article', class_=re.compile(r'list-card'))
            if not property_cards:
                property_cards = soup.find_all('div', attrs={'data-test': 'property-card'})
            
            listings = []
            for card in property_cards:
                listing = self._parse_property_card(card)
                if listing:
                    listing['source'] = 'zillow'
                    listing['source_url'] = url
                    listings.append(listing)
            
            return listings
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing page {url}: {e}")
            return []
    
    def _extract_json_data(self, soup: BeautifulSoup) -> Optional[Dict]:
        """
        Extract JSON data embedded in Zillow page scripts
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Parsed JSON data or None
        """
        try:
            # Look for Next.js data or similar
            scripts = soup.find_all('script', type='application/json')
            for script in scripts:
                if script.string and 'searchResults' in script.string:
                    data = json.loads(script.string)
                    return data
            
            # Look for inline JavaScript with data
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and '__NEXT_DATA__' in script.string:
                    # Extract JSON from script
                    match = re.search(r'__NEXT_DATA__\s*=\s*({.+})', script.string)
                    if match:
                        return json.loads(match.group(1))
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting JSON data: {e}")
            return None
    
    def _parse_json_listings(self, data: Dict) -> List[Dict[str, Any]]:
        """
        Parse listings from JSON data
        
        Args:
            data: JSON data structure
            
        Returns:
            List of listings
        """
        listings = []
        
        try:
            # Navigate to search results (structure varies)
            results = []
            
            # Try different JSON paths
            if 'searchResults' in data:
                results = data['searchResults'].get('listResults', [])
            elif 'cat1' in data:
                results = data['cat1'].get('searchResults', {}).get('listResults', [])
            
            for item in results:
                listing = {
                    'address': item.get('address', 'N/A'),
                    'price': clean_price(item.get('price', '')),
                    'beds': item.get('beds'),
                    'baths': item.get('baths'),
                    'sqft': clean_sqft(str(item.get('area', ''))),
                    'lot_size': clean_sqft(str(item.get('lotAreaValue', ''))),
                    'link': self.base_url + item.get('detailUrl', ''),
                    'zpid': item.get('zpid'),
                    'status': item.get('statusText', 'Unknown'),
                    'property_type': item.get('hdpData', {}).get('homeInfo', {}).get('homeType', 'Unknown'),
                    'source': 'zillow'
                }
                listings.append(listing)
            
        except Exception as e:
            self.logger.error(f"Error parsing JSON listings: {e}")
        
        return listings
    
    def _parse_property_card(self, card: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """
        Parse a single property card from Zillow HTML
        
        Args:
            card: BeautifulSoup element containing property data
            
        Returns:
            Dictionary with property details
        """
        try:
            listing = {}
            
            # Address
            address_elem = card.find('address')
            if address_elem:
                listing['address'] = address_elem.get_text(strip=True)
            else:
                listing['address'] = "N/A"
            
            # Price
            price_elem = card.find('span', attrs={'data-test': 'property-card-price'})
            if not price_elem:
                price_elem = card.find('div', class_=re.compile(r'price'))
            
            if price_elem:
                listing['price'] = clean_price(price_elem.get_text(strip=True))
            else:
                listing['price'] = None
            
            # Beds, Baths, Sqft
            details_elem = card.find('ul', class_=re.compile(r'list-card-details'))
            if details_elem:
                details_text = details_elem.get_text()
                
                beds_match = re.search(r'(\d+)\s*bd', details_text, re.IGNORECASE)
                listing['beds'] = int(beds_match.group(1)) if beds_match else None
                
                baths_match = re.search(r'([\d.]+)\s*ba', details_text, re.IGNORECASE)
                listing['baths'] = float(baths_match.group(1)) if baths_match else None
                
                sqft_match = re.search(r'([\d,]+)\s*sqft', details_text, re.IGNORECASE)
                listing['sqft'] = clean_sqft(sqft_match.group(1)) if sqft_match else None
            else:
                listing['beds'] = None
                listing['baths'] = None
                listing['sqft'] = None
            
            # Property link
            link_elem = card.find('a', class_=re.compile(r'list-card-link'))
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                listing['link'] = href if href.startswith('http') else self.base_url + href
            else:
                listing['link'] = None
            
            # ZPID (Zillow Property ID)
            zpid_match = re.search(r'/(\d+)_zpid', str(card))
            listing['zpid'] = zpid_match.group(1) if zpid_match else None
            
            # Status
            status_elem = card.find('div', class_=re.compile(r'list-card-status'))
            listing['status'] = status_elem.get_text(strip=True) if status_elem else "Unknown"
            
            return listing if listing.get('address') != "N/A" else None
            
        except Exception as e:
            self.logger.error(f"Error parsing property card: {e}")
            return None
    
    def scrape_property_details(self, property_url: str) -> Dict[str, Any]:
        """
        Scrape detailed information from a single Zillow property page
        
        Args:
            property_url: URL of the property detail page
            
        Returns:
            Dictionary with detailed property information
        """
        self.logger.info(f"Scraping property details: {property_url}")
        
        try:
            response = self.session.get(property_url, headers=self._get_headers(), timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {
                'url': property_url,
                'source': 'zillow'
            }
            
            # Try to extract structured data
            json_data = self._extract_json_data(soup)
            if json_data:
                # Parse from JSON if available
                home_info = json_data.get('props', {}).get('pageProps', {}).get('gdpClientCache', {})
                # Structure varies, adapt as needed
            
            # Year built
            year_elem = soup.find('span', string=re.compile(r'Year Built', re.IGNORECASE))
            if year_elem:
                year_parent = year_elem.find_parent()
                if year_parent:
                    year_match = re.search(r'\d{4}', year_parent.get_text())
                    details['year_built'] = clean_year(year_match.group()) if year_match else None
            
            # Lot size
            lot_elem = soup.find('span', string=re.compile(r'Lot', re.IGNORECASE))
            if lot_elem:
                lot_parent = lot_elem.find_parent()
                if lot_parent:
                    lot_match = re.search(r'([\d,]+)', lot_parent.get_text())
                    details['lot_size'] = clean_sqft(lot_match.group(1)) if lot_match else None
            
            # Description
            desc_elem = soup.find('div', class_=re.compile(r'description'))
            details['description'] = desc_elem.get_text(strip=True) if desc_elem else ""
            
            return details
            
        except Exception as e:
            self.logger.error(f"Error scraping property details: {e}")
            return {}


# Example usage
if __name__ == "__main__":
    scraper = ZillowScraper()
    listings = scraper.search_location("Newton", "MA", max_pages=2)
    
    print(f"\nFound {len(listings)} listings")
    for i, listing in enumerate(listings[:3], 1):
        print(f"\n{i}. {listing['address']}")
        print(f"   Price: ${listing['price']:,.0f}" if listing['price'] else "   Price: N/A")
        print(f"   Beds: {listing['beds']}, Baths: {listing['baths']}")
        print(f"   Sqft: {listing['sqft']}")
        print(f"   Status: {listing['status']}")