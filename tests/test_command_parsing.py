#!/usr/bin/env python3
# ABOUTME: Tests for LLM command parsing functionality using Groq API
# ABOUTME: Validates parsing of voice commands into tmux actions


def test_basic_approve_commands():
    """Test basic approval command variations"""
    from llm_calls import parse_voice_command

    approve_commands = [
        "approve",
        "approve this",
        "approve the request",
        "yes",
        "yes please",
        "accept",
        "ok",
        "okay",
    ]

    for command in approve_commands:
        result = parse_voice_command(command)
        assert result["action"] == "approve", f"Failed for: {command}"
        assert result["tmux_command"] == "A"


def test_basic_reject_commands():
    """Test basic rejection command variations"""
    from llm_calls import parse_voice_command

    reject_commands = [
        "reject",
        "reject this",
        "reject the request",
        "no",
        "no thanks",
        "decline",
        "cancel",
        "deny",
    ]

    for command in reject_commands:
        result = parse_voice_command(command)
        assert result["action"] == "reject", f"Failed for: {command}"
        assert result["tmux_command"] == "R"


def test_text_addition_commands():
    """Test commands that add custom text"""
    from llm_calls import parse_voice_command

    test_cases = [
        ("add the text hello world", "hello world"),
        ("add text hello", "hello"),
        ("type hello world", "hello world"),
        ("enter the text this is a test", "this is a test"),
        ("write hello there", "hello there"),
        ("input some sample text", "some sample text"),
    ]

    for command, expected_text in test_cases:
        result = parse_voice_command(command)
        assert result["action"] == "add_text", f"Failed action for: {command}"
        assert result["text"] == expected_text, f"Failed text for: {command}"
        assert result["tmux_command"] == expected_text


def test_natural_language_variations():
    """Test natural language command variations"""
    from llm_calls import parse_voice_command

    natural_commands = [
        ("I want to approve this", "approve", "A"),
        ("please reject this request", "reject", "R"),
        ("can you approve this", "approve", "A"),
        ("I think we should reject", "reject", "R"),
        ("go ahead and approve", "approve", "A"),
        ("let's reject this", "reject", "R"),
    ]

    for command, expected_action, expected_tmux in natural_commands:
        result = parse_voice_command(command)
        assert result["action"] == expected_action, f"Failed action for: {command}"
        assert result["tmux_command"] == expected_tmux, f"Failed tmux for: {command}"


def test_complex_text_extraction():
    """Test extraction of text from complex sentences"""
    from llm_calls import parse_voice_command

    complex_cases = [
        (
            "I want to add the text please update the documentation",
            "please update the documentation",
        ),
        ("can you type the message hello world from Chile", "hello world from Chile"),
        (
            "please enter this text this is a long message with punctuation",
            "this is a long message with punctuation",
        ),
        (
            "add text with numbers like 123 and symbols",
            "with numbers like 123 and symbols",
        ),
    ]

    for command, expected_text in complex_cases:
        result = parse_voice_command(command)
        assert result["action"] == "add_text", f"Failed action for: {command}"
        assert result["text"] == expected_text, f"Failed text extraction for: {command}"


def test_unclear_commands():
    """Test handling of unclear or ambiguous commands"""
    from llm_calls import parse_voice_command

    unclear_commands = [
        "um maybe",
        "I don't know",
        "what should I do",
        "hmm",
        "well",
        "let me think",
    ]

    for command in unclear_commands:
        result = parse_voice_command(command)
        assert result["action"] == "unclear", f"Failed for unclear command: {command}"
        assert result["tmux_command"] is None


def test_empty_or_invalid_input():
    """Test handling of empty or invalid input"""
    from llm_calls import parse_voice_command

    invalid_inputs = ["", "   ", None]

    for invalid_input in invalid_inputs:
        result = parse_voice_command(invalid_input)
        assert result["action"] == "unclear"
        assert result["tmux_command"] is None


def test_mixed_commands():
    """Test commands that might be ambiguous between approval and text"""
    from llm_calls import parse_voice_command

    # These should be interpreted as approval, not text addition
    mixed_cases = [
        "yes add this feature",  # Should be "approve", not "add text: add this feature"
        "ok write the code",  # Should be "approve", not "add text: write the code"
        "approve and add tests",  # Should be "approve"
    ]

    for command in mixed_cases:
        result = parse_voice_command(command)
        assert result["action"] == "approve", f"Failed mixed command: {command}"


def test_groq_api_fallback():
    """Test fallback behavior when Groq API fails"""
    from llm_calls import parse_voice_command
    from unittest.mock import patch

    # Mock Groq API failure
    with patch(
        "llm_calls.client.chat.completions.create", side_effect=Exception("API Error")
    ):
        result = parse_voice_command("approve this")

        # Should fall back to simple keyword matching
        assert result["action"] == "approve"
        assert result["tmux_command"] == "A"


if __name__ == "__main__":
    # Simple test runner
    test_functions = [
        test_basic_approve_commands,
        test_basic_reject_commands,
        test_text_addition_commands,
        test_natural_language_variations,
        test_complex_text_extraction,
        test_unclear_commands,
        test_empty_or_invalid_input,
        test_mixed_commands,
        test_groq_api_fallback,
    ]

    print("Running command parsing tests...")
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
