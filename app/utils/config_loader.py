# app/utils/config_loader.py

import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

class Config:
    """
    Loads configuration variables from environment.
    """
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.QDRANT_URL = os.getenv("QDRANT_URL")
        self.QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
        self.DEFAULT_OUTPUT_DIR = os.getenv("DEFAULT_OUTPUT_DIR", "outputs")

# Example usage
if __name__ == "__main__":
    config = Config()
    print("OpenAI Key:", "SET" if config.OPENAI_API_KEY else "MISSING")
    print("Qdrant URL:", config.QDRANT_URL)
