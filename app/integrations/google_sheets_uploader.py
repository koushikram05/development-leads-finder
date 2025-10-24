"""
Google Sheets Integration for Development Leads
Automatically uploads and updates classified listings to Google Sheets
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional


def _num_to_col(n: int) -> str:
    """Convert a column number (1-based) to a letter (A, B, ..., Z, AA, AB, ...)"""
    result = ""
    while n > 0:
        n -= 1
        result = chr(65 + (n % 26)) + result
        n //= 26
    return result


class GoogleSheetsUploader:
    """
    Manages uploading real estate listings to Google Sheets
    Features:
    - Auto-create sheets if not exists
    - Update existing sheets with latest data
    - Support for multiple sheet tabs
    - Sorting by development score
    - Preserve formatting and filters
    """
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Google Sheets uploader
        
        Args:
            credentials_path: Path to Google service account JSON (defaults to .env var)
        
        Raises:
            FileNotFoundError: If credentials file not found
            ValueError: If credentials not configured
        """
        self.logger = logging.getLogger('sheets_uploader')
        
        # Get credentials path from parameter or environment
        if credentials_path is None:
            credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'google_credentials.json')
        
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                f"Google credentials not found at {credentials_path}. "
                "Follow setup steps in FAST_TRACK_TODAY.md"
            )
        
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                credentials_path, scopes
            )
            self.client = gspread.authorize(credentials)
            self.logger.info("✓ Google Sheets authenticated successfully")
        except Exception as e:
            raise ValueError(f"Failed to authenticate Google Sheets: {e}")
    
    def upload_listings(
        self,
        listings: List[Dict],
        sheet_name: str = 'Development_Leads',
        location_filter: str = 'Newton, MA',
        sort_by: str = 'development_score'
    ) -> bool:
        """
        Upload listings to Google Sheet with automatic sorting and formatting
        
        Args:
            listings: List of listing dictionaries with classification data
            sheet_name: Name of Google Sheet (creates if doesn't exist)
            location_filter: Filter location (default: Newton, MA)
            sort_by: Column to sort by (default: development_score)
        
        Returns:
            bool: Success status
        """
        if not listings:
            self.logger.warning("No listings to upload")
            return False
        
        try:
            # Get or create spreadsheet
            try:
                sheet = self.client.open(sheet_name)
                self.logger.info(f"✓ Opened existing sheet: {sheet_name}")
            except gspread.SpreadsheetNotFound:
                sheet = self.client.create(sheet_name)
                self.logger.info(f"✓ Created new sheet: {sheet_name}")
            
            # Get first worksheet
            worksheet = sheet.sheet1
            
            # Filter listings by location
            filtered_listings = self._filter_by_location(listings, location_filter)
            self.logger.info(f"✓ Filtered {len(filtered_listings)} listings for {location_filter}")
            
            # Sort by development score (highest first)
            sorted_listings = sorted(
                filtered_listings,
                key=lambda x: x.get(sort_by, 0),
                reverse=True
            )
            
            # Prepare headers
            headers = self._get_headers(sorted_listings)
            
            # Prepare all data rows (headers + listings)
            all_rows = [headers]
            for listing in sorted_listings:
                row = self._listing_to_row(listing, headers)
                all_rows.append(row)
            
            # Clear worksheet
            worksheet.clear()
            
            # Calculate column range letter
            num_cols = len(headers)
            end_col = _num_to_col(num_cols)
            
            # Update rows one at a time with proper range notation
            for i, row in enumerate(all_rows, 1):
                try:
                    range_name = f'A{i}:{end_col}{i}'
                    worksheet.update(values=[row], range_name=range_name)
                except Exception as e:
                    self.logger.warning(f"Could not update row {i}: {e}")
            
            # Freeze header row
            try:
                worksheet.freeze(1, 0)
            except Exception as e:
                self.logger.warning(f"Could not freeze headers: {e}")
            
            # Add filter (optional - may not work on all versions)
            try:
                worksheet.add_filter(1, 1, len(sorted_listings) + 1, len(headers))
            except Exception as e:
                self.logger.warning(f"Could not add filter (gspread version may not support this): {e}")
            
            # Log summary
            self.logger.info(
                f"✓ Uploaded {len(sorted_listings)} listings to '{sheet_name}' "
                f"(Sorted by {sort_by})"
            )
            
            # Record upload in log
            self._log_upload_event(sheet_name, len(sorted_listings), location_filter)
            
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Failed to upload listings: {e}")
            return False
    
    def upload_with_tabs(
        self,
        listings: List[Dict],
        sheet_name: str = 'Development_Leads',
        locations: Optional[List[str]] = None
    ) -> bool:
        """
        Upload listings organized by location in separate tabs
        
        Args:
            listings: List of listings
            sheet_name: Main sheet name
            locations: List of locations to create separate tabs (e.g., ['Newton, MA', 'Waltham, MA'])
        
        Returns:
            bool: Success status
        """
        if locations is None:
            locations = ['Newton, MA']
        
        try:
            # Get or create spreadsheet
            try:
                sheet = self.client.open(sheet_name)
            except gspread.SpreadsheetNotFound:
                sheet = self.client.create(sheet_name)
            
            # Create or get worksheets for each location
            for location in locations:
                # Get or create worksheet
                try:
                    worksheet = sheet.worksheet(location)
                    worksheet.clear()
                except gspread.WorksheetNotFound:
                    worksheet = sheet.add_worksheet(title=location, rows=1000, cols=25)
                
                # Filter and sort listings for this location
                filtered = self._filter_by_location(listings, location)
                sorted_listings = sorted(
                    filtered,
                    key=lambda x: x.get('development_score', 0),
                    reverse=True
                )
                
                if sorted_listings:
                    headers = self._get_headers(sorted_listings)
                    
                    # Prepare all data rows (headers + listings)
                    all_rows = [headers]
                    for listing in sorted_listings:
                        row = self._listing_to_row(listing, headers)
                        all_rows.append(row)
                    
                    # Clear worksheet
                    worksheet.clear()
                    
                    # Calculate column range letter
                    num_cols = len(headers)
                    end_col = _num_to_col(num_cols)
                    
                    # Update rows one at a time with proper range notation
                    for i, row in enumerate(all_rows, 1):
                        try:
                            range_name = f'A{i}:{end_col}{i}'
                            worksheet.update(values=[row], range_name=range_name)
                        except Exception as e:
                            self.logger.warning(f"Could not update row {i} in {location}: {e}")
                    
                    try:
                        worksheet.freeze(1, 0)
                    except Exception as e:
                        self.logger.warning(f"Could not freeze tab {location}: {e}")
                    
                    try:
                        worksheet.add_filter(1, 1, len(sorted_listings) + 1, len(headers))
                    except Exception as e:
                        self.logger.warning(f"Could not add filter to tab {location}: {e}")
                
                self.logger.info(f"✓ Updated tab '{location}' with {len(sorted_listings)} listings")
            
            self._log_upload_event(sheet_name, len(listings), f"Multi-location: {locations}")
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Failed to upload with tabs: {e}")
            return False
    
    def _filter_by_location(self, listings: List[Dict], location: str) -> List[Dict]:
        """Filter listings by location (city, MA)"""
        target_city = location.split(',')[0].lower().strip()
        filtered = []
        for listing in listings:
            # Try 'city' field first, then extract from address
            city = listing.get('city', '').lower().strip()
            if not city and listing.get('address'):
                # Extract city from address (e.g., "42 Lindbergh Ave, Newton, MA 02465")
                # Look for the target city name in the address
                addr_lower = listing.get('address', '').lower()
                if target_city in addr_lower:
                    city = target_city
            
            if city == target_city:
                filtered.append(listing)
        
        return filtered
    
    def _get_headers(self, listings: List[Dict]) -> List[str]:
        """Extract column headers from listings, prioritizing key fields"""
        # Priority headers to show first
        priority_headers = [
            'address', 'city', 'price', 'beds', 'baths', 'sqft',
            'lot_size', 'year_built', 'zoning', 'label',
            'development_score', 'confidence', 'explanation',
            'latitude', 'longitude', 'url', 'source', 'first_seen'
        ]
        
        # Get all unique keys from listings
        all_keys = set()
        for listing in listings:
            all_keys.update(listing.keys())
        
        # Order: priority headers first, then rest
        headers = [h for h in priority_headers if h in all_keys]
        headers.extend([k for k in sorted(all_keys) if k not in headers])
        
        return headers
    
    def _listing_to_row(self, listing: Dict, headers: List[str]) -> List:
        """Convert listing dict to row data matching headers"""
        row = []
        for header in headers:
            value = listing.get(header, '')
            
            # Format specific fields
            if header in ['price', 'sqft', 'lot_size', 'development_score']:
                if isinstance(value, (int, float)):
                    value = str(value)
            elif header in ['latitude', 'longitude']:
                if isinstance(value, float):
                    value = f"{value:.6f}"
            elif header == 'first_seen' and value:
                if isinstance(value, datetime):
                    value = value.isoformat()
            
            row.append(str(value) if value else '')
        
        return row
    
    def _log_upload_event(self, sheet_name: str, count: int, location: str) -> None:
        """Log upload event to file for audit trail"""
        try:
            log_file = 'data/sheets_upload_log.txt'
            os.makedirs('data', exist_ok=True)
            
            with open(log_file, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(
                    f"{timestamp} | Sheet: {sheet_name} | Listings: {count} | "
                    f"Location: {location}\n"
                )
        except Exception as e:
            self.logger.warning(f"Failed to log upload event: {e}")
    
    def get_upload_log(self) -> str:
        """Retrieve upload history log"""
        log_file = 'data/sheets_upload_log.txt'
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    return f.read()
            return "No upload history found"
        except Exception as e:
            return f"Error reading log: {e}"
