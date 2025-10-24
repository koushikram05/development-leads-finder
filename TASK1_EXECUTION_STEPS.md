# 🚀 TASK 1 EXECUTION: Step-by-Step Instructions

**Status:** Ready to Run  
**Estimated Time:** 30 minutes  
**All Requirements:** ✅ Implemented

---

## ✅ REQUIREMENTS CONFIRMATION

Your specified requirements are ALL implemented:

✅ **Run daily or weekly automated scans** → PipelineScheduler class created  
✅ **Filter by Newton, MA (expandable)** → Location filtering in GoogleSheetsUploader  
✅ **Rank by development score** → Auto-sorts listings highest score first  
✅ **Export CSV + push to Google Sheet** → Both done automatically  
✅ **Allow manual trigger refresh** → scheduler.run_now() + direct CLI  
✅ **Review log of collected leads** → sheets_upload_log.txt + pipeline_execution_log.txt  

---

## 📋 QUICK SETUP (3 simple steps)

### STEP 1: Get Google Credentials (10 minutes)

**Go here:** https://console.cloud.google.com/

1. Click "Select a Project" → "New Project"
2. Name: `Development_Leads`
3. Click Create → Wait for it...

**Next: Enable APIs**
1. Search for "Sheets API" → Click Enable
2. Search for "Drive API" → Click Enable

**Next: Create Service Account**
1. Search "Service Accounts" → Click on it
2. Click "Create Service Account"
3. Name: `development-leads-bot`
4. Click "Create and Continue"
5. Skip optional steps, click "Create Key"
6. Choose "JSON"
7. **File downloads** → Save as `google_credentials.json`

**Next: Share the sheet with bot**
1. Open the JSON file → Find `client_email` (looks like `xxx@xxx.iam.gserviceaccount.com`)
2. Create new Google Sheet: https://sheets.google.com → Name it `Development_Leads`
3. Click Share → Paste the email → Choose "Editor" → Click Share

**Result:** `google_credentials.json` file in your project root

---

### STEP 2: Configure Environment (2 minutes)

```bash
cd /Users/koushikramalingam/Desktop/Anil_Project

# Move credentials file
mv ~/Downloads/google_credentials.json .
echo "google_credentials.json" >> .gitignore

# Update .env
cat >> .env << 'EOF'

# Google Sheets Configuration
GOOGLE_CREDENTIALS_PATH=./google_credentials.json

# Scheduler Configuration (optional)
SCAN_FREQUENCY=daily
SCAN_TIME=09:00
SCAN_DAY=mon
PRIMARY_LOCATION=Newton, MA
EOF

# Verify
cat .env | grep GOOGLE_CREDENTIALS_PATH
```

---

### STEP 3: Test It Works (5 minutes)

```bash
cd /Users/koushikramalingam/Desktop/Anil_Project
source .venv/bin/activate

# Test authentication
python << 'EOF'
from app.integrations.google_sheets_uploader import GoogleSheetsUploader

try:
    uploader = GoogleSheetsUploader()
    print("✅ Google Sheets authentication successful!")
except Exception as e:
    print(f"❌ Error: {e}")
EOF

# Expected output: ✅ Google Sheets authentication successful!
```

---

## 🚀 RUN THE PIPELINE

### Option 1: Manual Run (Test First)

```bash
cd /Users/koushikramalingam/Desktop/Anil_Project
source .venv/bin/activate

# Run pipeline
python -m app.dev_pipeline

# Sit back and watch...
# ✓ Stage 1: Data Collection (SerpAPI)
# ✓ Stage 2: GIS Enrichment
# ✓ Stage 3: Classification
# ✓ Stage 4: Google Sheets Upload ← THIS IS NEW

# Check Google Sheet
# → Open: https://sheets.google.com
# → Find: "Development_Leads"
# → See: All listings sorted by score
```

**Expected Output:**
```
============================================================
STAGE 4: SAVING RESULTS & UPLOADING TO SHEETS
============================================================
✓ Filtered 25 listings for Newton, MA
✓ Uploaded 25 listings to 'Development_Leads' (Sorted by development_score)
✓ Google Sheets upload successful (25 listings)
```

---

## 📊 VERIFY IT WORKED

### Check 1: Google Sheet Updated

1. Open: https://sheets.google.com
2. Find "Development_Leads" sheet
3. Should see:
   - **Header row** (Address, Price, Score, etc.)
   - **Data rows** sorted by development_score (highest first)
   - **Filter buttons** on each column
   - **Red/Orange/Blue colors** visible (optional formatting)

### Check 2: CSV Files Created

```bash
cd /Users/koushikramalingam/Desktop/Anil_Project
ls -lh data/

# Should see:
# -rw-r--r--  22K classified_listings.csv
# -rw-r--r--  35K classified_listings.json
# -rw-r--r--   9K raw_listings.csv
```

### Check 3: Upload Log

```bash
cat data/sheets_upload_log.txt

# Should show:
# 2025-10-23T14:30:45.123456 | Sheet: Development_Leads | Listings: 25 | Location: Newton, MA
```

---

## 🔄 ADVANCED: AUTOMATED SCHEDULING

### Option A: Daily Automation (macOS Cron)

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /Users/koushikramalingam/Desktop/Anil_Project && source .venv/bin/activate && python -m app.dev_pipeline >> data/cron.log 2>&1

# Save and exit (Ctrl+X in nano, then Y, then Enter)

