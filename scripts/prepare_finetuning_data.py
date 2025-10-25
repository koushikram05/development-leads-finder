#!/usr/bin/env python3
"""
Fine-tuning Data Preparation
Extracts and formats historical classification data for OpenAI fine-tuning
"""

import json
import os
from pathlib import Path
from app.integrations.database_manager import HistoricalDatabaseManager

def prepare_finetuning_data():
    """
    Extract training data from database and format for OpenAI fine-tuning
    
    Returns:
        Tuple of (output_file_path, number_of_examples)
    """
    
    print("📊 Preparing fine-tuning data...")
    print("=" * 60)
    
    # Initialize database
    db = HistoricalDatabaseManager()
    
    # Get historical classifications
    print("🔍 Extracting classifications from database...")
    classifications = db.get_training_data(min_classifications=1)
    
    if not classifications:
        print("❌ No classification data found in database")
        return None, 0
    
    print(f"✅ Found {len(classifications)} classifications")
    
    # Format data for OpenAI fine-tuning (Chat API format)
    training_data = []
    
    for idx, item in enumerate(classifications, 1):
        try:
            # Build the prompt
            address = item.get('address', 'Unknown')
            snippet = item.get('snippet', 'N/A')
            price = item.get('price', 'Unknown')
            lot_size = item.get('lot_size', 'Unknown')
            
            prompt = f"""Classify this real estate property as a development opportunity:

Address: {address}
Details: {snippet}
Price: ${price if price != 'Unknown' else 'N/A'}
Lot Size: {lot_size if lot_size != 'Unknown' else 'N/A'} sqft

Is this a good development opportunity? Respond with: "development_opportunity" or "not_opportunity"."""
            
            # Get the classification (label)
            classification = item.get('classification', 'unclear')
            if classification == 'development_opportunity':
                completion = "development_opportunity"
            elif classification == 'not_opportunity':
                completion = "not_opportunity"
            else:
                completion = "unclear"
            
            # Format for OpenAI Chat Completions fine-tuning
            training_example = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert real estate analyst specializing in identifying development opportunities. You classify properties as either development_opportunity or not_opportunity based on their potential for redevelopment."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    },
                    {
                        "role": "assistant",
                        "content": completion
                    }
                ]
            }
            
            training_data.append(training_example)
            
            # Progress indicator
            if idx % 10 == 0:
                print(f"  ✓ Processed {idx} examples...")
        
        except Exception as e:
            print(f"  ⚠️  Skipped example {idx}: {e}")
            continue
    
    if not training_data:
        print("❌ No valid training examples created")
        return None, 0
    
    # Save training data as JSONL (one JSON object per line)
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "finetuning_data.jsonl"
    
    print(f"\n💾 Saving {len(training_data)} training examples...")
    
    with open(output_file, 'w') as f:
        for example in training_data:
            f.write(json.dumps(example) + '\n')
    
    print(f"✅ Saved to: {output_file}")
    print(f"📊 File size: {output_file.stat().st_size / 1024:.1f} KB")
    
    # Print sample
    print("\n📋 Sample training example:")
    print("-" * 60)
    print(json.dumps(training_data[0], indent=2))
    print("-" * 60)
    
    # Statistics
    print("\n📈 Fine-tuning Data Statistics:")
    print(f"  Total examples: {len(training_data)}")
    print(f"  Development opportunities: {sum(1 for ex in training_data if 'development_opportunity' in str(ex))}")
    print(f"  Not opportunities: {sum(1 for ex in training_data if 'not_opportunity' in str(ex))}")
    print(f"  Unclear: {sum(1 for ex in training_data if 'unclear' in str(ex))}")
    
    print("\n✨ Data preparation complete!")
    print("📝 Next step: python scripts/create_finetuning_job.py")
    
    return str(output_file), len(training_data)

if __name__ == "__main__":
    try:
        output_file, count = prepare_finetuning_data()
        if output_file:
            print(f"\n✅ Success! Ready for fine-tuning with {count} examples.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
