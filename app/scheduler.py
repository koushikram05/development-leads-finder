"""
Scheduler for automated pipeline execution
Handles daily/weekly scans with logging and manual refresh support
"""

import logging
import os
from datetime import datetime
from typing import Callable, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


class PipelineScheduler:
    """
    Manages automated execution of development lead pipeline
    Features:
    - Daily/weekly scheduled runs
    - Manual trigger capability
    - Execution history logging
    - Error handling and retry logic
    """
    
    def __init__(self):
        """Initialize scheduler"""
        self.logger = logging.getLogger('pipeline_scheduler')
        self.scheduler = BackgroundScheduler()
        self.execution_log_file = 'data/pipeline_execution_log.txt'
        os.makedirs('data', exist_ok=True)
    
    def schedule_daily(
        self,
        pipeline_func: Callable,
        hour: int = 9,
        minute: int = 0,
        job_id: str = 'daily_scan'
    ) -> None:
        """
        Schedule daily pipeline execution
        
        Args:
            pipeline_func: Function to execute
            hour: Hour of day (0-23, default 9 AM)
            minute: Minute of hour (default 0)
            job_id: Unique job identifier
        """
        try:
            self.scheduler.add_job(
                func=self._run_with_logging(pipeline_func),
                trigger=CronTrigger(hour=hour, minute=minute),
                id=job_id,
                name=f'Daily pipeline run at {hour:02d}:{minute:02d}',
                replace_existing=True,
                coalesce=True,
                max_instances=1
            )
            self.logger.info(f"✓ Scheduled daily execution at {hour:02d}:{minute:02d}")
        except Exception as e:
            self.logger.error(f"Failed to schedule daily job: {e}")
    
    def schedule_weekly(
        self,
        pipeline_func: Callable,
        day_of_week: str = 'mon',
        hour: int = 9,
        minute: int = 0,
        job_id: str = 'weekly_scan'
    ) -> None:
        """
        Schedule weekly pipeline execution
        
        Args:
            pipeline_func: Function to execute
            day_of_week: Day name (mon, tue, wed, thu, fri, sat, sun)
            hour: Hour of day (default 9 AM)
            minute: Minute of hour (default 0)
            job_id: Unique job identifier
        """
        try:
            trigger = CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute)
            self.scheduler.add_job(
                func=self._run_with_logging(pipeline_func),
                trigger=trigger,
                id=job_id,
                name=f'Weekly pipeline run on {day_of_week.upper()} at {hour:02d}:{minute:02d}',
                replace_existing=True,
                coalesce=True,
                max_instances=1
            )
            self.logger.info(
                f"✓ Scheduled weekly execution every {day_of_week.upper()} "
                f"at {hour:02d}:{minute:02d}"
            )
        except Exception as e:
            self.logger.error(f"Failed to schedule weekly job: {e}")
    
    def run_now(self, pipeline_func: Callable) -> bool:
        """
        Manually trigger pipeline execution immediately
        
        Args:
            pipeline_func: Function to execute
        
        Returns:
            bool: Success status
        """
        self.logger.info("🔄 Manual pipeline trigger initiated...")
        try:
            pipeline_func()
            self._log_execution('MANUAL', 'SUCCESS')
            self.logger.info("✓ Manual execution completed successfully")
            return True
        except Exception as e:
            self._log_execution('MANUAL', f'FAILED: {e}')
            self.logger.error(f"✗ Manual execution failed: {e}")
            return False
    
    def start(self) -> None:
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            self.logger.info("✓ Pipeline scheduler started")
    
    def stop(self) -> None:
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.logger.info("✓ Pipeline scheduler stopped")
    
    def list_jobs(self) -> None:
        """List all scheduled jobs"""
        jobs = self.scheduler.get_jobs()
        if jobs:
            self.logger.info(f"Active jobs ({len(jobs)}):")
            for job in jobs:
                self.logger.info(f"  - {job.id}: {job.name}")
        else:
            self.logger.info("No scheduled jobs")
    
    def _run_with_logging(self, func: Callable) -> Callable:
        """Wrap function with logging and error handling"""
        def wrapper():
            try:
                self.logger.info(f"▶️  Running pipeline at {datetime.now().isoformat()}")
                func()
                self._log_execution('SCHEDULED', 'SUCCESS')
                self.logger.info("✓ Pipeline execution completed successfully")
            except Exception as e:
                error_msg = str(e)
                self._log_execution('SCHEDULED', f'FAILED: {error_msg}')
                self.logger.error(f"✗ Pipeline execution failed: {e}")
        return wrapper
    
    def _log_execution(self, trigger_type: str, status: str) -> None:
        """Log pipeline execution to file"""
        try:
            with open(self.execution_log_file, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"{timestamp} | {trigger_type} | {status}\n")
        except Exception as e:
            self.logger.warning(f"Failed to log execution: {e}")
    
    def get_execution_log(self) -> str:
        """Retrieve execution history"""
        try:
            if os.path.exists(self.execution_log_file):
                with open(self.execution_log_file, 'r') as f:
                    lines = f.readlines()
                    # Return last 20 executions
                    return ''.join(lines[-20:])
            return "No execution history found"
        except Exception as e:
            return f"Error reading log: {e}"
