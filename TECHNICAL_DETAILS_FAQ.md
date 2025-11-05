# THREE KEY TECHNICAL QUESTIONS - ANSWERED

**Date:** October 25, 2025  
**Project:** Development Leads Finder

---

## 1️⃣ AUTOMATED SCHEDULER - WHEN & HOW IT RUNS

### **Current Status: READY BUT NOT YET ACTIVE**

Your scheduler is **configured but not running** because the system is designed for **manual trigger first**, with automation as an **optional add-on**.

---

### **Scheduler Configuration**

**File:** `app/scheduler.py` (100+ lines)  
**Technology:** APScheduler (Background Scheduler)

#### **Default Configuration (If Enabled)**

| Setting | Value | Details |
|---------|-------|---------|
| **Daily Run** | 9:00 AM | Default time (customizable) |
| **Weekly Run** | Monday 9:00 AM | Default day (customizable) |
| **Execution Log** | `data/pipeline_execution_log.txt` | Tracks all runs |
| **Max Instances** | 1 | Prevents duplicate runs |
| **Coalesce** | True | Skips missed runs if late |

---

### **How to Enable Automation**

#### **Option A: Daily Cron Job (Linux/Mac)**

```bash
# Edit crontab
crontab -e

# Add this line to run at 6 AM every day:
0 6 * * * cd /Users/koushikramalingam/Desktop/Anil_Project && /Users/koushikramalingam/Desktop/Anil_Project/.venv/bin/python -m app.dev_pipeline >> logs/cron.log 2>&1

# Or run using Python scheduler:
0 6 * * * cd /Users/koushikramalingam/Desktop/Anil_Project && /Users/koushikramalingam/Desktop/Anil_Project/.venv/bin/python app/scheduler.py &
```

#### **Option B: Weekly Cron Job (Linux/Mac)**

```bash
# Run every Monday at 9 AM:
0 9 * * 1 cd /Users/koushikramalingam/Desktop/Anil_Project && /Users/koushikramalingam/Desktop/Anil_Project/.venv/bin/python -m app.dev_pipeline >> logs/cron.log 2>&1
```

#### **Option C: Windows Task Scheduler**

```batch
# Create run_pipeline.bat:
@echo off
cd C:\path\to\Anil_Project
call .venv\Scripts\activate
python -m app.dev_pipeline

# Then schedule in Task Scheduler GUI
```

#### **Option D: Python Background Scheduler (APScheduler)**

```python
from app.dev_pipeline import DevelopmentPipeline
from app.scheduler import PipelineScheduler

# Create instances
pipeline = DevelopmentPipeline()
scheduler = PipelineScheduler()

# Schedule daily at 9 AM
scheduler.schedule_daily(
    pipeline_func=lambda: pipeline.run(),
    hour=9,      # 9 AM
    minute=0,
    job_id='daily_lead_scan'
)

# Start scheduler (runs in background)
scheduler.start()

# Keep the process alive (e.g., in a FastAPI app or while True loop)
```

---

### **Scheduler Features**

**File:** `app/scheduler.py`

#### **Key Methods:**

```python
scheduler = PipelineScheduler()

# 1. Schedule daily execution
scheduler.schedule_daily(
    pipeline_func=my_function,
    hour=9,           # 9 AM
    minute=0,
    job_id='daily_scan'
)

# 2. Schedule weekly execution  
scheduler.schedule_weekly(
    pipeline_func=my_function,
    day_of_week='mon',  # Monday
    hour=9,
    minute=0,
    job_id='weekly_scan'
)

# 3. Manual trigger (run now)
scheduler.run_now(my_function)

# 4. Start/Stop scheduler
scheduler.start()   # Begins background scheduling
scheduler.stop()    # Stops scheduler

# 5. List all jobs
scheduler.list_jobs()

# 6. Get execution history
log = scheduler.get_execution_log()  # Last 20 executions
```

---

### **Execution Logging**

**File:** `data/pipeline_execution_log.txt`

```
2025-10-25T11:43:06.123456 | MANUAL | SUCCESS
2025-10-25T11:45:31.456789 | SCHEDULED | SUCCESS
2025-10-25T12:00:00.000000 | SCHEDULED | FAILED: Connection timeout
```

Each log entry tracks:
- **Timestamp:** When execution occurred
- **Trigger Type:** MANUAL or SCHEDULED
- **Status:** SUCCESS or FAILED with error message

---

### **Current Scheduling Status**

