"""
LLM-based classifier for identifying development opportunities
Uses OpenAI GPT for natural language classification
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI
from app.utils import setup_logging, get_env_variable


class LLMClassifier:
    """
    Classify properties as development opportunities using LLM
    """
    
    def __init__(self):
        self.logger = setup_logging('llm_classifier')
        api_key = get_env_variable('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Cost-effective and fast
        
    def classify_listing(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a single listing for development potential
        
        Args:
            listing: Property listing dictionary
            
        Returns:
            Listing with classification fields added
        """
        self.logger.info(f"Classifying: {listing.get('address', 'Unknown')}")
        
        # Build context for LLM
        context = self._build_classification_context(listing)
        
        # Get classification from LLM
        classification = self._get_llm_classification(context)
        
        # Add classification results to listing
        listing['label'] = classification['label']
        listing['confidence'] = classification['confidence']
        listing['explanation'] = classification['explanation']
        listing['development_score'] = self._calculate_development_score(listing, classification)
        
        return listing
    
    def classify_listings_batch(
        self, 
        listings: List[Dict[str, Any]],
        batch_size: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Classify multiple listings with batching
        
        Args:
            listings: List of property listings
            batch_size: Number of listings to classify at once
            
        Returns:
            List of classified listings
        """
        classified = []
        
        for i, listing in enumerate(listings):
            try:
                classified_listing = self.classify_listing(listing)
                classified.append(classified_listing)
                
                if (i + 1) % 10 == 0:
                    self.logger.info(f"Classified {i + 1}/{len(listings)} listings")
                    
            except Exception as e:
                self.logger.error(f"Error classifying listing: {e}")
                # Add default classification on error
                listing['label'] = 'unknown'
                listing['confidence'] = 0.0
                listing['explanation'] = f"Classification error: {str(e)}"
                listing['development_score'] = 0.0
                classified.append(listing)
        
        self.logger.info(f"Completed classification: {len(classified)} listings")
        return classified
    
    def _build_classification_context(self, listing: Dict[str, Any]) -> str:
        """
        Build context string for LLM classification
        
        Args:
            listing: Property listing
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Address
        if listing.get('address'):
            context_parts.append(f"Address: {listing['address']}")
        
        # Price
        if listing.get('price'):
            context_parts.append(f"Price: ${listing['price']:,.0f}")
        
        # Property details
        if listing.get('beds'):
            context_parts.append(f"Bedrooms: {listing['beds']}")
        if listing.get('baths'):
            context_parts.append(f"Bathrooms: {listing['baths']}")
        if listing.get('sqft'):
            context_parts.append(f"Square Footage: {listing['sqft']:,.0f} sqft")
        if listing.get('lot_size'):
            context_parts.append(f"Lot Size: {listing['lot_size']:,.0f} sqft")
        
        # Year and age
        if listing.get('year_built'):
            context_parts.append(f"Year Built: {listing['year_built']}")
        if listing.get('building_age'):
            context_parts.append(f"Building Age: {listing['building_age']} years")
        
        # Zoning
        if listing.get('zoning'):
            context_parts.append(f"Zoning: {listing['zoning']}")
        
        # Ratios and metrics
        if listing.get('price_per_sqft'):
            context_parts.append(f"Price per sqft: ${listing['price_per_sqft']:.2f}")
        if listing.get('lot_to_building_ratio'):
            context_parts.append(f"Lot to Building Ratio: {listing['lot_to_building_ratio']:.2f}")
        if listing.get('land_value_ratio'):
            context_parts.append(f"Land Value Ratio: {listing['land_value_ratio']:.2%}")
        
        # Description/Notes
        if listing.get('notes'):
            context_parts.append(f"Notes: {listing['notes']}")
        if listing.get('description'):
            context_parts.append(f"Description: {listing['description'][:500]}")  # Limit length
        if listing.get('snippet'):
            context_parts.append(f"Snippet: {listing['snippet']}")
        
        # Status
        if listing.get('status'):
            context_parts.append(f"Status: {listing['status']}")
        
        return "\n".join(context_parts)
    
    def _get_llm_classification(self, context: str) -> Dict[str, Any]:
        """
        Get classification from OpenAI LLM
        
        Args:
            context: Property context string
            
        Returns:
            Classification dictionary
        """
        system_prompt = """You are a real estate development opportunity classifier. 
Your task is to analyze property listings and determine if they represent good development or teardown opportunities.

Look for indicators such as:
- Keywords like "tear down", "builder special", "contractor special", "as-is", "development opportunity", "fixer-upper"
- Old buildings (pre-1960) on large lots
- High lot-to-building ratios (lot much larger than building)
- High land value relative to total value
- Properties described as needing significant work
- Large lots in desirable areas
- Underbuilt properties (small house on large lot)

Classify each property as:
- "development" - Strong teardown/development opportunity
- "potential" - Possible opportunity but needs more investigation
- "no" - Not a development opportunity

Provide your response in JSON format with these fields:
{
  "label": "development" | "potential" | "no",
  "confidence": 0.0 to 1.0,
  "explanation": "Brief explanation of your reasoning"
}"""
        
        user_prompt = f"""Analyze this property and determine if it's a development opportunity:

{context}

Respond in JSON format only."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            # Validate and normalize response
            classification = {
                'label': result.get('label', 'unknown').lower(),
                'confidence': float(result.get('confidence', 0.0)),
                'explanation': result.get('explanation', 'No explanation provided')
            }
            
            # Ensure label is valid
            if classification['label'] not in ['development', 'potential', 'no', 'unknown']:
                classification['label'] = 'unknown'
            
            # Ensure confidence is in valid range
            classification['confidence'] = max(0.0, min(1.0, classification['confidence']))
            
            return classification
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse LLM response as JSON: {e}")
            return {
                'label': 'unknown',
                'confidence': 0.0,
                'explanation': 'Error parsing LLM response'
            }
        except Exception as e:
            self.logger.error(f"LLM classification error: {e}")
            return {
                'label': 'unknown',
                'confidence': 0.0,
                'explanation': f'Classification error: {str(e)}'
            }
    
    def _calculate_development_score(
        self, 
        listing: Dict[str, Any], 
        classification: Dict[str, Any]
    ) -> float:
        """
        Calculate numerical development potential score (0-100)
        
        Args:
            listing: Property listing
            classification: LLM classification result
            
        Returns:
            Development score
        """
        score = 0.0
        
        # Base score from LLM classification
        label = classification['label']
        confidence = classification['confidence']
        
        if label == 'development':
            score += 50 * confidence
        elif label == 'potential':
            score += 30 * confidence
        
        # Bonus points for favorable metrics
        
        # Old building bonus (max 15 points)
        if listing.get('building_age'):
            age = listing['building_age']
            if age > 70:
                score += 15
            elif age > 50:
                score += 10
            elif age > 30:
                score += 5
        
        # Lot to building ratio bonus (max 15 points)
        if listing.get('lot_to_building_ratio'):
            ratio = listing['lot_to_building_ratio']
            if ratio > 4:
                score += 15
            elif ratio > 3:
                score += 10
            elif ratio > 2:
                score += 5
        
        # Land value ratio bonus (max 10 points)
        if listing.get('land_value_ratio'):
            land_ratio = listing['land_value_ratio']
            if land_ratio > 0.7:
                score += 10
            elif land_ratio > 0.5:
                score += 5
        
        # Low price per sqft bonus (max 10 points)
        if listing.get('price_per_sqft'):
            ppsf = listing['price_per_sqft']
            if ppsf < 200:
                score += 10
            elif ppsf < 300:
                score += 5
        
        # Large lot bonus (max 10 points)
        if listing.get('lot_size'):
            lot_size = listing['lot_size']
            if lot_size > 15000:
                score += 10
            elif lot_size > 10000:
                score += 5
        
        # Cap at 100
        return min(100.0, round(score, 2))
    
    def filter_development_opportunities(
        self, 
        listings: List[Dict[str, Any]],
        min_score: float = 50.0,
        include_potential: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Filter listings to only development opportunities
        
        Args:
            listings: List of classified listings
            min_score: Minimum development score threshold
            include_potential: Whether to include 'potential' classifications
            
        Returns:
            Filtered list of development opportunities
        """
        valid_labels = ['development']
        if include_potential:
            valid_labels.append('potential')
        
        filtered = [
            listing for listing in listings
            if listing.get('label') in valid_labels
            and listing.get('development_score', 0) >= min_score
        ]
        
        # Sort by development score (descending)
        filtered.sort(key=lambda x: x.get('development_score', 0), reverse=True)
        
        self.logger.info(f"Filtered {len(filtered)} development opportunities from {len(listings)} listings")
        return filtered


# Example usage
if __name__ == "__main__":
    classifier = LLMClassifier()
    
    # Test with sample listing
    test_listing = {
        'address': '68 Vernon St, Newton, MA',
        'price': 975000,
        'sqft': 1800,
        'lot_size': 9500,
        'year_built': 1950,
        'building_age': 75,
        'lot_to_building_ratio': 5.28,
        'notes': 'Tear down opportunity on large lot in desirable neighborhood'
    }
    
    classified = classifier.classify_listing(test_listing)
    
    print("\nClassification Results:")
    print(f"  Label: {classified['label']}")
    print(f"  Confidence: {classified['confidence']:.2f}")
    print(f"  Development Score: {classified['development_score']:.1f}/100")
    print(f"  Explanation: {classified['explanation']}")