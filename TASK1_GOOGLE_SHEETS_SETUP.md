# 🚀 TASK 1: GOOGLE SHEETS INTEGRATION - SETUP GUIDE

**Status:** ✅ Ready to Configure  
**Time Estimate:** 20-30 minutes  
**Difficulty:** Easy

---

## 📋 REQUIREMENTS CHECKLIST

Your requirements for this task:
- ✅ Run daily or weekly automated scans
- ✅ Filter by Newton, MA (expandable to nearby towns)
- ✅ Rank properties by development potential score
- ✅ Export structured CSV + push to Google Sheet
- ✅ Allow manual trigger refresh
- ✅ Review log of collected leads

**All integrated into the solution below ⬇️**

---

## 🔧 STEP-BY-STEP SETUP (30 minutes)

### STEP 1: Create Google Cloud Project (10 minutes)

1. Go to: https://console.cloud.google.com/
2. Click **"Select a Project"** → **"New Project"**
3. Name it: `Development_Leads`
4. Click **Create**
5. Wait for project to initialize...

### STEP 2: Enable Required APIs (5 minutes)

1. In Google Cloud Console, search for **"Sheets API"**
2. Click **Enable**
3. Search for **"Drive API"**
4. Click **Enable**

### STEP 3: Create Service Account (10 minutes)

1. Go to **"Service Accounts"** (search in console)
2. Click **Create Service Account**
3. Fill in:
   - Service account name: `development-leads-bot`
   - Click **Create and Continue**
4. Skip optional steps
5. Click **Create Key** → **JSON**
6. **Save the file** as `google_credentials.json` in your project root:

```bash
# Download file, then move it to project
mv ~/Downloads/*.json ~/Desktop/Anil_Project/google_credentials.json
echo "google_credentials.json" >> ~/Desktop/Anil_Project/.gitignore
```

### STEP 4: Share Google Sheet with Service Account

1. Open the downloaded `google_credentials.json`
2. Copy the `client_email` value (looks like: `xxx@xxx.iam.gserviceaccount.com`)
3. Create a new Google Sheet: https://sheets.google.com
4. Name it: **`Development_Leads`**
5. Click **Share** button
6. Paste the email, select **"Editor"**
7. **Uncheck** "Notify people"
8. Click **Share**

### STEP 5: Update `.env` File

Add these variables to `.env`:

```bash
# Google Sheets Configuration
GOOGLE_CREDENTIALS_PATH=./google_credentials.json

# Scheduler Configuration
SCAN_FREQUENCY=daily          # Options: daily, weekly
SCAN_TIME=09:00               # Time to run (24-hour format)
SCAN_DAY=mon                  # For weekly: mon, tue, wed, thu, fri, sat, sun

# Location Filtering
PRIMARY_LOCATION=Newton, MA
SECONDARY_LOCATIONS=Waltham, MA,Watertown, MA,Cambridge, MA
```

### STEP 6: Test Google Sheets Authentication

Run this Python command to verify:

```bash
cd /Users/koushikramalingam/Desktop/Anil_Project
source .venv/bin/activate
python << 'EOF'
import os
from app.integrations.google_sheets_uploader import GoogleSheetsUploader

try:
    uploader = GoogleSheetsUploader()
    print("✅ Google Sheets authentication successful!")
    print("Ready to upload listings")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
    print("Check that google_credentials.json exists and is valid")
EOF
```

---

## 📊 FEATURES IMPLEMENTED

### Feature 1: Automatic Daily/Weekly Scans

**How it works:**
- Scheduler runs pipeline at configured time (default: 9 AM daily)
- Collects listings → Enriches data → Classifies → Uploads to Google Sheet
- Execution logged for audit trail

**Configuration:**
```python
# In your main script or cron
from app.scheduler import PipelineScheduler
from app.dev_pipeline import DevelopmentPipeline

scheduler = PipelineScheduler()
pipeline = DevelopmentPipeline()

# Schedule daily at 9 AM
scheduler.schedule_daily(lambda: pipeline.run())

# OR schedule weekly on Monday
scheduler.schedule_weekly(lambda: pipeline.run(), day_of_week='mon')

# Start scheduler
scheduler.start()
```