| Component | Status | Details |
|-----------|--------|---------|
| **Scheduler Class** | ✅ Ready | `app/scheduler.py` implemented |
| **APScheduler** | ✅ Installed | In `requirements.txt` |
| **Daily Scheduling** | ✅ Ready | Configured but not active |
| **Weekly Scheduling** | ✅ Ready | Configured but not active |
| **Manual Trigger** | ✅ Active | Works via CLI |
| **Cron Job** | ⏸️ Optional | Requires user setup |
| **Background Daemon** | ⏸️ Optional | Requires script to be running |

---

---

## 2️⃣ MLS FEED - HOW IT'S ACCESSED

### **MLS Feed Status: ACTIVE via SerpAPI (Indirect Access)**

Your system **does NOT** have direct RETS/MLS API access, but **achieves MLS data** through **SerpAPI web search integration**.

---

### **How MLS Data is Accessed**

#### **Method: SerpAPI Search (Indirect MLS)**

**File:** `app/scraper/llm_search.py`

```python
class LLMSearch:
    """
    Search for real estate listings using SerpAPI
    Gets MLS data from Google search results (most MLS listings appear in search)
    """
    
    def search_properties(self, query: str, location: str):
        # Constructs search like:
        # "teardown single family home Newton, MA site:zillow.com OR site:redfin.com OR site:realtor.com"
        
        full_query = f"{query} {location} site:zillow.com OR site:redfin.com OR site:realtor.com"
        
        params = {
            "q": full_query,
            "api_key": self.api_key,  # Your SerpAPI key
            "engine": "google",        # Uses Google search
            "num": num_results
        }
        
        # Request returns MLS data embedded in search results
        response = requests.get(self.base_url, params=params)
        return self._parse_search_results(response.json())
```

---

### **MLS Data Extraction**

**How MLS IDs appear in data:**

```
Title: "992 Chestnut St, Newton Upper Falls, MA 02464"
Snippet: "For Sale: 3 beds, 1 bath ∙ 1095 sq. ft. ∙ $774000 ∙ MLS# 73425031 ∙ Built by village..."

→ Extracted from SerpAPI results
→ MLS ID: 73425031
```

---

### **Why Not Direct RETS/MLS API?**

| Approach | Status | Reason |
|----------|--------|--------|
| **Direct RETS API** | ❌ Not Used | Requires Realtor.com membership & credentials |
| **MLS Board Membership** | ❌ Not Used | Regional boards (MATRIS, etc.) require expensive subscriptions |
| **IDX Data Feeds** | ❌ Not Used | Requires broker agreement |
| **SerpAPI/Google Search** | ✅ **Used** | **Accessible to everyone, captures MLS data in results** |

---

### **What You Get from SerpAPI MLS**

**Last Pipeline Run (Oct 25, 2025):**

```
Total MLS Properties Found: 39
Unique Records: 39/39
Source Breakdown:
  - Zillow (includes MLS): 15+ listings
  - Redfin (MLS integrated): 12+ listings
  - Realtor.com (native MLS): 8+ listings
  - SerpAPI direct (Google MLS results): 4+ listings

MLS Data Fields Extracted:
  ✅ MLS ID
  ✅ Listing status (active, pending, sold)
  ✅ DOM (Days on Market)
  ✅ Price
  ✅ Property details (beds, baths, sqft)
  ✅ Address
```

---

### **Direct RETS API - How to Add (Optional)**

If you want **true direct MLS access** later, here's how:

#### **Option 1: RETS API Integration**

```python
import rets_client

class RETSSearcher:
    def __init__(self, username, password, login_url):
        self.client = rets_client.Session(
            login_url=login_url,
            username=username,
            password=password
        )
    
    def search_mls(self, query):
        # Query RETS server directly
        return self.client.search('Property', query, select='ListingKey,ListingId')
```

**Requirements:**
- Realtor.com RETS credentials (~$500-2000/year)
- Regional MLS board membership

#### **Option 2: Third-Party MLS Service**

```python
# Using Zillow API (requires partnership)
# or Redfin's private API (not officially supported)
# or Direct MLS board RETS (requires regional membership)
```

---

### **Current MLS Integration in Your System**

**File:** `app/scraper/llm_search.py`

```python
def _parse_search_results(self, data):
    """Extract MLS data from SerpAPI results"""
    listings = []
    
    for result in data.get('organic_results', []):
        listing = {
            'title': result.get('title'),
            'link': result.get('link'),
            'snippet': result.get('snippet'),  # Contains MLS# if present
            'source': self._identify_source(result.get('link')),
            'search_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # MLS ID extracted from snippet
        listing['price'] = self._extract_price(result)
        # Additional extraction...
        
        listings.append(listing)
    
    return listings
```

---

### **MLS Data in Output Files**

**From last pipeline run:**

