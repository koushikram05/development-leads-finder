try:
    import fastapi, openai, pandas, qdrant_client, spacy
    print("✅ Environment setup verified — all required libraries imported successfully!")
except Exception as e:
    print("❌ Import failed:", e)

