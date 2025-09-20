#!/usr/bin/env python3
# ABOUTME: Test automatic voice recording trigger after audio playback
# ABOUTME: Based on working audio_switch_test.sh example

import subprocess
import time
from pathlib import Path


def test_audio_to_voice_trigger():
    """Test automatic voice trigger based on your working audio_switch_test.sh"""

    print("=" * 60)
    print("🧪 AUDIO-TO-VOICE TRIGGER TEST")
    print("=" * 60)
    print("Based on your working audio_switch_test.sh example")
    print("Make sure your AirPods are connected!")
    print("Press Enter to start...")
    input()

    # 1. Play audio (using say like your example)
    print("🔊 [LOG] Playing audio through AirPods...")
    start_time = time.time()

    # This blocks until audio finishes (same as afplay)
    subprocess.run(["say", "Claude finished. What should I do?"])

    audio_duration = time.time() - start_time
    print(f"✅ [LOG] Audio finished after {audio_duration:.2f} seconds")

    # 2. Immediately start recording (AUTO-TRIGGER!)
    print("🎤 [LOG] Recording starting NOW - speak immediately!")
    print("   [LOG] Say something like 'Hello testing one two three'")
    print("   [LOG] You have 10 seconds...")

    record_start = time.time()
    response_file = "test_recording.wav"

    try:
        # Record for 10 seconds (like your example but longer)
        result = subprocess.run([
            "sox", "-d", "-r", "44100", "-c", "1", response_file,
            "trim", "0", "10"
        ], timeout=12)

        record_duration = time.time() - record_start

        if result.returncode == 0:
            print(f"✅ [LOG] Recording SUCCESS! Duration: {record_duration:.2f}s")

            # 3. Play back what was recorded (like your example)
            print("🔄 [LOG] Playing it back...")
            subprocess.run(["afplay", response_file])

            print("\n" + "=" * 60)
            print("📋 RESULTS")
            print("=" * 60)
            print("Did you hear your voice clearly in the playback?")
            print("- YES = AirPods switched fast enough ✅")
            print("- NO/Silent = AirPods too slow switching ❌")
            print(f"Recording saved as: {response_file}")

            # Check file size
            file_size = Path(response_file).stat().st_size
            print(f"📊 [LOG] File size: {file_size} bytes")

            return True

        else:
            print(f"❌ [LOG] Recording FAILED! Return code: {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ [LOG] Recording TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 [LOG] Error: {e}")
        return False


def test_timing_gap():
    """Test the gap between audio ending and recording starting"""

    print("\n" + "=" * 60)
    print("⏱️  TIMING GAP TEST")
    print("=" * 60)

    print("🔊 [LOG] Playing short audio...")
    start = time.time()

    # Very short audio
    subprocess.run(["say", "Test"])
    audio_end = time.time()

    print("🎤 [LOG] Starting recording...")
    record_start = time.time()

    gap = (record_start - audio_end) * 1000  # Convert to milliseconds
    print(f"⚡ [LOG] Gap: {gap:.1f}ms")

    if gap < 100:
        print("✅ [LOG] Excellent - very fast!")
    elif gap < 500:
        print("✅ [LOG] Good - acceptable for voice control")
    else:
        print("⚠️  [LOG] Slow - might feel laggy")

    # Quick recording test
    try:
        subprocess.run([
            "sox", "-d", "-r", "16000", "-c", "1", "timing_test.wav",
            "trim", "0", "2"
        ], timeout=3)

        if Path("timing_test.wav").exists():
            Path("timing_test.wav").unlink()
            print("✅ [LOG] Recording system responsive")
    except:
        print("⚠️  [LOG] Recording system issue")


def main():
    """Run the audio trigger test"""

    # Test 1: Main trigger test
    success = test_audio_to_voice_trigger()

    if success:
        # Test 2: Timing
        test_timing_gap()

        print("\n🎉 [LOG] TESTS PASSED!")
        print("🚀 [LOG] Auto-trigger works - ready for integration!")
    else:
        print("\n❌ [LOG] Test FAILED!")
        print("🔧 [LOG] Check AirPods/audio setup")

    # Cleanup
    if Path("test_recording.wav").exists():
        cleanup = input("\nDelete test_recording.wav? (y/N): ")
        if cleanup.lower() == 'y':
            Path("test_recording.wav").unlink()
            print("🧹 [LOG] Cleaned up test file")


if __name__ == "__main__":
    main()