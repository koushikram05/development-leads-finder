# 🎯 TASK 1: GOOGLE SHEETS - SETUP VERIFICATION GUIDE

**Current Status:** Code working, credentials needed  
**Next Step:** Follow these 3 steps to get credentials

---

## ✅ WHAT JUST HAPPENED

You ran:
```bash
python << 'EOF'
from app.integrations.google_sheets_uploader import GoogleSheetsUploader
u = GoogleSheetsUploader()
print("✅ Ready!")
EOF
```

**Result:** Got this error
```
ValueError: Failed to authenticate Google Sheets: ('Unexpected credentials type', None, 'Expected', 'service_account')
```

**What this means:**
- ✅ Code is working correctly
- ✅ GoogleSheetsUploader class loaded successfully
- ❌ `google_credentials.json` file is missing or invalid
- ✅ This is EXPECTED - you haven't created it yet

---

## 🚀 GET YOUR CREDENTIALS (Next 3 minutes)

### Step 1: Create Google Cloud Project

**Link:** https://console.cloud.google.com/

1. Click **"Select a Project"** (top left)
2. Click **"New Project"**
3. Name: `Development_Leads`
4. Click **Create**
5. Wait for it to finish...

### Step 2: Enable APIs

1. Search for **"Sheets API"** (search box top)
2. Click on it → Click **Enable**
3. Search for **"Drive API"**
4. Click on it → Click **Enable**

### Step 3: Create Service Account

1. Search for **"Service Accounts"**
2. Click on it
3. Click **"Create Service Account"** (blue button)
4. Fill in:
   - Service account name: `development-leads-bot`
5. Click **"Create and Continue"**
6. Skip the "Grant this service account access" section
7. Click **"Create Key"** (on the next screen)
8. Choose **JSON** type
9. A `.json` file downloads automatically

### Step 4: Save Credentials

**The JSON file just downloaded to your Downloads folder:**

```bash
# Move it to your project
mv ~/Downloads/*.json ~/Desktop/Anil_Project/google_credentials.json

# Add to .gitignore (so you don't commit secrets)
echo "google_credentials.json" >> ~/Desktop/Anil_Project/.gitignore

# Verify it's there
ls ~/Desktop/Anil_Project/google_credentials.json
```

### Step 5: Update .env

```bash
cd ~/Desktop/Anil_Project

# Add this line to .env
echo "GOOGLE_CREDENTIALS_PATH=./google_credentials.json" >> .env

# Verify
cat .env | grep GOOGLE_CREDENTIALS_PATH
# Should show: GOOGLE_CREDENTIALS_PATH=./google_credentials.json
```

---

## ✅ VERIFY CREDENTIALS ARE VALID

```bash
cd /Users/koushikramalingam/Desktop/Anil_Project

# Check the file exists
ls -lh google_credentials.json
# Should show: -rw-r--r-- ... google_credentials.json

# Check it's valid JSON
head -5 google_credentials.json
# Should show something like:
# {
#   "type": "service_account",
#   "project_id": "development-leads-xxx",
#   ...
```

---

## 🔑 SHARE GOOGLE SHEET WITH SERVICE ACCOUNT

The credentials file has a special email address. You need to share a Google Sheet with it.

### Step 1: Get Service Account Email

```bash
# Extract the email from your credentials
grep "client_email" ~/Desktop/Anil_Project/google_credentials.json
# You'll see something like:
# "client_email": "development-leads-bot@development-leads-xxx.iam.gserviceaccount.com",
```

Copy that email address (without the quotes)

### Step 2: Create Google Sheet

1. Go to: https://sheets.google.com
2. Click **"+ New"** → **"Blank spreadsheet"**
3. Name it: **`Development_Leads`** (exact name!)
4. Click on it to open

### Step 3: Share with Service Account

1. Click **"Share"** button (top right)
2. Paste the service account email you copied
3. Choose **"Editor"** from dropdown
4. **Uncheck** "Notify people"
5. Click **"Share"**

Now the bot can access this sheet!

---

## ✅ TEST AGAIN

Now try the authentication test again:

```bash
cd /Users/koushikramalingam/Desktop/Anil_Project
source .venv/bin/activate

python << 'EOF'
from app.integrations.google_sheets_uploader import GoogleSheetsUploader
u = GoogleSheetsUploader()
print("✅ Google Sheets connected successfully!")
EOF
```

**Expected output:**
```
✅ Google Sheets connected successfully!
```

---

## 🎯 IF YOU GET AN ERROR

### Error: "FileNotFoundError: google_credentials.json"
**Solution:**
- Did you move the file to project root? Check: `ls google_credentials.json`
- Is it the right file? Should be JSON downloaded from Google Cloud

### Error: "Failed to authenticate"
**Solution:**
- Is the JSON valid? Check: `cat google_credentials.json | head -1` (should show `{`)
- Did you share the Google Sheet with the service account email?
- Check the email is correct in the credentials file

### Error: "SpreadsheetNotFound"
**Solution:**
- Create the sheet manually: https://sheets.google.com
- Name it exactly: **`Development_Leads`**
- Share it with the service account email

---

## 🚀 NEXT: RUN THE PIPELINE

Once the auth test passes (✅):

```bash
python -m app.dev_pipeline

# Wait ~90 seconds for completion
# You should see: "✓ Google Sheets upload successful"
```

Then:
1. Open: https://sheets.google.com
2. Find: "Development_Leads" sheet
3. See: 25-30 properties sorted by development_score
4. Confirm: Filter buttons on headers, header row frozen

---

## 📋 FULL SETUP CHECKLIST

- [ ] Credentials JSON downloaded from Google Cloud
- [ ] File moved to project root: `google_credentials.json`
- [ ] File added to `.gitignore`
- [ ] `.env` updated with `GOOGLE_CREDENTIALS_PATH`
- [ ] Service account email extracted
- [ ] Google Sheet "Development_Leads" created
- [ ] Sheet shared with service account email
- [ ] Auth test passes: `✅ Google Sheets connected successfully!`
- [ ] Pipeline runs: `python -m app.dev_pipeline`
- [ ] Google Sheet has listings
- [ ] Listings sorted by development_score
- [ ] CSV file created: `data/classified_listings.csv`

**When all checked:** Task 1 complete! ✅

---

## 💡 QUICK REFERENCE

**Get credentials:** https://console.cloud.google.com/
**Create sheet:** https://sheets.google.com/
**Test auth:** `python << 'EOF'` (see code above)
**Run pipeline:** `python -m app.dev_pipeline`
**Check results:** https://sheets.google.com (refresh)

---

**Status:** Ready for credentials setup ✅
