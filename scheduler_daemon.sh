#!/bin/bash
# scheduler_daemon.sh
# Persistent background scheduler daemon for development leads pipeline
# This script keeps the scheduler running continuously

PROJECT_DIR="/Users/koushikramalingam/Desktop/Anil_Project"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
LOG_FILE="$PROJECT_DIR/logs/scheduler_daemon.log"
PID_FILE="$PROJECT_DIR/logs/scheduler.pid"

mkdir -p "$PROJECT_DIR/logs"

# Function to start scheduler
start_scheduler() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting scheduler daemon..." >> "$LOG_FILE"
    
    # Run the scheduler
    nohup $PYTHON_BIN "$PROJECT_DIR/activate_scheduler.py" --hour 9 --minute 0 >> "$LOG_FILE" 2>&1 &
    
    SCHEDULER_PID=$!
    echo $SCHEDULER_PID > "$PID_FILE"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Scheduler started with PID $SCHEDULER_PID" >> "$LOG_FILE"
}

# Function to stop scheduler
stop_scheduler() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Scheduler stopped (PID $PID)" >> "$LOG_FILE"
            rm "$PID_FILE"
        fi
    fi
}

# Function to check status
status_scheduler() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "✅ Scheduler is running (PID: $PID)"
            echo "📊 Log file: $LOG_FILE"
            echo ""
            echo "Recent logs:"
            tail -5 "$LOG_FILE"
        else
            echo "❌ Scheduler is not running (stale PID: $PID)"
            rm "$PID_FILE"
        fi
    else
        echo "❌ Scheduler is not running"
    fi
}

# Main logic
case "$1" in
    start)
        start_scheduler
        ;;
    stop)
        stop_scheduler
        ;;
    restart)
        stop_scheduler
        sleep 2
        start_scheduler
        ;;
    status)
        status_scheduler
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
