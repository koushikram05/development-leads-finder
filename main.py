from fastapi import FastAPI, HTTPException
from app.geo.zoning_loader import ZoningLoader
from app.geo.lot_analysis import LotAnalysis
from app.nlp.keyword_detector import KeywordDetector
from app.nlp.openai_classifier import OpenAIClassifier

app = FastAPI(title="Property & NLP Analysis API")

# Initialize core modules
zoning_loader = ZoningLoader("data/zoning_shapefile.shp")
# shapefile is already loaded during initialization

keyword_detector = KeywordDetector()
openai_classifier = OpenAIClassifier(api_key="YOUR_OPENAI_KEY")  # replace with your key

# Routes
@app.get("/")
def read_root():
    return {"message": "API is running!"}

@app.get("/lot/buildable")
def check_buildable(lat: float, lon: float, lot_size: float):
    zone_data = zoning_loader.get_zone(lat, lon)
    if zone_data.empty or zone_data.zone.isnull().all():
        raise HTTPException(status_code=404, detail="No zoning info for this location")
    
    zoning_type = zone_data.zone.iloc[0]
    lot = LotAnalysis(lot_size=lot_size, zoning_type=zoning_type)
    return {
        "zoning_type": zoning_type,
        "buildable": lot.is_buildable(),
        "lot_value_score": lot.lot_value_score()
    }

@app.post("/nlp/detect_keywords")
def detect_keywords(text: str):
    keywords = keyword_detector.extract_keywords(text)
    return {"keywords": keywords}

@app.post("/nlp/classify_text")
def classify_text(text: str):
    label = openai_classifier.classify(text)
    return {"label": label}
