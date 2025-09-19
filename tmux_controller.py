#!/usr/bin/env python3
# ABOUTME: TMUX controller for sending commands to Claude Code sessions
# ABOUTME: Handles session detection, command sending, and screen capture

import subprocess
import re


def find_claude_session():
    """Find active Claude Code tmux session"""
    try:
        # List all tmux sessions
        result = subprocess.run(
            ["tmux", "list-sessions"], capture_output=True, text=True, check=False
        )

        if result.returncode != 0:
            return None

        # Look for session named "claude-active"
        sessions = result.stdout.strip().split("\n")
        for session_line in sessions:
            if session_line.startswith("claude-active:"):
                return "claude-active"

        return None

    except Exception:
        return None


def send_command_to_claude(command):
    """Send command to Claude Code tmux session"""

    # Find Claude session
    session_name = find_claude_session()
    if not session_name:
        return False

    try:
        # Send the command
        result1 = subprocess.run(
            ["tmux", "send-keys", "-t", session_name, command],
            capture_output=True,
            check=False,
        )

        if result1.returncode != 0:
            return False

        # Send Enter key
        result2 = subprocess.run(
            ["tmux", "send-keys", "-t", session_name, "Enter"],
            capture_output=True,
            check=False,
        )

        return result2.returncode == 0

    except Exception:
        return False


def execute_parsed_command(command_data):
    """Execute parsed voice command using tmux"""

    action = command_data.get("action")
    tmux_command = command_data.get("tmux_command")

    if action == "unclear" or not tmux_command:
        return False

    # Send the command to Claude
    return send_command_to_claude(tmux_command)


def capture_claude_screen():
    """Capture current Claude Code screen content"""

    session_name = find_claude_session()
    if not session_name:
        return None

    try:
        result = subprocess.run(
            ["tmux", "capture-pane", "-t", session_name, "-p"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            return result.stdout
        else:
            return None

    except Exception:
        return None


def is_claude_waiting_for_input():
    """Check if Claude is waiting for user input"""

    screen_content = capture_claude_screen()
    if not screen_content:
        return False

    # Look for common Claude Code prompts
    waiting_patterns = [
        r"\[A\]pprove",
        r"\[R\]eject",
        r"\[M\]odify",
        r"What would you like to do",
        r"Please choose",
        r"Enter your choice",
    ]

    screen_lower = screen_content.lower()
    for pattern in waiting_patterns:
        if re.search(pattern.lower(), screen_lower):
            return True

    return False


def get_claude_status():
    """Get current status of Claude Code session"""

    session_name = find_claude_session()
    if not session_name:
        return {
            "session_found": False,
            "waiting_for_input": False,
            "screen_content": None,
        }

    screen_content = capture_claude_screen()
    waiting = is_claude_waiting_for_input()

    return {
        "session_found": True,
        "waiting_for_input": waiting,
        "screen_content": screen_content,
    }


if __name__ == "__main__":
    # Test the controller
    print("Testing TMUX controller...")

    # Check session
    session = find_claude_session()
    print(f"Claude session: {session}")

    if session:
        # Get status
        status = get_claude_status()
        print(f"Waiting for input: {status['waiting_for_input']}")

        # Show screen content
        if status["screen_content"]:
            print("\nClaude screen content:")
            print("-" * 40)
            print(status["screen_content"])
            print("-" * 40)

        # Test command (uncomment to test with real session)
        # print("\nSending test command...")
        # result = send_command_to_claude("A")
        # print(f"Command sent: {result}")

    else:
        print("No Claude session found. Start Claude Code with:")
        print('tmux new-session -s claude-active "claude"')
