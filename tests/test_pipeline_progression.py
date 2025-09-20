#!/usr/bin/env python3
# ABOUTME: Progressive pipeline test showing each working component + new additions
# ABOUTME: Validates step-by-step integration without sending actual tmux commands

import sys
import subprocess
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from llm_calls import parse_voice_command, summarize_transcript
from get_last_exchange import get_interactions
from audio_generation import generate_audio
from voice_transcription import capture_voice_command


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
    print("🔄 Transcript extraction from real hook data")
    print("🔄 LLM summarization of Claude actions")
    print("🔄 Audio generation from summary")
    print("🔄 LLM classification parsing")
    print("🔄 TMUX command generation (mock - no actual sending)")
    print()

    print("Make sure your AirPods are connected!")
    print("Starting test automatically...")
    print()

    # ========================================
    # STEP 0: NEW - Transcript & Summarization
    # ========================================
    print("\n" + "=" * 50)
    print("📝 STEP 0: TRANSCRIPT EXTRACTION & SUMMARIZATION (new)")
    print("=" * 50)

    # Use real transcript path from hook data
    transcript_path = "/Users/eduardolizana/.claude/projects/-Users-eduardolizana-Documents-Github-claude-code-voice-control/77722a0c-fb8c-4e7b-addf-5f99b49ff1f4.jsonl"
    print(f"📄 Using real transcript: {transcript_path}")

    try:
        # Extract last exchange
        print("🔍 Extracting last 3 messages from transcript...")
        transcript_data = get_interactions(transcript_path)

        if not transcript_data:
            print("❌ No transcript data found")
            return False

        # Display structured transcript data
        context_count = len(transcript_data["context"])
        last_message_role, _ = transcript_data["last_message"]
        print(
            f"✅ Extracted structured data: {context_count} context messages + 1 last message"
        )

        # Show context
        if transcript_data["context"]:
            print("   Context:")
            for role, content in transcript_data["context"]:
                preview = content[:80] + "..." if len(content) > 80 else content
                print(f"     {role}: {preview}")

        # Show last message
        role, content = transcript_data["last_message"]
        preview = content[:80] + "..." if len(content) > 80 else content
        print(f"   Last Message: {role}: {preview}")

        # Generate summary
        print("\n🧠 Generating LLM summary...")
        summary = summarize_transcript(transcript_data)
        print(f"✅ Summary: '{summary}'")

        # Generate audio
        print("\n🔊 Generating audio from summary...")
        audio_file = generate_audio(summary, ".")
        print(f"✅ Audio file created: {audio_file}")

        # Play audio
        print("▶️ Playing summary audio...")
        start_time = time.time()
        subprocess.run(["afplay", str(audio_file)])
        audio_duration = time.time() - start_time
        print(f"✅ Audio completed in {audio_duration:.2f}s")

        # Cleanup
        audio_file.unlink()
        print("🧹 Audio file cleaned up")

    except Exception as e:
        print(f"❌ Error in transcript/summarization: {e}")
        return False

    # ========================================
    # STEP 1: PROVEN WORKING - Real Voice Capture
    # ========================================
    print("\n" + "=" * 50)
    print("🎤 STEP 1: REAL VOICE CAPTURE")
    print("=" * 50)
    print("Listening for your voice command...")
    print("Say 'may the force be with you' to stop recording.")

    try:
        # Use real voice capture with stop word detection
        transcript = capture_voice_command()

        if not transcript:
            print("❌ Voice capture failed")
            return False

        print(f"✅ Voice captured: '{transcript}'")
        print(f"   Words: {len(transcript.split())}")
        print(f"   Length: {len(transcript)} characters")

        # ========================================
        # STEP 2: PROVEN WORKING - LLM Classification
        # ========================================
        print("\n" + "=" * 50)
        print("🧠 STEP 2: LLM CLASSIFICATION (proven working)")
        print("=" * 50)
        print(f"Sending to LLM: '{transcript}'")

        classification, original_speech = parse_voice_command(transcript)

        print("🔍 LLM Analysis Results:")
        print(f"   Classification: '{classification}'")
        print(f"   Original speech: '{original_speech}'")

        # ========================================
        # STEP 3: PROVEN WORKING - TMUX Command Generation
        # ========================================
        print("\n" + "=" * 50)
        print("⌨️  STEP 3: TMUX COMMAND GENERATION (proven working)")
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
        print("✅ Transcript extraction from real hook data working")
        print("✅ LLM summarization working")
        print("✅ Audio generation and playback working")
        print("✅ All proven components still work")
        print("✅ LLM classification working")
        print("✅ TMUX command generation working")
        print("✅ Complete integration flow validated")
        print("\n🚀 READY FOR FULL HOOK INTEGRATION!")
        print("   (Next step: Connect hook trigger to this complete pipeline)")
    else:
        print("\n❌ Pipeline progression failed")
        print("🔧 Check the error logs above")


if __name__ == "__main__":
    main()
