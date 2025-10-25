#!/bin/bash
# SCHEDULER SETUP - Cron Job Configuration
# This script sets up the pipeline to run automatically every day at 9 AM

set -e

PROJECT_DIR="/Users/koushikramalingam/Desktop/Anil_Project"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
LOG_DIR="$PROJECT_DIR/logs"
CRON_LOG="$LOG_DIR/cron_pipeline.log"

# Create logs directory
mkdir -p "$LOG_DIR"

echo "🔧 PIPELINE CRON JOB SETUP"
echo "================================"
echo "Project: $PROJECT_DIR"
echo "Python: $PYTHON_BIN"
echo "Log file: $CRON_LOG"
echo ""

# Check if Python virtual environment exists
if [ ! -f "$PYTHON_BIN" ]; then
    echo "❌ Error: Virtual environment not found at $PYTHON_BIN"
    exit 1
fi

echo "✓ Virtual environment found"
echo ""

# Function to add cron job
add_cron_job() {
    local hour=$1
    local minute=$2
    
    # Create cron command
    local cron_cmd="$minute $hour * * * cd $PROJECT_DIR && $PYTHON_BIN -m app.dev_pipeline >> $CRON_LOG 2>&1"
    
    echo "📅 Adding cron job:"
    echo "   Time: $hour:$(printf "%02d" $minute)"
    echo "   Command: $cron_cmd"
    echo ""
    
    # Check if job already exists
    if crontab -l 2>/dev/null | grep -q "dev_pipeline"; then
        echo "⚠️  Cron job already exists, removing old job..."
        crontab -l | grep -v "dev_pipeline" | crontab -
    fi
    
    # Add new cron job
    (crontab -l 2>/dev/null; echo "$cron_cmd") | crontab -
    
    echo "✅ Cron job added successfully!"
    echo ""
    
    # List cron jobs
    echo "📋 Current cron jobs:"
    crontab -l | grep -v "^#" | grep -v "^$"
}

# Main setup
echo "Select scheduler time (default 9:00 AM):"
echo "1. Daily at 6:00 AM"
echo "2. Daily at 9:00 AM (default)"
echo "3. Daily at 12:00 PM (noon)"
echo "4. Daily at 3:00 PM"
echo "5. Daily at 6:00 PM"
echo "6. Custom time"
echo ""

read -p "Enter choice (1-6) [default: 2]: " choice
choice=${choice:-2}

case $choice in
    1) add_cron_job 6 0 ;;
    2) add_cron_job 9 0 ;;
    3) add_cron_job 12 0 ;;
    4) add_cron_job 15 0 ;;
    5) add_cron_job 18 0 ;;
    6)
        read -p "Enter hour (0-23): " hour
        read -p "Enter minute (0-59): " minute
        add_cron_job $hour $minute
        ;;
    *) 
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "================================"
echo "✨ SETUP COMPLETE"
echo "================================"
echo ""
echo "📊 Execution Log:"
echo "   $CRON_LOG"
echo ""
echo "📝 To view/edit cron jobs:"
echo "   crontab -e"
echo ""
echo "📋 To view all cron jobs:"
echo "   crontab -l"
echo ""
echo "❌ To remove cron job:"
echo "   crontab -l | grep -v 'dev_pipeline' | crontab -"
echo ""
