#!/usr/bin/env python3
# ABOUTME: Unit tests for enhanced voice command parsing with context awareness
# ABOUTME: Tests event_type switching, text cleaning, and edge cases

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
client = Groq()


def enhanced_parse_voice_command(speech_text, event_type="notification"):
    """Enhanced voice command parser with context-aware prompts"""

    if not speech_text or not speech_text.strip():
        return {"action": "unclear", "text": speech_text}

    original_speech = speech_text.strip()

    # Choose prompt based on event type
    if event_type == "notification":
        system_prompt = """You are parsing voice commands when Claude Code is waiting for approval/rejection.

Context: Claude just made a suggestion and is waiting for user response.

Categories:
- 'approve': user agrees (→ send Enter key only)
- 'reject': user disagrees and gives alternative (→ send Escape + alternative text + Enter)

<thinking>
1. Is the user agreeing or disagreeing with Claude's suggestion?
2. If disagreeing, what alternative text should be sent to Claude?
3. Remove filler words like "no", "instead", "reject", "actually", "nah" from the actionable text.
4. Ignore any "and then" future commands - focus only on the current approval/rejection.
</thinking>

<response>
Return JSON format:
For approval: {"action": "approve"}
For rejection: {"action": "reject", "text": "clean alternative text"}
For unclear: {"action": "unclear"}
</response>"""

    else:  # event_type == "stop"
        system_prompt = """You are parsing voice commands when Claude Code is ready for new input.

Context: Claude finished a task and is ready for the next command.

Categories:
- 'command': user gives new instruction (→ send text + Enter)

<thinking>
1. What command does the user want to send to Claude?
2. Clean up the text but preserve the core instruction.
3. Remove hesitation words like "hmm", "maybe", "um", "actually", "you know what" but keep the actual command.
4. Remove temporal words like "now", "let's", "go ahead and" but keep the action.
</thinking>

<response>
Return JSON format:
For command: {"action": "command", "text": "clean command text"}
For unclear: {"action": "unclear"}
</response>"""

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Voice: {original_speech}"},
            ],
            temperature=0.1,
            max_completion_tokens=300,
            top_p=1,
            stream=False,
        )

        # Extract content from response
        full_response = completion.choices[0].message.content

        # Try to parse JSON from response
        try:
            # Look for JSON in the response
            start_idx = full_response.find("{")
            end_idx = full_response.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = full_response[start_idx:end_idx]
                result = json.loads(json_str)
                result["original_speech"] = original_speech
                return result
        except json.JSONDecodeError:
            pass

        # Fallback to unclear if JSON parsing fails
        return {"action": "unclear", "text": original_speech}

    except Exception as e:
        print(f"Error: {e}")
        return {"action": "unclear", "text": original_speech}


