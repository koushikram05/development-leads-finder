# Task 2 Email Alert - Which Email Gets the Notification? 📧

## 🎯 Quick Answer

**The email notification goes to: `SENDER_EMAIL` from your `.env` file**

```
.env file contains:
    SENDER_EMAIL=your_email@gmail.com  ← Notification comes HERE
```

---

## 📊 Complete Email Flow

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Pipeline Runs & Finds Properties                     │
│                                                               │
│ python -m app.dev_pipeline                                   │
│   ↓                                                           │
│ Finds 25 properties                                          │
│   ↓                                                           │
│ Scores them (0-100)                                          │
│   ↓                                                           │
│ Filters: development_score >= 70  ✓ High-Value              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Stage 5 - Alert Manager Checks                      │
│                                                               │
│ high_value = [properties with score >= 70]                  │
│                                                               │
│ if high_value:  # 12 properties found                        │
│     alert_manager.alert_on_opportunities(                    │
│         opportunities=high_value,                            │
│         recipient_email=None,  ← Use SENDER_EMAIL            │
│         run_type="manual"                                    │
│     )                                                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: AlertManager._send_email_alert()                    │
│                                                               │
│ recipient = recipient_email or self.sender_email             │
│            (None given, so use SENDER_EMAIL)                │
│                                                               │
│ sender_email:   "your_email@gmail.com"   (from .env)        │
│ recipient_email: "your_email@gmail.com"  (same)             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Send Email via Gmail SMTP                           │
│                                                               │
│ 1. Connect to smtp.gmail.com:587                            │
│ 2. Login with SENDER_EMAIL & SENDER_PASSWORD                │
│ 3. Create beautiful HTML email                              │
│ 4. Send TO: your_email@gmail.com                            │
│                                                               │
│ Result: ✓ Email arrives in inbox!                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration Steps

### Step 1: Set Your Email in `.env`

```bash
# Open your .env file and set:
SENDER_EMAIL=your_email@gmail.com        # Email that RECEIVES notifications
SENDER_PASSWORD=your_app_password        # Gmail app password (16 chars)
SMTP_SERVER=smtp.gmail.com               # Gmail SMTP server
SMTP_PORT=587                            # Standard SMTP port
```

### Step 2: Get Gmail App Password

**Why not just use your password?**
- Gmail blocks regular passwords for security
- You need an "App Password" instead

**How to get App Password:**

1. Go to: https://myaccount.google.com/security
2. Enable 2-Step Verification (if not already enabled)
3. Go back to Security tab
4. Find "App passwords" (appears only after 2FA enabled)
5. Select: App = Mail, Device = Windows/Mac/Linux
6. Google generates a 16-character password
7. Copy and paste into `.env` as `SENDER_PASSWORD`

**Example .env:**
```
SENDER_EMAIL=john.smith@gmail.com
SENDER_PASSWORD=abcd efgh ijkl mnop
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

---

## 📧 What Email Do You Receive?

### Email Subject
```
🏠 12 New Development Opportunities Found!
```

### Email Content

#### Beautiful HTML With:

1. **Header Section**
   ```
   Development Leads Found
   ─────────────────────
   Found 12 properties with development potential
   Run Type: Manual Scan
   Time: 2025-01-02 10:30 AM
   ```

2. **Summary Section**
   ```
   📊 Summary
   ─────────────────────
   Total Found: 12
   Average Score: 82.3/100
   Profit Potential: $2,500,000+
   ```

3. **Top 5 Properties with Details**
   ```
   1. 🔴 EXCELLENT - 123 Main St, Newton, MA
      Score: 88.5/100
      Price: $750,000
      Lot Size: 12,000 sqft
      Est. Profit: $250,000
      ➜ View in Google Sheets
   
   2. 🟠 GOOD - 456 Oak Ave, Newton, MA
      Score: 72.3/100
      Price: $650,000
      Lot Size: 8,500 sqft
      Est. Profit: $180,000
      ➜ View in Google Sheets
   
   (More properties...)
   ```

4. **Action Links**
   - "View All in Google Sheets" button
   - "Send Email" button (for Slack users)

5. **Footer**
   ```
   Development Leads Finder | Automated Property Analysis
   Generated: 2025-01-02 10:30:55 AM
   ```

---

## 💬 Email to Slack Mapping

| Receiving Channel | Email | Slack |
|-------------------|-------|-------|
| **Destination** | `SENDER_EMAIL` | `SLACK_WEBHOOK_URL` |
| **Message Format** | Beautiful HTML | Slack Blocks (interactive) |
| **Properties Shown** | Top 10 | Top 5 |
| **Includes** | Reasoning, Details | Quick Summary |

---

## 🔑 Key Code Points

### Where recipient email is set (in `app/dev_pipeline.py`):

```python
# Stage 5: Sending Alerts
alert_manager = AlertManager(email_enabled=True, slack_enabled=True)

