#!/bin/bash

echo "=== SIMPLE TMUX TEST ==="

# Kill any old test session
tmux kill-session -t test 2>/dev/null

# Start a session with bash that stays open
echo "1. Starting tmux session..."
tmux new-session -d -s test "bash"

# Send a command to it
echo "2. Sending 'echo Hello from kitchen!' to the session..."
tmux send-keys -t test "echo 'Hello from kitchen!'" Enter

# Wait a moment
sleep 0.5

# Show what's on screen
echo "3. What's displayed in the session:"
tmux capture-pane -t test -p

# Send another command
echo "4. Sending another command..."
tmux send-keys -t test "echo 'This simulates your voice command'" Enter

sleep 0.5

echo "5. Updated screen:"
tmux capture-pane -t test -p

# Clean up
tmux kill-session -t test
echo "✅ Done! If you saw the messages above, tmux remote control works!"