#!/usr/bin/env python3
# ABOUTME: Complete integration test for enhanced parsing + TMUX controller
# ABOUTME: Tests the full pipeline from voice input to TMUX commands before production implementation

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import the production functions
from llm_calls import parse_voice_command
from tmux_controller import send_classified_command


def test_complete_integration_pipeline(voice_input, event_type, expected_commands):
    """Test complete pipeline: voice → parsing → TMUX commands"""

    # Step 1: Parse voice command with context
    parsed_result = parse_voice_command(voice_input, event_type)

    # Step 2: Remove original_speech for TMUX controller
    tmux_input = {k: v for k, v in parsed_result.items() if k != "original_speech"}

    # Step 3: Send to TMUX controller (will fail with no session, but shows structure)
    tmux_result = send_classified_command(tmux_input)

    return {
        "voice_input": voice_input,
        "event_type": event_type,
        "parsed_result": parsed_result,
        "tmux_input": tmux_input,
        "tmux_result": tmux_result,
        "commands_sent": tmux_result.get("commands_sent", []),
        "success": tmux_result.get("success", False),
    }


class TestCompleteIntegration:
    """Test complete integration of enhanced parsing + TMUX controller"""

    def test_notification_approval_integration(self):
        """Test notification approval: voice → parsing → TMUX"""
        test_cases = [
            ("yes", ["Enter"]),
            ("approve this", ["Enter"]),
            ("sounds good", ["Enter"]),
            ("perfect", ["Enter"]),
        ]

        for voice_input, expected_commands in test_cases:
            result = test_complete_integration_pipeline(
                voice_input, "notification", expected_commands
            )

            assert result["success"], f"Pipeline failed for '{voice_input}'"
            assert result["parsed_result"]["action"] == "approve", (
                f"Wrong parsing for '{voice_input}'"
            )
            assert result["commands_sent"] == expected_commands, (
                f"Wrong commands for '{voice_input}'"
            )

    def test_notification_rejection_integration(self):
        """Test notification rejection with cleaned text"""
        test_cases = [
            # (voice_input, expected_text_contains, expected_command_pattern)
            ("no, add logging instead", "add logging", "text: add logging"),
            ("reject this, use async", "async", "text:"),
            ("nah, try recursion", "recursion", "text:"),
        ]

        for voice_input, expected_text_contains, expected_command_pattern in test_cases:
            result = test_complete_integration_pipeline(
                voice_input, "notification", None
            )

            assert result["success"], f"Pipeline failed for '{voice_input}'"
            assert result["parsed_result"]["action"] == "reject", (
                f"Wrong parsing for '{voice_input}'"
            )

            # Check cleaned text is extracted
            cleaned_text = result["parsed_result"].get("text", "")
            assert expected_text_contains.lower() in cleaned_text.lower(), (
                f"Expected '{expected_text_contains}' in cleaned text '{cleaned_text}'"
            )

            # Check TMUX uses cleaned text
            commands = result["commands_sent"]
            assert ["Escape"] == commands[:1], "Should start with Escape"
            assert "Enter" == commands[-1], "Should end with Enter"
            assert any(expected_command_pattern in cmd for cmd in commands), (
                f"Should contain '{expected_command_pattern}' in {commands}"
            )

    def test_stop_command_integration(self):
        """Test stop event commands"""
        test_cases = [
            ("run the tests", "run the tests"),
            ("add error handling", "add error handling"),
            ("check if tests pass", "check if tests pass"),
        ]

        for voice_input, expected_text_contains in test_cases:
            result = test_complete_integration_pipeline(voice_input, "stop", None)

            assert result["success"], f"Pipeline failed for '{voice_input}'"
            assert result["parsed_result"]["action"] == "command", (
                f"Wrong parsing for '{voice_input}'"
            )

            # Check text is preserved for commands
            command_text = result["parsed_result"].get("text", "")
            assert expected_text_contains.lower() in command_text.lower(), (
                f"Expected '{expected_text_contains}' in command text '{command_text}'"
            )

            # Check TMUX sends text + Enter
            commands = result["commands_sent"]
            assert len(commands) == 2, f"Should have 2 commands, got {commands}"
            assert commands[1] == "Enter", "Should end with Enter"
            assert f"text: {command_text}" == commands[0], "Should send cleaned text"

    def test_stop_command_cleaning_integration(self):
        """Test that stop commands clean filler words"""
        test_cases = [
            # (voice_input, expected_clean_part, words_to_remove)
            ("hmm maybe add logging", "add logging", ["hmm", "maybe"]),
            ("um, let's run the tests", "run the tests", ["um", "let's"]),
            ("go ahead and refactor this", "refactor this", ["go ahead and"]),
        ]

        for voice_input, expected_clean_part, words_to_remove in test_cases:
            result = test_complete_integration_pipeline(voice_input, "stop", None)

            assert result["success"], f"Pipeline failed for '{voice_input}'"
            assert result["parsed_result"]["action"] == "command", (
                f"Wrong parsing for '{voice_input}'"
            )

            # Check cleaning happened
            cleaned_text = result["parsed_result"].get("text", "")
            assert expected_clean_part.lower() in cleaned_text.lower(), (
                f"Expected '{expected_clean_part}' in cleaned text '{cleaned_text}'"
            )

            # Check filler words were removed
            for word in words_to_remove:
                assert word.lower() not in cleaned_text.lower(), (
                    f"Filler word '{word}' should be removed from '{cleaned_text}'"
                )

    def test_context_switching_integration(self):
        """Test same input behaves differently based on event_type"""
        voice_input = "add some logging"

        # Test with notification context
        notification_result = test_complete_integration_pipeline(
            voice_input, "notification", None
        )

        # Test with stop context
        stop_result = test_complete_integration_pipeline(voice_input, "stop", None)

        # Both should succeed
        assert notification_result["success"], "Notification context should succeed"
        assert stop_result["success"], "Stop context should succeed"

        # Should parse differently
        assert notification_result["parsed_result"]["action"] in [
            "reject",
            "unclear",
        ], "Notification should be reject or unclear"
        assert stop_result["parsed_result"]["action"] == "command", (
            "Stop should be command"
        )

        # Should generate different TMUX commands
        notification_commands = notification_result["commands_sent"]
        stop_commands = stop_result["commands_sent"]
        assert notification_commands != stop_commands, (
            "Should generate different commands"
        )

    def test_cleaned_vs_original_text_integration(self):
        """Test that TMUX gets cleaned text, not original speech"""
        voice_input = "no, add logging instead"

        result = test_complete_integration_pipeline(voice_input, "notification", None)

        assert result["success"], "Pipeline should succeed"
        assert result["parsed_result"]["action"] == "reject", "Should be rejection"

        # Original speech should be preserved in parsing result
        assert result["parsed_result"]["original_speech"] == voice_input, (
            "Should preserve original speech"
        )

        # But TMUX should get cleaned text
        cleaned_text = result["parsed_result"]["text"]
        commands = result["commands_sent"]

        # Check cleaned text doesn't contain filler words
        assert "no," not in cleaned_text, "Cleaned text shouldn't contain 'no,'"
        assert "instead" not in cleaned_text, "Cleaned text shouldn't contain 'instead'"
        assert "add logging" in cleaned_text, "Should contain core instruction"

        # Check TMUX uses cleaned text
        text_command = next((cmd for cmd in commands if cmd.startswith("text:")), None)
        assert text_command, "Should have text command"
        assert "add logging" in text_command, "TMUX should use cleaned text"
        assert "no," not in text_command, "TMUX shouldn't get filler words"

    def test_integration_error_handling(self):
        """Test error handling in complete pipeline"""
        # Test empty input
        result = test_complete_integration_pipeline("", "notification", None)
        assert result["parsed_result"]["action"] == "unclear", (
            "Empty input should be unclear"
        )

        # Test invalid action (shouldn't happen in real usage)
        fake_parsed = {"action": "invalid_action"}
        tmux_result = send_enhanced_command(fake_parsed, mock_mode=True)
        assert not tmux_result["success"], "Invalid action should fail"

    def test_all_integration_scenarios(self):
        """Test comprehensive integration scenarios"""
        scenarios = [
            # (voice_input, event_type, expected_action, expected_command_count)
            ("yes", "notification", "approve", 1),
            ("no, use async", "notification", "reject", 3),
            ("run tests", "stop", "command", 2),
            ("hmm maybe add logging", "stop", "command", 2),
        ]

        for (
            voice_input,
            event_type,
            expected_action,
            expected_command_count,
        ) in scenarios:
            result = test_complete_integration_pipeline(voice_input, event_type, None)

            assert result["success"], f"Scenario failed: {voice_input} ({event_type})"
            assert result["parsed_result"]["action"] == expected_action, (
                f"Wrong action for: {voice_input} ({event_type})"
            )
            assert len(result["commands_sent"]) == expected_command_count, (
                f"Wrong command count for: {voice_input} ({event_type})"
            )


def run_all_tests():
    """Run all integration tests"""
    test_instance = TestCompleteIntegration()

    test_methods = [
        test_instance.test_notification_approval_integration,
        test_instance.test_notification_rejection_integration,
        test_instance.test_stop_command_integration,
        test_instance.test_stop_command_cleaning_integration,
        test_instance.test_context_switching_integration,
        test_instance.test_cleaned_vs_original_text_integration,
        test_instance.test_integration_error_handling,
        test_instance.test_all_integration_scenarios,
    ]

    print("🔗 Running Complete Integration Tests")
    print("=" * 60)
    print("Testing: Enhanced Parsing → Enhanced TMUX Controller")
    print("=" * 60)

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

    print(f"\n📊 Integration Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Enhanced parsing + TMUX controller integration is working")
        print("✅ Ready to implement in production files")
    else:
        print(f"\n❌ {failed} integration tests failed")
        print("🔧 Fix issues before implementing in production")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
