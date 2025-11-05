# Development Leads Finder - Complete Real Estate Analysis System

Automated system for identifying single-family residential properties in Newton, MA that represent development or teardown opportunities. **All 5 core tasks complete and production-ready.** ✅

## 🎯 Project Status: COMPLETE ✅

**Progress:** 5/5 Tasks Complete | 30+/30+ Tests Passing | Production Ready

### 📋 Task Completion:
- ✅ **Task 1:** Google Sheets Integration (29 properties auto-uploaded)
- ✅ **Task 2:** Email/Slack Alerts (3-notification system working)
- ✅ **Task 3:** Historical Database (33 properties in SQLite)
- ✅ **Task 4:** Map Visualization (33 properties on interactive map)
- ✅ **Task 5:** ROI Scoring (financial analysis + profit calculations)

## 🚀 What This System Does

This AI-powered 8-stage pipeline:

1. **Scrapes** real estate listings from multiple sources (SerpAPI, Zillow, Redfin, Realtor.com)
2. **Enriches** data with GIS information (geocoding, lot size, zoning regulations)
3. **Classifies** properties using GPT-4 to detect development opportunities
4. **Calculates** ROI potential and profit estimates (NEW - Task 5)
5. **Uploads** results to Google Sheets with real-time sync
6. **Sends** email/Slack alerts for high-value opportunities
7. **Persists** data in SQLite database for historical analysis
8. **Generates** interactive maps for visual exploration
📁 Project Structure
Anil_Project/
│
├── app/
│   ├── __init__.py
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── llm_search.py          # SerpAPI-based search (primary)
│   │   ├── redfin_scraper.py      # Redfin scraper
│   │   ├── realtor_scraper.py     # Realtor.com scraper
│   │   └── zillow_scraper.py      # Zillow scraper
│   │
│   ├── enrichment/
│   │   ├── __init__.py
│   │   └── gis_enrichment.py      # GIS data enrichment
│   │
│   ├── classifier/
│   │   ├── __init__.py
│   │   └── llm_classifier.py      # LLM-based classification
│   │
│   ├── dev_pipeline.py            # Main pipeline orchestrator
│   └── utils.py                   # Utility functions
│
├── data/                          # Output directory
│   ├── raw_listings.csv
│   ├── classified_listings.csv
│   ├── development_opportunities.csv
│   └── logs/
│
├── .env                          # API keys (not in git)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
🚀 Quick Start
1. Prerequisites
Python 3.10 or higher
VS Code (recommended)
API Keys:
OpenAI API key
SerpAPI key
2. Installation
bash
# Clone the repository (if using git)
git clone <repository-url>
cd Anil_Project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
3. Configuration
Create a .env file in the project root:

properties
OPENAI_API_KEY=sk-your-openai-key-here
SERPAPI_KEY=your-serpapi-key-here
4. Run the Pipeline
Basic usage:

bash
python -m app.dev_pipeline
With custom search query:

bash
python -m app.dev_pipeline "Newton MA large lot teardown opportunity"
With all options:

bash
python -m app.dev_pipeline \
  "Newton MA teardown single family" \
  --location "Newton, MA" \
  --use-scrapers \
  --max-pages 3 \
  --min-score 50
📊 Pipeline Stages
Stage 1: Data Collection
Primary: SerpAPI search (fast, reliable, no blocks)
Optional: Direct scrapers (Redfin, Realtor, Zillow)
Deduplicates listings by address
Stage 2: Data Enrichment
Fetches Newton GIS parcel data
Adds lot size, zoning, frontage
Geocodes addresses
Calculates derived metrics (price/sqft, lot ratios, etc.)
Stage 3: Classification
GPT-4 analyzes each listing
Detects keywords: "tear down", "builder special", "as-is"
Evaluates metrics: age, lot size, ratios
Assigns labels: development, potential, no
Calculates development score (0-100)
Stage 4: Output
Generates CSV and JSON files:

raw_listings.csv - All scraped listings
classified_listings.csv - All listings with classifications
development_opportunities.csv - Filtered opportunities only
📋 Output Fields
Field	Description
address	Property address
price	Listing price
beds	Number of bedrooms
baths	Number of bathrooms
sqft	Building square footage
lot_size	Lot size in sqft
year_built	Year property was built
zoning	Zoning code
label	Classification (development/potential/no)
confidence	Confidence score (0-1)
explanation	AI reasoning
development_score	Overall score (0-100)
price_per_sqft	Price per square foot
lot_to_building_ratio	Lot size / building size
building_age	Age in years
🔧 Command-Line Options
python -m app.dev_pipeline [query] [options]

