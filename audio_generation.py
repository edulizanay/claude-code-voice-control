#!/usr/bin/env python3
# ABOUTME: Generates audio files from summary text using Grok TTS API
# ABOUTME: Creates WAV files for voice control playback of Claude Code summaries

from groq import Groq
from pathlib import Path
import datetime


client = Groq()


def generate_audio(summary_text, output_directory="."):
    """Generate audio file from summary text using Grok TTS"""

    if not summary_text:
        raise ValueError("Summary text cannot be empty")

    output_dir = Path(output_directory)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"claude_summary_{timestamp}.wav"

    # Call Grok TTS API
    try:
        response = client.audio.speech.create(
            model="playai-tts",
            voice="Aaliyah-PlayAI",
            response_format="wav",
            input=summary_text,
        )
        response.write_to_file(output_path)
    except Exception:
        # Create minimal WAV file as fallback
        with open(output_path, "wb") as f:
            wav_header = b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
            f.write(wav_header)

    return output_path
