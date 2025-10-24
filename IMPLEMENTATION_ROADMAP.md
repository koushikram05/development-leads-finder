# Implementation Roadmap - 5 Pending Tasks

**Date:** October 23, 2025  
**Status:** Ready for Sequential Implementation  
**Total Effort:** ~2-3 weeks for full completion

---

## 📋 Task Overview

| # | Task | Priority | Complexity | Est. Time | Value |
|---|------|----------|-----------|-----------|-------|
| 1 | Google Sheets Integration | 🔴 HIGH | 🟡 Medium | 2-3 days | 10/10 |
| 2 | Historical Tracking (Database) | 🔴 HIGH | 🟠 Hard | 3-4 days | 9/10 |
| 3 | Email/Slack Alerts | 🟡 MEDIUM | 🟢 Easy | 1-2 days | 8/10 |
| 4 | Map Visualization | 🟡 MEDIUM | 🟡 Medium | 2-3 days | 7/10 |
| 5 | ROI Scoring & Buildable SF | 🟠 LOW | 🟠 Hard | 3-5 days | 6/10 |

---

## RECOMMENDATION: Implementation Order

**Suggested sequence** (optimal for dependencies & value):

```
Week 1:
  ├─ Task 1: Google Sheets Integration ✓
  ├─ Task 3: Email/Slack Alerts ✓
  └─ Task 2: Historical Database Setup ✓

Week 2:
  ├─ Task 4: Map Visualization ✓
  └─ Task 5: ROI & Buildable SF Scoring ✓
```

---

## TASK 1: GOOGLE SHEETS INTEGRATION 🔴 HIGH PRIORITY

**Objective:** Export classified listings directly to Google Sheet (alternative to CRM)

### What You'll Build
```
Pipeline Output (CSV)
    ↓
Google Sheets API
    ↓
Shared Google Sheet (auto-updated daily)
```

### Implementation Steps

#### Step 1.1: Set Up Google Cloud Project
```bash
# Prerequisites installed:
pip install gspread oauth2client google-auth-oauthlib

# 1. Go to: https://console.cloud.google.com/
# 2. Create new project: "Anil_Project"
# 3. Enable APIs:
#    - Google Sheets API
#    - Google Drive API
# 4. Create Service Account
# 5. Download JSON key → save as `google_credentials.json`
# 6. Store in project root (add to .gitignore)
```

#### Step 1.2: Create New Module
**File:** `app/integrations/google_sheets_uploader.py`

```python
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime
import logging

class GoogleSheetsUploader:
    """Upload classified listings to Google Sheets"""
    
    def __init__(self, credentials_path='google_credentials.json'):
        self.logger = logging.getLogger('sheets_uploader')
        
        # Authenticate
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_path, scopes
        )
        self.client = gspread.authorize(credentials)
    
    def create_or_get_sheet(self, sheet_name='Development_Leads'):
        """Create sheet if not exists, or get existing"""
        try:
            # Try to open existing sheet
            sheet = self.client.open(sheet_name)
            self.logger.info(f"Opened existing sheet: {sheet_name}")
        except gspread.SpreadsheetNotFound:
            # Create new sheet
            sheet = self.client.create(sheet_name)
            sheet.share('your-email@gmail.com', perm_type='user', role='owner')
            self.logger.info(f"Created new sheet: {sheet_name}")
        
        return sheet
    
    def upload_listings(self, listings, sheet_name='Development_Leads'):
        """Upload listings to Google Sheet"""
        sheet = self.create_or_get_sheet(sheet_name)
        
        # Get first worksheet or create new one
        try:
            worksheet = sheet.get_worksheet(0)
        except:
            worksheet = sheet.add_worksheet(
                title=f"Leads_{datetime.now().strftime('%Y_%m_%d')}",
                rows=len(listings) + 1,
                cols=20
            )
        
        # Clear existing data
        worksheet.clear()
        
        # Add header row
        if listings:
            headers = list(listings[0].keys())
            worksheet.append_row(headers)
            
            # Add data rows
            for listing in listings:
                row = [str(listing.get(h, '')) for h in headers]
                worksheet.append_row(row)
            
            self.logger.info(f"Uploaded {len(listings)} listings to Google Sheet")
            return True
        
        return False

# Usage in pipeline
def upload_to_sheets(classified_listings):
    uploader = GoogleSheetsUploader()
    uploader.upload_listings(
        classified_listings,
        sheet_name='Development_Leads_Newton_MA'
    )
```

