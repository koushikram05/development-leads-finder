import csv
import os
from datetime import datetime

def ensure_dir(path: str):
    """Create a folder if it doesn’t exist."""
    os.makedirs(path, exist_ok=True)

def save_to_csv(data, filepath, fieldnames):
    """Save list of dicts to CSV."""
    ensure_dir(os.path.dirname(filepath))
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def log_message(message: str, log_path="logs/scrape_log.txt"):
    """Append timestamped logs."""
    ensure_dir(os.path.dirname(log_path))
    with open(log_path, "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    print(message)
