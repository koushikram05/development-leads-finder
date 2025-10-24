# Task 3: Historical Database (SQLite)

## Overview

The Historical Database system persists all property leads discovered by the pipeline, enabling:

- ✅ **Persistent Storage**: All findings preserved across runs (no data loss)
- ✅ **Trend Analysis**: Track price changes, score variations over time
- ✅ **Fine-tuning Data**: Comprehensive training data for model improvement
- ✅ **Analytics**: Query historical data for insights
- ✅ **Deduplication**: Automatic duplicate detection and updates

## Quick Start

### 1. What's Stored?

The database (`data/development_leads.db`) contains 4 interconnected tables:

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| **scan_runs** | Pipeline execution metadata | run_id, date, query, results, duration |
| **listings** | Core property data (unique by address) | listing_id, address, lot_size, price, location |
| **classifications** | Classification history per property | listing_id, score, label, reasoning, confidence |
| **price_history** | Price changes over time | listing_id, price, change %, date |

### 2. Automatic Integration

The database is **automatically integrated** into the pipeline as Stage 6:

```bash
# Every time you run the pipeline, it automatically:
python -m app.dev_pipeline

# Stage 1: Data Collection → Stage 2: Enrichment → Stage 3: Classification
# → Stage 4: Google Sheets → Stage 5: Alerts → Stage 6: Database ✓
```

**No additional setup required!** Just run the pipeline as usual.

### 3. View Your Data

Query the database after running the pipeline:

```python
from app.integrations.database_manager import HistoricalDatabaseManager

db = HistoricalDatabaseManager()

# Get recent high-value opportunities
recent = db.get_recent_opportunities(days=7, min_score=70)
for opp in recent:
    print(f"{opp['address']}: {opp['development_score']:.1f}/100")

# Get database statistics
stats = db.get_statistics(days=30)
print(f"Total properties: {stats['total_listings']}")
print(f"High-value leads: {stats['high_value_opportunities']}")

# Export to CSV for analysis
db.export_to_csv('export.csv', query_type='opportunities')
```

## Database Schema

### scan_runs Table
Records every pipeline execution:

```sql
CREATE TABLE scan_runs (
    run_id INTEGER PRIMARY KEY,
    run_date TIMESTAMP,
    search_query TEXT,
    location TEXT,
    run_type TEXT,              -- 'manual', 'daily', 'weekly'
    total_found INTEGER,
    opportunities_found INTEGER,
    high_value_found INTEGER,   -- score >= 70
    duration_seconds FLOAT,
    status TEXT
);
```

**Example:**
| run_id | run_date | location | total_found | opportunities_found | high_value_found | duration |
|--------|----------|----------|-------------|---------------------|------------------|----------|
| 1 | 2025-01-01 10:00 | Newton, MA | 150 | 45 | 18 | 87.5 |
| 2 | 2025-01-02 10:00 | Newton, MA | 160 | 48 | 21 | 92.3 |

### listings Table
Core property information (one record per unique address):

```sql
CREATE TABLE listings (
    listing_id INTEGER PRIMARY KEY,
    address TEXT UNIQUE,        -- Deduplication key
    city TEXT,
    state TEXT,
    latitude REAL,
    longitude REAL,
    lot_size REAL,
    square_feet REAL,
    bedrooms INTEGER,
    bathrooms REAL,
    year_built INTEGER,
    property_type TEXT,
    zoning_type TEXT,
    listing_url TEXT,
    first_seen TIMESTAMP,       -- When first discovered
    last_updated TIMESTAMP,     -- When last refreshed
    last_price REAL,
    status TEXT
);
```

**Example:**
| listing_id | address | city | lot_size | last_price | first_seen | last_updated |
|------------|---------|------|----------|------------|------------|--------------|
| 1 | 123 Main St | Newton | 10000 | 750000 | 2025-01-01 | 2025-01-02 |

### classifications Table
Classification history (enables trend tracking):

```sql
CREATE TABLE classifications (
    classification_id INTEGER PRIMARY KEY,
    listing_id INTEGER,         -- Foreign key to listings
    run_id INTEGER,             -- Foreign key to scan_runs
    run_date TIMESTAMP,
    label TEXT,                 -- 'excellent', 'good', 'fair', 'poor'
    development_score REAL,     -- 0-100
    reasoning TEXT,
    confidence_score REAL,
    buildable_sqft REAL,        -- Task 5 data
    estimated_profit REAL,      -- Task 5 data
    roi_score REAL,             -- Task 5 data
    model_version TEXT
);
```

