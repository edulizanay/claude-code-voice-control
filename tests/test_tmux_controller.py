#!/usr/bin/env python3
# ABOUTME: Test version of TMUX controller for enhanced JSON parsing validation
# ABOUTME: Handles new JSON structure with action/text fields and adds mock mode for testing

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


def send_enhanced_command(parsed_result, mock_mode=False):
    """Send command to Claude based on enhanced JSON parsing result

    Args:
        parsed_result: Dict with {"action": "approve/reject/command", "text": "clean_text"}
        mock_mode: If True, print what would be sent instead of sending

    Returns:
        Dict with {"success": bool, "commands_sent": list}
    """

    if not isinstance(parsed_result, dict) or "action" not in parsed_result:
        return {"success": False, "error": "Invalid parsed result format"}

    action = parsed_result["action"]
    text = parsed_result.get("text", "")

    session_name = find_claude_session()
    commands_sent = []

    if not mock_mode and not session_name:
        return {"success": False, "error": "No Claude session found"}

    try:
        if action == "approve":
            # Send Enter key only
            commands_sent.append("Enter")
            if mock_mode:
                print(f"MOCK: Would send Enter to {session_name or 'claude-active'}")
            else:
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
            if mock_mode:
                print(
                    f"MOCK: Would send Escape + '{text}' + Enter to {session_name or 'claude-active'}"
                )
            else:
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
            if mock_mode:
                print(
                    f"MOCK: Would send '{text}' + Enter to {session_name or 'claude-active'}"
                )
            else:
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


# Backward compatibility function that converts old format to new
def send_classified_command(classification, original_speech, mock_mode=False):
    """Backward compatibility wrapper - converts old format to new"""

    # Convert old format to new JSON structure
    if classification == "approve":
        parsed_result = {"action": "approve"}
    elif classification == "reject":
        parsed_result = {"action": "reject", "text": original_speech}
    elif classification == "approve_all":
        # Handle this as a special case (not in new parser yet)
        return {
            "success": False,
            "error": "approve_all not implemented in enhanced parser",
        }
    else:
        parsed_result = {"action": "unclear", "text": original_speech}

    return send_enhanced_command(parsed_result, mock_mode)


if __name__ == "__main__":
    # Test the enhanced controller
    print("Testing Enhanced TMUX Controller...")

    # Test cases with new JSON format
    test_cases = [
        {"action": "approve"},
        {"action": "reject", "text": "add logging"},
        {"action": "command", "text": "run the tests"},
        {"action": "reject", "text": "use async await syntax"},
    ]

    print("\nTesting with mock mode:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case}")
        result = send_enhanced_command(test_case, mock_mode=True)
        print(f"Result: {result}")