#### Step 1.3: Integrate into Pipeline
**File:** `app/dev_pipeline.py` (add to Stage 4)

```python
# Add to imports
from app.integrations.google_sheets_uploader import GoogleSheetsUploader

# Add to Stage 4: Saving Results
if classified_listings:
    # ... existing CSV/JSON saves ...
    
    # NEW: Upload to Google Sheets
    try:
        self.logger.info("Uploading to Google Sheets...")
        sheets_uploader = GoogleSheetsUploader()
        sheets_uploader.upload_listings(
            classified_listings,
            sheet_name='Development_Leads_Newton'
        )
        self.logger.info("✓ Google Sheets upload successful")
    except Exception as e:
        self.logger.warning(f"Google Sheets upload failed: {e}")
```

#### Step 1.4: Update .env
```properties
GOOGLE_CREDENTIALS_PATH=./google_credentials.json
GOOGLE_SHEET_NAME=Development_Leads_Newton
```

#### Step 1.5: Test
```bash
python -m app.dev_pipeline

# Check: New sheet should appear in your Google Drive
# Share link with team → real-time collaboration
```

### Output
- ✅ Real-time Google Sheet with all classified leads
- ✅ Auto-updates on each pipeline run
- ✅ Shareable with team (no file downloads needed)
- ✅ Built-in history (can keep old sheets)

---

## TASK 2: HISTORICAL TRACKING (DATABASE) 🔴 HIGH PRIORITY

**Objective:** Track leads over time, detect trends, new opportunities

### What You'll Build
```
Daily Pipeline Runs
    ↓ (each run saves to DB)
SQLite Database (leads_history.db)
    ├─ listings table (all properties ever seen)
    ├─ classifications table (score history)
    └─ alerts table (new/changed properties)
```

### Implementation Steps

#### Step 2.1: Create Database Schema
**File:** `app/database/schema.py`

```python
import sqlite3
from datetime import datetime
import os

class LeadsDatabase:
    """SQLite database for historical tracking"""
    
    def __init__(self, db_path='data/leads_history.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create tables if not exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Listings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT UNIQUE NOT NULL,
                price REAL,
                beds INTEGER,
                baths INTEGER,
                sqft INTEGER,
                lot_size INTEGER,
                year_built INTEGER,
                url TEXT,
                source TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Classifications table (track score changes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER NOT NULL,
                label TEXT,
                development_score REAL,
                confidence REAL,
                explanation TEXT,
                classified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(listing_id) REFERENCES listings(id)
            )
        ''')
        
        # Price history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER NOT NULL,
                price REAL,
                date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(listing_id) REFERENCES listings(id)
            )
        ''')
        
        # Alerts (new/changed properties)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER NOT NULL,
                alert_type TEXT,  -- 'new', 'price_drop', 'score_increase'
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(listing_id) REFERENCES listings(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_listing(self, listing):
        """Insert or update listing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO listings (
                    address, price, beds, baths, sqft, lot_size, 
                    year_built, url, source, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                listing.get('address'),
                listing.get('price'),
                listing.get('beds'),
                listing.get('baths'),
                listing.get('sqft'),
                listing.get('lot_size'),
                listing.get('year_built'),
                listing.get('url'),
                listing.get('source'),
                datetime.now()
            ))
            
            conn.commit()
            listing_id = cursor.lastrowid
            return listing_id
        finally:
            conn.close()
    
    def insert_classification(self, listing_id, classification):
        """Store classification with score"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO classifications (
                    listing_id, label, development_score, confidence, explanation
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                listing_id,
                classification.get('label'),
                classification.get('development_score'),
                classification.get('confidence'),
                classification.get('explanation')
            ))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_new_listings(self, days=1):
        """Get listings added in last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT address, price, development_score FROM listings l
            JOIN classifications c ON l.id = c.listing_id
            WHERE l.first_seen > datetime('now', '-' || ? || ' days')
            ORDER BY c.development_score DESC
        ''', (days,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_score_trends(self, address, limit=10):
        """Get classification score history for property"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.development_score, c.classified_date 
            FROM classifications c
            JOIN listings l ON c.listing_id = l.id
            WHERE l.address = ?
            ORDER BY c.classified_date DESC
            LIMIT ?
        ''', (address, limit))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def detect_price_changes(self, threshold=50000):
        """Find properties with significant price changes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT l.address, MAX(ph1.price) as current_price, 
                   MAX(ph2.price) as previous_price
            FROM listings l
            JOIN price_history ph1 ON l.id = ph1.listing_id
            JOIN price_history ph2 ON l.id = ph2.listing_id
            WHERE ph1.date_recorded > ph2.date_recorded
            GROUP BY l.address
            HAVING ABS(current_price - previous_price) > ?
        ''', (threshold,))
        
        results = cursor.fetchall()
        conn.close()
        return results

# Usage in pipeline
def save_to_database(db, classified_listings):
    for listing in classified_listings:
        # Insert listing
        listing_id = db.insert_listing(listing)
        
        # Insert classification
        db.insert_classification(listing_id, {
            'label': listing.get('label'),
            'development_score': listing.get('development_score'),
            'confidence': listing.get('confidence'),
            'explanation': listing.get('explanation')
        })
```

