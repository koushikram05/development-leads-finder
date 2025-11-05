# 🚀 SCHEDULER ACTIVATION - COMPLETE GUIDE

**Status:** ✅ **SCHEDULER NOW ACTIVATED**  
**Activation Time:** October 25, 2025 12:25:57  
**Daily Run Time:** 9:00 AM (Customizable)

---

## ✅ ACTIVATION CONFIRMATION

```
✅ SCHEDULER ACTIVATED SUCCESSFULLY!
====================================
📅 Scheduled for: Daily at 09:00
⏱️  Current time: 12:25:57
📊 Execution log: data/pipeline_execution_log.txt

📋 Active Scheduled Jobs:
   - daily_development_leads: Daily pipeline run at 09:00
   
✨ Scheduler is now running in the background...
```

---

## 📊 WHAT'S NOW AUTOMATED

Your pipeline will **automatically run EVERY DAY at 9:00 AM** with:

| Stage | Component | Auto-Enabled |
|-------|-----------|--------------|
| 1️⃣ | Data Collection (SerpAPI) | ✅ Yes |
| 2️⃣ | Enrichment (GIS, Geocoding) | ✅ Yes |
| 3️⃣ | Classification (GPT-4 LLM) | ✅ Yes |
| 4️⃣ | ROI Scoring (Financial) | ✅ Yes |
| 5️⃣ | Export (CSV, JSON) | ✅ Yes |
| 6️⃣ | Google Sheets Sync | ✅ Yes |
| 7️⃣ | Email/Slack Alerts | ✅ Yes |
| 8️⃣ | Database Storage | ✅ Yes |

---

## 📁 SCHEDULER ACTIVATION FILES

### 1. **Activation Script** (Just Used)
**File:** `activate_scheduler.py`
```python
# Starts scheduler in background for current session
# Usage:
python activate_scheduler.py --hour 9 --minute 0
```

**Status:** ✅ Currently running (PID: 75692)

### 2. **Cron Job Setup** (Optional for permanent automation)
**File:** `setup_cron_scheduler.sh`
```bash
# Interactive setup for permanent system-level scheduling
# Usage:
chmod +x setup_cron_scheduler.sh
./setup_cron_scheduler.sh
```

**Features:**
- Persistent across system reboots
- System-level scheduling (cron)
- Multiple time options
- Automatic logging

---

## 🔄 HOW TO MANAGE THE SCHEDULER

### **View Active Jobs**
```python
python -c "
from app.scheduler import PipelineScheduler
scheduler = PipelineScheduler()
scheduler.list_jobs()
"
```

### **Change Execution Time**

**Option A: Restart with New Time**
```bash
# Stop the current scheduler (see below)
# Then run with new time:
python activate_scheduler.py --hour 6 --minute 0  # 6 AM

python activate_scheduler.py --hour 14 --minute 30  # 2:30 PM

python activate_scheduler.py --hour 18 --minute 0  # 6 PM
```

**Option B: Modify Cron Job** (Linux/Mac)
```bash
# Edit cron jobs
crontab -e

# Find the line with dev_pipeline and modify the time:
# Format: minute hour * * * command
# Examples:
0 6 * * * /path/to/dev_pipeline    # 6 AM
30 8 * * * /path/to/dev_pipeline   # 8:30 AM
0 17 * * * /path/to/dev_pipeline   # 5 PM
```

### **Stop the Scheduler**
```bash
# Kill the running process
pkill -f "activate_scheduler.py"

# Or from Python:
python -c "
from app.scheduler import PipelineScheduler
scheduler = PipelineScheduler()
scheduler.stop()
"
```

### **View Execution Log**
```bash
# See all pipeline runs
cat data/pipeline_execution_log.txt

# See last 10 runs
tail -10 data/pipeline_execution_log.txt

# Follow live execution log
tail -f data/pipeline_execution_log.txt
```

### **Check Cron Jobs** (Linux/Mac)
```bash
# List all cron jobs
crontab -l

# View logs (macOS)
log stream --predicate 'process == "cron"' --level debug

# View logs (Linux)
grep CRON /var/log/syslog
```

---

## 📋 EXECUTION LOG TRACKING

**File:** `data/pipeline_execution_log.txt`

