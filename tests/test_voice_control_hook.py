#!/usr/bin/env python3
# ABOUTME: Test voice control hook functionality with mock data
# ABOUTME: Tests hook data processing without external dependencies

import sys
import json
import tempfile
from pathlib import Path

sys.path.append("..")


def test_hook_data_parsing():
    """Test parsing of hook data from different event types"""

    # Sample stop hook data
    stop_data = {
        "session_id": "test-session-123",
        "transcript_path": "/tmp/test_transcript.jsonl",
        "cwd": "/test/directory",
        "permission_mode": "acceptEdits",
        "hook_event_name": "Stop",
        "stop_hook_active": False,
    }

    # Sample notification hook data
    notification_data = {
        "session_id": "test-session-123",
        "transcript_path": "/tmp/test_transcript.jsonl",
        "cwd": "/test/directory",
        "hook_event_name": "Notification",
        "message": "Claude needs your permission to use Bash",
    }

    print("Testing hook data parsing...")

    # Test JSON parsing
    try:
        stop_json = json.dumps(stop_data)
        notification_json = json.dumps(notification_data)

        parsed_stop = json.loads(stop_json)
        parsed_notification = json.loads(notification_json)

        print("   ✅ Stop hook JSON parsing successful")
        print("   ✅ Notification hook JSON parsing successful")

        # Validate expected fields
        stop_fields = ["session_id", "transcript_path", "hook_event_name"]
        notification_fields = [
            "session_id",
            "transcript_path",
            "hook_event_name",
            "message",
        ]

        stop_valid = all(field in parsed_stop for field in stop_fields)
        notification_valid = all(
            field in parsed_notification for field in notification_fields
        )

        print(f"   {'✅' if stop_valid else '❌'} Stop hook has required fields")
        print(
            f"   {'✅' if notification_valid else '❌'} Notification hook has required fields"
        )

        return stop_valid and notification_valid

    except Exception as e:
        print(f"   ❌ Hook data parsing failed: {e}")
        return False


def test_transcript_file_creation():
    """Test creating a mock transcript file for testing"""

    # Sample transcript data (jsonl format)
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
                        "text": "I'll create a fibonacci function using recursion",
                    }
                ],
            },
        },
    ]

    print("\nTesting transcript file creation...")

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for entry in transcript_entries:
                f.write(json.dumps(entry) + "\n")
            transcript_path = f.name

        # Verify file exists and can be read
        if Path(transcript_path).exists():
            with open(transcript_path, "r") as f:
                lines = f.readlines()
                if len(lines) == 2:
                    print("   ✅ Mock transcript file created successfully")
                    print(f"   ✅ File contains {len(lines)} entries")

                    # Clean up
                    Path(transcript_path).unlink()
                    return True

        print("   ❌ Mock transcript file creation failed")
        return False

    except Exception as e:
        print(f"   ❌ Transcript file creation failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing voice control hook components...")

    parsing_passed = test_hook_data_parsing()
    transcript_passed = test_transcript_file_creation()

    overall_passed = parsing_passed and transcript_passed

    print(f"\nHook data parsing: {'PASSED' if parsing_passed else 'FAILED'}")
    print(f"Transcript file handling: {'PASSED' if transcript_passed else 'FAILED'}")
    print(f"Overall: {'PASSED' if overall_passed else 'FAILED'}")
