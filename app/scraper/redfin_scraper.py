"""
Redfin scraper for real estate listings
Uses requests + BeautifulSoup for efficient scraping
"""

import time
import re
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from app.utils import setup_logging, clean_price, clean_sqft, clean_year


class RedfinScraper:
    """
    Scraper for Redfin.com real estate listings
    """
    
    def __init__(self):
        self.base_url = "https://www.redfin.com"
        self.logger = setup_logging('redfin_scraper')
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
            'Upgrade-Insecure-Requests': '1'
        }
    
    def search_location(
        self, 
        city: str = "Newton",
        state: str = "MA",
        property_type: str = "house",
        max_pages: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search Redfin for properties in a specific location
        
        Args:
            city: City name
            state: State abbreviation
            property_type: Type of property (house, condo, etc.)
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of property listings
        """
        self.logger.info(f"Scraping Redfin: {city}, {state}")
        
        # Construct Redfin search URL
        search_url = f"{self.base_url}/city/{self._format_url_part(city)}/{state}/filter/property-type={property_type}"
        
        all_listings = []
        
        for page in range(1, max_pages + 1):
            page_url = f"{search_url}/page-{page}" if page > 1 else search_url
            
            try:
                listings = self._scrape_search_page(page_url)
                if not listings:
                    self.logger.info(f"No more listings found on page {page}")
                    break
                
                all_listings.extend(listings)
                self.logger.info(f"Page {page}: Found {len(listings)} listings")
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                self.logger.error(f"Error scraping page {page}: {e}")
                continue
        
        self.logger.info(f"Total Redfin listings scraped: {len(all_listings)}")
        return all_listings
    
    def _scrape_search_page(self, url: str) -> List[Dict[str, Any]]:
        """
        Scrape a single Redfin search results page
        
        Args:
            url: Page URL
            
        Returns:
            List of listings from the page
        """
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Redfin uses specific div classes for property cards
            property_cards = soup.find_all('div', class_=re.compile(r'HomeCard'))
            
            if not property_cards:
                # Try alternative selectors
                property_cards = soup.find_all('div', attrs={'data-rf-test-name': 'HomeCard'})
            
            listings = []
            for card in property_cards:
                listing = self._parse_property_card(card)
                if listing:
                    listing['source'] = 'redfin'
                    listing['source_url'] = url
                    listings.append(listing)
            
            return listings
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing page {url}: {e}")
            return []
    
    def _parse_property_card(self, card: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """
        Parse a single property card from Redfin
        
        Args:
            card: BeautifulSoup element containing property data
            
        Returns:
            Dictionary with property details
        """
        try:
            listing = {}
            
            # Address
            address_elem = card.find('div', class_=re.compile(r'address|homeAddress'))
            if address_elem:
                listing['address'] = address_elem.get_text(strip=True)
            else:
                listing['address'] = "N/A"
            
            # Price
            price_elem = card.find('span', class_=re.compile(r'price|homeprice'))
            if not price_elem:
                price_elem = card.find('div', attrs={'data-rf-test-id': 'abp-price'})
            
            if price_elem:
                listing['price'] = clean_price(price_elem.get_text(strip=True))
            else:
                listing['price'] = None
            
            # Beds & Baths
            stats_elem = card.find('div', class_=re.compile(r'stats|HomeStatsV2'))
            if stats_elem:
                stats_text = stats_elem.get_text()
                
                beds_match = re.search(r'(\d+)\s*bd', stats_text, re.IGNORECASE)
                listing['beds'] = int(beds_match.group(1)) if beds_match else None
                
                baths_match = re.search(r'([\d.]+)\s*ba', stats_text, re.IGNORECASE)
                listing['baths'] = float(baths_match.group(1)) if baths_match else None
                
                sqft_match = re.search(r'([\d,]+)\s*sq', stats_text, re.IGNORECASE)
                listing['sqft'] = clean_sqft(sqft_match.group(1)) if sqft_match else None
            else:
                listing['beds'] = None
                listing['baths'] = None
                listing['sqft'] = None
            
            # Property link
            link_elem = card.find('a', class_=re.compile(r'link|homecard'))
            if link_elem and link_elem.get('href'):
                listing['link'] = self.base_url + link_elem.get('href')
            else:
                listing['link'] = None
            
            # Status
            status_elem = card.find('span', class_=re.compile(r'status'))
            listing['status'] = status_elem.get_text(strip=True) if status_elem else "Unknown"
            
            # Description/Notes
            desc_elem = card.find('div', class_=re.compile(r'remarks|HomeRemarksV2'))
            listing['notes'] = desc_elem.get_text(strip=True) if desc_elem else ""
            
            return listing if listing.get('address') != "N/A" else None
            
        except Exception as e:
            self.logger.error(f"Error parsing property card: {e}")
            return None
    
    def scrape_property_details(self, property_url: str) -> Dict[str, Any]:
        """
        Scrape detailed information from a single property page
        
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
                'source': 'redfin'
            }
            
            # Year built
            year_elem = soup.find(string=re.compile(r'Year Built', re.IGNORECASE))
            if year_elem:
                year_parent = year_elem.find_parent()
                if year_parent:
                    year_text = year_parent.get_text()
                    year_match = re.search(r'\d{4}', year_text)
                    details['year_built'] = clean_year(year_match.group()) if year_match else None
            
            # Lot size
            lot_elem = soup.find(string=re.compile(r'Lot Size', re.IGNORECASE))
            if lot_elem:
                lot_parent = lot_elem.find_parent()
                if lot_parent:
                    lot_text = lot_parent.get_text()
                    lot_match = re.search(r'([\d,]+)', lot_text)
                    details['lot_size'] = clean_sqft(lot_match.group(1)) if lot_match else None
            
            # Description
            desc_elem = soup.find('div', class_=re.compile(r'description|remarks'))
            details['description'] = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # MLS number
            mls_elem = soup.find(string=re.compile(r'MLS#', re.IGNORECASE))
            if mls_elem:
                mls_match = re.search(r'MLS#\s*:?\s*(\w+)', mls_elem)
                details['mls_number'] = mls_match.group(1) if mls_match else None
            
            return details
            
        except Exception as e:
            self.logger.error(f"Error scraping property details: {e}")
            return {}
    
    def _format_url_part(self, text: str) -> str:
        """Format text for URL (lowercase, hyphens)"""
        return text.lower().replace(' ', '-')


# Example usage
if __name__ == "__main__":
    scraper = RedfinScraper()
    listings = scraper.search_location("Newton", "MA", max_pages=2)
    
    print(f"\nFound {len(listings)} listings")
    for i, listing in enumerate(listings[:3], 1):
        print(f"\n{i}. {listing['address']}")
        print(f"   Price: ${listing['price']:,.0f}" if listing['price'] else "   Price: N/A")
        print(f"   Beds: {listing['beds']}, Baths: {listing['baths']}")
        print(f"   Sqft: {listing['sqft']}")
        print(f"   Status: {listing['status']}")