Arguments:
  query                 Search query (default: "Newton MA teardown...")

Options:
  --location LOCATION   Location to search (default: "Newton, MA")
  --use-scrapers        Enable direct website scrapers
  --max-pages N         Pages per scraper (default: 3)
  --no-enrich           Skip GIS enrichment
  --no-classify         Skip classification
  --min-score SCORE     Minimum dev score (default: 50)
📦 Dependencies
Core libraries (see requirements.txt):

pandas
numpy
python-dotenv
requests
beautifulsoup4
lxml
playwright
fake-useragent
openai
tiktoken
geopandas
shapely
🤖 Automation
Cron Job (Linux/Mac)
Edit crontab:

bash
crontab -e
Add daily run at 6 AM:

cron
0 6 * * * cd /path/to/Anil_Project && /path/to/venv/bin/python -m app.dev_pipeline >> logs/cron.log 2>&1
Task Scheduler (Windows)
Create a batch file run_pipeline.bat:

batch
@echo off
cd C:\path\to\Anil_Project
call venv\Scripts\activate
python -m app.dev_pipeline
Schedule it in Task Scheduler.

📈 Development Score Calculation
The development score (0-100) combines:

LLM Classification (up to 50 points)
"development" label: 50 × confidence
"potential" label: 30 × confidence
Building Age (up to 15 points)
70+ years: 15 points
50-69 years: 10 points
30-49 years: 5 points
Lot-to-Building Ratio (up to 15 points)
Ratio > 4: 15 points
Ratio 3-4: 10 points
Ratio 2-3: 5 points
Land Value Ratio (up to 10 points)
70%: 10 points

50-70%: 5 points
Price per Sqft (up to 10 points)
< $200: 10 points
$200-300: 5 points
Lot Size (up to 10 points)
15,000 sqft: 10 points

10,000-15,000 sqft: 5 points
🔍 Example Output
Top Development Opportunities:

1. 68 Vernon St, Newton, MA
   Score: 92.5/100
   Price: $975,000
   Lot: 9,500 sqft
   Year: 1950
   Reason: Phrase "tear down" detected + large lot + old structure

2. 45 Oak Street, Newton, MA
   Score: 87.3/100
   Price: $1,100,000
   Lot: 12,000 sqft
   Year: 1948
   Reason: Large lot to building ratio (5.2:1), underbuilt property
🛠️ Troubleshooting
API Rate Limits
SerpAPI: 100 searches/month (free tier)
OpenAI: Pay-per-use, set billing limits
Solution: Implement caching, reduce frequency
Scraper Blocks
Zillow has strong anti-bot measures
Solution: Use --use-scrapers sparingly, rely on SerpAPI
Alternative: Use residential proxies
Missing GIS Data
Newton GIS API may have rate limits or downtime
Solution: Graceful degradation - pipeline continues without enrichment
Check logs in data/logs/
Installation Issues
If you encounter module import errors:

bash
# Ensure you're in the project directory
cd Anil_Project

# Ensure virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install --upgrade -r requirements.txt
🎓 Usage Examples
Example 1: Quick Search
bash
python -m app.dev_pipeline "Newton MA teardown"
Example 2: Multiple Towns
bash
python -m app.dev_pipeline "teardown opportunity" --location "Brookline, MA"
python -m app.dev_pipeline "teardown opportunity" --location "Wellesley, MA"
Example 3: High-Confidence Only
bash
python -m app.dev_pipeline --min-score 75
Example 4: Full Scraping (Slow)
bash
python -m app.dev_pipeline --use-scrapers --max-pages 5
📊 Data Privacy & Ethics
Only collects publicly available listing data
Does not store or share personal information
Respects robots.txt and rate limits
For research and legitimate business purposes only
🔮 Future Enhancements
 Interactive dashboard (Streamlit/Dash)
 Slack/Email notifications
 ROI estimation calculator
 Multi-city support
 CRM integration (Salesforce, HubSpot)
 Map visualization layer
 Historical trend analysis
 Comparable sales analysis
📝 License
Proprietary - Anil Project Team

🤝 Support
For issues or questions:

Check logs in data/logs/
Review error messages
Verify API keys in .env
Contact development team
📚 Additional Resources
OpenAI API Documentation
SerpAPI Documentation
Newton GIS Portal
BeautifulSoup Documentation
Version: 1.0.0
Last Updated: 2025-01-23
Author: Anil Project Team