#### Step 2.2: Integrate into Pipeline
**File:** `app/dev_pipeline.py` (modify Stage 4)

```python
from app.database.schema import LeadsDatabase

# In DevelopmentPipeline.__init__
self.db = LeadsDatabase()

# In Stage 4: Saving Results
self.logger.info("\n" + "=" * 60)
self.logger.info("STAGE 4: SAVING RESULTS")
self.logger.info("=" * 60)

# Save to database
for listing in classified_listings:
    listing_id = self.db.insert_listing(listing)
    self.db.insert_classification(listing_id, listing)
self.logger.info(f"Saved {len(classified_listings)} to database")

# Existing CSV/JSON saves...
if classified_listings:
    save_to_csv(classified_listings, 'classified_listings.csv')
    save_to_json(classified_listings, 'classified_listings.json')
```

#### Step 2.3: Create Reporting Module
**File:** `app/reports/history_report.py`

```python
from app.database.schema import LeadsDatabase
from datetime import datetime, timedelta
import csv

class HistoryReporter:
    """Generate reports from historical data"""
    
    def __init__(self, db_path='data/leads_history.db'):
        self.db = LeadsDatabase(db_path)
    
    def new_opportunities_report(self, days=7):
        """Report on new high-scoring opportunities"""
        new_leads = self.db.get_new_listings(days)
        
        filename = f"data/new_opportunities_{datetime.now().strftime('%Y_%m_%d')}.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Address', 'Price', 'Dev Score'])
            for row in new_leads:
                writer.writerow(row)
        
        return filename, len(new_leads)
    
    def price_change_report(self, threshold=50000):
        """Report properties with significant price changes"""
        changes = self.db.detect_price_changes(threshold)
        
        filename = f"data/price_changes_{datetime.now().strftime('%Y_%m_%d')}.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Address', 'Current Price', 'Previous Price', 'Change'])
            for row in changes:
                address, current, previous = row
                change = current - previous if previous else 0
                writer.writerow([address, current, previous, change])
        
        return filename, len(changes)

# Usage
reporter = HistoryReporter()
report_file, count = reporter.new_opportunities_report(days=7)
print(f"New opportunities: {count} (see {report_file})")
```

#### Step 2.4: Test Database
```bash
# Run pipeline - should create data/leads_history.db
python -m app.dev_pipeline

# Check database
sqlite3 data/leads_history.db ".tables"
sqlite3 data/leads_history.db "SELECT COUNT(*) FROM listings;"
```

### Output
- ✅ SQLite database storing all historical data
- ✅ Track price changes over time
- ✅ Score history per property
- ✅ Auto-detection of new high-value leads
- ✅ Historical reporting capabilities

