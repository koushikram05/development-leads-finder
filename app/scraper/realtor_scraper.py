"""
Realtor.com scraper for real estate listings
Uses requests + BeautifulSoup for data extraction
"""

import time
import re
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from app.utils import setup_logging, clean_price, clean_sqft, clean_year


class RealtorScraper:
    """
    Scraper for Realtor.com real estate listings
    """
    
    def __init__(self):
        self.base_url = "https://www.realtor.com"
        self.logger = setup_logging('realtor_scraper')
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
            'Referer': 'https://www.realtor.com'
        }
    
    def search_location(
        self, 
        city: str = "Newton",
        state: str = "MA",
        property_type: str = "single_family",
        max_pages: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search Realtor.com for properties in a specific location
        
        Args:
            city: City name
            state: State abbreviation
            property_type: Type of property
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of property listings
        """
        self.logger.info(f"Scraping Realtor.com: {city}, {state}")
        
        # Construct Realtor.com search URL
        city_formatted = city.replace(' ', '_')
        search_url = f"{self.base_url}/realestateandhomes-search/{city_formatted}_{state}/type-{property_type}"
        
        all_listings = []
        
        for page in range(1, max_pages + 1):
            page_url = f"{search_url}/pg-{page}" if page > 1 else search_url
            
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
        
        self.logger.info(f"Total Realtor.com listings scraped: {len(all_listings)}")
        return all_listings
    
    def _scrape_search_page(self, url: str) -> List[Dict[str, Any]]:
        """
        Scrape a single Realtor.com search results page
        
        Args:
            url: Page URL
            
        Returns:
            List of listings from the page
        """
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Realtor.com uses specific data attributes
            property_cards = soup.find_all('li', attrs={'data-testid': 'property-card'})
            
            if not property_cards:
                # Try alternative selectors
                property_cards = soup.find_all('div', class_=re.compile(r'property-card|PropertyCard'))
            
            listings = []
            for card in property_cards:
                listing = self._parse_property_card(card)
                if listing:
                    listing['source'] = 'realtor'
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
        Parse a single property card from Realtor.com
        
        Args:
            card: BeautifulSoup element containing property data
            
        Returns:
            Dictionary with property details
        """
        try:
            listing = {}
            
            # Address
            address_elem = card.find('div', attrs={'data-testid': 'property-address'})
            if not address_elem:
                address_elem = card.find('div', class_=re.compile(r'address'))
            
            if address_elem:
                listing['address'] = address_elem.get_text(strip=True)
            else:
                listing['address'] = "N/A"
            
            # Price
            price_elem = card.find('span', attrs={'data-testid': 'property-price'})
            if not price_elem:
                price_elem = card.find('div', class_=re.compile(r'price'))
            
            if price_elem:
                listing['price'] = clean_price(price_elem.get_text(strip=True))
            else:
                listing['price'] = None
            
            # Beds & Baths
            beds_elem = card.find('li', attrs={'data-testid': 'property-meta-beds'})
            if beds_elem:
                beds_match = re.search(r'(\d+)', beds_elem.get_text())
                listing['beds'] = int(beds_match.group(1)) if beds_match else None
            else:
                listing['beds'] = None
            
            baths_elem = card.find('li', attrs={'data-testid': 'property-meta-baths'})
            if baths_elem:
                baths_match = re.search(r'([\d.]+)', baths_elem.get_text())
                listing['baths'] = float(baths_match.group(1)) if baths_match else None
            else:
                listing['baths'] = None
            
            # Square footage
            sqft_elem = card.find('li', attrs={'data-testid': 'property-meta-sqft'})
            if sqft_elem:
                listing['sqft'] = clean_sqft(sqft_elem.get_text())
            else:
                listing['sqft'] = None
            
            # Lot size
            lot_elem = card.find('li', attrs={'data-testid': 'property-meta-lot-size'})
            if lot_elem:
                listing['lot_size'] = clean_sqft(lot_elem.get_text())
            else:
                listing['lot_size'] = None
            
            # Property link
            link_elem = card.find('a', class_=re.compile(r'property-link'))
            if not link_elem:
                link_elem = card.find('a', href=re.compile(r'/realestateandhomes-detail'))
            
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                listing['link'] = href if href.startswith('http') else self.base_url + href
            else:
                listing['link'] = None
            
            # Status
            status_elem = card.find('span', class_=re.compile(r'status'))
            listing['status'] = status_elem.get_text(strip=True) if status_elem else "Unknown"
            
            # Property type
            type_elem = card.find('div', attrs={'data-testid': 'property-type'})
            listing['property_type'] = type_elem.get_text(strip=True) if type_elem else "Unknown"
            
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
                'source': 'realtor'
            }
            
            # Year built
            year_elem = soup.find('span', string=re.compile(r'Year Built', re.IGNORECASE))
            if year_elem:
                year_parent = year_elem.find_parent()
                if year_parent:
                    year_match = re.search(r'\d{4}', year_parent.get_text())
                    details['year_built'] = clean_year(year_match.group()) if year_match else None
            
            # Lot size
            lot_elem = soup.find('span', string=re.compile(r'Lot Size', re.IGNORECASE))
            if lot_elem:
                lot_parent = lot_elem.find_parent()
                if lot_parent:
                    lot_match = re.search(r'([\d,]+)', lot_parent.get_text())
                    details['lot_size'] = clean_sqft(lot_match.group(1)) if lot_match else None
            
            # Description
            desc_elem = soup.find('div', attrs={'data-testid': 'description'})
            if not desc_elem:
                desc_elem = soup.find('div', class_=re.compile(r'description'))
            details['description'] = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # MLS number
            mls_elem = soup.find(string=re.compile(r'MLS#', re.IGNORECASE))
            if mls_elem:
                mls_match = re.search(r'MLS#\s*:?\s*(\w+)', mls_elem)
                details['mls_number'] = mls_match.group(1) if mls_match else None
            
            # Zoning
            zoning_elem = soup.find('span', string=re.compile(r'Zoning', re.IGNORECASE))
            if zoning_elem:
                zoning_parent = zoning_elem.find_parent()
                if zoning_parent:
                    details['zoning'] = zoning_parent.get_text().replace('Zoning', '').strip()
            
            return details
            
        except Exception as e:
            self.logger.error(f"Error scraping property details: {e}")
            return {}


# Example usage
if __name__ == "__main__":
    scraper = RealtorScraper()
    listings = scraper.search_location("Newton", "MA", max_pages=2)
    
    print(f"\nFound {len(listings)} listings")
    for i, listing in enumerate(listings[:3], 1):
        print(f"\n{i}. {listing['address']}")
        print(f"   Price: ${listing['price']:,.0f}" if listing['price'] else "   Price: N/A")
        print(f"   Beds: {listing['beds']}, Baths: {listing['baths']}")
        print(f"   Sqft: {listing['sqft']}, Lot: {listing.get('lot_size')}")
        print(f"   Status: {listing['status']}")