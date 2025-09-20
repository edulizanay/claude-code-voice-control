#!/usr/bin/env python3
# ABOUTME: Simplified TMUX controller for sending commands to Claude Code sessions
# ABOUTME: Handles session detection and 5 command types: approve, approve_all, reject, single_escape, double_escape

import subprocess


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


def send_classified_command(classification, original_speech):
    """Send command to Claude based on simple classification"""

    session_name = find_claude_session()
    if not session_name:
        return False

    try:
        if classification == "approve":
            # Send Enter key
            result = subprocess.run(
                ["tmux", "send-keys", "-t", session_name, "Enter"],
                capture_output=True,
                check=False,
            )
            return result.returncode == 0

        elif classification == "approve_all":
            # Send Shift+Tab (BTab is the correct tmux syntax)
            result = subprocess.run(
                ["tmux", "send-keys", "-t", session_name, "BTab"],
                capture_output=True,
                check=False,
            )
            return result.returncode == 0

        elif classification == "reject":
            # Send Escape, then original speech, then Enter
            # First send Escape
            result1 = subprocess.run(
                ["tmux", "send-keys", "-t", session_name, "Escape"],
                capture_output=True,
                check=False,
            )
            if result1.returncode != 0:
                return False

            # Then send the original speech text (prepend space to avoid cutting first char)
            result2 = subprocess.run(
                ["tmux", "send-keys", "-t", session_name, " " + original_speech],
                capture_output=True,
                check=False,
            )
            if result2.returncode != 0:
                return False

            # Finally send Enter
            result3 = subprocess.run(
                ["tmux", "send-keys", "-t", session_name, "Enter"],
                capture_output=True,
                check=False,
            )
            return result3.returncode == 0

        elif classification == "single_escape":
            # Send single Escape key
            result = subprocess.run(
                ["tmux", "send-keys", "-t", session_name, "Escape"],
                capture_output=True,
                check=False,
            )
            return result.returncode == 0

        elif classification == "double_escape":
            # Send double Escape (closes Claude Code)
            result1 = subprocess.run(
                ["tmux", "send-keys", "-t", session_name, "Escape"],
                capture_output=True,
                check=False,
            )
            if result1.returncode != 0:
                return False

            result2 = subprocess.run(
                ["tmux", "send-keys", "-t", session_name, "Escape"],
                capture_output=True,
                check=False,
            )
            return result2.returncode == 0

        else:  # unclear or unknown
            return False

    except Exception:
        return False


def get_claude_status():
    """Get basic status of Claude Code session"""

    session_name = find_claude_session()
    if not session_name:
        return {"session_found": False}

    return {"session_found": True}


if __name__ == "__main__":
    # Test the controller
    print("Testing TMUX controller...")

    # Check session
    session = find_claude_session()
    print(f"Claude session: {session}")

    if session:
        # Get status
        status = get_claude_status()
        print(f"Session found: {status['session_found']}")
    else:
        print("No Claude session found. Start Claude Code with:")
        print('tmux new-session -s claude-active "claude"')
