# Task 2 Enhanced - Three-Notification Email System 📧

## Overview

Your email notification system now sends **3 different types** of alerts:

1. **🔄 Scan Started** - Notification when scan begins
2. **ℹ️ Scan Completed** - Summary when scan completes (no new high-value found)
3. **🏠 High-Value Found** - Full detailed alert with properties (score >= 70)

---

## How It Works

```
You Run Pipeline
      ↓
NOTIFICATION 1️⃣ : "🔄 Scan Started"
      ↓
Pipeline searches (Stage 1-3)
      ↓
Stage 5: Alerts Check
      ├─ Found High-Value (score >= 70)?
      │   YES → NOTIFICATION 3️⃣ : "🏠 High-Value Found" (Full Details)
      │   NO  → NOTIFICATION 2️⃣ : "ℹ️ Scan Completed" (Summary)
      ↓
Stage 6: Database saves everything
      ↓
Done! ✅
```

---

## Notification 1️⃣: Scan Started

### When It Sends
- **Immediately** when you run: `python -m app.dev_pipeline`
- For manual, daily, or weekly scans

### Email You Receive

**Subject:** 🔄 Manual Scan Started

```
┌─────────────────────────────────────────┐
│   🔄 Scan Started                        │
│                                          │
│   Manual scan has been initiated.        │
│                                          │
│   Time: 2025-01-02 10:30:00             │
│   Type: Manual Scan                     │
│   Status: ⏳ In Progress                 │
│                                          │
│   You'll receive a follow-up email      │
│   when the scan completes with results. │
└─────────────────────────────────────────┘
```

### Slack Notification
```
🔄 Manual Scan Started
2025-01-02 10:30:00
```

**Purpose:** Let you know scan has started processing

---

## Notification 2️⃣: Scan Completed (No High-Value Found)

### When It Sends
- After pipeline completes (Stage 5)
- **Only if NO high-value properties found** (score < 70)
- Includes scan summary

### Email You Receive

**Subject:** ℹ️ Manual Scan Complete

```
┌────────────────────────────────────────────────┐
│  ℹ️ Scan Complete                             │
│                                                │
│  No new high-value properties found           │
│                                                │
│  ┌──────────────────────────────────────────┐│
│  │ Total Properties Found:        25        ││
│  │ Development Opportunities:     8         ││
│  │ High-Value (Score ≥ 70):      0         ││
│  └──────────────────────────────────────────┘│
│                                                │
│  Scan Details:                                │
│  Time: 2025-01-02 10:35:22                   │
│  Type: Manual Scan                           │
└────────────────────────────────────────────────┘
```

### Slack Notification
```
⚪ No New High-Value Found
Manual Scan Complete

Total Found: 25
Opportunities: 8
High-Value (≥70): 0
Time: 2025-01-02 10:35:22
```

**Purpose:** Confirm scan ran, show summary (even if no high-value found)

---

## Notification 3️⃣: High-Value Found (Full Details)

### When It Sends
- After pipeline completes (Stage 5)
- **Only if high-value properties found** (score >= 70)
- Includes full details of top properties

### Email You Receive

**Subject:** 🏠 12 New Development Opportunities Found!

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  🏠 DEVELOPMENT LEADS FOUND                             │
│  ────────────────────────────────────────────────────   │
│  Found 12 properties with development potential          │
│                                                          │
│  📊 Summary                                             │
│  ────────────────────────────────────────────────────   │
│  • Total Found: 12                                      │
│  • Average Score: 82.3/100                             │
│  • Profit Potential: $2,500,000+                       │
│                                                          │
│  🏆 Top Properties:                                    │
│                                                          │
│  1. 🔴 EXCELLENT - 123 Main St, Newton, MA             │
│     Score: 88.5/100 | Label: excellent                │
│     Price: $750,000 | Lot: 12,000 sqft                │
│     Est. Profit: $250,000                              │
│     ➜ View in Google Sheets                            │
│                                                          │
│  2. 🟠 GOOD - 456 Oak Ave, Newton, MA                  │
│     Score: 72.3/100 | Label: good                     │
│     Price: $650,000 | Lot: 8,500 sqft                 │
│     Est. Profit: $180,000                              │
│     ➜ View in Google Sheets                            │
│                                                          │
│  (More properties...)                                   │
│                                                          │
│  ⭐ High-value opportunities found!                    │
│  Check your Google Sheets for detailed listings.       │
│                                                          │
│  [View All in Google Sheets]                           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Slack Notification
```
🟢 High-Value Found!
Manual Scan Complete

Total Found: 25
Opportunities: 12
High-Value (≥70): 12
Time: 2025-01-02 10:40:00

Top Property: 123 Main St - 88.5/100
```

**Purpose:** Alert you immediately to high-value opportunities with full details

---

## Complete Email Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│  Stage 0: Scan Initialization                       │
│  ✉️ NOTIFICATION 1️⃣: "Scan Started"                 │
│  "Your scan has been initiated"                      │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Stages 1-4: Collection, Enrichment,                │
│  Classification, Google Sheets                       │
│  (No emails sent during these stages)               │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Stage 5: Alerts & Notifications                    │
│                                                      │
│  Check: High-Value Properties (score >= 70)?        │
│  ├─ YES (e.g., 12 found)                           │
│  │   ✉️ NOTIFICATION 3️⃣: "High-Value Found"         │
│  │   Full HTML with property details                │
│  │   (Beautiful formatting, links to Sheets)        │
│  │                                                  │
│  └─ NO (e.g., 0 found)                             │
│      ✉️ NOTIFICATION 2️⃣: "Scan Completed"          │
│      Summary table with scan results                │
│      (Small, informational)                         │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Stage 6: Database                                  │
│  (Data saved to SQLite)                             │
└─────────────────────────────────────────────────────┘
```

---

## Example: A Complete Scan

### **10:00 AM** - You Run Pipeline
```bash
python -m app.dev_pipeline
```

### **10:00 AM** ✉️ Email #1 Arrives
```
Subject: 🔄 Manual Scan Started
From: koushik.ram05@gmail.com
To: koushik.ram05@gmail.com

