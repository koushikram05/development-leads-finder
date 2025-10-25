#!/usr/bin/env python3
"""
SCHEDULER ACTIVATION SCRIPT
Activates automatic daily pipeline execution at 9 AM
"""

import logging
import sys
import time
from datetime import datetime
from app.scheduler import PipelineScheduler
from app.dev_pipeline import DevelopmentPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('scheduler_activation')

def activate_scheduler(hour: int = 9, minute: int = 0):
    """
    Activate the pipeline scheduler
    
    Args:
        hour: Hour of day to run (0-23, default 9 for 9 AM)
        minute: Minute of hour (default 0)
    """
    logger.info("=" * 60)
    logger.info("🚀 PIPELINE SCHEDULER ACTIVATION")
    logger.info("=" * 60)
    
    try:
        # Initialize components
        logger.info("📦 Initializing pipeline and scheduler...")
        pipeline = DevelopmentPipeline()
        scheduler = PipelineScheduler()
        
        # Schedule daily execution
        logger.info(f"⏰ Scheduling daily execution at {hour:02d}:{minute:02d}")
        scheduler.schedule_daily(
            pipeline_func=pipeline.run,
            hour=hour,
            minute=minute,
            job_id='daily_development_leads'
        )
        
        # Start scheduler
        logger.info("▶️  Starting scheduler...")
        scheduler.start()
        
        # Confirm activation
        logger.info("=" * 60)
        logger.info("✅ SCHEDULER ACTIVATED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info(f"📅 Scheduled for: Daily at {hour:02d}:{minute:02d}")
        logger.info(f"⏱️  Current time: {datetime.now().strftime('%H:%M:%S')}")
        logger.info("📊 Execution log: data/pipeline_execution_log.txt")
        logger.info("=" * 60)
        
        # List active jobs
        logger.info("\n📋 Active Scheduled Jobs:")
        scheduler.list_jobs()
        
        # Keep scheduler running
        logger.info("\n✨ Scheduler is now running in the background...")
        logger.info("Press Ctrl+C to stop the scheduler\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n⏹️  Stopping scheduler...")
            scheduler.stop()
            logger.info("✓ Scheduler stopped")
            
    except Exception as e:
        logger.error(f"❌ Failed to activate scheduler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Activate automatic pipeline scheduler"
    )
    parser.add_argument(
        "--hour",
        type=int,
        default=9,
        help="Hour of day to run (0-23, default 9 for 9 AM)"
    )
    parser.add_argument(
        "--minute",
        type=int,
        default=0,
        help="Minute of hour (default 0)"
    )
    
    args = parser.parse_args()
    
    # Validate hour and minute
    if not (0 <= args.hour <= 23):
        logger.error("❌ Hour must be between 0 and 23")
        sys.exit(1)
    if not (0 <= args.minute <= 59):
        logger.error("❌ Minute must be between 0 and 59")
        sys.exit(1)
    
    activate_scheduler(hour=args.hour, minute=args.minute)
