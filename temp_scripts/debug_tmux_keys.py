#!/usr/bin/env python3
# ABOUTME: Debug tmux key sending to see what's actually happening
# ABOUTME: Tests individual key sends to understand the sequence

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tmux_controller import find_claude_session, capture_claude_screen
import subprocess


def send_single_key(key):
    """Send a single key and show result"""
    session_name = find_claude_session()
    if not session_name:
        print("❌ No Claude session found!")
        return False

    print(f"📤 Sending key: '{key}'")

    # Capture before
    before = capture_claude_screen()
    print("Before:")
    print(before[-200:] if before else "No screen")
    print("-" * 30)

    # Send key
    try:
        result = subprocess.run(
            ["tmux", "send-keys", "-t", session_name, key],
            capture_output=True,
            check=False,
        )

        if result.returncode != 0:
            print(f"❌ tmux command failed: {result.stderr}")
            return False

        # Wait a bit
        time.sleep(1)

        # Capture after
        after = capture_claude_screen()
        print("After:")
        print(after[-200:] if after else "No screen")
        print("-" * 30)

        return True

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def debug_sequence():
    """Debug the reject sequence step by step"""
    print("=== DEBUG REJECT SEQUENCE ===")

    session = find_claude_session()
    if not session:
        print("❌ No Claude session found!")
        return

    print("Current screen:")
    screen = capture_claude_screen()
    print(screen[-300:] if screen else "No screen")
    print("=" * 50)

    print("\nStep 1: Send Escape key")
    success = send_single_key("Escape")
    if not success:
        return

    print("\nStep 2: Send test text")
    success = send_single_key("hello test message")
    if not success:
        return

    print("\nStep 3: Send Enter")
    success = send_single_key("Enter")
    if not success:
        return

    print("\n✅ Sequence complete!")


def test_different_keys():
    """Test different key names to see which works"""
    print("=== TEST DIFFERENT KEY NAMES ===")

    key_variants = [
        "Escape",
        "Esc",
        "C-[",  # Control+[ is often equivalent to Escape
    ]

    for key in key_variants:
        print(f"\nTesting key variant: {key}")
        success = send_single_key(key)
        if success:
            input("Press Enter to continue to next key...")
        else:
            print("Failed, moving to next...")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "sequence":
            debug_sequence()
        elif sys.argv[1] == "keys":
            test_different_keys()
        else:
            print("Usage: debug_tmux_keys.py [sequence|keys]")
    else:
        print("Usage:")
        print("  debug_tmux_keys.py sequence  - Debug the full reject sequence")
        print("  debug_tmux_keys.py keys      - Test different Escape key variants")
