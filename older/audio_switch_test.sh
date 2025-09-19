#!/bin/bash

echo "=== AIRPODS AUDIO SWITCH TEST ==="
echo "Make sure your AirPods are connected!"
echo "Press Enter to start..."
read

# Play a short sound through AirPods
echo "1. Playing audio through AirPods..."
say "Claude finished. What should I do?"

# Immediately start recording
echo "2. Recording starting NOW - speak immediately!"
echo "   (Say something like 'Hello testing one two three')"

# Record for 5 seconds to a file
sox -d -r 44100 -c 1 test_recording.wav trim 0 25

echo "3. Recording complete. Playing it back..."

# Play back what was recorded
afplay test_recording.wav

echo ""
echo "=== RESULTS ==="
echo "Did you hear your voice clearly in the playback?"
echo "- YES = AirPods switched fast enough ✅"
echo "- NO/Silent = AirPods too slow switching ❌"
echo ""
echo "Recording saved as: test_recording.wav"