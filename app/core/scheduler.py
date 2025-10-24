# app/core/scheduler.py

import time
import threading
from typing import Callable

class Scheduler:
    """
    Simple scheduler to run tasks periodically in a separate thread.
    """

    def __init__(self, interval: int = 60):
        self.interval = interval  # in seconds
        self.tasks = []

    def add_task(self, func: Callable):
        self.tasks.append(func)

    def _run_task(self, func: Callable):
        while True:
            func()
            time.sleep(self.interval)

    def start(self):
        for task in self.tasks:
            thread = threading.Thread(target=self._run_task, args=(task,), daemon=True)
            thread.start()


# Example usage
if __name__ == "__main__":
    def sample_task():
        print("Running scheduled task...")

    scheduler = Scheduler(interval=10)
    scheduler.add_task(sample_task)
    scheduler.start()

    # Keep the main thread alive
    while True:
        time.sleep(1)
