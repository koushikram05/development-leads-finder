# app/nlp/keyword_detector.py

import re
from typing import List

class KeywordDetector:
    """
    Detects predefined keywords in property descriptions.
    """
    def __init__(self, keywords: List[str] = None):
        # Default keywords if none provided
        self.keywords = keywords or [
            "garage", "pool", "basement", "zoning", "lot", "renovated", "fireplace", "garden"
        ]
        # Precompile regex for performance
        self.patterns = [re.compile(rf"\b{kw}\b", re.IGNORECASE) for kw in self.keywords]

    def detect(self, text: str) -> List[str]:
        """
        Detects which keywords are present in the given text.
        
        Args:
            text (str): The property description or text to scan.
        
        Returns:
            List[str]: List of detected keywords.
        """
        detected = [kw for kw, pattern in zip(self.keywords, self.patterns) if pattern.search(text)]
        return detected


# Example usage
if __name__ == "__main__":
    detector = KeywordDetector()
    sample_text = "This beautiful house comes with a pool, garage, and a renovated kitchen."
    print("Detected keywords:", detector.detect(sample_text))