### Feature 2: Location Filtering (Newton, MA + Expandable)

**How it works:**
- Automatically filters by city in listings
- Can filter multiple locations in separate tabs
- Location names from GIS data

**Supports:**
- Newton, MA (primary)
- Waltham, MA, Watertown, MA, Cambridge, MA (secondary)
- Easily expandable to any other towns

**Code usage:**
```python
uploader.upload_listings(
    listings=classified_listings,
    location_filter='Newton, MA'  # Single location
)

# OR multi-location with separate tabs:
uploader.upload_with_tabs(
    listings=classified_listings,
    locations=['Newton, MA', 'Waltham, MA', 'Cambridge, MA']
)
```

### Feature 3: Ranked by Development Score

**How it works:**
- Automatically sorts all listings by `development_score` (highest first)
- Red = Excellent (score ≥ 70)
- Orange = Good (score ≥ 50)
- Blue = Fair (score < 50)
- Score from LLM classification + lot analysis

**Column Order:**
```
1. Address (clickable)
2. City
3. Price
4. Beds/Baths/SqFt
5. Lot Size
6. Year Built
7. Zoning
8. Label (Development/Hold/Pass)
9. Development Score (75.8)  ← Highest first
10. Confidence
11. Explanation
12. Map Link
13. URL (source)
```

### Feature 4: CSV Export + Google Sheet Push

**How it works:**
- Exports structured CSV to: `data/classified_listings.csv`
- Simultaneously uploads to Google Sheet
- Google Sheet auto-updates each run

**Output Files:**
```
data/
├── classified_listings.csv        ← Excel-ready
├── classified_listings.json       ← API-ready
└── sheets_upload_log.txt          ← Upload history
```

### Feature 5: Manual Refresh Trigger

**How it works:**
- Manual run command that executes pipeline immediately
- Useful for testing or on-demand updates

**Usage:**
```python
# Manual trigger with one command
scheduler.run_now(lambda: pipeline.run())

# Or standalone
pipeline = DevelopmentPipeline()
pipeline.run()
# Check Google Sheet - updates in real-time
```

### Feature 6: Execution Log & Review

**How it works:**
- Every pipeline run is logged with timestamp
- Success/failure status recorded
- Access execution history

**Log files:**
```
data/
├── sheets_upload_log.txt          ← Google Sheet upload history
└── pipeline_execution_log.txt     ← All execution history
```

**View logs:**
```python
# View upload history
uploader = GoogleSheetsUploader()
print(uploader.get_upload_log())

# View execution history
scheduler = PipelineScheduler()
print(scheduler.get_execution_log())
```

---

## 💻 INTEGRATION: Modified Pipeline

**File:** `app/dev_pipeline.py` - Stage 4 (Saving Results)

Replace the Stage 4 code with:

```python
# Stage 4: Save Results & Upload to Google Sheets
self.logger.info("\n" + "=" * 60)
self.logger.info("STAGE 4: SAVING RESULTS & UPLOADING TO SHEETS")
self.logger.info("=" * 60)

# Initialize Google Sheets uploader
from app.integrations.google_sheets_uploader import GoogleSheetsUploader

try:
    sheets_uploader = GoogleSheetsUploader()
    
    # Option A: Single location (Newton, MA)
    success = sheets_uploader.upload_listings(
        listings=classified_listings,
        sheet_name='Development_Leads',
        location_filter='Newton, MA',
        sort_by='development_score'
    )
    
    if success:
        self.logger.info("✓ Successfully uploaded to Google Sheets")
    
    # Option B: Multiple locations in separate tabs (uncomment to use)
    # sheets_uploader.upload_with_tabs(
    #     listings=classified_listings,
    #     locations=['Newton, MA', 'Waltham, MA', 'Cambridge, MA']
    # )
    
except Exception as e:
    self.logger.error(f"Google Sheets upload failed: {e}")

# Save CSV & JSON as before
save_to_csv(classified_listings, 'classified_listings.csv')
save_to_json(classified_listings, 'classified_listings.json')

self.logger.info("✓ All outputs saved successfully")
```

