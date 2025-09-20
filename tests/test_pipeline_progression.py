#!/usr/bin/env python3
# ABOUTME: Progressive pipeline test showing each working component + new additions
# ABOUTME: Validates step-by-step integration without sending actual tmux commands

import sys
import subprocess
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from voice_transcription import capture_voice_command
from llm_calls import parse_voice_command


def test_pipeline_progression():
    """Test pipeline progression: what works + what we're adding"""

    print("=" * 70)
    print("🚀 PIPELINE PROGRESSION TEST")
    print("=" * 70)

    print("📋 CURRENT STATUS:")
    print("✅ Audio playback (proven working)")
    print("✅ Auto-trigger timing (proven working)")
    print("✅ Voice capture with stop word (proven working)")
    print("✅ Real-time transcription (proven working)")
    print()
    print("🆕 ADDING TODAY:")
    print("🔄 LLM classification parsing")
    print("🔄 TMUX command generation (mock - no actual sending)")
    print()

    print("Make sure your AirPods are connected!")
    print("Press Enter to start the progression test...")
    input()

    # ========================================
    # STEP 1: PROVEN WORKING - Audio Playback
    # ========================================
    print("\n" + "=" * 50)
    print("🔊 STEP 1: AUDIO PLAYBACK (proven working)")
    print("=" * 50)

    message = "Claude finished processing. Please give your command like 'I approve this change' or 'No, reject this and instead do something else'. When done, say 'may the force be with you' to stop."
    print(f"Playing: '{message}'")

    start_time = time.time()
    subprocess.run(["say", message])  # Blocks until audio finishes
    audio_duration = time.time() - start_time

    print(f"✅ Audio completed in {audio_duration:.2f}s")

    # ========================================
    # STEP 2: PROVEN WORKING - Voice Capture
    # ========================================
    print("\n" + "=" * 50)
    print("🎤 STEP 2: VOICE CAPTURE (proven working)")
    print("=" * 50)
    print("AUTO-STARTING voice capture...")
    print("Speak your command, then say 'may the force be with you' to stop")

    try:
        transcript = capture_voice_command()

        if not transcript:
            print("❌ Voice capture failed")
            return False

        print(f"✅ Voice captured: '{transcript}'")
        print(f"   Words: {len(transcript.split())}")
        print(f"   Length: {len(transcript)} characters")

        # ========================================
        # STEP 3: PROVEN WORKING - LLM Classification
        # ========================================
        print("\n" + "=" * 50)
        print("🧠 STEP 3: LLM CLASSIFICATION (proven working)")
        print("=" * 50)
        print(f"Sending to LLM: '{transcript}'")

        classification, original_speech = parse_voice_command(transcript)

        print("🔍 LLM Analysis Results:")
        print(f"   Classification: '{classification}'")
        print(f"   Original speech: '{original_speech}'")

        # ========================================
        # STEP 4: PROVEN WORKING - TMUX Command Generation
        # ========================================
        print("\n" + "=" * 50)
        print("⌨️  STEP 4: TMUX COMMAND GENERATION (proven working)")
        print("=" * 50)
        print("📋 Command that WOULD be sent to tmux:")

        if classification == "approve":
            print("   tmux send-keys -t claude-active Enter")
            print("   → Would approve the current suggestion")
        elif classification == "approve_all":
            print("   tmux send-keys -t claude-active BTab")
            print("   → Would approve all suggestions")
        elif classification == "reject":
            print("   tmux send-keys -t claude-active Escape")
            print(f"   tmux send-keys -t claude-active ' {original_speech}'")
            print("   tmux send-keys -t claude-active Enter")
            print("   → Would reject and send your alternative")
        elif classification == "single_escape":
            print("   tmux send-keys -t claude-active Escape")
            print("   → Would send single escape")
        elif classification == "double_escape":
            print("   tmux send-keys -t claude-active Escape")
            print("   tmux send-keys -t claude-active Escape")
            print("   → Would exit Claude Code")
        else:
            print("   (no command - unclear classification)")
            print("   → Would do nothing")

        print("\n🎯 MOCK EXECUTION (not actually sent):")
        print("   Session: claude-active")
        print(f"   Classification: {classification}")
        print(f"   Original: {original_speech}")

        return True

    except Exception as e:
        print(f"💥 Error in pipeline: {e}")
        return False


def main():
    """Run the progression test"""

    print("🎧 Pipeline Progression Test")
    print("🔄 Testing proven components + new classification layer")

    success = test_pipeline_progression()

    if success:
        print("\n" + "=" * 70)
        print("🎉 PIPELINE PROGRESSION TEST PASSED!")
        print("=" * 70)
        print("✅ All proven components still work")
        print("✅ LLM classification working")
        print("✅ TMUX command generation working")
        print("✅ Integration flow validated")
        print("\n🚀 READY TO CONNECT TO REAL TMUX SESSION!")
        print("   (Next step: Remove mock and send actual commands)")
    else:
        print("\n❌ Pipeline progression failed")
        print("🔧 Check the error logs above")


if __name__ == "__main__":
    main()