Your scan has been initiated and is processing...
```

**✅ You know scan is running**

---

### **10:05 AM** - Pipeline Finishes
- Searched 50 properties
- Found 12 development opportunities
- **Found 3 with score >= 70** ✨

### **10:05 AM** ✉️ Email #2 Arrives
```
Subject: 🏠 3 New Development Opportunities Found!
From: koushik.ram05@gmail.com
To: koushik.ram05@gmail.com

🏠 DEVELOPMENT LEADS FOUND

Found 3 properties with development potential

📊 Summary
• Total Found: 3
• Average Score: 82.0/100
• Profit Potential: $600,000+

🏆 Top Properties:
1. 🔴 EXCELLENT - 123 Main St
   Score: 88.5/100
   ...
```

**✅ You immediately see high-value opportunities**

---

### **Alternate Scenario: No High-Value Found**

### **10:05 AM** - Pipeline Finishes
- Searched 50 properties
- Found 8 development opportunities
- **Found 0 with score >= 70**

### **10:05 AM** ✉️ Email #2 Arrives (Different)
```
Subject: ℹ️ Manual Scan Complete
From: koushik.ram05@gmail.com
To: koushik.ram05@gmail.com

ℹ️ Scan Complete

No new high-value properties found

┌──────────────────────────────────────┐
│ Total Properties Found:        50    │
│ Development Opportunities:     8     │
│ High-Value (Score ≥ 70):      0     │
└──────────────────────────────────────┘
```

**✅ You know scan completed but no high-value found**

---

## Configuration

All 3 notifications use the same `.env` settings:

```bash
SENDER_EMAIL=koushik.ram05@gmail.com
SENDER_PASSWORD=ckzq tnax bine ryhd
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**To disable all notifications:**
```python
# In app/dev_pipeline.py, around line 68:
alert_manager = AlertManager(email_enabled=False, slack_enabled=True)
```

**To disable only specific notification types:**
Currently all three send if email_enabled=True. You can customize by editing the pipeline.

---

## API Usage

### Send Notification 1️⃣: Scan Started
```python
from app.integrations.alert_manager import AlertManager

alert_manager = AlertManager(email_enabled=True, slack_enabled=True)

# Notify scan has started
alert_manager.notify_scan_started(run_type="manual")
```

### Send Notification 2️⃣: Scan Completed
```python
alert_manager.notify_scan_completed(
    total_found=50,
    opportunities_found=8,
    high_value_found=0,
    run_type="manual"
)
```

### Send Notification 3️⃣: High-Value Found
```python
high_value_properties = [...]  # Properties with score >= 70

alert_manager.alert_on_opportunities(
    opportunities=high_value_properties,
    recipient_email=None,  # Uses SENDER_EMAIL
    run_type="manual"
)
```

---

## Timing

| Notification | When | Duration |
|--------------|------|----------|
| 1️⃣ Scan Started | Immediately (Stage 0) | < 1 second |
| Pipeline Processing | Stages 1-4 | ~90 seconds |
| 2️⃣ or 3️⃣ Alert | Stage 5 | < 2 seconds |
| Database Save | Stage 6 | < 1 second |

**Total Pipeline Time:** ~90-95 seconds

**You get:**
- Email #1 at 0 seconds (start)
- Email #2 or #3 at 90 seconds (completion)

---

## Troubleshooting

### Not receiving emails?

**Check 1:** Are you receiving Notification 1️⃣ (Scan Started)?
- If YES → Email works, check why Notification 2/3 not sending
- If NO → Email configuration issue

**Check 2:** Run test:
```bash
python test_alerts.py
```

**Check 3:** View logs:
```bash
tail -f data/logs/pipeline_*.log | grep -i "email\|alert"
```

### Getting too many emails?

**Reduce frequency:**
- Change from daily to weekly scans in scheduler
- Or disable notifications by setting `email_enabled=False`

### Want to customize which properties trigger alerts?

Edit in `app/dev_pipeline.py` Stage 5:
```python
# Change score threshold from 70 to 80:
high_value = [l for l in classified_listings 
              if float(l.get('development_score', 0)) >= 80.0]
```

---

## Next Steps

1. ✅ Run pipeline to test all 3 notifications
2. ✅ Check emails arrive at your Gmail
3. ✅ Review timing and content
4. ⏭️ Set up scheduler for daily/weekly runs (Optional)
5. ⏭️ Move to Task 4: Map Visualization

---

## Summary

**Three Notifications = Complete Visibility:**

| Type | Purpose | Content |
|------|---------|---------|
| 1️⃣ Scan Started | Confirm start | Quick status |
| 2️⃣ Scan Completed | Summary (no finds) | Statistics |
| 3️⃣ High-Value Found | Alert (new opportunities) | Full details |

You're always informed at every stage! 📧✅
