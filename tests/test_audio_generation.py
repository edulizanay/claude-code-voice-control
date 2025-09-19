#!/usr/bin/env python3
# ABOUTME: Test audio generation functionality
# ABOUTME: Tests Groq TTS API connectivity and file generation

import sys

sys.path.append("..")
from audio_generation import generate_audio
import tempfile


def test_audio_generation():
    """Test audio generation with sample text"""

    try:
        # Test with simple text
        test_text = "Claude completed a task successfully"

        # Generate audio in temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_file = generate_audio(test_text, temp_dir)

            # Check if file was created
            if audio_file.exists():
                file_size = audio_file.stat().st_size
                print(f"✅ Audio file created: {audio_file}")
                print(f"   File size: {file_size} bytes")
                return True
            else:
                print(f"❌ Audio file not created: {audio_file}")
                return False

    except Exception as e:
        print(f"❌ Audio generation failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing audio generation...")
    success = test_audio_generation()
    print(f"Audio generation test: {'PASSED' if success else 'FAILED'}")
