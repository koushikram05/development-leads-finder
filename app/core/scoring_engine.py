# app/core/scoring_engine.py

from typing import Dict

class ScoringEngine:
    """
    Calculates a property score based on predefined criteria.
    """

    def __init__(self, weights: Dict[str, float] = None):
        # Default weights for each feature
        self.weights = weights or {
            "garage": 1.5,
            "pool": 2.0,
            "basement": 1.2,
            "zoning": 1.0,
            "lot": 1.3,
            "renovated": 1.7,
            "fireplace": 1.4,
            "garden": 1.1
        }

    def calculate_score(self, detected_keywords: list) -> float:
        """
        Calculate property score based on detected keywords.
        """
        score = sum(self.weights.get(kw, 0) for kw in detected_keywords)
        return score


# Example usage
if __name__ == "__main__":
    engine = ScoringEngine()
    sample_keywords = ["garage", "pool", "renovated"]
