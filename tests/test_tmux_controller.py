#!/usr/bin/env python3
# ABOUTME: Tests for tmux controller functionality for Claude Code session control
# ABOUTME: Validates session detection, command sending, and error handling


def test_session_detection():
    """Test detection of active Claude Code tmux session"""
    from tmux_controller import find_claude_session

    # This test requires a running tmux session named "claude-active"
    # We'll test the function logic without requiring actual session
    session_name = find_claude_session()

    # Should return either "claude-active" if session exists, or None
    assert session_name is None or session_name == "claude-active"


def test_session_detection_with_multiple_sessions():
    """Test session detection when multiple sessions exist"""
    from tmux_controller import find_claude_session
    from unittest.mock import patch

    # Mock tmux list-sessions output with multiple sessions
    mock_output = "main: 1 windows (created Thu Sep 19 14:00:00 2025) [100x40]\nclaude-active: 1 windows (created Thu Sep 19 14:30:00 2025) [100x40]\nother: 1 windows (created Thu Sep 19 14:45:00 2025) [100x40]"

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = mock_output
        mock_run.return_value.returncode = 0

        session_name = find_claude_session()
        assert session_name == "claude-active"


def test_session_detection_no_claude_session():
    """Test session detection when no Claude session exists"""
    from tmux_controller import find_claude_session
    from unittest.mock import patch

    # Mock tmux output without claude-active session
    mock_output = "main: 1 windows (created Thu Sep 19 14:00:00 2025) [100x40]\nother: 1 windows (created Thu Sep 19 14:45:00 2025) [100x40]"

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = mock_output
        mock_run.return_value.returncode = 0

        session_name = find_claude_session()
        assert session_name is None


def test_send_approve_command():
    """Test sending approve command to tmux session"""
    from tmux_controller import send_command_to_claude
    from unittest.mock import patch

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0

        result = send_command_to_claude("A")

        # Should have called tmux send-keys twice (command + Enter)
        assert mock_run.call_count == 2

        # Check the calls made
        calls = mock_run.call_args_list
        assert "send-keys" in str(calls[0])
        assert "A" in str(calls[0])
        assert "Enter" in str(calls[1])

        assert result is True


def test_send_reject_command():
    """Test sending reject command to tmux session"""
    from tmux_controller import send_command_to_claude
    from unittest.mock import patch

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0

        result = send_command_to_claude("R")

        # Should have called tmux send-keys twice
        assert mock_run.call_count == 2
        assert result is True


def test_send_custom_text():
    """Test sending custom text to tmux session"""
    from tmux_controller import send_command_to_claude
    from unittest.mock import patch

    custom_text = "hello world"

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0

        result = send_command_to_claude(custom_text)

        # Should have called tmux send-keys twice (text + Enter)
        assert mock_run.call_count == 2

        calls = mock_run.call_args_list
        assert custom_text in str(calls[0])
        assert "Enter" in str(calls[1])

        assert result is True


def test_send_command_session_not_found():
    """Test error handling when Claude session is not found"""
    from tmux_controller import send_command_to_claude
    from unittest.mock import patch

    with patch("tmux_controller.find_claude_session") as mock_find:
        mock_find.return_value = None

        result = send_command_to_claude("A")
        assert result is False


def test_send_command_tmux_error():
    """Test error handling when tmux command fails"""
    from tmux_controller import send_command_to_claude
    from unittest.mock import patch

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1  # Command failed

        result = send_command_to_claude("A")
        assert result is False


def test_execute_parsed_command_approve():
    """Test executing parsed command for approval"""
    from tmux_controller import execute_parsed_command
    from unittest.mock import patch

    command_data = {"action": "approve", "tmux_command": "A", "text": None}

    with patch("tmux_controller.send_command_to_claude") as mock_send:
        mock_send.return_value = True

        result = execute_parsed_command(command_data)

        mock_send.assert_called_once_with("A")
        assert result is True


def test_execute_parsed_command_add_text():
    """Test executing parsed command for text addition"""
    from tmux_controller import execute_parsed_command
    from unittest.mock import patch

    command_data = {
        "action": "add_text",
        "tmux_command": "hello world",
        "text": "hello world",
    }

    with patch("tmux_controller.send_command_to_claude") as mock_send:
        mock_send.return_value = True

        result = execute_parsed_command(command_data)

        mock_send.assert_called_once_with("hello world")
        assert result is True


def test_execute_parsed_command_unclear():
    """Test executing unclear command (should do nothing)"""
    from tmux_controller import execute_parsed_command

    command_data = {"action": "unclear", "tmux_command": None, "text": None}

    result = execute_parsed_command(command_data)
    assert result is False


def test_capture_claude_screen():
    """Test capturing Claude Code screen content"""
    from tmux_controller import capture_claude_screen
    from unittest.mock import patch

    mock_output = "[A]pprove, [R]eject, [M]odify\nWhat would you like to do?"

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = mock_output
        mock_run.return_value.returncode = 0

        content = capture_claude_screen()
        assert content == mock_output


if __name__ == "__main__":
    # Simple test runner
    test_functions = [
        test_session_detection,
        test_session_detection_with_multiple_sessions,
        test_session_detection_no_claude_session,
        test_send_approve_command,
        test_send_reject_command,
        test_send_custom_text,
        test_send_command_session_not_found,
        test_send_command_tmux_error,
        test_execute_parsed_command_approve,
        test_execute_parsed_command_add_text,
        test_execute_parsed_command_unclear,
        test_capture_claude_screen,
    ]

    print("Running tmux controller tests...")
    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
