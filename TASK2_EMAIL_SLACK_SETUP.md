# 📧 Task 2: Email/Slack Alerts - Complete Setup Guide

## ✨ **What You Get**

Automatic **email and Slack notifications** when high-value development properties are found:

✅ **Email alerts** with beautiful HTML formatting
✅ **Slack messages** with interactive buttons  
✅ **Automatic triggering** on pipeline run (daily, weekly, or manual)
✅ **Customizable threshold** (default: score ≥ 70)
✅ **Property summaries** with scores, addresses, and explanations
✅ **Pipeline execution reports** after each run

---

## 🚀 **Quick Setup (10 minutes)**

### **Step 1: Gmail Configuration (for Email)**

1. **Enable 2-Factor Authentication** on your Google account:
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Create App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Google generates a 16-character password
   - Copy this password

3. **Update `.env` file**:
   ```
   SENDER_EMAIL=your_gmail@gmail.com
   SENDER_PASSWORD=xxxxxxxx xxxx xxxx  # 16-character app password
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   ```

### **Step 2: Slack Configuration (for Slack)**

1. **Create Slack Webhook**:
   - Go to https://api.slack.com/messaging/webhooks
   - Click "Create New App" or select existing workspace
   - Enable "Incoming Webhooks"
   - Click "Add New Webhook to Workspace"
   - Select channel (e.g., #development-leads)
   - Authorize

2. **Copy Webhook URL**:
   - It looks like: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX`
   - Paste into `.env`:
   ```
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
   ```

3. **Test Webhook** (optional):
   ```bash
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Test message"}' \
     YOUR_WEBHOOK_URL
   ```

---

## 📋 **How It Works**

### **Automatic Triggering**

```
Pipeline runs (daily/weekly/manual)
         ↓
Classifies all properties  
         ↓
Filters for score >= 70
         ↓
Found high-value properties?
         ├─ YES → Send Email + Slack
         └─ NO → Skip alerts
```

### **Email Alert Format**

- 📧 Subject: "🏠 N New Development Opportunities Found!"
- 📊 Summary section with statistics
- 🏘️ Top 10 properties with details
- 🔗 Link to Google Sheets
- ⏰ Timestamp and run type

### **Slack Alert Format**

- 🔴 Color-coded by score (Red=Excellent, Orange=Good)
- 📍 Property address, score, and explanation
- 🎯 Top 5 properties from this run
- 🔘 Action buttons to Google Sheets
- ✅ Pipeline execution summary after each run

---

## 🧪 **Test the Alerts**

### **Test Email Alert**

```python
from app.integrations.alert_manager import AlertManager

# Create sample opportunities
test_opps = [
    {
        'address': '123 Main St, Newton, MA',
        'development_score': '85.5',
        'label': 'development',
        'explanation': 'Large lot with development potential',
        'price': '500000'
    }
]

# Send test alert
alert = AlertManager(email_enabled=True, slack_enabled=False)
results = alert.alert_on_opportunities(
    opportunities=test_opps,
    recipient_email='your_email@gmail.com',
    run_type='manual'
)

print(f"Email sent: {results['email']}")
```

### **Test Slack Alert**

```python
from app.integrations.alert_manager import AlertManager

test_opps = [...]  # Same as above

alert = AlertManager(email_enabled=False, slack_enabled=True)
results = alert.alert_on_opportunities(
    opportunities=test_opps,
    run_type='manual'
)

print(f"Slack sent: {results['slack']}")
```

---

## 🔧 **Pipeline Integration**

The alerts are **automatically triggered** after each pipeline run:

```bash
python -m app.dev_pipeline
```

This will:
1. ✅ Collect listings
2. ✅ Classify properties  
3. ✅ Upload to Google Sheets
4. ✅ **Send alerts for score >= 70** ← NEW!

### **Disable Alerts (Optional)**

Edit `dev_pipeline.py` line 180:
```python
alert_manager = AlertManager(email_enabled=False, slack_enabled=False)
```

### **Change Score Threshold**

Edit `alert_manager.py` line 51:
```python
self.score_threshold = 80.0  # Change from 70.0 to 80.0
```

---

## 📊 **Alert Examples**

### **Email Alert Preview**

```
TO: your_email@gmail.com
SUBJECT: 🏠 3 New Development Opportunities Found!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏠 NEW DEVELOPMENT OPPORTUNITIES
Manual Scan - 2025-10-24 17:12:00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SUMMARY
• Found 3 high-value properties (Score ≥ 70)
• Top Score: 92.5/100
• Location: Newton, MA Area

TOP OPPORTUNITIES

1. 42 Lindbergh Ave, Newton, MA 02465
   Score: 92.5/100 | Label: development
   Prime opportunity for those seeking a teardown project...
   Price: $500,000

2. 371 Cherry St, Newton, MA 02465
   Score: 78.0/100 | Label: potential
   Good development potential with large lot...
   Price: $450,000

...

[VIEW FULL LIST IN GOOGLE SHEETS]
```

### **Slack Alert Preview**

```
────────────────────────────────────────────────────
🏠 New Development Opportunities Found!
────────────────────────────────────────────────────

Manual Scan Results — 2025-10-24 17:12:00
3 high-value properties with score ≥ 70

────────────────────────────────────────────────────

🔴 1. 42 Lindbergh Ave, Newton, MA 02465
Score: 92.5/100 | Label: development
Prime opportunity for those seeking a teardown project...

🟠 2. 371 Cherry St, Newton, MA 02465
Score: 78.0/100 | Label: potential
Good development potential...

...

[📊 View in Google Sheets] [📧 Email Details]
```

---

## 🐛 **Troubleshooting**

### **Email not sending?**

1. Check `.env` has `SENDER_EMAIL` and `SENDER_PASSWORD`
2. Verify Gmail 2FA and App Password are set up correctly
3. Check firewall isn't blocking SMTP port 587
4. Test with: `python test_email_alert.py`

### **Slack not posting?**

1. Verify `SLACK_WEBHOOK_URL` is correct
2. Check Slack workspace permissions
3. Test webhook: `curl -X POST ... YOUR_WEBHOOK_URL`
4. Check logs: `tail -f data/logs/*.log`

### **Getting "No opportunities to alert on"?**

- This is normal! Means no properties scored >= 70
- Change threshold in `alert_manager.py`
- Or check if classified data is being generated

---

## 📈 **Next Steps**

After Task 2 is complete:

✅ **Task 2: Email/Slack Alerts** - DONE  
→ **Task 3: Historical Database** - Store all leads forever  
→ **Task 4: Map Visualization** - See properties on interactive maps  
→ **Task 5: ROI Scoring** - Calculate profit potential  
→ **Fine-tune Model** - Improve accuracy with history

---

## 🚀 **Ready to Test?**

1. Update `.env` with email and Slack configs
2. Run: `python -m app.dev_pipeline`
3. Watch for alerts in your email and Slack! 📧💬

**Questions?** Check the code in `app/integrations/alert_manager.py` 🔍
