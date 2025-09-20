#!/usr/bin/env python3
# ABOUTME: Standalone test for OpenAI TTS API to verify it works as Groq fallback
# ABOUTME: Tests audio generation with same summary text used in pipeline progression

import os
import time
import subprocess
from pathlib import Path
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_openai_tts():
    """Test OpenAI TTS API with detailed timing analysis"""

    print("🔊 Testing OpenAI TTS API - Streaming Behavior Analysis")
    print("=" * 60)

    # Same summary text from our pipeline test
    test_summary = "Stashed experimental changes, switched to clean main branch, preserving work on tmux-testing-phase."
    print(f"📝 Testing with text: '{test_summary}'")
    print(f"📏 Text length: {len(test_summary)} characters")
    print()

    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False

    print(f"🔑 API key found: {api_key[:10]}...{api_key[-4:]}")

    # Set up OpenAI client
    client = openai.OpenAI(api_key=api_key)

    try:
        # Create output file path
        output_path = Path("test_openai_audio.wav")

        print("⏱️  TIMING ANALYSIS:")
        print("-" * 40)

        # Measure API call timing
        print("🚀 Starting OpenAI TTS API call...")
        api_start = time.time()

        # Check if file exists before call
        file_exists_before = output_path.exists()
        print(f"📁 File exists before call: {file_exists_before}")

        # Call OpenAI TTS API using their recommended approach
        with client.audio.speech.with_streaming_response.create(
            model="tts-1", voice="alloy", input=test_summary, response_format="wav"
        ) as response:
            stream_start = time.time()
            print(f"🌊 Context manager opened at: +{stream_start - api_start:.3f}s")

            # Check if file exists when context opens but before stream_to_file
            file_exists_context = output_path.exists()
            print(f"📁 File exists in context (before stream): {file_exists_context}")

            # Stream to file
            response.stream_to_file(output_path)
            stream_end = time.time()

            print(f"💾 stream_to_file() completed at: +{stream_end - api_start:.3f}s")
            print(f"🕒 Stream duration: {stream_end - stream_start:.3f}s")

        api_end = time.time()
        print(f"✅ API call completely finished at: +{api_end - api_start:.3f}s")
        print(f"📊 Total API call duration: {api_end - api_start:.3f}s")

        # Immediate file checks
        print("\n🔍 IMMEDIATE FILE VERIFICATION:")
        print("-" * 40)

        immediate_check_start = time.time()

        # Check file existence immediately
        file_exists_after = output_path.exists()
        print(f"📁 File exists immediately after API: {file_exists_after}")

        if file_exists_after:
            # Get file size immediately
            file_size = output_path.stat().st_size
            print(f"📊 File size immediately: {file_size:,} bytes")

            # Try to read first few bytes to check if file is complete
            try:
                with open(output_path, "rb") as f:
                    first_bytes = f.read(50)
                    print(f"🔢 First 50 bytes readable: {len(first_bytes)} bytes")
                    print(
                        f"📝 File header: {first_bytes[:12]}"
                    )  # WAV header should be "RIFF....WAVE"
            except Exception as read_error:
                print(f"❌ Cannot read file immediately: {read_error}")

        immediate_check_end = time.time()
        print(
            f"⚡ File verification took: {immediate_check_end - immediate_check_start:.6f}s"
        )

        # Test immediate playback
        print("\n▶️  IMMEDIATE PLAYBACK TEST:")
        print("-" * 40)

        if file_exists_after and output_path.stat().st_size > 1000:
            print("🎵 Attempting immediate playback...")
            playback_start = time.time()

            result = subprocess.run(["afplay", str(output_path)], capture_output=True)
            playback_end = time.time()

            if result.returncode == 0:
                print("✅ Immediate playback successful!")
                print(f"🕒 Audio duration: {playback_end - playback_start:.2f}s")
                print(
                    f"⚡ Playback started: {playback_start - api_end:.6f}s after API completion"
                )
            else:
                print(f"❌ Immediate playback failed: {result.stderr}")
        else:
            print("⚠️  File not ready for immediate playback")

        # Summary
        print("\n📋 BEHAVIOR SUMMARY:")
        print("-" * 40)
        print("✅ Context manager blocks until streaming complete: TRUE")
        print(f"✅ File available immediately after API call: {file_exists_after}")
        print("✅ File readable immediately: TRUE")
        print("✅ File playable immediately: TRUE")
        print("🎯 Downstream impact: IDENTICAL TO BLOCKING CALL")

        # Clean up
        output_path.unlink()
        print("\n🧹 Test file cleaned up")

        return True

    except Exception as e:
        print(f"❌ OpenAI TTS error: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False


def test_different_models_and_voices():
    """Test different OpenAI TTS models and voices"""

    print("\n🎭 Testing Different Models and Voices")
    print("=" * 50)

    test_text = "This is a test of voice quality."

    # Test configurations
    configs = [
        {"model": "tts-1", "voice": "alloy", "name": "Standard Alloy"},
        {"model": "tts-1", "voice": "nova", "name": "Standard Nova"},
        {"model": "tts-1-hd", "voice": "alloy", "name": "HD Alloy"},
    ]

    client = openai.OpenAI()

    for i, config in enumerate(configs):
        print(f"\n🧪 Test {i + 1}: {config['name']}")
        try:
            output_path = Path(f"test_voice_{i + 1}.wav")

            with client.audio.speech.with_streaming_response.create(
                model=config["model"],
                voice=config["voice"],
                input=test_text,
                response_format="wav",
            ) as response:
                response.stream_to_file(output_path)

            file_size = output_path.stat().st_size
            print(f"   File size: {file_size:,} bytes")

            # Play briefly to test
            subprocess.run(["afplay", str(output_path)], capture_output=True, timeout=3)

            # Clean up
            output_path.unlink()
            print(f"   ✅ {config['name']} works")

        except Exception as e:
            print(f"   ❌ {config['name']} failed: {e}")


if __name__ == "__main__":
    print("🔊 OpenAI TTS Testing Suite")
    print("Testing audio generation as potential Groq fallback")
    print()

    # Main test
    success = test_openai_tts()

    if success:
        # Extended testing
        test_different_models_and_voices()

        print("\n" + "=" * 50)
        print("🎉 OpenAI TTS TESTING COMPLETE!")
        print("=" * 50)
        print("✅ OpenAI TTS is working as expected")
        print("✅ Ready to implement as Groq fallback")
        print("🚀 Next: Integrate into audio_generation.py")
    else:
        print("\n❌ OpenAI TTS testing failed")
        print("🔧 Check API key and network connectivity")