**Example (Track Score Changes Over Time):**
| listing_id | run_date | score | label | reasoning |
|------------|----------|-------|-------|-----------|
| 1 | 2025-01-01 10:00 | 85 | excellent | Large lot, good location |
| 1 | 2025-01-02 10:00 | 88 | excellent | (same property, new scan) |

**Why Track History?**
- Identify properties with improving/declining potential
- Detect scoring anomalies or model drift
- Use historical trends for fine-tuning

### price_history Table
Track price changes over time:

```sql
CREATE TABLE price_history (
    price_id INTEGER PRIMARY KEY,
    listing_id INTEGER,
    run_id INTEGER,
    record_date TIMESTAMP,
    price REAL,
    price_change REAL,          -- $ amount
    price_change_percent REAL   -- % change
);
```

**Example:**
| listing_id | record_date | price | price_change | % |
|------------|-------------|-------|------|-----|
| 1 | 2025-01-01 | 750000 | NULL | NULL |
| 1 | 2025-01-02 | 745000 | -5000 | -0.67% |

## API Usage

### Record a Scan Run

```python
run_id = db.record_scan_run(
    search_query="Newton MA development",
    location="Newton, MA",
    run_type="manual",           # or "daily", "weekly"
    total_found=150,
    opportunities_found=45,
    high_value_found=18,
    duration_seconds=87.5
)
# Returns: run_id (1)
```

### Save Listings

```python
stats = db.save_listings(
    listings=classified_listings,  # List of dicts from pipeline
    run_id=1,
    auto_classify=True             # Record classifications
)
# Returns: {'new_listings': 10, 'updated_listings': 5, 'classifications_added': 15, 'errors': 0}
```

### Get Recent Opportunities

```python
recent = db.get_recent_opportunities(
    days=7,           # Look back 7 days
    min_score=70.0,   # Score >= 70
    limit=100         # Max 100 results
)

for opp in recent:
    print(f"{opp['address']}: ${opp['price']:,.0f}")
    print(f"  Score: {opp['development_score']:.1f}/100")
    print(f"  Est. Profit: ${opp['estimated_profit']:,.0f}")
```

### Get Training Data (For Fine-tuning)

```python
training_data = db.get_training_data(
    min_classifications=2,  # Listings with 2+ classifications
    days=90                 # Last 90 days
)

# Each record includes classification history
for record in training_data:
    print(f"{record['address']}")
    print(f"  Avg Score: {record['avg_score']:.1f}")
    print(f"  Score Range: {record['min_score']:.0f} - {record['max_score']:.0f}")
    print(f"  Classifications: {record['num_classifications']}")
    
    # All classifications for this property
    for classification in record['classification_history']:
        print(f"    {classification['run_date']}: {classification['development_score']:.1f}")
```

### Database Statistics

```python
stats = db.get_statistics(days=30)

# Output:
# {
#     'total_listings': 450,
#     'recent_listings': 120,           # Added in last 30 days
#     'high_value_opportunities': 78,   # Score >= 70
#     'average_score': 64.5,
#     'score_range': {'min': 10, 'max': 95},
#     'recent_runs': 30,                # Pipeline runs
#     'avg_run_duration': 87.3,
#     'last_scan': '2025-01-02T10:30:00',
#     'lookback_days': 30
# }

print(f"Average Score: {stats['average_score']:.1f}/100")
print(f"High-Value Properties: {stats['high_value_opportunities']}")
```

### Export Data

```python
# Export all listings
db.export_to_csv('export_all.csv', query_type='all')

# Export only high-value opportunities
db.export_to_csv('export_opportunities.csv', query_type='opportunities')

# Export recent listings (last 7 days)
db.export_to_csv('export_recent.csv', query_type='recent')
```

## Deduplication Strategy

The database **automatically deduplicates** by address:

1. **New Property**: Address not in database → Create new listing
2. **Seen Before**: Address exists → Update location, price, lot info
3. **Track Changes**: Price differences recorded in price_history table

**Example:**

```
Run 1: Finds "123 Main St" at $750,000
  → Creates listing_id 1

Run 2: Finds "123 Main St" at $745,000
  → Updates listing 1 with new price
  → Records price change: -$5,000 (-0.67%)

Run 3: Score changes 85 → 88
  → Updates classification with new score
  → Tracks score history for fine-tuning
```

## Use Cases

### 1. Fine-Tuning the ML Model

```python
# Get training data with classification history
training_data = db.get_training_data(min_classifications=2, days=90)

# Use for retraining:
# - Properties with multiple classifications = ground truth examples
# - Score trends identify model improvements needed
# - Classification history enables weakly-supervised learning

for record in training_data:
    # Train on why scores changed
    if record['max_score'] > record['min_score']:
        print(f"Score evolution: {record['address']}")
        print(f"  {record['min_score']:.0f} → {record['max_score']:.0f}")
```

