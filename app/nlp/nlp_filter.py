import pandas as pd
import spacy

# Load English NLP model
nlp = spacy.load("en_core_web_sm")

# Keywords that signal a development opportunity
DEV_KEYWORDS = [
    "tear down", "teardown", "builder", "contractor", "rehab",
    "development opportunity", "renovate", "fixer", "as is", "needs work"
]

def detect_development_opportunities(text):
    text_lower = text.lower()
    for kw in DEV_KEYWORDS:
        if kw in text_lower:
            return True
    return False

def analyze_listings(input_csv="data/raw_listings.csv", output_csv="data/entities.csv"):
    df = pd.read_csv(input_csv)
    print(f"🔍 Loaded {len(df)} listings for analysis")

    # Add NLP insights
    df["dev_opportunity"] = df["description"].apply(
        lambda text: detect_development_opportunities(str(text))
    )

    df["entities"] = df["description"].apply(
        lambda text: [ent.text for ent in nlp(str(text)).ents]
    )

    # Filter likely development leads
    leads = df[df["dev_opportunity"] == True]
    leads.to_csv(output_csv, index=False)

    print(f"✅ Saved {len(leads)} potential development leads to {output_csv}")

if __name__ == "__main__":
    analyze_listings()
