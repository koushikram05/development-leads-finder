# app/nlp/openai_classifier.py

import os
from openai import OpenAI
from typing import List

class OpenAIClassifier:
    """
    Uses OpenAI API to classify property descriptions into predefined categories.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    def classify(self, text: str, categories: List[str]) -> str:
        """
        Classifies text into one of the given categories using OpenAI.
        
        Args:
            text (str): Property description to classify.
            categories (List[str]): List of category labels.
        
        Returns:
            str: Predicted category.
        """
        prompt = f"Classify the following property description into one of these categories: {categories}\n\nDescription:\n{text}\n\nCategory:"
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        category = response.choices[0].message.content.strip()
        return category


# Example usage
if __name__ == "__main__":
    classifier = OpenAIClassifier()
    sample_text = "This house has a large backyard, swimming pool, and a modern kitchen."
    categories = ["Residential", "Commercial", "Land", "Mixed-use"]
    print("Predicted category:", classifier.classify(sample_text, categories))
