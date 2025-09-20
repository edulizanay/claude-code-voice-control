#!/usr/bin/env python3
# ABOUTME: Complete voice command pipeline from speech to tmux action
# ABOUTME: Integrates voice transcription, LLM parsing, and tmux control

from voice_transcription import capture_voice_command
from llm_calls import parse_voice_command
from tmux_controller import execute_parsed_command, get_claude_status
import sys


def run_voice_command_pipeline():
    """Run complete voice command pipeline"""

    print("=== VOICE COMMAND PIPELINE ===")
    print("Say 'may the force be with you' to end recording\n")

    # Check Claude session first
    print("🔍 Checking for Claude session...")
    status = get_claude_status()
    print(f"   Session check result: {status}")

    if not status["session_found"]:
        print("❌ No Claude Code session found!")
        print('Start Claude Code with: tmux new-session -s claude-active "claude"')
        return False

    print("✅ Claude session found")
    print(f"   Waiting for input: {status['waiting_for_input']}")

    if status["screen_content"]:
        print("\nCurrent Claude screen:")
        print("-" * 40)
        print(status["screen_content"][-200:])  # Show last 200 chars
        print("-" * 40)

    # Step 1: Capture voice command
    print("\n🎤 Listening for voice command...")
    print("   Starting voice transcription...")

    try:
        speech_content = capture_voice_command()
        print(
            f"   Voice capture returned: '{speech_content}' (type: {type(speech_content)})"
        )
    except Exception as e:
        print(f"❌ Voice capture error: {e}")
        return False

    if not speech_content or not speech_content.strip():
        print("❌ No speech captured or empty result")
        return False

    print(f"✅ Captured: '{speech_content}'")

    # Step 2: Parse voice command
    print("\n🧠 Parsing command...")
    print(f"   Input to parser: '{speech_content}'")

    try:
        command_data = parse_voice_command(speech_content)
        print(f"   Parser returned: {command_data}")
    except Exception as e:
        print(f"❌ Parsing error: {e}")
        return False

    print(f"✅ Parsed: {command_data}")

    if command_data["action"] == "unclear":
        print("❌ Could not understand command")
        print(
            f"   Unclear because: action='{command_data['action']}', tmux_command='{command_data['tmux_command']}'"
        )
        return False

    # Step 3: Execute via tmux
    print(f"\n⚡ Executing: {command_data['action']}")
    if command_data["action"] == "add_text":
        print(f"   Text: '{command_data['text']}'")
    print(f"   TMUX command: '{command_data['tmux_command']}'")

    try:
        success = execute_parsed_command(command_data)
        print(f"   Execution returned: {success}")
    except Exception as e:
        print(f"❌ Execution error: {e}")
        return False

    if success:
        print("✅ Command executed successfully!")

        # Show updated Claude status
        print("\n📱 Checking Claude status after command...")
        new_status = get_claude_status()
        if new_status["screen_content"]:
            print("Updated Claude screen:")
            print("-" * 40)
            print(new_status["screen_content"][-200:])
            print("-" * 40)

        return True
    else:
        print("❌ Command execution failed")
        return False


def quick_test_pipeline():
    """Quick test of pipeline components without voice input"""

    print("=== QUICK PIPELINE TEST ===")

    # Test parsing
    test_commands = [
        "approve this request",
        "reject it",
        "add text hello world",
        "unclear command",
    ]

    for cmd in test_commands:
        print(f"\nTesting: '{cmd}'")
        result = parse_voice_command(cmd)
        print(f"  → {result}")

    # Test tmux status
    print("\nClaude session status:")
    status = get_claude_status()
    print(f"  Session found: {status['session_found']}")
    print(f"  Waiting for input: {status['waiting_for_input']}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        quick_test_pipeline()
    else:
        run_voice_command_pipeline()
