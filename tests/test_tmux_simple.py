#!/usr/bin/env python3
# ABOUTME: Simple test script for TMUX voice command classification and sending
# ABOUTME: Tests the new simplified voice command system without voice pipeline

from llm_calls import parse_voice_command
from tmux_controller import (
    send_classified_command,
    find_claude_session,
    get_claude_status,
)


def test_classification_only():
    """Test just the classification without sending to TMUX"""
    print("=== CLASSIFICATION TEST MODE ===")
    print("Testing LLM classification without sending commands to Claude")
    print("Type 'quit' to exit\n")

    while True:
        try:
            user_input = input("Enter text to classify: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                break

            if not user_input:
                continue

            # Test classification
            classification, original_speech = parse_voice_command(user_input)
            print(f"  Input: '{user_input}'")
            print(f"  Classification: '{classification}'")
            print(f"  Original speech: '{original_speech}'")

            # Show what would be sent to TMUX
            if classification == "approve":
                print("  → Would send: Enter key")
            elif classification == "approve_all":
                print("  → Would send: Shift+Tab key")
            elif classification == "reject":
                print(f"  → Would send: Escape + '{original_speech}' + Enter")
            else:
                print("  → Would send: Nothing (unclear)")
            print()

        except KeyboardInterrupt:
            print("\nExiting...")
            break


def test_with_claude():
    """Test with actual Claude Code session"""
    print("=== CLAUDE INTEGRATION TEST MODE ===")
    print("Testing with actual Claude Code session")
    print("Type 'quit' to exit\n")

    # Check for Claude session first
    session = find_claude_session()
    if not session:
        print("❌ No Claude session found!")
        print('Start Claude Code with: tmux new-session -s claude-active "claude"')
        return

    print(f"✅ Found Claude session: {session}")

    # Show current status
    status = get_claude_status()
    print(f"   Waiting for input: {status['waiting_for_input']}")

    if status["screen_content"]:
        print("\nCurrent Claude screen (last 200 chars):")
        print("-" * 40)
        print(status["screen_content"][-200:])
        print("-" * 40)

    print("\n⚠️  WARNING: Commands will be sent to Claude Code!")
    print("Make sure Claude is ready to receive commands.")

    confirm = input("\nProceed with sending commands? (y/N): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    while True:
        try:
            user_input = input("\nEnter command to send: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                break

            if not user_input:
                continue

            # Classify command
            classification, original_speech = parse_voice_command(user_input)
            print(f"  Classification: '{classification}'")
            print(f"  Original speech: '{original_speech}'")

            if classification == "unclear":
                print("  → Skipping unclear command")
                continue

            # Send to Claude
            print("  → Sending to Claude...")
            success = send_classified_command(classification, original_speech)

            if success:
                print("  ✅ Command sent successfully")

                # Show updated screen
                new_status = get_claude_status()
                if new_status["screen_content"]:
                    print("\nUpdated Claude screen (last 200 chars):")
                    print("-" * 40)
                    print(new_status["screen_content"][-200:])
                    print("-" * 40)
            else:
                print("  ❌ Failed to send command")

        except KeyboardInterrupt:
            print("\nExiting...")
            break


def run_predefined_tests():
    """Run predefined test cases"""
    print("=== PREDEFINED TEST CASES ===")

    test_cases = [
        "yes",
        "approve",
        "approve all changes",
        "no",
        "reject",
        "no this is completely wrong",
        "I disagree with this approach",
        "unclear command",
        "maybe",
    ]

    for test_input in test_cases:
        classification, original_speech = parse_voice_command(test_input)
        print(f"'{test_input}' → '{classification}' | original: '{original_speech}'")


def main():
    """Main test interface"""
    print("TMUX Voice Command Test Script")
    print("=" * 40)

    while True:
        print("\nSelect test mode:")
        print("1. Classification only (safe)")
        print("2. Test with Claude Code (sends real commands)")
        print("3. Run predefined test cases")
        print("4. Exit")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            test_classification_only()
        elif choice == "2":
            test_with_claude()
        elif choice == "3":
            run_predefined_tests()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
