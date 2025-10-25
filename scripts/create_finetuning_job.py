#!/usr/bin/env python3
"""
Create OpenAI Fine-tuning Job
Uploads training data and submits fine-tuning job
"""

import json
import os
from pathlib import Path
from openai import OpenAI

def create_finetuning_job(model: str = "gpt-4-turbo"):
    """
    Create OpenAI fine-tuning job
    
    Args:
        model: Base model to fine-tune ("gpt-4-turbo" or "gpt-3.5-turbo")
    
    Returns:
        Job ID of the created fine-tuning job
    """
    
    print("🚀 Creating OpenAI Fine-tuning Job")
    print("=" * 60)
    
    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        return None
    
    client = OpenAI(api_key=api_key)
    
    # Check if training file exists
    training_file = Path("data/finetuning_data.jsonl")
    if not training_file.exists():
        print(f"❌ Training file not found: {training_file}")
        print("   Run: python scripts/prepare_finetuning_data.py")
        return None
    
    print(f"📁 Training file: {training_file}")
    print(f"📊 File size: {training_file.stat().st_size / 1024:.1f} KB")
    
    # Upload training file
    print("\n📤 Uploading training file to OpenAI...")
    try:
        with open(training_file, "rb") as f:
            response = client.files.create(
                file=f,
                purpose="fine-tune"
            )
        
        file_id = response.id
        print(f"✅ File uploaded successfully")
        print(f"   File ID: {file_id}")
    
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return None
    
    # Create fine-tuning job
    print(f"\n🔄 Creating fine-tuning job with model: {model}")
    try:
        job = client.fine_tuning.jobs.create(
            training_file=file_id,
            model=model,
            suffix="dev-leads-classifier"
        )
        
        job_id = job.id
        print(f"✅ Fine-tuning job created successfully")
        print(f"   Job ID: {job_id}")
        print(f"   Status: {job.status}")
        print(f"   Created at: {job.created_at}")
    
    except Exception as e:
        print(f"❌ Error creating fine-tuning job: {e}")
        return None
    
    # Save job ID for reference
    print("\n💾 Saving job ID...")
    job_id_file = Path("data/finetuning_job_id.txt")
    with open(job_id_file, "w") as f:
        f.write(job_id)
    print(f"✅ Job ID saved to: {job_id_file}")
    
    # Display next steps
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS:")
    print("=" * 60)
    print(f"\n1. Monitor progress:")
    print(f"   python scripts/check_finetuning_status.py")
    print(f"\n2. Or via OpenAI CLI:")
    print(f"   openai api fine_tuning.jobs.retrieve -i {job_id}")
    print(f"\n3. Fine-tuning typically takes 30 mins - 2 hours")
    print(f"   You'll receive email when complete")
    print(f"\n4. Once complete, update pipeline:")
    print(f"   classifier = OpenAIClassifier(use_finetuned=True)")
    
    # Print estimated costs
    print("\n" + "=" * 60)
    print("💰 ESTIMATED COSTS:")
    print("=" * 60)
    print(f"\n  Fine-tuning: $5-15 (one-time)")
    if model == "gpt-4-turbo":
        print(f"  Usage: $0.001/1K input tokens (fine-tuned)")
    else:
        print(f"  Usage: $0.0005/1K input tokens (fine-tuned)")
    print(f"\n✨ Job submitted! Monitor status with commands above.")
    
    return job_id

if __name__ == "__main__":
    import sys
    
    # Get model from command line or use default
    model = sys.argv[1] if len(sys.argv) > 1 else "gpt-4-turbo"
    
    valid_models = ["gpt-4-turbo", "gpt-3.5-turbo"]
    if model not in valid_models:
        print(f"❌ Invalid model: {model}")
        print(f"   Valid options: {', '.join(valid_models)}")
        sys.exit(1)
    
    try:
        job_id = create_finetuning_job(model=model)
        if job_id:
            print(f"\n✅ Success! Job ID: {job_id}")
        else:
            print("\n❌ Failed to create fine-tuning job")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
