# ⚡ FAST-TRACK: ALL 5 TASKS TODAY

**Created:** October 23, 2025  
**Mission:** Complete all 5 tasks in ONE day  
**Total Estimated Time:** 6-8 hours

---

## ✅ OPENAI API CONFIRMATION

**YES - Project Uses OpenAI API Key**

Evidence found in code:
```python
# app/classifier/llm_classifier.py (Line 8)
from openai import OpenAI

# Line 19-20
api_key = get_env_variable('OPENAI_API_KEY')
self.client = OpenAI(api_key=api_key)

# Using GPT-4o-mini for cost-effective classification
self.model = "gpt-4o-mini"
```

**Your .env must have:**
```properties
OPENAI_API_KEY=sk-your-openai-key-here
```

---

## 🚀 TODAY'S EXECUTION PLAN

### ⏱️ Timeline: 6-8 Hours Total

```
08:00 - 09:30 (1.5h)   Task 1: Google Sheets Setup
09:30 - 10:30 (1h)     Task 3: Email/Slack Alerts  
10:30 - 11:30 (1h)     Task 2: Database Setup
11:30 - 12:30 (1h)     Task 4: Map Visualization
12:30 - 14:00 (1.5h)   Task 5: ROI Scoring
14:00 - 14:30 (0.5h)   Testing & Integration
─────────────────────────────────
TOTAL:                  ~7-8 hours
```

---

## 🎯 RECOMMENDED START ORDER (Optimized for Speed)

### START HERE: Task 1 (Google Sheets) - 1.5 hours

**Why first?**
- Easiest setup (no code dependencies)
- Foundation for other tasks
- Quick wins build momentum

**What to do:**
1. Create Google Cloud project (15 min)
2. Enable APIs (10 min)
3. Download credentials (5 min)
4. Create `app/integrations/google_sheets_uploader.py` (20 min)
5. Integrate into pipeline (10 min)
6. Test (10 min)

**Output:** Google Sheet auto-populating with leads

---

## 📋 TASK-BY-TASK IMPLEMENTATION

### TASK 1: Google Sheets (1.5 hours) ⭐ START HERE

**File:** `app/integrations/google_sheets_uploader.py`

```python
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging

class GoogleSheetsUploader:
    def __init__(self, credentials_path='google_credentials.json'):
        self.logger = logging.getLogger('sheets_uploader')
        
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_path, scopes
        )
        self.client = gspread.authorize(credentials)
    
    def upload_listings(self, listings, sheet_name='Development_Leads'):
        try:
            sheet = self.client.open(sheet_name)
        except gspread.SpreadsheetNotFound:
            sheet = self.client.create(sheet_name)
        
        worksheet = sheet.sheet1
        worksheet.clear()
        
        if listings:
            headers = list(listings[0].keys())
            worksheet.append_row(headers)
            
            for listing in listings:
                row = [str(listing.get(h, '')) for h in headers]
                worksheet.append_row(row)
            
            self.logger.info(f"✓ Uploaded {len(listings)} to Google Sheet")
            return True
        return False
```

**Setup Steps:**
```bash
# 1. Install packages
pip install gspread oauth2client

# 2. Go to Google Cloud Console
# https://console.cloud.google.com/
# Create project → Enable Sheets API & Drive API
# Create Service Account → Download JSON

# 3. Save credentials
mv ~/Downloads/*.json ./google_credentials.json
echo "google_credentials.json" >> .gitignore

# 4. Add to .env
echo "GOOGLE_CREDENTIALS_PATH=./google_credentials.json" >> .env

# 5. Integrate into pipeline (app/dev_pipeline.py, Stage 4)
from app.integrations.google_sheets_uploader import GoogleSheetsUploader

# In Stage 4:
sheets_uploader = GoogleSheetsUploader()
sheets_uploader.upload_listings(classified_listings)
```

---

### TASK 3: Email/Slack Alerts (1 hour) - NEXT

**File:** `app/integrations/alerts.py`

