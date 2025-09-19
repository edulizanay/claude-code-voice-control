#!/usr/bin/env python3
# ABOUTME: Test tmux command syntax without requiring Claude Code
# ABOUTME: Creates a test tmux session to verify our commands work

import subprocess
import time


def test_tmux_commands():
    """Test our tmux command syntax with a simple bash session"""

    print("=== TESTING TMUX COMMAND SYNTAX ===")

    # Kill any existing test session
    subprocess.run(
        ["tmux", "kill-session", "-t", "test-syntax"], capture_output=True, check=False
    )

    # Create a new test session with bash
    print("1. Creating test tmux session...")
    result = subprocess.run(
        ["tmux", "new-session", "-d", "-s", "test-syntax", "bash"],
        capture_output=True,
        check=False,
    )

    if result.returncode != 0:
        print("❌ Failed to create tmux session")
        return False

    print("✅ Test session created")

    # Test 1: Send Escape key
    print("\n2. Testing Escape key...")
    result = subprocess.run(
        ["tmux", "send-keys", "-t", "test-syntax", "Escape"],
        capture_output=True,
        check=False,
    )
    print("✅ Escape sent" if result.returncode == 0 else "❌ Escape failed")

    # Test 2: Send text
    print("\n3. Testing text sending...")
    test_text = "hello world test message"
    result = subprocess.run(
        ["tmux", "send-keys", "-t", "test-syntax", test_text],
        capture_output=True,
        check=False,
    )
    print("✅ Text sent" if result.returncode == 0 else "❌ Text failed")

    # Test 3: Send Enter
    print("\n4. Testing Enter key...")
    result = subprocess.run(
        ["tmux", "send-keys", "-t", "test-syntax", "Enter"],
        capture_output=True,
        check=False,
    )
    print("✅ Enter sent" if result.returncode == 0 else "❌ Enter failed")

    # Test 4: Capture what's on screen
    print("\n5. Capturing screen content...")
    time.sleep(0.5)  # Wait for commands to process
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", "test-syntax", "-p"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0:
        print("✅ Screen captured")
        print("Screen content:")
        print("-" * 50)
        print(result.stdout)
        print("-" * 50)

        # Check if our text appears in the output
        if test_text in result.stdout:
            print("✅ SUCCESS: Our test text appears in the session!")
        else:
            print("⚠️  Test text not visible (may be normal in bash)")
    else:
        print("❌ Screen capture failed")

    # Test 5: Test the sequence together (like our reject function)
    print("\n6. Testing complete sequence (Escape + text + Enter)...")

    # Send a command first so we have something to work with
    subprocess.run(
        [
            "tmux",
            "send-keys",
            "-t",
            "test-syntax",
            "echo 'Starting sequence test'",
            "Enter",
        ],
        capture_output=True,
        check=False,
    )
    time.sleep(0.5)

    # Now test our sequence
    sequence_text = "this is a sequence test"

    # Step 1: Escape
    result1 = subprocess.run(
        ["tmux", "send-keys", "-t", "test-syntax", "Escape"],
        capture_output=True,
        check=False,
    )

    # Step 2: Text
    result2 = subprocess.run(
        ["tmux", "send-keys", "-t", "test-syntax", sequence_text],
        capture_output=True,
        check=False,
    )

    # Step 3: Enter
    result3 = subprocess.run(
        ["tmux", "send-keys", "-t", "test-syntax", "Enter"],
        capture_output=True,
        check=False,
    )

    if all(r.returncode == 0 for r in [result1, result2, result3]):
        print("✅ Complete sequence sent successfully")

        # Capture final state
        time.sleep(0.5)
        final_result = subprocess.run(
            ["tmux", "capture-pane", "-t", "test-syntax", "-p"],
            capture_output=True,
            text=True,
            check=False,
        )

        print("Final screen state:")
        print("-" * 50)
        print(final_result.stdout)
        print("-" * 50)
    else:
        print("❌ Sequence failed")

    # Cleanup
    print("\n7. Cleaning up...")
    subprocess.run(
        ["tmux", "kill-session", "-t", "test-syntax"], capture_output=True, check=False
    )
    print("✅ Test session cleaned up")

    print("\n=== TMUX SYNTAX TEST COMPLETE ===")
    return True


if __name__ == "__main__":
    test_tmux_commands()