alert_results = alert_manager.alert_on_opportunities(
    opportunities=high_value,
    recipient_email=None,        # ← No specific recipient
    run_type="manual"
)
```

### How it resolves (in `alert_manager.py`):

```python
def alert_on_opportunities(self, opportunities, recipient_email=None, run_type="manual"):
    # ...
    if self.email_enabled:
        recipient = recipient_email or self.sender_email  # ← Uses SENDER_EMAIL
        results['email'] = self._send_email_alert(high_value, recipient, run_type)
```

So if `recipient_email=None`, it uses `SENDER_EMAIL` from `.env`

---

## ✅ Quick Check: Will I Get the Email?

**YES ✓** if:
1. ✅ `SENDER_EMAIL` is set in `.env` (your Gmail address)
2. ✅ `SENDER_PASSWORD` is set (Gmail app password)
3. ✅ Pipeline finds properties with score >= 70
4. ✅ Email alerts are enabled (default: True)

**NO ✗** if:
- ❌ Email config missing/empty in `.env`
- ❌ All properties score below 70
- ❌ Pipeline encounters an error

---

## 🧪 Test Email Sending

To test without running full pipeline:

```bash
python test_alerts.py
```

This will:
1. Check if `.env` is configured correctly
2. Send a test email to `SENDER_EMAIL`
3. Send a test Slack message (if configured)
4. Show success/failure for each

---

## 📋 Checklist Before First Run

- [ ] Gmail 2FA enabled
- [ ] App Password generated (16 characters)
- [ ] `SENDER_EMAIL=your_email@gmail.com` in `.env`
- [ ] `SENDER_PASSWORD=your_16_char_password` in `.env`
- [ ] `.env` file exists (copied from `.env.example`)
- [ ] `.env` is in `.gitignore` (not committed)

**Then run:**
```bash
python -m app.dev_pipeline
```

**Result:** You'll receive an email when high-value properties found! ✓

---

## ❓ FAQ

**Q: Can I send to a DIFFERENT email?**

A: Yes! Modify `app/dev_pipeline.py` Stage 5:

```python
alert_results = alert_manager.alert_on_opportunities(
    opportunities=high_value,
    recipient_email="different_email@gmail.com",  # ← Change this
    run_type="manual"
)
```

But `SENDER_EMAIL` must still be your Gmail account (to authenticate with Gmail SMTP).

---

**Q: Will the email come from `SENDER_EMAIL`?**

A: Yes. The email "From:" field is `SENDER_EMAIL`. That's your Gmail account.

---

**Q: Can I send to multiple emails?**

A: Currently no. But you can:
1. Set up a Gmail group and use group email as `SENDER_EMAIL`
2. Or manually forward the emails to others
3. Or share the Google Sheet instead

---

**Q: What if I don't want email?**

A: In `app/dev_pipeline.py` Stage 5, change:

```python
alert_manager = AlertManager(email_enabled=False, slack_enabled=True)  # Email off
```

---

## Summary

```
Your email (SENDER_EMAIL in .env)
    ↓
Gmail SMTP Server
    ↓
Receives notification when:
    - Pipeline runs
    - AND finds properties with score >= 70
    - AND Stage 5 sends alerts
    ↓
Beautiful HTML email in your inbox!
```

**TLDR: Email goes to whatever you set as `SENDER_EMAIL` in `.env`** 📧
