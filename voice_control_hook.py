#!/usr/bin/env python3
# ABOUTME: Voice control hook that processes Claude Code notifications/stops
# ABOUTME: Converts Claude actions to audio summaries for hands-free operation

import json
import sys
import subprocess
from get_last_exchange import get_interactions
from transcript_summary import summarize_claude_actions
from audio_generation import generate_audio


def process_hook():
    """Process Claude Code hook data and generate audio summary"""

    try:
        # Read hook data from stdin
        hook_data_raw = sys.stdin.read().strip()

        if not hook_data_raw:
            # No data received (shouldn't happen with current hooks)
            return

        # Parse JSON hook data
        hook_data = json.loads(hook_data_raw)

        # Extract transcript path
        transcript_path = hook_data.get("transcript_path")
        if not transcript_path:
            # No transcript path available
            return

        # Get transcript data
        transcript_data = get_interactions(transcript_path)

        if not transcript_data:
            # No transcript data to summarize
            return

        # Generate summary
        summary = summarize_claude_actions(transcript_data)

        # Generate audio file
        audio_file = generate_audio(summary)

        # Play audio
        subprocess.run(["afplay", str(audio_file)], check=True)

        # Clean up audio file after playing
        audio_file.unlink()

    except json.JSONDecodeError:
        # Invalid JSON data - silently fail
        pass
    except FileNotFoundError:
        # Transcript file not found or afplay not available - silently fail
        pass
    except Exception:
        # Any other error - silently fail to not disrupt Claude Code
        pass


if __name__ == "__main__":
    process_hook()
