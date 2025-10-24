"""
Utility functions for the Anil Project
Includes logging, CSV operations, data cleaning, and helper functions
"""

import os
import csv
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project directories
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = DATA_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


def setup_logging(name: str = "anil_project", level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging with both file and console handlers
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler
    log_file = LOGS_DIR / f"pipeline_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_env_variable(key: str, default: Optional[str] = None) -> str:
    """
    Get environment variable with error handling
    
    Args:
        key: Environment variable key
        default: Default value if not found
        
    Returns:
        Environment variable value
    """
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Environment variable {key} not found")
    return value


def save_to_csv(data: List[Dict[str, Any]], filename: str, append: bool = False) -> str:
    """
    Save data to CSV file
    
    Args:
        data: List of dictionaries to save
        filename: Output filename
        append: Whether to append to existing file
        
    Returns:
        Full path to saved file
    """
    if not data:
        logger = setup_logging()
        logger.warning(f"No data to save to {filename}")
        return ""
    
    filepath = DATA_DIR / filename
    df = pd.DataFrame(data)
    
    mode = 'a' if append else 'w'
    header = not append or not filepath.exists()
    
    df.to_csv(filepath, mode=mode, header=header, index=False, encoding='utf-8')
    
    logger = setup_logging()
    logger.info(f"Saved {len(data)} records to {filepath}")
    
    return str(filepath)


def load_from_csv(filename: str) -> List[Dict[str, Any]]:
    """
    Load data from CSV file
    
    Args:
        filename: Input filename
        
    Returns:
        List of dictionaries
    """
    filepath = DATA_DIR / filename
    
    if not filepath.exists():
        logger = setup_logging()
        logger.warning(f"File not found: {filepath}")
        return []
    
    df = pd.read_csv(filepath)
    return df.to_dict('records')


def save_to_json(data: List[Dict[str, Any]], filename: str) -> str:
    """
    Save data to JSON file
    
    Args:
        data: List of dictionaries to save
        filename: Output filename
        
    Returns:
        Full path to saved file
    """
    filepath = DATA_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger = setup_logging()
    logger.info(f"Saved {len(data)} records to {filepath}")
    
    return str(filepath)


def clean_price(price_str: str) -> Optional[float]:
    """
    Clean and convert price string to float
    
    Args:
        price_str: Price string (e.g., "$1,200,000")
        
    Returns:
        Float price or None
    """
    if not price_str or price_str == "N/A":
        return None
    
    try:
        # Remove $, commas, and other non-numeric characters
        cleaned = ''.join(c for c in str(price_str) if c.isdigit() or c == '.')
        return float(cleaned) if cleaned else None
    except (ValueError, AttributeError):
        return None


def clean_sqft(sqft_str: str) -> Optional[float]:
    """
    Clean and convert square footage string to float
    
    Args:
        sqft_str: Square footage string (e.g., "9,500 sqft")
        
    Returns:
        Float sqft or None
    """
    if not sqft_str or sqft_str == "N/A":
        return None
    
    try:
        # Remove commas, 'sqft', and other non-numeric characters
        cleaned = ''.join(c for c in str(sqft_str) if c.isdigit() or c == '.')
        return float(cleaned) if cleaned else None
    except (ValueError, AttributeError):
        return None


def clean_year(year_str: str) -> Optional[int]:
    """
    Clean and convert year string to int
    
    Args:
        year_str: Year string
        
    Returns:
        Integer year or None
    """
    if not year_str or year_str == "N/A":
        return None
    
    try:
        year = int(''.join(c for c in str(year_str) if c.isdigit()))
        # Validate year is reasonable
        if 1700 <= year <= datetime.now().year:
            return year
        return None
    except (ValueError, AttributeError):
        return None


def extract_city_state(address: str) -> tuple:
    """
    Extract city and state from address string
    
    Args:
        address: Full address string
        
    Returns:
        Tuple of (city, state)
    """
    try:
        parts = address.split(',')
        if len(parts) >= 3:
            city = parts[-2].strip()
            state = parts[-1].strip().split()[0]
            return city, state
        return "Unknown", "Unknown"
    except Exception:
        return "Unknown", "Unknown"


def deduplicate_listings(listings: List[Dict[str, Any]], key: str = 'address') -> List[Dict[str, Any]]:
    """
    Remove duplicate listings based on a key
    
    Args:
        listings: List of listing dictionaries
        key: Key to use for deduplication
        
    Returns:
        Deduplicated list
    """
    seen = set()
    unique_listings = []
    
    for listing in listings:
        identifier = listing.get(key, '')
        if identifier and identifier not in seen:
            seen.add(identifier)
            unique_listings.append(listing)
    
    logger = setup_logging()
    logger.info(f"Deduplicated {len(listings)} -> {len(unique_listings)} listings")
    
    return unique_listings


def calculate_price_per_sqft(price: Optional[float], sqft: Optional[float]) -> Optional[float]:
    """
    Calculate price per square foot
    
    Args:
        price: Property price
        sqft: Square footage
        
    Returns:
        Price per sqft or None
    """
    if price and sqft and sqft > 0:
        return round(price / sqft, 2)
    return None


def get_timestamp() -> str:
    """
    Get current timestamp as formatted string
    
    Returns:
        Timestamp string
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def merge_listings(
    existing: List[Dict[str, Any]], 
    new: List[Dict[str, Any]], 
    key: str = 'address'
) -> List[Dict[str, Any]]:
    """
    Merge new listings with existing ones, updating duplicates
    
    Args:
        existing: Existing listings
        new: New listings to merge
        key: Key to use for matching
        
    Returns:
        Merged list
    """
    existing_dict = {item[key]: item for item in existing if key in item}
    
    for item in new:
        if key in item:
            existing_dict[item[key]] = item
    
    return list(existing_dict.values())