---

## TASK 3: EMAIL/SLACK ALERTS 🟡 MEDIUM PRIORITY

**Objective:** Notify team of new opportunities daily

### What You'll Build
```
Pipeline Run (detects new leads)
    ↓
Alert Logic (score > threshold)
    ↓
Email + Slack Notification
    ↓
Team gets instant notification
```

### Implementation Steps

#### Step 3.1: Create Alert Module
**File:** `app/integrations/alerts.py`

```python
import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
import os

class AlertManager:
    """Send email and Slack notifications"""
    
    def __init__(self):
        self.logger = logging.getLogger('alerts')
        self.email_from = os.getenv('ALERT_EMAIL')
        self.email_password = os.getenv('ALERT_EMAIL_PASSWORD')
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    
    def send_email_alert(self, to_emails, subject, listings):
        """Send email with opportunity summary"""
        try:
            # Build HTML email
            html = self._build_email_html(listings)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = ', '.join(to_emails)
            
            msg.attach(MIMEText(html, 'html'))
            
            # Send via Gmail SMTP
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.email_from, self.email_password)
            server.sendmail(self.email_from, to_emails, msg.as_string())
            server.quit()
            
            self.logger.info(f"Email sent to {len(to_emails)} recipients")
            return True
        except Exception as e:
            self.logger.error(f"Email send failed: {e}")
            return False
    
    def send_slack_alert(self, opportunities):
        """Send Slack message with top opportunities"""
        try:
            # Build Slack message
            blocks = self._build_slack_message(opportunities)
            
            response = requests.post(
                self.slack_webhook,
                json={'blocks': blocks}
            )
            
            if response.status_code == 200:
                self.logger.info("Slack notification sent")
                return True
            else:
                self.logger.error(f"Slack send failed: {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Slack send failed: {e}")
            return False
    
    def _build_email_html(self, listings):
        """Generate HTML email content"""
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ background-color: #2c3e50; color: white; padding: 20px; }}
                    .opportunity {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; }}
                    .score {{ color: #27ae60; font-weight: bold; font-size: 18px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>🏠 Development Opportunity Alert</h2>
                    <p>Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <p>Hi Team,</p>
                <p>Found <strong>{len(listings)}</strong> new development opportunities in Newton, MA:</p>
        """
        
        for listing in listings[:10]:  # Top 10
            html += f"""
                <div class="opportunity">
                    <h3>{listing['address']}</h3>
                    <p><strong>Price:</strong> ${listing['price']:,.0f}</p>
                    <p><strong>Lot Size:</strong> {listing.get('lot_size', 'N/A'):,} sqft</p>
                    <p><strong>Year Built:</strong> {listing.get('year_built', 'N/A')}</p>
                    <p class="score">Dev Score: {listing['development_score']:.1f}/100</p>
                    <p><strong>Reason:</strong> {listing.get('explanation', '')[:200]}...</p>
                </div>
            """
        
        html += """
                <p>Log in to Google Sheets to review all leads.</p>
                <p>Best regards,<br>AI Lead Agent</p>
            </body>
        </html>
        """
        return html
    
    def _build_slack_message(self, opportunities):
        """Generate Slack message blocks"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🏠 Development Opportunities Found"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Found {len(opportunities)} new opportunities in Newton, MA"
                }
            }
        ]
        
        for opp in opportunities[:5]:  # Top 5
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{opp['address']}*\n" +
                           f"Price: ${opp['price']:,.0f} | Score: {opp['development_score']:.0f}/100\n" +
                           f"Lot: {opp.get('lot_size', 'N/A'):,} sqft | Year: {opp.get('year_built', 'N/A')}"
                }
            })
        
        return blocks

# Usage in pipeline
def send_alerts(classified_listings, min_score=70):
    high_value = [l for l in classified_listings if l.get('development_score', 0) >= min_score]
    
    if high_value:
        alert_manager = AlertManager()
        
        # Send email
        alert_manager.send_email_alert(
            to_emails=['your-email@gmail.com', 'team@company.com'],
            subject=f"🏠 {len(high_value)} New Development Opportunities",
            listings=high_value
        )
        
        # Send Slack
        alert_manager.send_slack_alert(high_value)
```

