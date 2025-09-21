#!/bin/bash
# ABOUTME: Production hook script that triggers voice control pipeline
# ABOUTME: Captures Claude's hook data and runs voice pipeline in background

# Uncomment the line below to pause voice control for testing
 exit 0

HOOK_TYPE=$1
TIMESTAMP=$(date '+%H:%M:%S')


echo "[$TIMESTAMP] 🎣 Hook triggered: $HOOK_TYPE" >> /tmp/debug.log
echo "[$TIMESTAMP] 🎣 Hook triggered: $HOOK_TYPE"

# Capture raw stdin data
HOOK_DATA=$(cat)
DATA_SIZE=$(echo "$HOOK_DATA" | wc -c)

echo "[$TIMESTAMP] 📦 Captured $DATA_SIZE bytes of hook data"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run voice control pipeline in background and exit immediately
echo "[$TIMESTAMP] 🚀 Starting voice control pipeline in background..."
(echo "$HOOK_DATA" | python3 "$SCRIPT_DIR/voice_control_main.py" "$HOOK_TYPE" 2>&1) &

echo "[$TIMESTAMP] ✅ Hook returned control to Claude"
exit 0