```python
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

class AlertManager:
    def __init__(self):
        self.logger = logging.getLogger('alerts')
        self.email_from = os.getenv('ALERT_EMAIL')
        self.email_password = os.getenv('ALERT_EMAIL_PASSWORD')
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    
    def send_email_alert(self, to_emails, subject, listings):
        try:
            html = f"""
            <html><head><style>
            body {{ font-family: Arial; }}
            .header {{ background: #2c3e50; color: white; padding: 20px; }}
            .opp {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; }}
            .score {{ color: #27ae60; font-weight: bold; }}
            </style></head><body>
            <div class="header"><h2>🏠 Development Opportunities</h2></div>
            <p>Found {len(listings)} opportunities:</p>
            """
            
            for listing in listings[:10]:
                html += f"""
                <div class="opp">
                    <h3>{listing['address']}</h3>
                    <p>Price: ${listing.get('price', 0):,.0f}</p>
                    <p>Score: <span class="score">{listing.get('development_score', 0):.1f}/100</span></p>
                    <p>{listing.get('explanation', '')[:150]}...</p>
                </div>
                """
            
            html += "</body></html>"
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = ', '.join(to_emails)
            msg.attach(MIMEText(html, 'html'))
            
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.email_from, self.email_password)
            server.sendmail(self.email_from, to_emails, msg.as_string())
            server.quit()
            
            self.logger.info(f"✓ Email sent to {len(to_emails)} recipients")
            return True
        except Exception as e:
            self.logger.error(f"Email failed: {e}")
            return False
    
    def send_slack_alert(self, opportunities):
        try:
            blocks = [
                {"type": "header", "text": {"type": "plain_text", "text": "🏠 Development Opportunities"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"Found {len(opportunities)} opportunities:"}}
            ]
            
            for opp in opportunities[:5]:
                blocks.append({
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*{opp['address']}*\nScore: {opp['development_score']:.0f}/100 | Price: ${opp.get('price', 0):,.0f}"}
                })
            
            response = requests.post(self.slack_webhook, json={'blocks': blocks})
            if response.status_code == 200:
                self.logger.info("✓ Slack notification sent")
                return True
        except Exception as e:
            self.logger.error(f"Slack failed: {e}")
        return False
```

**Setup Steps:**
```bash
# 1. Get Gmail app password
# https://myaccount.google.com/apppasswords
# Select Mail & Mac, copy password

# 2. Get Slack webhook
# https://api.slack.com/apps → Create App → Incoming Webhooks

# 3. Add to .env
echo "ALERT_EMAIL=your-email@gmail.com" >> .env
echo "ALERT_EMAIL_PASSWORD=your-app-password" >> .env
echo "SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL" >> .env
echo "ALERT_RECIPIENTS=team@company.com,manager@company.com" >> .env

# 4. Install packages
pip install requests

# 5. Integrate into pipeline (Stage 4)
from app.integrations.alerts import AlertManager

high_value = [l for l in classified_listings if l.get('development_score', 0) >= 70]
if high_value:
    alert_manager = AlertManager()
    alert_manager.send_email_alert(
        to_emails=os.getenv('ALERT_RECIPIENTS', '').split(','),
        subject=f"🏠 {len(high_value)} Dev Opportunities",
        listings=high_value
    )
    alert_manager.send_slack_alert(high_value)
```

---

### TASK 2: Database (1 hour) - AFTER TASK 1

**File:** `app/database/schema.py`

```python
import sqlite3
from datetime import datetime
import logging

class LeadsDatabase:
    def __init__(self, db_path='data/leads_history.db'):
        self.db_path = db_path
        self.logger = logging.getLogger('database')
        self.init_db()
    
    def init_db(self):
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
        
        # Classifications table
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
        
        conn.commit()
        conn.close()
        self.logger.info("✓ Database initialized")
    
    def insert_listing(self, listing):
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
```

**Setup Steps:**
```bash
# 1. Create directory
mkdir -p app/database
touch app/database/__init__.py

# 2. Install (sqlite3 built-in)
# No installation needed!

# 3. Integrate into pipeline (Stage 4)
from app.database.schema import LeadsDatabase

db = LeadsDatabase()

# After loading classified_listings:
for listing in classified_listings:
    listing_id = db.insert_listing(listing)
    db.insert_classification(listing_id, listing)
    self.logger.info(f"Saved to database: {listing['address']}")
```

---

### TASK 4: Map Visualization (1 hour)

**File:** `app/visualizations/map_generator.py`

```python
import folium
from folium import plugins
import logging

class MapGenerator:
    def __init__(self, center_lat=42.3376, center_lon=-71.2092):
        self.center = [center_lat, center_lon]
        self.logger = logging.getLogger('map_generator')
    
    def generate_opportunity_map(self, listings, output_file='data/opportunity_map.html'):
        m = folium.Map(
            location=self.center,
            zoom_start=13,
            tiles='OpenStreetMap'
        )
        
        for listing in listings:
            if listing.get('latitude') and listing.get('longitude'):
                lat = float(listing['latitude'])
                lon = float(listing['longitude'])
                
                score = listing.get('development_score', 0)
                if score >= 70:
                    color = 'red'
                elif score >= 50:
                    color = 'orange'
                else:
                    color = 'blue'
                
                popup_text = f"""
                <b>{listing['address']}</b><br>
                Price: ${listing.get('price', 'N/A'):,.0f}<br>
                Score: {score:.1f}/100<br>
                Label: {listing.get('label', 'N/A')}<br>
                <a href="{listing.get('url', '#')}" target="_blank">View</a>
                """
                
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_text, max_width=300),
                    icon=folium.Icon(color=color, icon='star'),
                    tooltip=listing['address']
                ).add_to(m)
        
        # Add heatmap
        heat_data = [
            [float(l['latitude']), float(l['longitude']), l.get('development_score', 0) / 100]
            for l in listings
            if l.get('latitude') and l.get('longitude')
        ]
        
        if heat_data:
            plugins.HeatMap(heat_data, radius=20, blur=15, max_zoom=1).add_to(m)
        
        folium.LayerControl().add_to(m)
        m.save(output_file)
        self.logger.info(f"✓ Map saved to {output_file}")
        return output_file
```