#### Step 3.2: Update .env
```properties
# Email alerts
ALERT_EMAIL=your-email@gmail.com
ALERT_EMAIL_PASSWORD=your-app-specific-password
ALERT_RECIPIENTS=team@company.com,manager@company.com

# Slack webhook
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

#### Step 3.3: Integrate into Pipeline
**File:** `app/dev_pipeline.py` (add to Stage 4)

```python
from app.integrations.alerts import AlertManager

# In Stage 4
if development_opportunities:
    self.logger.info("Sending alerts...")
    alert_manager = AlertManager()
    alert_manager.send_email_alert(
        to_emails=os.getenv('ALERT_RECIPIENTS', '').split(','),
        subject=f"🏠 {len(development_opportunities)} New Dev Opportunities",
        listings=development_opportunities
    )
    alert_manager.send_slack_alert(development_opportunities)
```

#### Step 3.4: Get Slack Webhook URL
```bash
# 1. Go to https://api.slack.com/apps
# 2. Create New App
# 3. Enable "Incoming Webhooks"
# 4. Add New Webhook to Workspace
# 5. Copy URL → paste into .env as SLACK_WEBHOOK_URL
```

### Output
- ✅ Daily email digest of new opportunities
- ✅ Slack channel notifications (real-time)
- ✅ Formatted with scores, prices, details
- ✅ Links to source listings

---

## TASK 4: MAP VISUALIZATION 🟡 MEDIUM PRIORITY

**Objective:** Interactive map showing property locations

### What You'll Build
```
Classified Listings
    ↓
Folium Map Generation
    ↓
HTML Map (opportunity_map.html)
    ↓
View in browser or embed in dashboard
```

### Implementation Steps

#### Step 4.1: Create Map Module
**File:** `app/visualizations/map_generator.py`

```python
import folium
from folium import plugins
import logging
from datetime import datetime

