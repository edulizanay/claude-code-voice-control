#!/usr/bin/env python3
# ABOUTME: Main voice control orchestrator that handles Claude hook events
# ABOUTME: Runs complete pipeline from transcript extraction to tmux command execution

import sys
import json
import time
from datetime import datetime

# Import our existing modules
from get_last_exchange import get_interactions
from llm_calls import summarize_transcript, parse_voice_command
from audio_generation import generate_audio
from voice_transcription import capture_voice_command
from tmux_controller import send_classified_command


def timestamp():
    """Get current timestamp for logging"""
    return datetime.now().strftime("%H:%M:%S")


def run_voice_pipeline(hook_data, hook_type):
    """Run the complete voice control pipeline"""

    print(f"[{timestamp()}] 🚀 Starting voice control pipeline")
    print(f"[{timestamp()}] 📊 Hook type: {hook_type}")

    # Extract session info directly
    session_id = hook_data.get("session_id")
    transcript_path = hook_data.get("transcript_path")
    event_type = hook_data.get("hook_event_name", "").lower()

    print(f"[{timestamp()}] 📋 Session ID: {session_id}")
    print(f"[{timestamp()}] 📂 Transcript path: {transcript_path}")
    print(f"[{timestamp()}] 🏷️  Event type: {event_type}")

    # Step 1: Get transcript data
    print(f"[{timestamp()}] 📝 Extracting transcript...")
    transcript_data = get_interactions(transcript_path)
    if not transcript_data:
        raise Exception("Failed to extract transcript data")

    context_count = len(transcript_data["context"])
    print(
        f"[{timestamp()}] ✅ Got transcript: {context_count} context messages + 1 last message"
    )

    # Step 2: Generate summary
    print(f"[{timestamp()}] 🧠 Generating LLM summary...")
    summary = summarize_transcript(transcript_data)
    print(f"[{timestamp()}] ✅ Summary: '{summary}'")

    # Step 3: Generate and play audio
    print(f"[{timestamp()}] 🔊 Generating audio...")
    audio_file = generate_audio(summary, ".")
    print(f"[{timestamp()}] 🎵 Playing audio summary...")

    import subprocess

    start_time = time.time()
    subprocess.run(["afplay", str(audio_file)])
    audio_duration = time.time() - start_time
    print(f"[{timestamp()}] ✅ Audio completed in {audio_duration:.2f}s")

    # Cleanup audio
    audio_file.unlink()
    print(f"[{timestamp()}] 🧹 Audio file cleaned up")

    # Step 4: Capture voice response
    print(f"[{timestamp()}] 🎤 Starting voice capture...")
    print(
        f"[{timestamp()}] 💬 Say your response, then 'may the force be with you' to stop"
    )

    transcript = capture_voice_command()
    if not transcript:
        raise Exception("Voice capture failed or timed out")

    print(f"[{timestamp()}] ✅ Voice captured: '{transcript}'")

    # Step 5: Parse command based on event type
    print(f"[{timestamp()}] 🧠 Parsing voice command as {event_type} event...")
    parsed_result = parse_voice_command(transcript, event_type=event_type)

    action = parsed_result.get("action", "unknown")
    text = parsed_result.get("text", "")
    print(f"[{timestamp()}] ✅ Parsed - Action: '{action}', Text: '{text}'")

    # Step 6: Send to tmux
    print(f"[{timestamp()}] ⌨️  Sending command to tmux...")
    result = send_classified_command(parsed_result)

    if result.get("success"):
        commands_sent = result.get("commands_sent", [])
        print(f"[{timestamp()}] ✅ Command executed successfully!")
        print(f"[{timestamp()}] 📤 Commands sent: {commands_sent}")
        print(f"[{timestamp()}] 🎯 Check your Claude Code session!")
    else:
        error_msg = result.get("error", "Unknown error")
        raise Exception(f"Tmux command failed: {error_msg}")

    print(f"[{timestamp()}] 🎉 Voice control pipeline completed successfully!")


def main():
    """Main entry point"""

    print(f"[{timestamp()}] 🎤 Voice Control Main Orchestrator Started")

    try:
        # Get hook type from command line argument
        if len(sys.argv) < 2:
            raise Exception("Hook type not provided as argument")

        hook_type = sys.argv[1]
        print(f"[{timestamp()}] 📥 Hook type from args: {hook_type}")

        # Read hook data from stdin
        print(f"[{timestamp()}] 📖 Reading hook data from stdin...")
        raw_data = sys.stdin.read()

        if not raw_data.strip():
            raise Exception("No hook data received from stdin")

        hook_data = json.loads(raw_data)
        print(f"[{timestamp()}] ✅ Parsed hook data successfully")

        # Run the complete pipeline
        run_voice_pipeline(hook_data, hook_type)

    except Exception as e:
        print(f"[{timestamp()}] ❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