**Setup Steps:**
```bash
# 1. Install folium
pip install folium

# 2. Create directory
mkdir -p app/visualizations
touch app/visualizations/__init__.py

# 3. Integrate into pipeline (Stage 4)
from app.visualizations.map_generator import MapGenerator

if classified_listings:
    map_gen = MapGenerator()
    map_gen.generate_opportunity_map(classified_listings)
    self.logger.info("✓ Maps generated")
```

---

### TASK 5: ROI Scoring (1.5 hours)

**File:** `app/analysis/roi_calculator.py`

```python
import logging

class ROICalculator:
    def __init__(self):
        self.logger = logging.getLogger('roi_calculator')
        self.newton_avg_price_per_sqft = 350
        self.construction_cost_per_sqft = 150
        self.soft_costs_percent = 0.20
        self.realtor_commission = 0.06
    
    def calculate_buildable_sf(self, property_data):
        lot_size = property_data.get('lot_size', 0)
        zoning_code = property_data.get('zoning', '')
        
        far_map = {
            'R1': 0.5,
            'R2': 0.75,
            'R3': 1.0,
            'C1': 1.5,
            'C2': 2.0,
        }
        
        far = far_map.get(zoning_code.split()[0] if zoning_code else '', 0.5)
        max_buildable = lot_size * far
        current_sqft = property_data.get('sqft', 0)
        additional_buildable = max(0, max_buildable - current_sqft)
        
        return {
            'lot_size': lot_size,
            'far': far,
            'max_buildable_sf': int(max_buildable),
            'current_sqft': current_sqft,
            'additional_buildable_sf': int(additional_buildable),
        }
    
    def calculate_roi_potential(self, property_data):
        buildable = self.calculate_buildable_sf(property_data)
        additional_sf = buildable['additional_buildable_sf']
        
        direct_costs = additional_sf * self.construction_cost_per_sqft
        soft_costs = direct_costs * self.soft_costs_percent
        total_construction = direct_costs + soft_costs
        
        acquisition_price = property_data.get('price', 0)
        demolition_cost = 50000
        total_investment = acquisition_price + demolition_cost + total_construction
        
        new_sqft = property_data.get('sqft', 0) + additional_sf
        resale_value = new_sqft * self.newton_avg_price_per_sqft
        selling_costs = resale_value * self.realtor_commission
        net_profit = resale_value - total_investment - selling_costs
        roi_percent = (net_profit / total_investment * 100) if total_investment > 0 else 0
        
        # ROI Score
        if roi_percent >= 20:
            roi_score = min(100, 50 + roi_percent)
        elif roi_percent >= 10:
            roi_score = 60 + (roi_percent - 10) * 4
        elif roi_percent >= 5:
            roi_score = 30 + (roi_percent - 5) * 6
        else:
            roi_score = max(0, roi_percent * 6)
        
        return {
            'buildable_sf': int(additional_sf),
            'construction_cost': int(total_construction),
            'roi_percent': round(roi_percent, 1),
            'roi_score': round(roi_score, 1),
            'net_profit': int(net_profit),
            'feasibility': 'Excellent' if roi_score >= 70 else 'Good' if roi_score >= 50 else 'Fair' if roi_score >= 30 else 'Poor'
        }
```

**Setup Steps:**
```bash
# 1. Create directory
mkdir -p app/analysis
touch app/analysis/__init__.py

# 2. No new packages needed!

# 3. Integrate into pipeline (Stage 3 - after classification)
from app.analysis.roi_calculator import ROICalculator

roi_calc = ROICalculator()
for listing in classified_listings:
    roi_data = roi_calc.calculate_roi_potential(listing)
    listing['roi_score'] = roi_data['roi_score']
    listing['roi_percent'] = roi_data['roi_percent']
    listing['buildable_sf'] = roi_data['buildable_sf']
    listing['net_profit'] = roi_data['net_profit']
    listing['feasibility'] = roi_data['feasibility']
```