class MapGenerator:
    """Generate interactive maps of opportunities"""
    
    def __init__(self, center_lat=42.3376, center_lon=-71.2092):
        self.center = [center_lat, center_lon]
        self.logger = logging.getLogger('map_generator')
    
    def generate_opportunity_map(self, listings, output_file='data/opportunity_map.html'):
        """Create interactive map with all opportunities"""
        
        # Initialize map
        m = folium.Map(
            location=self.center,
            zoom_start=13,
            tiles='OpenStreetMap'
        )
        
        # Add markers for each listing
        for listing in listings:
            if listing.get('latitude') and listing.get('longitude'):
                lat = float(listing['latitude'])
                lon = float(listing['longitude'])
                
                # Color based on development score
                score = listing.get('development_score', 0)
                if score >= 70:
                    color = 'red'
                    icon = 'star'
                elif score >= 50:
                    color = 'orange'
                    icon = 'info-sign'
                else:
                    color = 'blue'
                    icon = 'cloud'
                
                # Build popup
                popup_text = f"""
                <b>{listing['address']}</b><br>
                Price: ${listing.get('price', 'N/A'):,.0f}<br>
                Score: {score:.1f}/100<br>
                Lot: {listing.get('lot_size', 'N/A'):,} sqft<br>
                Label: {listing.get('label', 'N/A')}<br>
                <a href="{listing.get('url', '#')}" target="_blank">View Listing</a>
                """
                
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_text, max_width=300),
                    icon=folium.Icon(color=color, icon=icon),
                    tooltip=listing['address']
                ).add_to(m)
        
        # Add heatmap layer
        heat_data = [
            [float(l['latitude']), float(l['longitude']), 
             l.get('development_score', 0) / 100]
            for l in listings
            if l.get('latitude') and l.get('longitude')
        ]
        
        if heat_data:
            plugins.HeatMap(heat_data, radius=20, blur=15, max_zoom=1).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save map
        m.save(output_file)
        self.logger.info(f"Map saved to {output_file}")
        return output_file
    
    def generate_score_heatmap(self, listings, output_file='data/score_heatmap.html'):
        """Generate heatmap based on development scores"""
        
        m = folium.Map(
            location=self.center,
            zoom_start=13,
            tiles='CartoDB positron'
        )
        
        # Prepare heat data
        heat_data = [
            [float(l['latitude']), float(l['longitude']), 
             l.get('development_score', 0)]
            for l in listings
            if l.get('latitude') and l.get('longitude')
        ]
        
        plugins.HeatMap(
            heat_data,
            name='Development Score Heatmap',
            min_opacity=0.2,
            radius=30,
            blur=20,
            max_zoom=1
        ).add_to(m)
        
        folium.LayerControl().add_to(m)
        
        m.save(output_file)
        self.logger.info(f"Heatmap saved to {output_file}")
        return output_file
    
    def generate_comparison_map(self, listings, output_file='data/comparison_map.html'):
        """Side-by-side comparison: high vs low score properties"""
        
        m = folium.Map(
            location=self.center,
            zoom_start=13,
            tiles='OpenStreetMap'
        )
        
        # High score layer
        fg_high = folium.FeatureGroup(name='High Score (70+)')
        # Low score layer
        fg_low = folium.FeatureGroup(name='Low Score (<70)')
        
        for listing in listings:
            if listing.get('latitude') and listing.get('longitude'):
                lat = float(listing['latitude'])
                lon = float(listing['longitude'])
                score = listing.get('development_score', 0)
                
                popup = f"{listing['address']}: {score:.1f}/100"
                
                if score >= 70:
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=8,
                        popup=popup,
                        color='red',
                        fill=True,
                        fillColor='red',
                        fillOpacity=0.7,
                        weight=2
                    ).add_to(fg_high)
                else:
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=5,
                        popup=popup,
                        color='blue',
                        fill=True,
                        fillColor='blue',
                        fillOpacity=0.5,
                        weight=1
                    ).add_to(fg_low)
        
        fg_high.add_to(m)
        fg_low.add_to(m)
        folium.LayerControl().add_to(m)
        
        m.save(output_file)
        self.logger.info(f"Comparison map saved to {output_file}")
        return output_file
```

#### Step 4.2: Integrate into Pipeline
**File:** `app/dev_pipeline.py` (add to Stage 4)

```python
from app.visualizations.map_generator import MapGenerator

# In Stage 4: Saving Results
if classified_listings:
    self.logger.info("Generating maps...")
    map_gen = MapGenerator()
    
    # Add latitude/longitude to listings (from enrichment)
    map_gen.generate_opportunity_map(classified_listings)
    map_gen.generate_score_heatmap(classified_listings)
    
    self.logger.info("✓ Maps generated in data/ directory")
```

#### Step 4.3: Install Dependencies
```bash
pip install folium
```

#### Step 4.4: Test
```bash
python -m app.dev_pipeline