### 2. Track Price Trends

```python
from app.integrations.database_manager import HistoricalDatabaseManager

db = HistoricalDatabaseManager()

# Find properties with price drops > 5%
with sqlite3.connect('data/development_leads.db') as conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT l.address, p.price_change_percent, p.record_date
        FROM price_history p
        JOIN listings l ON p.listing_id = l.listing_id
        WHERE p.price_change_percent < -5.0
        ORDER BY p.price_change_percent
        LIMIT 10
    """)
    
    for row in cursor:
        print(f"{row[0]}: {row[1]:.1f}% price drop")
```

### 3. Identify Emerging Opportunities

```python
# Find properties recently added with high scores
recent_high_value = db.get_recent_opportunities(
    days=1,          # Last 24 hours
    min_score=80,
    limit=50
)

print(f"🔥 {len(recent_high_value)} new opportunities found!")
for opp in recent_high_value:
    print(f"  {opp['address']}: {opp['development_score']:.1f}/100")
```

### 4. Historical Analysis

```python
# Compare runs over time
import sqlite3

with sqlite3.connect('data/development_leads.db') as conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT run_date, total_found, opportunities_found, high_value_found
        FROM scan_runs
        WHERE location = 'Newton, MA'
        ORDER BY run_date DESC
        LIMIT 10
    """)
    
    print("Pipeline Performance (Last 10 Runs):")
    print("Date          | Total | Opportunities | High-Value")
    for row in cursor:
        print(f"{row[0]:<15} | {row[1]:<5} | {row[2]:<14} | {row[3]:<10}")
```

## Performance Optimizations

### Indexes
The database includes indexes on:
- `listings.address` - Fast duplicate detection
- `listings.city, state` - Location-based queries
- `classifications.run_date` - Time-range queries
- `classifications.development_score` - Score-based filtering

### Connection Management
```python
# Efficient context manager usage
with db._get_connection() as conn:
    cursor = conn.cursor()
    # Multiple queries in single transaction
    # Automatic commit/rollback
```

### Batch Operations
```python
# Efficient saving of multiple listings
stats = db.save_listings(listings, run_id)  # Batch insert/update
# Single transaction for all records
```

## Database File Size

Typical sizes based on leads:
- 100 properties: ~50 KB
- 500 properties: ~200 KB
- 1000 properties: ~400 KB

**Cleanup old data:**
```python
# Delete data older than 180 days
db.cleanup_old_data(days=180)
```

## Integration with Other Tasks

### Task 4: Map Visualization
```python
# Get all properties with coordinates
recent = db.get_recent_opportunities(days=30)
# Use latitude/longitude for map markers
```

### Task 5: ROI Scoring
```python
# Get data with buildable_sqft and estimated_profit
training_data = db.get_training_data()
# Use for ROI analysis
```

### Fine-tuning ML Model
```python
# Get properties with multiple classifications
training_data = db.get_training_data(min_classifications=2)
# Use classification history to retrain model
```

## Troubleshooting

### Database Locked Error
```python
# Increase timeout for concurrent access
sqlite3.connect('data/development_leads.db', timeout=20)
```

### Duplicate Addresses
The database uses `address` as a unique key. If duplicates occur due to formatting variations (e.g., "123 Main St" vs "123 Main Street"):

```python
# Pre-normalize addresses before saving
def normalize_address(address):
    return ' '.join(address.lower().split())
```

### Reset Database
```python
import os
os.remove('data/development_leads.db')
# Database will be recreated on next run
```

## Next Steps

1. ✅ **Run Pipeline** - Database auto-saves all findings
2. ✅ **View Stats** - Check `db.get_statistics()`
3. ✅ **Export Data** - Create CSV for analysis: `db.export_to_csv()`
4. ✅ **Query Trends** - Analyze price/score changes
5. ⏭️ **Task 4: Map Visualization** - Visualize properties on map
6. ⏭️ **Task 5: ROI Scoring** - Add ROI calculations
7. ⏭️ **Fine-tune Model** - Use training data from database

## API Reference

See `app/integrations/database_manager.py` for complete API documentation.

**Key Methods:**
- `record_scan_run()` - Log pipeline execution
- `save_listings()` - Persist property data
- `get_recent_opportunities()` - Query high-value leads
- `get_training_data()` - Get data for fine-tuning
- `get_statistics()` - Database analytics
- `export_to_csv()` - Export for external analysis
- `cleanup_old_data()` - Remove old records