Each execution is logged with:
- **Timestamp:** ISO format (YYYY-MM-DDTHH:MM:SS.ffffff)
- **Trigger Type:** MANUAL or SCHEDULED
- **Status:** SUCCESS or FAILED (with error message)

**Example Log:**
```
2025-10-25T09:00:00.123456 | SCHEDULED | SUCCESS
2025-10-25T10:00:00.234567 | MANUAL | SUCCESS
2025-10-25T11:00:00.345678 | SCHEDULED | FAILED: Connection timeout
```

---

## 🎯 COMMON SCENARIOS

### **Scenario 1: Schedule for Early Morning (6 AM)**
```bash
python activate_scheduler.py --hour 6 --minute 0
# or via cron:
crontab -e
# Add: 0 6 * * * cd /path/to/project && python -m app.dev_pipeline
```

### **Scenario 2: Schedule for Business Hours (10 AM)**
```bash
python activate_scheduler.py --hour 10 --minute 0
```

### **Scenario 3: Schedule for End of Day (5 PM)**
```bash
python activate_scheduler.py --hour 17 --minute 0
```

### **Scenario 4: Schedule Multiple Times Per Day**
```bash
# Not built-in, but you can add multiple cron jobs:
crontab -e
# Add multiple lines:
0 6 * * * cd /path && python -m app.dev_pipeline    # 6 AM
0 12 * * * cd /path && python -m app.dev_pipeline   # 12 PM
0 18 * * * cd /path && python -m app.dev_pipeline   # 6 PM
```

---

## 🔧 TROUBLESHOOTING

### **Problem: Scheduler not starting**
```bash
# Check if virtual environment is active
which python

# Should show: /Users/.../Desktop/Anil_Project/.venv/bin/python

# If not, activate manually:
source /Users/koushikramalingam/Desktop/Anil_Project/.venv/bin/activate
```

### **Problem: ModuleNotFoundError**
```bash
# Install missing dependencies
cd /Users/koushikramalingam/Desktop/Anil_Project
.venv/bin/pip install -r requirements.txt
```

### **Problem: Scheduler runs but pipeline fails**
```bash
# Check execution log
cat data/pipeline_execution_log.txt

# Run manually to see detailed error
.venv/bin/python -m app.dev_pipeline

# Check API keys are set
echo $SERPAPI_KEY
echo $OPENAI_API_KEY
```

### **Problem: Cron job not running**

**macOS/Linux:**
```bash
# Check if cron daemon is running
sudo launchctl list | grep cron  # macOS
ps aux | grep cron              # Linux

# Check cron logs
log stream --predicate 'process == "cron"' --level debug  # macOS
tail -f /var/log/cron                                     # Linux

# Re-add cron job
crontab -e
# Then add: 0 9 * * * cd /path && /path/.venv/bin/python -m app.dev_pipeline
```

---

## 📞 SUPPORT & DOCUMENTATION

**Related Files:**
- 📄 `TECHNICAL_DETAILS_FAQ.md` - Scheduler configuration details
- 📄 `REQUIREMENTS_COMPLIANCE_FULL_ANALYSIS.md` - Compliance verification
- 📄 `PROJECT_COMPLETE_ALL_TASKS.md` - Project overview
- 📁 `app/scheduler.py` - Source code
- 📁 `app/dev_pipeline.py` - Pipeline logic

**Commands Reference:**
```bash
# Activate scheduler
python activate_scheduler.py

# Setup persistent cron
./setup_cron_scheduler.sh

# View execution history
tail -f data/pipeline_execution_log.txt

# List scheduled jobs
crontab -l

# Edit scheduled jobs
crontab -e

# Stop scheduler
pkill -f "activate_scheduler.py"

# Manual pipeline run
python -m app.dev_pipeline
```

---

## 🎉 WHAT'S NEXT

1. ✅ **Scheduler Active** - Running daily at 9 AM
2. 🔄 **Wait for First Run** - 9 AM tomorrow (Oct 26, 2025)
3. 📊 **Check Execution Log** - `data/pipeline_execution_log.txt`
4. 📧 **Monitor Alerts** - Email & Slack notifications daily
5. 📈 **Review Results** - Google Sheets updated automatically

---

**Activation Status:** ✅ **COMPLETE**  
**Next Run:** October 26, 2025 at 09:00 AM  
**Last Updated:** October 25, 2025 12:25:57 UTC

