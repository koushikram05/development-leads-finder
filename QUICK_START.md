# Quick Reference - Implementation Guide

**Start here if you just want to dive in!**

---

## 🎯 THE 5 TASKS AT A GLANCE

| # | Task | Setup | Code | Time | Start? |
|---|------|-------|------|------|--------|
| 1️⃣ | **Google Sheets** | 30 min | 100 lines | 2-3d | ✅ HERE |
| 2️⃣ | **Database** | 15 min | 200 lines | 3-4d |  |
| 3️⃣ | **Email/Slack** | 20 min | 150 lines | 1-2d |  |
| 4️⃣ | **Maps** | 5 min | 200 lines | 2-3d |  |
| 5️⃣ | **ROI Scoring** | 0 min | 300 lines | 3-5d |  |

---

## 🚀 RECOMMENDED: Start with Task 1 (Google Sheets)

### Why?
- ✅ Easiest to implement
- ✅ Fastest value delivery  
- ✅ No infrastructure needed
- ✅ Team collaboration instantly

### What You'll Get
```
Pipeline Output (CSV)
       ↓
   Google API
       ↓
Shared Google Sheet (auto-updated daily)
       ↓
Team accesses from anywhere
```

### Setup Time Breakdown
- **5 min:** Create Google Cloud project
- **10 min:** Enable APIs & get credentials
- **15 min:** Download credentials JSON
- **30 min:** Write google_sheets_uploader.py
- **15 min:** Integrate into pipeline
- **10 min:** Test & verify

**Total: ~1.5 hours to get running**

---

## 📋 STEP-BY-STEP: Task 1 Walkthrough

### Step 1: Create Google Cloud Project
```bash
# 1. Visit https://console.cloud.google.com/
# 2. Click "Create Project"
# 3. Name: "Anil_Project"
# 4. Wait for project to initialize
```

### Step 2: Enable APIs
```bash
# In Google Cloud Console:
# 1. Search "Google Sheets API"
# 2. Click "Enable"
# 3. Search "Google Drive API"  
# 4. Click "Enable"
```

### Step 3: Create Service Account
```bash
# In Google Cloud Console:
# 1. Go to "Service Accounts"
# 2. Create New Service Account
# 3. Name: "anil-lead-agent"
# 4. Grant roles:
#    - Editor (for development)
# 5. Create key (JSON format)
# 6. Download JSON file
```

### Step 4: Save Credentials
```bash
# Save downloaded JSON to project root:
cd /Users/koushikramalingam/Desktop/Anil_Project
mv ~/Downloads/anil-lead-agent-*.json ./google_credentials.json

# Add to .gitignore
echo "google_credentials.json" >> .gitignore
```

### Step 5: Install Package
```bash
pip install gspread oauth2client
```

### Step 6: Create Module
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
        """Upload listings to Google Sheet"""
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

### Step 7: Integrate into Pipeline
**File:** `app/dev_pipeline.py`

Add to imports:
```python
from app.integrations.google_sheets_uploader import GoogleSheetsUploader
```

Add to Stage 4 (Saving Results):
```python
# Upload to Google Sheets
try:
    sheets_uploader = GoogleSheetsUploader()
    sheets_uploader.upload_listings(classified_listings)
    self.logger.info("✓ Google Sheets upload successful")
except Exception as e:
    self.logger.error(f"Google Sheets upload failed: {e}")
```

### Step 8: Test
```bash
# Activate venv
source .venv/bin/activate

# Run pipeline
python -m app.dev_pipeline

# Check your Google Drive - new sheet should appear!
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] Created Google Cloud project
- [ ] Enabled Sheets & Drive APIs
- [ ] Created Service Account
- [ ] Downloaded credentials JSON
- [ ] Installed `gspread` and `oauth2client`
- [ ] Created `app/integrations/google_sheets_uploader.py`
- [ ] Updated `app/dev_pipeline.py` with imports & integration
- [ ] Updated `.gitignore` to exclude credentials
- [ ] Ran pipeline successfully
- [ ] Google Sheet appears in Google Drive
- [ ] 30+ listings auto-populated in sheet

---

## 🎉 SUCCESS!

When you see this in pipeline output:
```
2025-10-23 15:32:55 - dev_pipeline - INFO - ✓ Google Sheets upload successful
```

You now have:
✅ Automatic Google Sheet updates  
✅ Shared link for your team  
✅ No file downloads needed  
✅ Data syncs every time you run pipeline  

---

## 🔗 NEXT TASK (Optional)

After Task 1 works, add Task 3 (Email/Slack) for just 1-2 more days:

```python
# Same pattern - create alerts.py module
# Add to pipeline Stage 4
# Team gets instant notifications
```

Or jump straight to Task 2 (Database) if you want historical tracking.

---

## 📞 NEED HELP?

If you hit issues:

**Error: "Credentials not found"**
→ Ensure `google_credentials.json` is in project root

**Error: "API not enabled"**
→ Go back to Google Cloud Console and enable both APIs

**Error: "Module not found"**
→ Run: `pip install gspread oauth2client`

**Error: "403 Forbidden"**
→ Service account doesn't have permissions - check roles

**Google Sheet doesn't update**
→ Ensure service account email has access to sheet
→ Share sheet with service account email

---

## 📁 FILES CREATED

After Task 1:
```
app/
├── integrations/
│   └── google_sheets_uploader.py  (NEW)
└── dev_pipeline.py                (MODIFIED)

.gitignore                          (MODIFIED)
google_credentials.json             (NEW - NOT in git)
```

---

## 🚀 YOU'RE READY!

Choose one:

**A) Implement Task 1 now** ← START HERE
→ Reply: "Implement Task 1" and I'll walk through each step

**B) Skip to Task 2 (Database)**
→ Reply: "Implement Task 2" 

**C) Skip to Task 3 (Email/Slack)**
→ Reply: "Implement Task 3"

**D) Do all 5**
→ Reply: "Implement all" and I'll do one per day

---

## 📊 EXPECTED RESULT

```
BEFORE:
- CSV files in /data/
- Manual sharing needed
- Team doesn't know about new leads

AFTER Task 1:
- Google Sheet auto-updates  
- Shared link (Google Drive)
- Team sees new leads in real-time
- No file management
- Collaborative filtering/sorting
```

**Ready?** Let me know which task and I'll guide you through it! 🎯
