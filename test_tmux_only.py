#!/usr/bin/env python3
# ABOUTME: Simple TMUX-only test script without LLM dependencies
# ABOUTME: Tests sending commands directly to Claude Code session

from tmux_controller import (
    send_classified_command,
    find_claude_session,
    get_claude_status,
)


def main():
    """Test TMUX commands directly"""
    print("=== TMUX ONLY TEST ===")

    # Check for Claude session
    session = find_claude_session()
    if not session:
        print("❌ No Claude session found!")
        print('Start Claude Code with: tmux new-session -s claude-active "claude"')
        return

    print(f"✅ Found Claude session: {session}")

    while True:
        print("\nCommands:")
        print("1. Send 'hi' (Escape + 'hi' + Enter)")
        print("2. Send 'approve' (Enter)")
        print("3. Send 'approve all' (Shift+Tab)")
        print("4. Send custom text")
        print("5. Send single escape")
        print("6. Send double escape (closes Claude)")
        print("7. Show Claude status")
        print("8. Exit")

        choice = input("\nEnter choice (1-8): ").strip()

        if choice == "1":
            result = send_classified_command("reject", "hi")
            print(f"Sent 'hi': {result}")

        elif choice == "2":
            result = send_classified_command("approve", "")
            print(f"Sent approve (Enter): {result}")

        elif choice == "3":
            result = send_classified_command("approve_all", "")
            print(f"Sent approve all (Shift+Tab): {result}")

        elif choice == "4":
            text = input("Enter text to send: ")
            result = send_classified_command("reject", text)
            print(f"Sent '{text}': {result}")

        elif choice == "5":
            result = send_classified_command("single_escape", "")
            print(f"Sent single escape: {result}")

        elif choice == "6":
            result = send_classified_command("double_escape", "")
            print(f"Sent double escape (closes Claude): {result}")

        elif choice == "7":
            status = get_claude_status()
            print("\nClaude session status:")
            print(f"  Session found: {status['session_found']}")

        elif choice == "8":
            print("Goodbye!")
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