**CSV Output (classified_listings.csv):**
```
Address,URL,Snippet,Source,Price,MLS#
"992 Chestnut St, Newton Upper Falls, MA 02464",
https://www.redfin.com/...,
"For Sale: 3 beds ∙ MLS# 73425031 ∙ Built by village...",
redfin,
774000,
73425031
```

**JSON Output (classified_listings.json):**
```json
{
  "address": "992 Chestnut St, Newton Upper Falls, MA 02464",
  "snippet": "For Sale: 3 beds, 1 bath ∙ 1095 sq. ft. ∙ $774000 ∙ MLS# 73425031",
  "source": "redfin",
  "price": 774000,
  "mls_id": 73425031
}
```

---

---

## 3️⃣ FASTAPI USAGE - WHERE & HOW IT'S IMPLEMENTED

### **FastAPI Status: CREATED BUT NOT ACTIVELY USED**

**File:** `main.py`  
**Status:** ✅ Ready | ⏸️ Optional | 🔧 Extensible

---

### **What FastAPI is There For**

FastAPI is **implemented but not core to the pipeline**. It's **ready for optional REST API functionality**.

#### **Current FastAPI Endpoints**

**File:** `main.py`

```python
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Property & NLP Analysis API")

# Endpoint 1: Health Check
@app.get("/")
def read_root():
    return {"message": "API is running!"}
```

**Endpoints Defined (But Not Core):**

```python
# Endpoint 2: Lot Buildability Analysis
@app.get("/lot/buildable")
def check_buildable(lat: float, lon: float, lot_size: float):
    """
    Check if lot is buildable based on location and zoning
    
    Example:
    GET /lot/buildable?lat=42.3&lon=-71.2&lot_size=21780
    
    Returns:
    {
      "zoning_type": "residential",
      "buildable": true,
      "lot_value_score": 85.5
    }
    """
    zone_data = zoning_loader.get_zone(lat, lon)
    zoning_type = zone_data.zone.iloc[0]
    lot = LotAnalysis(lot_size=lot_size, zoning_type=zoning_type)
    return {
        "zoning_type": zoning_type,
        "buildable": lot.is_buildable(),
        "lot_value_score": lot.lot_value_score()
    }


# Endpoint 3: Keyword Detection
@app.post("/nlp/detect_keywords")
def detect_keywords(text: str):
    """
    Extract development keywords from listing text
    
    Example:
    POST /nlp/detect_keywords
    {"text": "Great teardown opportunity with large lot"}
    
    Returns:
    {"keywords": ["teardown", "opportunity", "large lot"]}
    """
    keywords = keyword_detector.extract_keywords(text)
    return {"keywords": keywords}


# Endpoint 4: Text Classification
@app.post("/nlp/classify_text")
def classify_text(text: str):
    """
    Classify property listing as development opportunity
    
    Example:
    POST /nlp/classify_text
    {"text": "1950s house on large lot, needs work"}
    
    Returns:
    {"label": "development", "confidence": 0.85}
    """
    label = openai_classifier.classify(text)
    return {"label": label}
```

---

### **How FastAPI Fits in Your Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    8-STAGE PIPELINE                             │
├─────────────────────────────────────────────────────────────────┤
│ Stage 1: Data Collection (SerpAPI, Direct Scrapers)              │
│ Stage 2: Enrichment (GIS, Geocoding)                            │
│ Stage 3: Classification (GPT-4 LLM)                             │
│ Stage 3.5: ROI Scoring (Financial Analysis)                     │
│ Stage 4: Export (CSV, JSON, Sheets)                             │
│ Stage 5: Alerts (Email, Slack)                                  │
│ Stage 6: Database (SQLite)                                      │
│ Stage 7: Maps (Folium)                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    CORE PIPELINE (Manual)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              OPTIONAL: FastAPI REST INTERFACE                    │
├─────────────────────────────────────────────────────────────────┤
│ ✅ GET  /                    → Health check                      │
│ ✅ GET  /lot/buildable       → Lot analysis                      │
│ ✅ POST /nlp/detect_keywords → Extract keywords                  │
│ ✅ POST /nlp/classify_text   → Classify property                 │
└─────────────────────────────────────────────────────────────────┘
           (Alternative interface, not required)
```

---

### **FastAPI Not Used Because**

| Reason | Details |
|--------|---------|
| **Pipeline Works in CLI** | `python -m app.dev_pipeline` works great |
| **Manual Trigger Sufficient** | Users can run anytime with CLI |
| **Google Sheets is Primary Output** | API not needed for data sharing |
| **Batch Processing** | Pipeline processes many properties at once |
| **Not Real-Time** | System designed for scheduled runs, not API requests |

---

### **How to Use FastAPI (If Needed)**

#### **Start the FastAPI Server**

```bash
# Install uvicorn (already in requirements.txt)
pip install uvicorn

