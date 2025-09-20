#!/usr/bin/env python3
# ABOUTME: Simple test of audio playback -> voice capture -> transcription flow
# ABOUTME: Uses real APIs but no classification or tmux control

import sys
import subprocess
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from voice_transcription import capture_voice_command


def test_simple_audio_to_speech():
    """Test: Play audio -> User speaks -> Transcribe speech"""

    print("=" * 60)
    print("🧪 SIMPLE AUDIO-TO-SPEECH TEST")
    print("=" * 60)
    print("This will:")
    print("1. Play a message asking you to speak")
    print("2. Automatically start recording when audio ends")
    print("3. Record for 10 seconds")
    print("4. Show you the transcription")
    print("\nMake sure your AirPods are connected!")
    print("Press Enter to start...")
    input()

    # Step 1: Play audio message
    message = "Hello! Please speak now. Say something like 'I approve this change' or 'No, reject this'. When done, say 'may the force be with you' to stop."
    print(f"🔊 Playing: '{message}'")

    start_time = time.time()
    subprocess.run(["say", message])  # Blocks until audio finishes
    audio_duration = time.time() - start_time

    print(f"✅ Audio finished after {audio_duration:.2f}s")

    # Step 2: Auto-trigger voice capture with stop word
    print("🎤 AUTO-STARTING voice capture...")
    print("   Speak your command, then say 'may the force be with you' to stop")

    try:
        # Use real voice capture with stop word detection
        transcript = capture_voice_command()

        if transcript:
            print("\n" + "=" * 60)
            print("📋 TRANSCRIPTION RESULT")
            print("=" * 60)
            print(f"You said: '{transcript}'")

            # Basic analysis
            word_count = len(transcript.split())
            print(f"Word count: {word_count}")
            print(f"Length: {len(transcript)} characters")

            return True

        else:
            print("❌ No speech detected or transcription failed")
            return False

    except Exception as e:
        print(f"💥 Error: {e}")
        return False


def main():
    """Run the simple test"""

    print("🎧 Audio-to-Speech Pipeline Test")
    print("🔑 This validates the core flow before adding complexity")

    success = test_simple_audio_to_speech()

    if success:
        print("\n🎉 SUCCESS!")
        print("✅ Audio playback works")
        print("✅ Auto-trigger timing works")
        print("✅ Voice capture works")
        print("✅ Transcription works")
        print("\n🚀 Ready to add classification next!")
    else:
        print("\n❌ Test failed - check audio/microphone setup")


if __name__ == "__main__":
    main()
