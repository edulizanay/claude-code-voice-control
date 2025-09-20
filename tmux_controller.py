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


def send_classified_command(parsed_result):
    """Send command to Claude based on parsed JSON result

    Args:
        parsed_result: Dict with {"action": "approve/reject/command", "text": "clean_text"}

    Returns:
        Dict with {"success": bool, "commands_sent": list, "error": str}
    """

    if not isinstance(parsed_result, dict) or "action" not in parsed_result:
        return {"success": False, "error": "Invalid parsed result format"}

    action = parsed_result["action"]
    text = parsed_result.get("text", "")

    session_name = find_claude_session()
    commands_sent = []

    if not session_name:
        return {"success": False, "error": "No Claude session found"}

    try:
        if action == "approve":
            # Send Enter key only
            commands_sent.append("Enter")
            result = subprocess.run(
                ["tmux", "send-keys", "-t", session_name, "Enter"],
                capture_output=True,
                check=False,
            )
            if result.returncode != 0:
                return {"success": False, "error": "Failed to send Enter"}

        elif action == "reject":
            # Send Escape + cleaned text + Enter
            commands_sent.extend(["Escape", f"text: {text}", "Enter"])

            # Send Escape
            result1 = subprocess.run(
                ["tmux", "send-keys", "-t", session_name, "Escape"],
                capture_output=True,
                check=False,
            )
            if result1.returncode != 0:
                return {"success": False, "error": "Failed to send Escape"}

            # Send cleaned text (prepend space to avoid cutting first char)
            result2 = subprocess.run(
                ["tmux", "send-keys", "-t", session_name, " " + text],
                capture_output=True,
                check=False,
            )
            if result2.returncode != 0:
                return {"success": False, "error": "Failed to send text"}

            # Send Enter
            result3 = subprocess.run(
                ["tmux", "send-keys", "-t", session_name, "Enter"],
                capture_output=True,
                check=False,
            )
            if result3.returncode != 0:
                return {"success": False, "error": "Failed to send Enter"}

        elif action == "command":
            # Send cleaned text + Enter (for STOP events - new commands)
            commands_sent.extend([f"text: {text}", "Enter"])

            # Send the command text (prepend space to avoid cutting first char)
            result1 = subprocess.run(
                ["tmux", "send-keys", "-t", session_name, " " + text],
                capture_output=True,
                check=False,
            )
            if result1.returncode != 0:
                return {"success": False, "error": "Failed to send command text"}

            # Send Enter
            result2 = subprocess.run(
                ["tmux", "send-keys", "-t", session_name, "Enter"],
                capture_output=True,
                check=False,
            )
            if result2.returncode != 0:
                return {"success": False, "error": "Failed to send Enter"}

        else:
            return {"success": False, "error": f"Unknown action: {action}"}

        return {"success": True, "commands_sent": commands_sent}

    except Exception as e:
        return {"success": False, "error": str(e)}


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