# Check for generated maps
ls -lh data/*.html
# Open in browser: open data/opportunity_map.html
```

### Output
- ✅ Interactive map with all properties
- ✅ Color-coded by development score
- ✅ Clickable markers with listing details
- ✅ Heatmap visualization of opportunity clusters
- ✅ Exportable HTML (embeddable in dashboard)

---

## TASK 5: ROI & BUILDABLE SF SCORING 🟠 LOW PRIORITY

**Objective:** Estimate profit potential and construction capacity

### What You'll Build
```
Property Data (lot size, zoning, price)
    ↓
GIS Zoning Data (FAR, setbacks)
    ↓
Calculation Engine
    ├─ Buildable SF estimation
    ├─ Construction cost estimate
    ├─ Comparable sales analysis
    └─ ROI potential score
    ↓
Added to output: roi_score, buildable_sf, profit_estimate
```

### Implementation Steps

#### Step 5.1: Create ROI Module
**File:** `app/analysis/roi_calculator.py`

```python
import logging
import requests
from typing import Dict, Any

class ROICalculator:
    """Calculate ROI potential for properties"""
    
    def __init__(self):
        self.logger = logging.getLogger('roi_calculator')
        
        # Newton market rates (configure based on your data)
        self.newton_avg_price_per_sqft = 350  # $350/sqft average
        self.construction_cost_per_sqft = 150  # $150/sqft construction
        self.soft_costs_percent = 0.20  # 20% soft costs
        self.realtor_commission = 0.06  # 6% commission
    
    def calculate_buildable_sf(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate buildable square footage based on FAR and lot size"""
        
        lot_size = property_data.get('lot_size', 0)
        zoning_code = property_data.get('zoning', '')
        
        # FAR by zoning (example - customize for Newton)
        far_map = {
            'R1': 0.5,   # Single family residential
            'R2': 0.75,  # Multi-family
            'R3': 1.0,
            'C1': 1.5,   # Commercial
            'C2': 2.0,
        }
        
        # Determine FAR
        far = far_map.get(zoning_code.split()[0], 0.5)
        
        # Maximum building size = lot_size * FAR
        max_buildable = lot_size * far
        
        # Current building size
        current_sqft = property_data.get('sqft', 0)
        
        # Additional buildable space
        additional_buildable = max(0, max_buildable - current_sqft)
        
        return {
            'lot_size': lot_size,
            'far': far,
            'max_buildable_sf': int(max_buildable),
            'current_sqft': current_sqft,
            'additional_buildable_sf': int(additional_buildable),
            'zoning_utilization': current_sqft / max_buildable if max_buildable > 0 else 0
        }
    
    def calculate_construction_costs(self, buildable_sf: int) -> Dict[str, float]:
        """Estimate construction costs"""
        
        direct_costs = buildable_sf * self.construction_cost_per_sqft
        soft_costs = direct_costs * self.soft_costs_percent
        
        return {
            'direct_construction': direct_costs,
            'soft_costs': soft_costs,
            'total_construction_cost': direct_costs + soft_costs
        }
    
    def calculate_resale_value(self, property_data: Dict[str, Any], 
                               additional_sf: int) -> float:
        """Estimate resale value after expansion"""
        
        # New building value
        new_sqft = property_data.get('sqft', 0) + additional_sf
        estimated_resale = new_sqft * self.newton_avg_price_per_sqft
        
        return estimated_resale
    
    def calculate_roi_potential(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive ROI metrics"""
        
        # Step 1: Buildable capacity
        buildable = self.calculate_buildable_sf(property_data)
        additional_sf = buildable['additional_buildable_sf']
        
        # Step 2: Construction costs
        costs = self.calculate_construction_costs(additional_sf)
        
        # Step 3: Acquisition costs
        acquisition_price = property_data.get('price', 0)
        demolition_cost = 50000  # Rough estimate
        
        # Step 4: Resale value
        resale_value = self.calculate_resale_value(property_data, additional_sf)
        
        # Step 5: Calculate profits
        total_investment = (acquisition_price + 
                           demolition_cost + 
                           costs['total_construction_cost'])
        
        selling_costs = resale_value * self.realtor_commission
        net_profit = resale_value - total_investment - selling_costs
        roi_percent = (net_profit / total_investment * 100) if total_investment > 0 else 0
        
        # ROI Score (0-100)
        # 20%+ ROI = excellent (100 points)
        # 10-20% = good (60-100 points)
        # 5-10% = fair (30-60 points)
        # <5% = poor (0-30 points)
        if roi_percent >= 20:
            roi_score = min(100, 50 + roi_percent)
        elif roi_percent >= 10:
            roi_score = 60 + (roi_percent - 10) * 4
        elif roi_percent >= 5:
            roi_score = 30 + (roi_percent - 5) * 6
        else:
            roi_score = max(0, roi_percent * 6)
        
        return {
            'buildable_analysis': buildable,
            'construction_costs': costs,
            'acquisition_cost': acquisition_price,
            'demolition_cost': demolition_cost,
            'resale_value': int(resale_value),
            'total_investment': int(total_investment),
            'selling_costs': int(selling_costs),
            'net_profit': int(net_profit),
            'roi_percent': round(roi_percent, 1),
            'roi_score': round(roi_score, 1),
            'feasibility': 'Excellent' if roi_score >= 70 else 'Good' if roi_score >= 50 else 'Fair' if roi_score >= 30 else 'Poor'
        }

# Usage in classifier
def enrich_with_roi(listings):
    roi_calc = ROICalculator()
    
    for listing in listings:
        try:
            roi_data = roi_calc.calculate_roi_potential(listing)
            listing.update({
                'additional_buildable_sf': roi_data['buildable_analysis']['additional_buildable_sf'],
                'roi_score': roi_data['roi_score'],
                'roi_percent': roi_data['roi_percent'],
                'net_profit_potential': roi_data['net_profit'],
                'feasibility': roi_data['feasibility']
            })
        except Exception as e:
            logging.error(f"ROI calculation failed for {listing.get('address')}: {e}")
    
    return listings
```

#### Step 5.2: Integrate into Pipeline
**File:** `app/dev_pipeline.py` (modify Stage 3)

```python
from app.analysis.roi_calculator import ROICalculator

# In Stage 3: Classification
if classify_data and all_listings:
    self.logger.info("\n" + "=" * 60)
    self.logger.info("STAGE 3: CLASSIFICATION & ROI")
    self.logger.info("=" * 60)
    
    classified_listings = self.classifier.classify_listings_batch(all_listings)
    
    # NEW: Calculate ROI for each listing
    roi_calc = ROICalculator()
    for listing in classified_listings:
        roi_data = roi_calc.calculate_roi_potential(listing)
        listing['roi_score'] = roi_data['roi_score']
        listing['roi_percent'] = roi_data['roi_percent']
        listing['buildable_sf'] = roi_data['buildable_analysis']['additional_buildable_sf']
        listing['net_profit'] = roi_data['net_profit']
```

#### Step 5.3: Update Output Fields
**File:** `app/utils.py` (modify CSV headers)

```python
# Add to CSV headers
ROI_FIELDS = [
    'roi_score',
    'roi_percent',
    'buildable_sf',
    'net_profit',
    'feasibility'
]
```

#### Step 5.4: Test
```bash
python -m app.dev_pipeline

# Check output includes ROI columns
head -n 1 data/classified_listings.csv | tr ',' '\n' | grep roi
```

### Output
- ✅ Buildable square footage estimation
- ✅ Construction cost estimates
- ✅ Resale value projection
- ✅ Net profit calculation
- ✅ ROI percentage & score
- ✅ Feasibility rating

---

## 📊 IMPLEMENTATION SUMMARY

### What Gets Added to Output

After all 5 tasks:

```csv
address,price,beds,baths,...
,development_score,label,confidence,

-- Task 1: Google Sheets
(auto-upload to shared sheet)

-- Task 2: Database
(all data stored historically)

-- Task 3: Email/Slack
(daily alerts sent automatically)

-- Task 4: Maps
(interactive HTML map generated)

-- Task 5: ROI Scoring
,roi_score,roi_percent,buildable_sf,net_profit,feasibility
```

---

## ✅ QUICK START CHECKLIST

```bash
# Task 1: Google Sheets
[ ] Create Google Cloud project
[ ] Download credentials JSON
[ ] Create google_sheets_uploader.py
[ ] Test upload

# Task 2: Database
[ ] Create database schema
[ ] Create database.py module
[ ] Initialize SQLite DB
[ ] Test insert/query

# Task 3: Email/Slack
[ ] Get email credentials (Gmail)
[ ] Get Slack webhook URL
[ ] Create alerts.py module
[ ] Test send

# Task 4: Maps
[ ] Install folium
[ ] Create map_generator.py
[ ] Generate test map
[ ] Verify HTML output

# Task 5: ROI
[ ] Create roi_calculator.py
[ ] Integrate into classifier
[ ] Test ROI calculations
[ ] Verify output fields
```

---

## 🎯 NEXT STEPS

Choose one task and I'll provide:
1. Complete code file
2. Step-by-step setup instructions
3. Testing procedure
4. Integration into pipeline

**Recommendation**: Start with **Task 1 (Google Sheets)** or **Task 3 (Email/Slack)** - they're lower complexity but high value.

Which task would you like me to implement first?