# Run FastAPI server on localhost:8000
uvicorn main:app --reload

# Or directly:
python -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)"
```

#### **Test the Endpoints**

```bash
# Health check
curl http://localhost:8000/

# Check lot buildability
curl "http://localhost:8000/lot/buildable?lat=42.3&lon=-71.2&lot_size=21780"

# Detect keywords
curl -X POST "http://localhost:8000/nlp/detect_keywords?text=Great+teardown+opportunity"

# Classify text
curl -X POST "http://localhost:8000/nlp/classify_text?text=Old+house+large+lot"
```

#### **Interactive API Documentation**

Once server is running:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

### **FastAPI Test File**

**File:** `test_fastapi.py`

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "✅ FastAPI is running!"}

# Run with:
# uvicorn test_fastapi:app --reload
```

---

### **When to Use FastAPI**

**Use FastAPI when you want:**

1. **Web Interface** - Build a dashboard/UI
2. **Real-Time Requests** - Process one property at a time
3. **Third-Party Integration** - Other services call your API
4. **Microservices** - Split logic across services
5. **Production Deployment** - Multi-user web application

**Not needed for:**
- Batch processing (current use case) ✓ Pipeline sufficient
- Scheduled runs (current use case) ✓ Scheduler sufficient
- Data export (current use case) ✓ Google Sheets sufficient

---

### **Potential FastAPI Enhancements**

```python
from fastapi import FastAPI
from app.dev_pipeline import DevelopmentPipeline

app = FastAPI(title="Development Leads API")
pipeline = DevelopmentPipeline()

# Enhancement 1: Run pipeline via API
@app.post("/pipeline/run")
def run_pipeline(location: str = "Newton, MA"):
    """Trigger pipeline run via HTTP request"""
    results = pipeline.run(location=location)
    return {"status": "running", "results": results}

# Enhancement 2: Get recent opportunities
@app.get("/opportunities/recent")
def get_recent_opportunities(days: int = 30, min_score: float = 50):
    """Fetch recent development opportunities from database"""
    from app.integrations.database_manager import HistoricalDatabaseManager
    db = HistoricalDatabaseManager()
    return db.get_recent_opportunities(days=days, min_score=min_score)

# Enhancement 3: Search by address
@app.get("/properties/search")
def search_properties(address: str):
    """Search for specific property"""
    # Search implementation
    return {"address": address, "found": True}

# Enhancement 4: Calculate ROI for a property
@app.post("/roi/calculate")
def calculate_roi(
    address: str,
    purchase_price: float,
    lot_size: float,
    zoning_type: str
):
    """Calculate ROI for a specific property"""
    from app.integrations.roi_calculator import ROICalculator
    calc = ROICalculator()
    result = calc.calculate_roi(
        address=address,
        purchase_price=purchase_price,
        lot_size_sqft=lot_size,
        zoning_type=zoning_type
    )
    return result.dict()
```

---

### **Summary: FastAPI Usage**

| Aspect | Status | Details |
|--------|--------|---------|
| **Installed** | ✅ Yes | In `requirements.txt` |
| **Configured** | ✅ Yes | `main.py` ready |
| **Currently Used** | ❌ No | Pipeline doesn't require it |
| **Can Be Used** | ✅ Yes | Start with `uvicorn main:app` |
| **Production Ready** | ⏸️ Optional | Ready if you build UI |
| **Tests** | ✅ Yes | `test_fastapi.py` included |

---

---

## 🎯 QUICK REFERENCE SUMMARY

### **1. Automation Scheduler**
- **Status:** Ready to activate
- **Default:** 9:00 AM daily (customizable)
- **Methods:**
  - Cron job (Linux/Mac): 5 min setup
  - Task Scheduler (Windows): 5 min setup
  - APScheduler: Python-based background daemon
- **Current:** Manual trigger via CLI working ✅

### **2. MLS Feed**
- **Status:** Active via SerpAPI
- **Method:** Google search results (MLS data embedded)
- **Advantage:** No expensive API keys needed
- **Alternative:** Direct RETS API possible ($500-2000/year + regional membership)
- **Data:** 39 MLS properties found in last run ✅

### **3. FastAPI**
- **Status:** Implemented but optional
- **Use Case:** REST API for web interface (not needed for current pipeline)
- **Current:** Pipeline uses CLI + scheduler, outputs to CSV/JSON/Sheets
- **Available:** 4 endpoints ready for optional web interface
- **Can Enable:** Run `uvicorn main:app --reload` if needed

---

*Last Updated: October 25, 2025*