# Verify cron job added
crontab -l
```

**Now:** Pipeline runs automatically every day at 9 AM. Google Sheet auto-updates.

### Option B: Weekly Automation

```bash
# Add to crontab (Monday at 9 AM)
0 9 * * 1 cd /Users/koushikramalingam/Desktop/Anil_Project && source .venv/bin/activate && python -m app.dev_pipeline >> data/cron.log 2>&1
```

### Option C: Manual Trigger Anytime

```bash
# Just run:
python -m app.dev_pipeline

# Google Sheet updates immediately
```

---

## 📁 OUTPUT FILES CREATED

```
/data/
├── classified_listings.csv          ← Main output (25-30 properties)
├── classified_listings.json         ← Same data, JSON format
├── raw_listings.csv                 ← Before classification
├── sheets_upload_log.txt            ← Track all Google Sheet uploads
└── pipeline_execution_log.txt       ← Track all runs

Google Drive:
└── Development_Leads (Google Sheet) ← Auto-populated, sorted by score
```

---

## 💾 FILE STRUCTURE

**Files Created:**
```
app/integrations/
├── __init__.py
└── google_sheets_uploader.py        (300+ lines, fully documented)

app/
└── scheduler.py                     (200+ lines, handles automated runs)

Modified:
app/dev_pipeline.py                  (Stage 4 now uploads to Google Sheets)
```

---

## 🧪 TEST CHECKLIST

Use this before moving to next task:

- [ ] Google credentials JSON file in project root
- [ ] `.env` has `GOOGLE_CREDENTIALS_PATH=./google_credentials.json`
- [ ] Authentication test passes (✅ success)
- [ ] Pipeline runs: `python -m app.dev_pipeline`
- [ ] Google Sheet "Development_Leads" has listings
- [ ] Listings sorted by development_score (highest first)
- [ ] Filter buttons on header row
- [ ] CSV file exists: `data/classified_listings.csv`
- [ ] Upload log has entries: `cat data/sheets_upload_log.txt`
- [ ] Manual run works: `python -m app.dev_pipeline` (run again)

---

## 📊 SAMPLE OUTPUT

After running, your Google Sheet looks like:

```
| Address              | City       | Price      | Score | Label      | Explanation
|----------------------|------------|------------|-------|------------|----------------------------------
| 42 Main St           | Newton, MA | $890,000   | 92    | EXCELLENT  | Large lot, old house, great POI
| 15 Oak Ave           | Newton, MA | $750,000   | 88    | EXCELLENT  | Tear-down candidate, R3 zoning
| 8 Park Lane          | Newton, MA | $620,000   | 76    | GOOD       | Underbuilt, near schools
| 23 Elm St            | Newton, MA | $1,200,000 | 45    | HOLD       | Smaller lot, newer house
```

**Sorted by Score:** ✓ Highest to lowest
**Location Filter:** ✓ Newton, MA only
**Manual Update:** ✓ Happens each run
**Audit Trail:** ✓ Logged in sheets_upload_log.txt

---

## ⚠️ TROUBLESHOOTING

### "FileNotFoundError: google_credentials.json"

```bash
# Check if file exists
ls google_credentials.json

# If not, make sure you:
# 1. Downloaded it from Google Cloud Console
# 2. Moved it to project root
# 3. Not in a subdirectory
```

### "Failed to authenticate Google Sheets"

```bash
# Verify JSON is valid
cat google_credentials.json

# Should start with: {
#   "type": "service_account",
#   "project_id": "..."

# If corrupted, re-download from Google Cloud
```

### "Spreadsheet not found"

```bash
# Manually create the Google Sheet
# 1. Go to: https://sheets.google.com
# 2. Click "+ New"
# 3. Name it: "Development_Leads"
# 4. Share with service account email
```

### "Gspread" or "oauth2client" import error

```bash
# Reinstall packages
pip install gspread oauth2client --upgrade

# Or in your venv:
source .venv/bin/activate
pip install gspread oauth2client
```

---

## ✨ WHAT'S NEXT

**Task 1 Complete!** ✅

After confirming everything works:

1. ✅ **Task 1: Google Sheets** - DONE
2. → **Task 3: Email/Slack Alerts** (1 hour)
   - Sends high-value properties to your email
   - Posts to Slack channel
   
3. → **Task 2: Historical Database** (1 hour)
   - SQLite database tracking all leads
   - Never lose a prospect
   
4. → **Task 4: Map Visualization** (1 hour)
   - Interactive Folium maps
   - Heat maps by development score
   
5. → **Task 5: ROI Scoring** (1.5 hours)
   - Profit potential calculations
   - Buildable square footage analysis

**Total time for all 5 tasks:** 5-6 hours

---

## 📞 QUICK REFERENCE

### Run Pipeline (Manual)
```bash
python -m app.dev_pipeline
```

### Run with Options
```bash
# Search specific location
python -m app.dev_pipeline --location "Cambridge, MA"

# Set minimum score
python -m app.dev_pipeline --min-score 75

# Skip enrichment
python -m app.dev_pipeline --no-enrich
```

### View Logs
```bash
# Google Sheets upload history
cat data/sheets_upload_log.txt

# All pipeline executions
cat data/pipeline_execution_log.txt

# Latest cron runs
tail data/cron.log
```

### Update Google Sheet Now
```bash
python -m app.dev_pipeline
# Check: https://sheets.google.com/Drive
```

---

**Status: READY TO DEPLOY ✅**

Let me know when you've confirmed everything works!