---

## 🔧 INTEGRATION CHECKLIST

### Step 1: Create Directories
```bash
mkdir -p app/integrations
mkdir -p app/database
mkdir -p app/visualizations
mkdir -p app/analysis

touch app/integrations/__init__.py
touch app/database/__init__.py
touch app/visualizations/__init__.py
touch app/analysis/__init__.py
```

### Step 2: Install All Packages
```bash
pip install gspread oauth2client folium requests
```

### Step 3: Update `.env`
```bash
cat >> .env << 'EOF'

# Google Sheets
GOOGLE_CREDENTIALS_PATH=./google_credentials.json

# Email Alerts
ALERT_EMAIL=your-email@gmail.com
ALERT_EMAIL_PASSWORD=your-app-password
ALERT_RECIPIENTS=team@company.com

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
EOF
```

### Step 4: Modify `app/dev_pipeline.py`
**Stage 4: Saving Results** - Replace current code with:

```python
# Stage 4: Save Results
self.logger.info("\n" + "=" * 60)
self.logger.info("STAGE 4: SAVING RESULTS & NOTIFICATIONS")
self.logger.info("=" * 60)

# Initialize components
from app.integrations.google_sheets_uploader import GoogleSheetsUploader
from app.integrations.alerts import AlertManager
from app.database.schema import LeadsDatabase
from app.visualizations.map_generator import MapGenerator

db = LeadsDatabase()
sheets_uploader = GoogleSheetsUploader()
map_gen = MapGenerator()

# 1. Save to Database
for listing in classified_listings:
    listing_id = db.insert_listing(listing)
    db.insert_classification(listing_id, listing)
self.logger.info(f"✓ Saved {len(classified_listings)} to database")

# 2. Upload to Google Sheets
try:
    sheets_uploader.upload_listings(classified_listings)
    self.logger.info("✓ Google Sheets upload successful")
except Exception as e:
    self.logger.error(f"Google Sheets failed: {e}")

# 3. Save CSV/JSON
if classified_listings:
    save_to_csv(classified_listings, 'classified_listings.csv')
    save_to_json(classified_listings, 'classified_listings.json')

# 4. Generate Maps
try:
    map_gen.generate_opportunity_map(classified_listings)
    self.logger.info("✓ Maps generated")
except Exception as e:
    self.logger.error(f"Map generation failed: {e}")

# 5. Send Alerts
high_value = [l for l in classified_listings if l.get('development_score', 0) >= 70]
if high_value:
    try:
        alert_manager = AlertManager()
        alert_manager.send_email_alert(
            to_emails=os.getenv('ALERT_RECIPIENTS', '').split(','),
            subject=f"🏠 {len(high_value)} Development Opportunities",
            listings=high_value
        )
        alert_manager.send_slack_alert(high_value)
        self.logger.info("✓ Alerts sent")
    except Exception as e:
        self.logger.error(f"Alerts failed: {e}")
```

---

## 🚀 FINAL EXECUTION COMMAND

```bash
# Activate environment
source .venv/bin/activate

# Run complete pipeline with all enhancements
python -m app.dev_pipeline

# Expected output:
# ✓ Stage 1: Data Collection (30 listings)
# ✓ Stage 2: GIS Enrichment
# ✓ Stage 3: Classification with ROI
# ✓ Stage 4: Database save
# ✓ Google Sheets upload
# ✓ Maps generated
# ✓ Alerts sent (email + Slack)
```

---

## ✅ SUCCESS CHECKLIST

After running pipeline, verify:

- [ ] `data/classified_listings.csv` updated
- [ ] `data/opportunity_map.html` created
- [ ] `data/leads_history.db` created
- [ ] New Google Sheet appears in Drive
- [ ] Email digest received
- [ ] Slack notification posted
- [ ] `roi_score` column in CSV
- [ ] `buildable_sf` column in CSV

---

## 📊 Final Output Structure

```
/data/
├── classified_listings.csv          (with roi_score, buildable_sf)
├── classified_listings.json
├── opportunity_map.html             (interactive map)
├── leads_history.db                 (SQLite database)
└── logs/
    └── pipeline_2025-10-23.log

Google Drive:
├── Development_Leads (auto-updated sheet)

Email/Slack:
├── Daily digest (morning)
├── Slack alerts (real-time)
```

---

## 🎯 START NOW

**All 5 tasks ready to implement.**

Choose one to start immediately, or I can implement all at once if you provide credentials.

**What you need:**
1. Google Cloud credentials JSON
2. Gmail app password
3. Slack webhook URL

**Should I proceed with implementation?**
