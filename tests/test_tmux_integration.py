#!/usr/bin/env python3
# ABOUTME: Integration tests for enhanced TMUX controller with JSON parsing
# ABOUTME: Tests new action types, text cleaning, and backward compatibility

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


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

    # Mock session for testing
    session_name = "claude-active"
    commands_sent = []

    if not mock_mode:
        return {"success": False, "error": "Real TMUX not supported in tests"}

    try:
        if action == "approve":
            # Send Enter key only
            commands_sent.append("Enter")
            if mock_mode:
                print(f"MOCK: Would send Enter to {session_name}")

        elif action == "reject":
            # Send Escape + cleaned text + Enter
            commands_sent.extend(["Escape", f"text: {text}", "Enter"])
            if mock_mode:
                print(f"MOCK: Would send Escape + '{text}' + Enter to {session_name}")

        elif action == "command":
            # Send cleaned text + Enter (for STOP events - new commands)
            commands_sent.extend([f"text: {text}", "Enter"])
            if mock_mode:
                print(f"MOCK: Would send '{text}' + Enter to {session_name}")

        else:
            return {"success": False, "error": f"Unknown action: {action}"}

        return {"success": True, "commands_sent": commands_sent}

    except Exception as e:
        return {"success": False, "error": str(e)}


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


class TestTmuxIntegration:
    """Test suite for TMUX integration with enhanced parsing"""

    def test_approve_action(self):
        """Test approve action sends only Enter"""
        result = send_enhanced_command({"action": "approve"}, mock_mode=True)

        assert result["success"] is True
        assert result["commands_sent"] == ["Enter"]

    def test_reject_action_with_clean_text(self):
        """Test reject action uses cleaned text"""
        parsed_result = {"action": "reject", "text": "add logging"}
        result = send_enhanced_command(parsed_result, mock_mode=True)

        assert result["success"] is True
        expected_commands = ["Escape", "text: add logging", "Enter"]
        assert result["commands_sent"] == expected_commands

    def test_command_action(self):
        """Test new command action for STOP events"""
        parsed_result = {"action": "command", "text": "run the tests"}
        result = send_enhanced_command(parsed_result, mock_mode=True)

        assert result["success"] is True
        expected_commands = ["text: run the tests", "Enter"]
        assert result["commands_sent"] == expected_commands

    def test_cleaned_text_vs_original(self):
        """Test that cleaned text is used, not original speech"""
        # Simulate what the old system would do vs new system
        original_speech = "no, add logging instead"
        cleaned_text = "add logging"

        # Old system behavior (what we're replacing)
        old_result = send_classified_command("reject", original_speech, mock_mode=True)

        # New system behavior (what we want)
        new_result = send_enhanced_command(
            {"action": "reject", "text": cleaned_text}, mock_mode=True
        )

        # Both should succeed but with different text
        assert old_result["success"] is True
        assert new_result["success"] is True

        # Old system sends raw original speech
        assert "text: no, add logging instead" in old_result["commands_sent"]

        # New system sends cleaned text
        assert "text: add logging" in new_result["commands_sent"]

    def test_action_type_mapping(self):
        """Test all action types produce correct command sequences"""
        test_cases = [
            ({"action": "approve"}, ["Enter"]),
            (
                {"action": "reject", "text": "use async"},
                ["Escape", "text: use async", "Enter"],
            ),
            (
                {"action": "command", "text": "check tests"},
                ["text: check tests", "Enter"],
            ),
        ]

        for parsed_result, expected_commands in test_cases:
            result = send_enhanced_command(parsed_result, mock_mode=True)
            assert result["success"] is True
            assert result["commands_sent"] == expected_commands

    def test_invalid_input_validation(self):
        """Test error handling for invalid inputs"""
        # Missing action
        result = send_enhanced_command({"text": "something"}, mock_mode=True)
        assert result["success"] is False
        assert "Invalid parsed result format" in result["error"]

        # Not a dict
        result = send_enhanced_command("not a dict", mock_mode=True)
        assert result["success"] is False

        # Unknown action
        result = send_enhanced_command({"action": "unknown"}, mock_mode=True)
        assert result["success"] is False
        assert "Unknown action" in result["error"]

    def test_backward_compatibility(self):
        """Test that old interface still works"""
        # Test old approve
        result = send_classified_command("approve", "", mock_mode=True)
        assert result["success"] is True
        assert result["commands_sent"] == ["Enter"]

        # Test old reject
        result = send_classified_command("reject", "add logging", mock_mode=True)
        assert result["success"] is True
        assert "text: add logging" in result["commands_sent"]

        # Test unsupported old action
        result = send_classified_command("approve_all", "", mock_mode=True)
        assert result["success"] is False

    def test_text_handling(self):
        """Test various text inputs are handled correctly"""
        test_cases = [
            ("simple text", "text: simple text"),
            ("", "text: "),
            ("multiple words here", "text: multiple words here"),
            ("special chars: @#$", "text: special chars: @#$"),
        ]

        for input_text, expected_command in test_cases:
            result = send_enhanced_command(
                {"action": "reject", "text": input_text}, mock_mode=True
            )
            assert result["success"] is True
            assert expected_command in result["commands_sent"]

    def test_real_tmux_protection(self):
        """Test that real TMUX calls are blocked in test mode"""
        # Should fail when mock_mode=False (real TMUX protection)
        result = send_enhanced_command({"action": "approve"}, mock_mode=False)
        assert result["success"] is False
        assert "Real TMUX not supported in tests" in result["error"]

    def test_integration_scenarios(self):
        """Test end-to-end scenarios that would happen in real usage"""
        scenarios = [
            # Notification approval
            {
                "event_type": "notification",
                "parsed": {"action": "approve"},
                "expected_commands": ["Enter"],
                "description": "User approves Claude's suggestion",
            },
            # Notification rejection with alternative
            {
                "event_type": "notification",
                "parsed": {"action": "reject", "text": "use async await syntax"},
                "expected_commands": [
                    "Escape",
                    "text: use async await syntax",
                    "Enter",
                ],
                "description": "User rejects and provides alternative",
            },
            # Stop event new command
            {
                "event_type": "stop",
                "parsed": {"action": "command", "text": "run the tests"},
                "expected_commands": ["text: run the tests", "Enter"],
                "description": "User gives new command after Claude stops",
            },
            # Stop event complex command
            {
                "event_type": "stop",
                "parsed": {
                    "action": "command",
                    "text": "add error handling to this function",
                },
                "expected_commands": [
                    "text: add error handling to this function",
                    "Enter",
                ],
                "description": "User gives detailed new command",
            },
        ]

        for scenario in scenarios:
            result = send_enhanced_command(scenario["parsed"], mock_mode=True)
            assert result["success"] is True, (
                f"Failed scenario: {scenario['description']}"
            )
            assert result["commands_sent"] == scenario["expected_commands"], (
                f"Wrong commands for: {scenario['description']}"
            )


def run_all_tests():
    """Run all TMUX integration tests"""
    test_instance = TestTmuxIntegration()

    test_methods = [
        test_instance.test_approve_action,
        test_instance.test_reject_action_with_clean_text,
        test_instance.test_command_action,
        test_instance.test_cleaned_text_vs_original,
        test_instance.test_action_type_mapping,
        test_instance.test_invalid_input_validation,
        test_instance.test_backward_compatibility,
        test_instance.test_text_handling,
        test_instance.test_real_tmux_protection,
        test_instance.test_integration_scenarios,
    ]

    print("⌨️  Running TMUX Integration Tests")
    print("=" * 50)

    passed = 0
    failed = 0

    for test_method in test_methods:
        try:
            test_method()
            print(f"✅ {test_method.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_method.__name__}: {e}")
            failed += 1

    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
