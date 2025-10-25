#!/usr/bin/env python3
"""
Check Fine-tuning Job Status
Monitor and retrieve results of fine-tuning jobs
"""

import os
from pathlib import Path
from openai import OpenAI

def check_finetuning_status(job_id: str = None):
    """
    Check status of fine-tuning job
    
    Args:
        job_id: Optional job ID. If not provided, reads from saved file.
    
    Returns:
        Job details dictionary
    """
    
    print("🔍 Checking Fine-tuning Job Status")
    print("=" * 60)
    
    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        return None
    
    client = OpenAI(api_key=api_key)
    
    # Get job ID
    if not job_id:
        job_id_file = Path("data/finetuning_job_id.txt")
        if job_id_file.exists():
            with open(job_id_file, "r") as f:
                job_id = f.read().strip()
            print(f"📋 Using saved job ID: {job_id}")
        else:
            print("❌ No job ID provided and no saved job ID found")
            print("   Run: python scripts/create_finetuning_job.py")
            return None
    
    # Retrieve job details
    try:
        print(f"\n📡 Querying OpenAI for job: {job_id}")
        job = client.fine_tuning.jobs.retrieve(job_id)
    
    except Exception as e:
        print(f"❌ Error retrieving job: {e}")
        return None
    
    # Display job information
    print("\n" + "=" * 60)
    print("JOB INFORMATION:")
    print("=" * 60)
    print(f"Job ID:           {job.id}")
    print(f"Model:            {job.model}")
    print(f"Status:           {job.status}")
    print(f"Created:          {job.created_at}")
    
    if job.status == "succeeded":
        print(f"\n✅ FINE-TUNING COMPLETE!")
        print(f"   Fine-tuned Model: {job.fine_tuned_model}")
        print(f"   Finished at:      {job.finished_at}")
        
        # Save fine-tuned model ID
        model_file = Path("data/finetuned_model_id.txt")
        with open(model_file, "w") as f:
            f.write(job.fine_tuned_model)
        print(f"\n   Saved to: {model_file}")
        
        print("\n🎉 NEXT STEPS:")
        print("   1. Update your classifier to use the fine-tuned model:")
        print(f"      classifier = OpenAIClassifier(use_finetuned=True)")
        print(f"   2. The classifier will automatically use: {job.fine_tuned_model}")
        print(f"   3. Test with: python -m app.dev_pipeline")
    
    elif job.status == "running":
        print(f"\n⏳ TRAINING IN PROGRESS...")
        if job.trained_tokens:
            print(f"   Trained tokens: {job.trained_tokens}")
        print(f"\n   Estimated time: 30 mins - 2 hours")
        print(f"   Check again with: python scripts/check_finetuning_status.py")
        
        # Show training events if available
        if hasattr(job, 'events') and job.events:
            print(f"\n   Recent events:")
            for event in job.events[-3:]:
                print(f"     - {event.created_at}: {event.message}")
    
    elif job.status == "failed":
        print(f"\n❌ FINE-TUNING FAILED")
        if job.error:
            print(f"   Error: {job.error}")
        print(f"\n   Try:")
        print(f"   1. Check training data quality: python scripts/prepare_finetuning_data.py")
        print(f"   2. Use cheaper model: python scripts/create_finetuning_job.py gpt-3.5-turbo")
    
    elif job.status == "queued":
        print(f"\n⏳ JOB QUEUED - WAITING TO START")
        print(f"   Will begin training soon")
        print(f"   Check again: python scripts/check_finetuning_status.py")
    
    # Additional metrics
    print("\n" + "=" * 60)
    print("METRICS:")
    print("=" * 60)
    if hasattr(job, 'result_files') and job.result_files:
        print(f"Result files:     Available")
    
    print("\n" + "=" * 60)
    
    return job

def list_all_jobs():
    """List all fine-tuning jobs for this account"""
    
    print("\n📋 Your Fine-tuning Jobs:")
    print("=" * 60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    try:
        jobs = client.fine_tuning.jobs.list()
        
        if not jobs.data:
            print("No fine-tuning jobs found")
            return
        
        for job in jobs.data:
            status_emoji = {
                "succeeded": "✅",
                "running": "⏳",
                "failed": "❌",
                "queued": "⏱️"
            }.get(job.status, "❓")
            
            print(f"{status_emoji} {job.id} | {job.model} | {job.status}")
            if job.status == "succeeded":
                print(f"   → {job.fine_tuned_model}")
    
    except Exception as e:
        print(f"Error listing jobs: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            list_all_jobs()
        else:
            job_id = sys.argv[1]
            check_finetuning_status(job_id)
    else:
        job = check_finetuning_status()
        
        # Also show all jobs
        print("\n")
        list_all_jobs()
