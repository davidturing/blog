#!/bin/bash
set -e

# Configuration
AGENT_DIR="skills/self-learning-agent"
LOG_FILE="$AGENT_DIR/logs/pipeline.log"
DATE=$(date +"%Y-%m-%d %H:%M:%S")

mkdir -p "$AGENT_DIR/logs"

echo "[$DATE] Pipeline Start" >> "$LOG_FILE"

# Step 1: Ingest (Batch) - Handles rate limiting internally
echo "[$DATE] Running Ingest..." >> "$LOG_FILE"
python3 "$AGENT_DIR/src/ingest_x_batch.py" >> "$LOG_FILE" 2>&1

# Step 2: Refinery (Process & Knowledge Extraction)
echo "[$DATE] Running Refinery..." >> "$LOG_FILE"
python3 "$AGENT_DIR/src/knowledge_refinery.py" >> "$LOG_FILE" 2>&1

echo "[$DATE] Pipeline Complete" >> "$LOG_FILE"