class TestEnhancedParsing:
    """Test suite for enhanced voice command parsing"""

    def test_notification_approvals(self):
        """Test various approval patterns for notifications"""
        test_cases = [
            ("yes", {"action": "approve"}),
            ("approve", {"action": "approve"}),
            ("sounds good", {"action": "approve"}),
            ("perfect", {"action": "approve"}),
            ("go ahead", {"action": "approve"}),
            ("that works", {"action": "approve"}),
        ]

        for input_text, expected in test_cases:
            result = enhanced_parse_voice_command(input_text, "notification")
            actual = {k: v for k, v in result.items() if k != "original_speech"}
            assert actual == expected, (
                f"Failed for '{input_text}': expected {expected}, got {actual}"
            )

    def test_notification_rejections(self):
        """Test rejection patterns with alternatives for notifications"""
        test_cases = [
            ("no, add logging", {"action": "reject", "text": "add logging"}),
            (
                "reject this, use async instead",
                {"action": "reject", "text": "use async"},
            ),
            (
                "nah, I'd rather use recursion",
                {"action": "reject", "text": "use recursion"},
            ),
            (
                "not quite, make it return a promise",
                {"action": "reject", "text": "make it return a promise"},
            ),
        ]

        for input_text, expected in test_cases:
            result = enhanced_parse_voice_command(input_text, "notification")
            actual = {k: v for k, v in result.items() if k != "original_speech"}
            # For rejections, we check action and that text is reasonable (LLM may vary slightly)
            assert actual["action"] == expected["action"], (
                f"Wrong action for '{input_text}'"
            )
            assert "text" in actual, f"Missing text for rejection '{input_text}'"
            assert len(actual["text"]) > 0, f"Empty text for rejection '{input_text}'"

    def test_stop_commands(self):
        """Test command patterns for stop events"""
        test_cases = [
            ("run the tests", {"action": "command", "text": "run the tests"}),
            ("add error handling", {"action": "command", "text": "add error handling"}),
            (
                "check if tests pass",
                {"action": "command", "text": "check if tests pass"},
            ),
            (
                "refactor this function",
                {"action": "command", "text": "refactor this function"},
            ),
        ]

        for input_text, expected in test_cases:
            result = enhanced_parse_voice_command(input_text, "stop")
            actual = {k: v for k, v in result.items() if k != "original_speech"}
            # For commands, we check action and that text is reasonable
            assert actual["action"] == expected["action"], (
                f"Wrong action for '{input_text}'"
            )
            assert "text" in actual, f"Missing text for command '{input_text}'"
            assert len(actual["text"]) > 0, f"Empty text for command '{input_text}'"

    def test_text_cleaning(self):
        """Test that filler words are properly removed"""
        test_cases = [
            # Notification rejections should clean filler words
            ("no, add logging instead", "notification", "add logging"),
            ("reject this, I want async", "notification", "async"),
            ("nah, use recursion", "notification", "recursion"),
            # Stop commands should clean hesitation words
            ("hmm maybe add logging", "stop", "add logging"),
            ("um, can you refactor this", "stop", "refactor this"),
            ("let's go ahead and run tests", "stop", "run tests"),
        ]

        for input_text, event_type, expected_clean_part in test_cases:
            result = enhanced_parse_voice_command(input_text, event_type)
            actual_text = result.get("text", "")

            # Check that the cleaned text contains the expected clean part
            assert expected_clean_part.lower() in actual_text.lower(), (
                f"Expected '{expected_clean_part}' in cleaned text '{actual_text}' for '{input_text}'"
            )

    def test_context_switching(self):
        """Test that same input produces different results based on event_type"""
        # Same input should behave differently for notification vs stop
        input_text = "add some logging"

        notification_result = enhanced_parse_voice_command(input_text, "notification")
        stop_result = enhanced_parse_voice_command(input_text, "stop")

        # In notification context, this might be unclear or reject
        # In stop context, this should be a command
        assert stop_result["action"] == "command", "Stop event should parse as command"
        assert notification_result["action"] in ["reject", "unclear"], (
            "Notification should be reject or unclear"
        )

    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        # Empty input
        result = enhanced_parse_voice_command("", "notification")
        assert result["action"] == "unclear"

        # None input
        result = enhanced_parse_voice_command(None, "notification")
        assert result["action"] == "unclear"

        # Whitespace only
        result = enhanced_parse_voice_command("   ", "notification")
        assert result["action"] == "unclear"

        # Invalid event_type defaults to notification behavior
        result = enhanced_parse_voice_command("yes", "invalid_event")
        assert result["action"] == "approve"

    def test_future_commands_ignored(self):
        """Test that future commands in approvals are ignored"""
        test_cases = [
            "approve this and then run tests",
            "sounds good, after this we should add logging",
            "perfect, and later implement error handling",
        ]

        for input_text in test_cases:
            result = enhanced_parse_voice_command(input_text, "notification")
            # Should be approval, not command or reject
            assert result["action"] == "approve", (
                f"'{input_text}' should be approval, not {result['action']}"
            )


def run_all_tests():
    """Run all unit tests"""
    test_instance = TestEnhancedParsing()

    test_methods = [
        test_instance.test_notification_approvals,
        test_instance.test_notification_rejections,
        test_instance.test_stop_commands,
        test_instance.test_text_cleaning,
        test_instance.test_context_switching,
        test_instance.test_edge_cases,
        test_instance.test_future_commands_ignored,
    ]

    print("🧪 Running Enhanced Parsing Unit Tests")
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
