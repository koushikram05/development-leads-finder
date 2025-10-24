# 🔧 FIX: GOOGLE SHEET NAME MISMATCH

**Issue Found:** Sheet name is `DevelopmentLeads` but code expects `Development_Leads`

**Good News:** Easy fix! Just 2 options:

---

## ✅ OPTION 1: Rename Your Google Sheet (Easiest)

1. Go to: https://sheets.google.com
2. Find your sheet: `DevelopmentLeads`
3. Click the sheet name at the top
4. Type: `Development_Leads` (with underscore)
5. Press Enter

**Then test:**
```bash
python -m app.dev_pipeline
```

✅ Should work now!

---

## ✅ OPTION 2: Update Code to Match Your Sheet Name

If you prefer to keep the sheet name as `DevelopmentLeads`:

**File:** `app/dev_pipeline.py`

Find this section (around line 157):
```python
success = sheets_uploader.upload_listings(
    listings=classified_listings,
    sheet_name='Development_Leads',  ← CHANGE THIS
    location_filter=location,
    sort_by='development_score'
)
```

Change to:
```python
success = sheets_uploader.upload_listings(
    listings=classified_listings,
    sheet_name='DevelopmentLeads',  ← YOUR SHEET NAME
    location_filter=location,
    sort_by='development_score'
)
```

**Then test:**
```bash
python -m app.dev_pipeline
```

---

## 🎯 RECOMMENDATION

**Use Option 1** (rename to `Development_Leads`)

Why?
- Matches all documentation
- Standard naming convention (underscores for spaces)
- All example code will work as-is
- Easier to remember

---

## ✅ AFTER FIXING

Run:
```bash
python -m app.dev_pipeline
```

You should see:
```
✓ Filtered 28 listings for Newton, MA
✓ Uploaded 28 listings to 'Development_Leads' (Sorted by development_score)
✓ Google Sheets upload successful (28 listings)
```

Then check: https://sheets.google.com
- Your sheet should now have 25-30 properties
- Sorted by development_score (highest first)
- Filter buttons on headers

---

## 🎉 THEN YOU'RE DONE WITH TASK 1!

✅ Code working  
✅ Google Sheet updating  
✅ CSV files created  
✅ Logs tracking  

**Next:** Task 3 (Email/Slack Alerts) - 1 hour

---

**Which option do you prefer?** 1 or 2?