---

## 🔄 AUTOMATED SCHEDULING: Setup

**File:** `app/scheduler_config.py` (create new)

```python
"""
Scheduler configuration for automated pipeline runs
"""

from app.scheduler import PipelineScheduler
from app.dev_pipeline import DevelopmentPipeline
import logging
import os

logger = logging.getLogger(__name__)

def setup_scheduler(
    frequency: str = 'daily',
    scan_time: str = '09:00',
    scan_day: str = 'mon'
):
    """
    Setup automated pipeline scheduler
    
    Args:
        frequency: 'daily' or 'weekly'
        scan_time: 'HH:MM' format (24-hour)
        scan_day: 'mon', 'tue', etc. (for weekly only)
    """
    
    scheduler = PipelineScheduler()
    pipeline = DevelopmentPipeline()
    
    # Parse time
    hour, minute = map(int, scan_time.split(':'))
    
    if frequency == 'daily':
        scheduler.schedule_daily(
            pipeline_func=lambda: pipeline.run(),
            hour=hour,
            minute=minute,
            job_id='daily_dev_scan'
        )
        logger.info(f"✓ Scheduled daily scan at {scan_time}")
    
    elif frequency == 'weekly':
        scheduler.schedule_weekly(
            pipeline_func=lambda: pipeline.run(),
            day_of_week=scan_day,
            hour=hour,
            minute=minute,
            job_id='weekly_dev_scan'
        )
        logger.info(f"✓ Scheduled weekly scan every {scan_day.upper()} at {scan_time}")
    
    # Start scheduler
    scheduler.start()
    scheduler.list_jobs()
    
    return scheduler


if __name__ == '__main__':
    # Load config from .env
    frequency = os.getenv('SCAN_FREQUENCY', 'daily')
    scan_time = os.getenv('SCAN_TIME', '09:00')
    scan_day = os.getenv('SCAN_DAY', 'mon')
    
    scheduler = setup_scheduler(frequency, scan_time, scan_day)
    
    # Keep running
    try:
        print("✓ Scheduler running. Press Ctrl+C to stop")
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
        print("\n✓ Scheduler stopped")
```

---

## 🧪 TESTING CHECKLIST

### Test 1: Google Sheets Authentication ✓

```bash
cd /Users/koushikramalingam/Desktop/Anil_Project
source .venv/bin/activate
python -c "from app.integrations.google_sheets_uploader import GoogleSheetsUploader; u = GoogleSheetsUploader(); print('✓ Auth OK')"
```

Expected: `✓ Auth OK`

### Test 2: Manual Upload

```bash
source .venv/bin/activate
python << 'EOF'
from app.dev_pipeline import DevelopmentPipeline

# Run full pipeline
pipeline = DevelopmentPipeline()
pipeline.run()

# Check outputs
print("\n✓ Pipeline complete!")
print("Check:")
print("  - Google Sheet: https://sheets.google.com")
print("  - Local CSV: data/classified_listings.csv")
EOF
```

Expected: 
- Google Sheet updates with listings
- CSV file appears in `data/` folder
- Log shows "✓ Uploaded X listings"

### Test 3: Verify Google Sheet

1. Open Google Sheets: https://sheets.google.com
2. Find sheet named **"Development_Leads"**
3. Should see:
   - Header row with all columns
   - Listings sorted by development_score (highest first)
   - Rows frozen at top
   - Filter buttons on headers

### Test 4: Check Upload Log

```bash
source .venv/bin/activate
python << 'EOF'
from app.integrations.google_sheets_uploader import GoogleSheetsUploader

uploader = GoogleSheetsUploader()
print(uploader.get_upload_log())
EOF
```

Expected: Shows upload history with timestamps

### Test 5: Manual Trigger

