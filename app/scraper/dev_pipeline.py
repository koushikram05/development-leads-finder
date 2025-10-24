from app.scraper.zillow_scraper import scrape_zillow
from app.scraper.redfin_scraper import scrape_redfin
from app.scraper.realtor_scraper import scrape_realtor
from app.scraper.gis_enrichment import enrich_with_gis
from app.scraper.llm_classifier import classify_listings
import sys

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv)>1 else ""
    if not query: raise ValueError("Provide search query")

    # 1️⃣ Scrape all sources
    scrape_zillow("https://www.zillow.com/newton-ma/single-family-home/")
    scrape_redfin("https://www.redfin.com/city/11619/MA/Newton/filter/single-family-home")
    scrape_realtor("https://www.realtor.com/realestateandhomes-search/Newton_MA/type-single-family-home")

    # 2️⃣ Enrich with GIS/Assessor data
    enrich_with_gis()

    # 3️⃣ Classify with LLM
    classify_listings()
