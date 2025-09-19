#!/bin/bash
HOOK_TYPE=$1
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')

# Create output directory for logging
OUTPUT_DIR="/Users/eduardolizana/Documents/Github/claude-code-voice-control/claude_outputs"
mkdir -p "$OUTPUT_DIR"

# Log that hook fired
echo "[$TIMESTAMP] Hook triggered: $HOOK_TYPE" >> "$OUTPUT_DIR/hooks.log"

# Capture raw stdin data
HOOK_DATA=$(cat)

# Save the raw data for debugging
echo "$HOOK_DATA" > "$OUTPUT_DIR/raw_${HOOK_TYPE}_${TIMESTAMP}.json"

# Log what we captured
echo "[$TIMESTAMP] Captured data for $HOOK_TYPE ($(echo "$HOOK_DATA" | wc -c) bytes)" >> "$OUTPUT_DIR/hooks.log"

# Process with voice control (pass data via stdin)
echo "$HOOK_DATA" | python3 /Users/eduardolizana/Documents/Github/claude-code-voice-control/voice_control_hook.py

# Log completion
echo "[$TIMESTAMP] Voice control processing completed for $HOOK_TYPE" >> "$OUTPUT_DIR/hooks.log"