```bash
source .venv/bin/activate
python << 'EOF'
from app.scheduler import PipelineScheduler
from app.dev_pipeline import DevelopmentPipeline

scheduler = PipelineScheduler()
pipeline = DevelopmentPipeline()

# Trigger manually
scheduler.run_now(pipeline.run)

# Check execution log
print("\n" + scheduler.get_execution_log())
EOF
```

Expected: Manual run logged as SUCCESS

---

## 📅 DEPLOYMENT OPTIONS

### Option A: Manual Runs Only (Simplest)

```bash
# Run pipeline anytime
python -m app.dev_pipeline

# Automatically uploads to Google Sheet
```

### Option B: Daily Automation (Recommended)

**macOS Cron Job:**

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /Users/koushikramalingam/Desktop/Anil_Project && source .venv/bin/activate && python -m app.dev_pipeline >> logs/cron.log 2>&1
```

### Option C: Weekly Automation

```bash
# Add to crontab (runs Mondays at 9 AM)
0 9 * * 1 cd /Users/koushikramalingam/Desktop/Anil_Project && source .venv/bin/activate && python -m app.dev_pipeline >> logs/cron.log 2>&1
```

### Option D: Background Scheduler (Advanced)

```bash
# Run scheduler continuously
python /Users/koushikramalingam/Desktop/Anil_Project/app/scheduler_config.py &
```

---

## 📊 OUTPUT STRUCTURE

After running, you'll have:

```
📁 /Data/
├── 📄 classified_listings.csv          (Structured data)
├── 📄 classified_listings.json         (API-ready)
├── 📄 raw_listings.csv                 (Before classification)
├── 📄 sheets_upload_log.txt            (Upload audit trail)
└── 📄 pipeline_execution_log.txt       (Execution history)

☁️ Google Drive/
├── 📊 Development_Leads               (Auto-updated Google Sheet)
│   └── Rows: Sorted by score (highest first)
│   └── Columns: Address, Price, Score, Label, Explanation, URL...
```

---

## ✅ SUCCESS CRITERIA

You'll know it's working when:

- ✅ Google Sheet "Development_Leads" appears in your Google Drive
- ✅ Listings automatically populate sorted by development_score
- ✅ Sheet updates each time you run `python -m app.dev_pipeline`
- ✅ Filter buttons appear on header row
- ✅ Log files track all uploads and executions
- ✅ Newton, MA properties filtered correctly
- ✅ CSV exports match Google Sheet data

---

## 🐛 TROUBLESHOOTING

### Issue: "FileNotFoundError: google_credentials.json"

**Solution:**
```bash
# Verify file exists
ls -la google_credentials.json

# If not found, re-download from Google Cloud Console
# Service Accounts → Your account → Keys → Add Key → JSON
```

### Issue: "Failed to authenticate Google Sheets"

**Solution:**
- Verify JSON file is valid: `cat google_credentials.json`
- Ensure service account email is shared on the Google Sheet
- Try regenerating the key

### Issue: "gspread.exceptions.SpreadsheetNotFound"

**Solution:**
- Create the sheet manually: https://sheets.google.com
- Name it: **`Development_Leads`**
- Share with service account email

### Issue: Listings not appearing in sheet

**Solution:**
- Check data was collected: `head data/classified_listings.csv`
- Verify classifier ran: Check development_score column exists
- Review logs: `cat data/sheets_upload_log.txt`

---

## 🎉 NEXT STEPS

After confirming this task works:

1. ✅ **Task 1 Complete:** Google Sheets integration working
2. → Move to **Task 3:** Email/Slack alerts (1 hour)
3. → Then **Task 2:** Historical database (1 hour)
4. → Then **Task 4:** Maps visualization (1 hour)
5. → Finally **Task 5:** ROI scoring (1.5 hours)

**Estimated total time:** 5-6 hours for all 5 tasks

---

## 📞 SUPPORT

If issues occur:

1. Check `data/sheets_upload_log.txt` for error details
2. Run with verbose logging: Add `--verbose` flag
3. Verify environment: `source .venv/bin/activate`
4. Test auth: Run authentication test above

---

**Status: READY TO DEPLOY** ✅
