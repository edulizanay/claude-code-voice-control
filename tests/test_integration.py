#!/usr/bin/env python3
# ABOUTME: Integration test for complete voice control flow
# ABOUTME: Tests end-to-end functionality with mock data and external APIs

import sys
import json
import tempfile
from pathlib import Path

sys.path.append("..")
from get_last_exchange import get_interactions
from llm_calls import summarize_transcript, parse_voice_command
from audio_generation import generate_audio


def test_complete_flow():
    """Test complete flow from transcript to audio to command parsing"""

    print("Testing complete voice control integration...")

    # Step 1: Create mock transcript
    transcript_entries = [
        {
            "type": "user",
            "message": {
                "role": "user",
                "content": "write a function to calculate fibonacci",
            },
        },
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I'll create a fibonacci function using recursion with proper error handling",
                    }
                ],
            },
        },
    ]

    try:
        # Create temporary transcript file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for entry in transcript_entries:
                f.write(json.dumps(entry) + "\n")
            transcript_path = f.name

        print(f"   ✅ Created mock transcript: {transcript_path}")

        # Step 2: Parse transcript
        interactions = get_interactions(transcript_path)
        if not interactions:
            print("   ❌ Failed to parse transcript")
            return False

        print(f"   ✅ Parsed {len(interactions)} interactions")

        # Step 3: Generate summary
        summary = summarize_transcript(interactions)
        if not summary:
            print("   ❌ Failed to generate summary")
            return False

        print(f"   ✅ Generated summary: '{summary[:50]}...'")

        # Step 4: Generate audio
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_file = generate_audio(summary, temp_dir)
            if not audio_file.exists():
                print("   ❌ Failed to generate audio")
                return False

            print(f"   ✅ Generated audio file: {audio_file.name}")

        # Step 5: Test voice command parsing
        test_commands = ["approve this request", "reject it", "add text hello world"]

        for cmd in test_commands:
            result = parse_voice_command(cmd)
            if result["action"] == "unclear":
                print(f"   ❌ Failed to parse command: '{cmd}'")
                return False
            print(f"   ✅ Parsed '{cmd}' -> {result['action']}")

        # Cleanup
        Path(transcript_path).unlink()

        print("   ✅ Integration test completed successfully")
        return True

    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        return False


def test_hook_simulation():
    """Test simulated hook processing"""

    print("\nTesting hook simulation...")

    # Mock hook data
    hook_data = {
        "session_id": "integration-test-123",
        "transcript_path": "/tmp/mock_transcript.jsonl",
        "cwd": "/test/directory",
        "hook_event_name": "Stop",
        "stop_hook_active": False,
    }

    try:
        # Test JSON serialization/deserialization
        hook_json = json.dumps(hook_data)
        parsed_hook = json.loads(hook_json)

        # Validate required fields
        required_fields = ["session_id", "transcript_path", "hook_event_name"]
        if all(field in parsed_hook for field in required_fields):
            print("   ✅ Hook data structure valid")
        else:
            print("   ❌ Hook data missing required fields")
            return False

        # Test transcript path extraction
        transcript_path = parsed_hook.get("transcript_path")
        if transcript_path:
            print(f"   ✅ Extracted transcript path: {transcript_path}")
        else:
            print("   ❌ Failed to extract transcript path")
            return False

        return True

    except Exception as e:
        print(f"   ❌ Hook simulation failed: {e}")
        return False


if __name__ == "__main__":
    print("Running integration tests...")

    flow_passed = test_complete_flow()
    hook_passed = test_hook_simulation()

    overall_passed = flow_passed and hook_passed

    print(f"\nComplete flow test: {'PASSED' if flow_passed else 'FAILED'}")
    print(f"Hook simulation test: {'PASSED' if hook_passed else 'FAILED'}")
    print(f"Integration tests: {'PASSED' if overall_passed else 'FAILED'}")
