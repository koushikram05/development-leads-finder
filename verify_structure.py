import os

EXPECTED = [
    "app",
    "app/__init__.py",
    "app/scraper",
    "app/scraper/__init__.py",
    "app/scraper/zillow_scraper.py",
    "app/scraper/redfin_scraper.py",
    "app/scraper/realtor_scraper.py",
    "app/scraper/llm_search.py",
    "app/enrichment",
    "app/enrichment/__init__.py",
    "app/enrichment/gis_enrichment.py",
    "app/classifier",
    "app/classifier/__init__.py",
    "app/classifier/llm_classifier.py",
    "app/dev_pipeline.py",
    "app/utils.py",
    "data",
    "data/raw_listings.csv",
    "data/classified_listings.csv",
    ".env",
    "requirements.txt",
    "README.md",
]

print(f"🔍 Checking folder structure in: {os.getcwd()}\n")

missing = []
for path in EXPECTED:
    if not os.path.exists(path):
        missing.append(path)
        print(f"❌ Missing: {path}")
    else:
        print(f"✅ Found:   {path}")

print("\n📊 Summary:")
print(f"Total expected: {len(EXPECTED)}")
print(f"Missing: {len(missing)}")

if missing:
    print("\n🚨 You need to create or move these:")
    for m in missing:
        print("   ", m)
else:
    print("\n✅ Project structure is perfect!")
