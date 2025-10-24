"""
Historical Database Manager for Development Leads
Persists all leads, tracks changes, enables trend analysis, and supports model fine-tuning
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class HistoricalDatabaseManager:
    """
    Manages SQLite database for historical lead tracking
    
    Tables:
    - listings: Core property data (deduplicated by address)
    - classifications: Classification history (tracks score changes)
    - price_history: Price tracking (detect value changes)
    - scan_runs: Pipeline execution metadata
    """
    
    def __init__(self, db_path: str = "data/development_leads.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connection pooling
        self._local_conn = None
        self._initialize_db()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _initialize_db(self):
        """Create tables if they don't exist"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Scan runs table - tracks pipeline executions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_runs (
                    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    search_query TEXT,
                    location TEXT,
                    run_type TEXT,
                    total_found INTEGER,
                    opportunities_found INTEGER,
                    high_value_found INTEGER,
                    duration_seconds FLOAT,
                    status TEXT DEFAULT 'success'
                )
            """)
            
            # Core listings table - one record per unique property
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    listing_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    address TEXT UNIQUE NOT NULL,
                    city TEXT,
                    state TEXT,
                    zip_code TEXT,
                    latitude REAL,
                    longitude REAL,
                    lot_size REAL,
                    square_feet REAL,
                    bedrooms INTEGER,
                    bathrooms REAL,
                    year_built INTEGER,
                    property_type TEXT,
                    zoning_type TEXT,
                    source TEXT,
                    listing_url TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_price REAL,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # Classifications table - tracks classification history for fine-tuning
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS classifications (
                    classification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    listing_id INTEGER NOT NULL,
                    run_id INTEGER,
                    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    label TEXT,
                    development_score REAL,
                    reasoning TEXT,
                    confidence_score REAL,
                    buildable_sqft REAL,
                    estimated_profit REAL,
                    roi_score REAL,
                    model_version TEXT,
                    FOREIGN KEY(listing_id) REFERENCES listings(listing_id),
                    FOREIGN KEY(run_id) REFERENCES scan_runs(run_id)
                )
            """)
            
            # Price history table - track price changes over time
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    price_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    listing_id INTEGER NOT NULL,
                    run_id INTEGER,
                    record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    price REAL,
                    price_change REAL,
                    price_change_percent REAL,
                    days_on_market INTEGER,
                    FOREIGN KEY(listing_id) REFERENCES listings(listing_id),
                    FOREIGN KEY(run_id) REFERENCES scan_runs(run_id)
                )
            """)
            
            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_listings_address ON listings(address)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_listings_location ON listings(city, state)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_classifications_date ON classifications(run_date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_classifications_score ON classifications(development_score)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_price_history_date ON price_history(record_date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_scan_runs_date ON scan_runs(run_date)
            """)
            
            logger.info(f"Database initialized at {self.db_path}")
    
    def record_scan_run(
        self,
        search_query: str,
        location: str,
        run_type: str = "manual",
        total_found: int = 0,
        opportunities_found: int = 0,
        high_value_found: int = 0,
        duration_seconds: float = 0.0
    ) -> int:
        """
        Record a pipeline scan run
        
        Args:
            search_query: Search query used
            location: Location searched
            run_type: Type of run (manual, daily, weekly)
            total_found: Total properties found
            opportunities_found: Development opportunities found
            high_value_found: High-value opportunities (score >= 70)
            duration_seconds: Pipeline execution time
            
        Returns:
            run_id for tracking
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scan_runs
                (search_query, location, run_type, total_found, opportunities_found, 
                 high_value_found, duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (search_query, location, run_type, total_found, opportunities_found,
                  high_value_found, duration_seconds))
            
            run_id = cursor.lastrowid
            logger.info(f"Recorded scan run {run_id}: {opportunities_found} opportunities in {duration_seconds:.1f}s")
            return run_id
    
    def save_listings(
        self,
        listings: List[Dict[str, Any]],
        run_id: int,
        auto_classify: bool = True
    ) -> Dict[str, int]:
        """
        Save listings to database, handling duplicates
        
        Args:
            listings: List of listing dictionaries
            run_id: Associated scan run ID
            auto_classify: Whether to record classifications
            
        Returns:
            Dictionary with new/updated counts
        """
        stats = {
            'new_listings': 0,
            'updated_listings': 0,
            'classifications_added': 0,
            'errors': 0
        }
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            for listing in listings:
                try:
                    address = listing.get('address', '').strip()
                    if not address:
                        continue
                    
                    # Prepare listing data
                    listing_data = {
                        'address': address,
                        'city': listing.get('city', ''),
                        'state': listing.get('state', ''),
                        'zip_code': listing.get('zip_code', ''),
                        'latitude': listing.get('latitude'),
                        'longitude': listing.get('longitude'),
                        'lot_size': listing.get('lot_size'),
                        'square_feet': listing.get('square_feet'),
                        'bedrooms': listing.get('bedrooms'),
                        'bathrooms': listing.get('bathrooms'),
                        'year_built': listing.get('year_built'),
                        'property_type': listing.get('property_type', ''),
                        'zoning_type': listing.get('zoning_type', ''),
                        'source': listing.get('source', 'scraped'),
                        'listing_url': listing.get('listing_url', ''),
                        'last_price': listing.get('price')
                    }
                    
                    # Try to get existing listing
                    cursor.execute("SELECT listing_id FROM listings WHERE address = ?", (address,))
                    result = cursor.fetchone()
                    
                    if result:
                        # Update existing listing
                        listing_id = result['listing_id']
                        cursor.execute("""
                            UPDATE listings SET
                            city = ?, state = ?, zip_code = ?,
                            latitude = ?, longitude = ?,
                            lot_size = ?, square_feet = ?,
                            bedrooms = ?, bathrooms = ?,
                            year_built = ?, property_type = ?,
                            zoning_type = ?, source = ?,
                            listing_url = ?, last_price = ?,
                            last_updated = CURRENT_TIMESTAMP
                            WHERE listing_id = ?
                        """, (
                            listing_data['city'], listing_data['state'], listing_data['zip_code'],
                            listing_data['latitude'], listing_data['longitude'],
                            listing_data['lot_size'], listing_data['square_feet'],
                            listing_data['bedrooms'], listing_data['bathrooms'],
                            listing_data['year_built'], listing_data['property_type'],
                            listing_data['zoning_type'], listing_data['source'],
                            listing_data['listing_url'], listing_data['last_price'],
                            listing_id
                        ))
                        stats['updated_listings'] += 1
                        
                        # Track price changes
                        if listing_data['last_price']:
                            self._track_price_change(cursor, listing_id, listing_data['last_price'], run_id)
                    else:
                        # Insert new listing
                        cursor.execute("""
                            INSERT INTO listings
                            (address, city, state, zip_code, latitude, longitude,
                             lot_size, square_feet, bedrooms, bathrooms,
                             year_built, property_type, zoning_type, source,
                             listing_url, last_price)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, tuple(listing_data.values()))
                        
                        listing_id = cursor.lastrowid
                        stats['new_listings'] += 1
                        
                        # Record initial price
                        if listing_data['last_price']:
                            cursor.execute("""
                                INSERT INTO price_history
                                (listing_id, run_id, price)
                                VALUES (?, ?, ?)
                            """, (listing_id, run_id, listing_data['last_price']))
                    
                    # Record classification
                    if auto_classify and listing.get('development_score') is not None:
                        cursor.execute("""
                            INSERT INTO classifications
                            (listing_id, run_id, label, development_score, reasoning,
                             confidence_score, buildable_sqft, estimated_profit, roi_score, model_version)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            listing_id,
                            run_id,
                            listing.get('label', ''),
                            float(listing.get('development_score', 0)),
                            listing.get('reasoning', ''),
                            listing.get('confidence_score'),
                            listing.get('buildable_sqft'),
                            listing.get('estimated_profit'),
                            listing.get('roi_score'),
                            listing.get('model_version', 'gpt-4o-mini')
                        ))
                        stats['classifications_added'] += 1
                
                except Exception as e:
                    logger.error(f"Error saving listing {address}: {e}")
                    stats['errors'] += 1
        
        logger.info(f"Saved listings: {stats['new_listings']} new, "
                   f"{stats['updated_listings']} updated, "
                   f"{stats['classifications_added']} classified")
        return stats
    
    def _track_price_change(self, cursor, listing_id: int, current_price: float, run_id: int):
        """Track price changes for a listing"""
        cursor.execute("""
            SELECT price FROM price_history
            WHERE listing_id = ?
            ORDER BY record_date DESC
            LIMIT 1
        """, (listing_id,))
        
        result = cursor.fetchone()
        if result:
            last_price = result['price']
            if last_price and current_price != last_price:
                price_change = current_price - last_price
                price_change_percent = (price_change / last_price * 100) if last_price != 0 else 0
                
                cursor.execute("""
                    INSERT INTO price_history
                    (listing_id, run_id, price, price_change, price_change_percent)
                    VALUES (?, ?, ?, ?, ?)
                """, (listing_id, run_id, current_price, price_change, price_change_percent))
                
                logger.debug(f"Price change tracked: ${price_change:+,.0f} ({price_change_percent:+.1f}%)")
    
    def get_recent_opportunities(
        self,
        days: int = 7,
        min_score: float = 70.0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent high-value opportunities
        
        Args:
            days: Look back N days
            min_score: Minimum development score
            limit: Maximum results
            
        Returns:
            List of opportunities with latest classification
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    l.listing_id,
                    l.address,
                    l.city,
                    l.state,
                    l.lot_size,
                    l.square_feet,
                    l.last_price,
                    l.latitude,
                    l.longitude,
                    c.development_score,
                    c.label,
                    c.reasoning,
                    c.estimated_profit,
                    c.roi_score,
                    c.run_date,
                    ROW_NUMBER() OVER (
                        PARTITION BY l.listing_id ORDER BY c.run_date DESC
                    ) as rn
                FROM listings l
                LEFT JOIN classifications c ON l.listing_id = c.listing_id
                WHERE c.run_date >= ?
                AND c.development_score >= ?
            """, (cutoff_date, min_score))
            
            opportunities = []
            for row in cursor.fetchall():
                if row['rn'] == 1:  # Latest classification only
                    opportunities.append({
                        'listing_id': row['listing_id'],
                        'address': row['address'],
                        'city': row['city'],
                        'state': row['state'],
                        'lot_size': row['lot_size'],
                        'square_feet': row['square_feet'],
                        'price': row['last_price'],
                        'latitude': row['latitude'],
                        'longitude': row['longitude'],
                        'development_score': row['development_score'],
                        'label': row['label'],
                        'reasoning': row['reasoning'],
                        'estimated_profit': row['estimated_profit'],
                        'roi_score': row['roi_score'],
                        'classified_date': row['run_date']
                    })
            
            return opportunities[:limit]
    
    def get_training_data(
        self,
        min_classifications: int = 2,
        days: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Get historical data for model fine-tuning
        
        Args:
            min_classifications: Minimum classifications per listing
            days: Look back N days
            
        Returns:
            List of listings with classification history
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Find listings with multiple classifications (enable trend tracking)
            cursor.execute("""
                SELECT
                    l.listing_id,
                    l.address,
                    l.city,
                    l.lot_size,
                    l.square_feet,
                    l.last_price,
                    COUNT(c.classification_id) as num_classifications,
                    AVG(c.development_score) as avg_score,
                    MIN(c.development_score) as min_score,
                    MAX(c.development_score) as max_score
                FROM listings l
                JOIN classifications c ON l.listing_id = c.listing_id
                WHERE c.run_date >= ?
                GROUP BY l.listing_id
                HAVING COUNT(c.classification_id) >= ?
            """, (cutoff_date, min_classifications))
            
            training_data = []
            for row in cursor.fetchall():
                # Get all classifications for this listing
                cursor.execute("""
                    SELECT
                        development_score,
                        label,
                        reasoning,
                        confidence_score,
                        buildable_sqft,
                        estimated_profit,
                        run_date
                    FROM classifications
                    WHERE listing_id = ?
                    ORDER BY run_date DESC
                """, (row['listing_id'],))
                
                classifications = [dict(r) for r in cursor.fetchall()]
                
                training_data.append({
                    'listing_id': row['listing_id'],
                    'address': row['address'],
                    'city': row['city'],
                    'lot_size': row['lot_size'],
                    'square_feet': row['square_feet'],
                    'price': row['last_price'],
                    'num_classifications': row['num_classifications'],
                    'avg_score': row['avg_score'],
                    'min_score': row['min_score'],
                    'max_score': row['max_score'],
                    'classification_history': classifications
                })
            
            logger.info(f"Retrieved {len(training_data)} listings with {min_classifications}+ classifications")
            return training_data
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get database statistics
        
        Args:
            days: Look back N days for recent stats
            
        Returns:
            Dictionary with statistics
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total listings
            cursor.execute("SELECT COUNT(*) as count FROM listings")
            total_listings = cursor.fetchone()['count']
            
            # Recent listings
            cursor.execute("SELECT COUNT(*) as count FROM listings WHERE first_seen >= ?",
                         (cutoff_date,))
            recent_listings = cursor.fetchone()['count']
            
            # High-value opportunities
            cursor.execute("""
                SELECT COUNT(DISTINCT listing_id) as count
                FROM classifications
                WHERE development_score >= 70 AND run_date >= ?
            """, (cutoff_date,))
            high_value_count = cursor.fetchone()['count']
            
            # Average scores
            cursor.execute("""
                SELECT
                    AVG(development_score) as avg_score,
                    MIN(development_score) as min_score,
                    MAX(development_score) as max_score
                FROM classifications
                WHERE run_date >= ?
            """, (cutoff_date,))
            
            score_stats = dict(cursor.fetchone())
            
            # Recent runs
            cursor.execute("""
                SELECT COUNT(*) as count, AVG(duration_seconds) as avg_duration
                FROM scan_runs
                WHERE run_date >= ?
            """, (cutoff_date,))
            
            run_stats = dict(cursor.fetchone())
            
            # Most recently classified
            cursor.execute("""
                SELECT MAX(run_date) as last_run FROM scan_runs
            """)
            
            last_run = cursor.fetchone()['last_run']
            
            return {
                'total_listings': total_listings,
                'recent_listings': recent_listings,
                'high_value_opportunities': high_value_count,
                'average_score': score_stats['avg_score'],
                'score_range': {
                    'min': score_stats['min_score'],
                    'max': score_stats['max_score']
                },
                'recent_runs': run_stats['count'],
                'avg_run_duration': run_stats['avg_duration'],
                'last_scan': last_run,
                'lookback_days': days
            }
    
    def export_to_csv(self, filename: str, query_type: str = "all"):
        """
        Export data to CSV for analysis
        
        Args:
            filename: Output filename
            query_type: Type of export (all, opportunities, high_value, recent)
        """
        import csv
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if query_type == "opportunities":
                # Export high-value opportunities
                cursor.execute("""
                    SELECT DISTINCT
                        l.address,
                        l.city,
                        l.state,
                        l.lot_size,
                        l.square_feet,
                        l.last_price,
                        c.development_score,
                        c.label,
                        c.reasoning,
                        c.estimated_profit,
                        c.roi_score
                    FROM listings l
                    JOIN classifications c ON l.listing_id = c.listing_id
                    WHERE c.development_score >= 70
                    ORDER BY c.development_score DESC
                """)
            
            elif query_type == "recent":
                # Last 7 days
                cursor.execute("""
                    SELECT DISTINCT
                        l.address,
                        l.city,
                        l.state,
                        l.last_price,
                        c.development_score,
                        c.run_date
                    FROM listings l
                    JOIN classifications c ON l.listing_id = c.listing_id
                    WHERE c.run_date >= datetime('now', '-7 days')
                    ORDER BY c.run_date DESC
                """)
            
            else:
                # All listings with latest classification
                cursor.execute("""
                    SELECT
                        l.address,
                        l.city,
                        l.state,
                        l.lot_size,
                        l.square_feet,
                        l.last_price,
                        c.development_score,
                        c.label,
                        l.first_seen,
                        l.last_updated
                    FROM listings l
                    LEFT JOIN classifications c ON (
                        l.listing_id = c.listing_id AND
                        c.classification_id = (
                            SELECT classification_id FROM classifications
                            WHERE listing_id = l.listing_id
                            ORDER BY run_date DESC LIMIT 1
                        )
                    )
                """)
            
            rows = cursor.fetchall()
            if not rows:
                logger.warning(f"No data found for export type: {query_type}")
                return
            
            # Write CSV
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([description[0] for description in cursor.description])
                writer.writerows(rows)
            
            logger.info(f"Exported {len(rows)} rows to {filename}")
    
    def cleanup_old_data(self, days: int = 180):
        """
        Remove old scan runs and related data
        
        Args:
            days: Remove data older than N days
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get run IDs to delete
            cursor.execute(
                "SELECT run_id FROM scan_runs WHERE run_date < ?",
                (cutoff_date,)
            )
            
            run_ids = [r['run_id'] for r in cursor.fetchall()]
            
            if run_ids:
                placeholders = ','.join('?' * len(run_ids))
                
                # Delete related records
                cursor.execute(f"DELETE FROM price_history WHERE run_id IN ({placeholders})", run_ids)
                cursor.execute(f"DELETE FROM classifications WHERE run_id IN ({placeholders})", run_ids)
                cursor.execute(f"DELETE FROM scan_runs WHERE run_id IN ({placeholders})", run_ids)
                
                logger.info(f"Deleted {len(run_ids)} old scan runs (older than {days} days)")


def main():
    """Test the database manager"""
    db = HistoricalDatabaseManager()
    
    # Test sample data
    sample_listings = [
        {
            'address': '123 Main St, Newton, MA',
            'city': 'Newton',
            'state': 'MA',
            'lot_size': 10000,
            'square_feet': 3500,
            'price': 750000,
            'development_score': 85,
            'label': 'excellent',
            'reasoning': 'Large lot, good location'
        },
        {
            'address': '456 Oak Ave, Newton, MA',
            'city': 'Newton',
            'state': 'MA',
            'lot_size': 8000,
            'square_feet': 3000,
            'price': 650000,
            'development_score': 72,
            'label': 'good',
            'reasoning': 'Decent potential'
        }
    ]
    
    # Record a scan run
    run_id = db.record_scan_run(
        search_query="Newton MA development",
        location="Newton, MA",
        total_found=100,
        opportunities_found=25,
        high_value_found=12,
        duration_seconds=45.5
    )
    
    # Save listings
    stats = db.save_listings(sample_listings, run_id)
    print(f"Saved listings: {stats}")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"\nDatabase statistics:")
    print(f"  Total listings: {stats['total_listings']}")
    print(f"  High-value opportunities (last 30 days): {stats['high_value_opportunities']}")
    print(f"  Average score: {stats['average_score']:.1f}")
    
    # Get recent opportunities
    opportunities = db.get_recent_opportunities()
    print(f"\nRecent opportunities: {len(opportunities)}")
    for opp in opportunities:
        print(f"  - {opp['address']}: {opp['development_score']:.1f}")
    
    # Get training data
    training_data = db.get_training_data(min_classifications=1)
    print(f"\nTraining data records: {len(training_data)}")
    
    # Export
    db.export_to_csv('data/export_all.csv', 'all')
    db.export_to_csv('data/export_opportunities.csv', 'opportunities')


if __name__ == "__main__":
    main()
