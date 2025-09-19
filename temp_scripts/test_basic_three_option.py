#!/usr/bin/env python3
# ABOUTME: Basic three-option system test without requiring Groq API
# ABOUTME: Tests detection and TMUX functions without LLM parsing

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tmux_controller import (
    find_claude_session,
    capture_claude_screen,
    send_approve,
    send_approve_all,
    send_reject_with_text,
)
from temp_scripts.approval_test import is_claude_waiting_for_approval


def test_basic_detection():
    """Test basic Claude session detection and prompt recognition"""
    print("=== BASIC THREE-OPTION DETECTION TEST ===")

    # Check for Claude session
    session = find_claude_session()
    if not session:
        print("❌ No Claude session found!")
        print("Start Claude Code with:")
        print('tmux new-session -s claude-active "claude"')
        print("\nThen trigger a permission prompt with:")
        print('write some_file.txt "test content"')
        return False

    print(f"✅ Found Claude session: {session}")

    # Show current screen
    print("\n📸 Current Claude screen:")
    screen = capture_claude_screen()
    if screen:
        print("-" * 60)
        print(screen[-500:])  # Show last 500 chars for more context
        print("-" * 60)

        # Test our detection
        waiting, reason = is_claude_waiting_for_approval()
        print(f"\n🔍 Approval detection result: {waiting}")
        print(f"   Detection reason: {reason}")

        if waiting:
            print("\n✅ SUCCESS: Claude is waiting for approval!")
            print("   The three-option system should be ready to test")
            return True
        else:
            print("\n⚠️  Claude doesn't appear to be waiting for approval")
            print("   You may need to trigger a permission request first")
            print('   Try running in Claude: write test_file.txt "hello world"')
            return False
    else:
        print("❌ Could not capture screen content")
        return False


def test_manual_commands():
    """Test manual command sending"""
    print("\n=== MANUAL COMMAND TEST ===")

    session = find_claude_session()
    if not session:
        print("❌ No Claude session found!")
        return False

    print("Available commands:")
    print("  1. Test approve (Enter)")
    print("  2. Test approve all (Shift+Tab)")
    print("  3. Test reject with text (Esc + text + Enter)")
    print("  4. Show current screen")
    print("  5. Quit")

    while True:
        try:
            choice = input("\nEnter choice (1-5): ").strip()

            if choice == "1":
                print("Sending approve command (Enter)...")
                success = send_approve()
                print("✅ Sent successfully" if success else "❌ Failed")

            elif choice == "2":
                print("Sending approve all command (Shift+Tab)...")
                success = send_approve_all()
                print("✅ Sent successfully" if success else "❌ Failed")

            elif choice == "3":
                text = input("Enter rejection text (or leave empty): ").strip()
                if not text:
                    text = None
                print(f"Sending reject command with text: '{text}'...")
                success = send_reject_with_text(text)
                print("✅ Sent successfully" if success else "❌ Failed")

            elif choice == "4":
                screen = capture_claude_screen()
                if screen:
                    print("\nCurrent screen:")
                    print("-" * 50)
                    print(screen[-400:])
                    print("-" * 50)
                else:
                    print("Could not capture screen")

            elif choice == "5":
                print("👋 Goodbye!")
                break

            else:
                print("Invalid choice. Please enter 1-5.")

            # Show updated screen after command
            if choice in ["1", "2", "3"]:
                print("\nUpdated screen:")
                screen = capture_claude_screen()
                if screen:
                    print("-" * 50)
                    print(screen[-300:])
                    print("-" * 50)

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        test_manual_commands()
    else:
        success = test_basic_detection()
        if success:
            print("\n🎯 Detection successful! You can now test with:")
            print("python3 temp_scripts/test_basic_three_option.py manual")
