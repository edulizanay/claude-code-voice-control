#!/usr/bin/env python3
# ABOUTME: Generates audio files from summary text with Groq TTS primary and OpenAI fallback
# ABOUTME: Creates WAV files for voice control playback of Claude Code summaries

from groq import Groq
import openai
import yaml
from pathlib import Path
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Load configuration
def _load_config():
    """Load configuration from config.yaml file"""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


CONFIG = _load_config()

# Initialize TTS clients
groq_client = Groq()
openai_client = openai.OpenAI()


def _generate_groq_audio(summary_text, output_path):
    """Generate audio using Groq TTS API"""
    response = groq_client.audio.speech.create(
        model=CONFIG["tts"]["groq"]["model"],
        voice=CONFIG["tts"]["groq"]["voice"],
        response_format=CONFIG["tts"]["groq"]["response_format"],
        input=summary_text,
    )
    response.write_to_file(output_path)
    return output_path


def _generate_openai_audio(summary_text, output_path):
    """Generate audio using OpenAI TTS API as fallback"""
    with openai_client.audio.speech.with_streaming_response.create(
        model=CONFIG["tts"]["openai"]["model"],
        voice=CONFIG["tts"]["openai"]["voice"],
        input=summary_text,
        response_format=CONFIG["tts"]["openai"]["response_format"],
    ) as response:
        response.stream_to_file(output_path)
    return output_path


def _generate_fallback_wav(output_path):
    """Generate minimal silent WAV file as last resort"""
    with open(output_path, "wb") as f:
        wav_header = b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
        f.write(wav_header)
    return output_path


def generate_audio(summary_text, output_directory="."):
    """Generate audio file with fallback hierarchy: Groq → OpenAI → Silent WAV"""

    if not summary_text:
        raise ValueError("Summary text cannot be empty")

    output_dir = Path(output_directory)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"claude_summary_{timestamp}.wav"

    # Try Groq TTS first
    try:
        print("🎵 Trying Groq TTS...")
        return _generate_groq_audio(summary_text, output_path)
    except Exception as groq_error:
        print(f"⚠️  Groq TTS failed: {groq_error}")

        # Fallback to OpenAI TTS
        try:
            print("🎵 Trying OpenAI TTS fallback...")
            return _generate_openai_audio(summary_text, output_path)
        except Exception as openai_error:
            print(f"⚠️  OpenAI TTS failed: {openai_error}")

            # Final fallback to silent WAV
            print("🔇 Using silent WAV fallback...")
            return _generate_fallback_wav(output_path)
