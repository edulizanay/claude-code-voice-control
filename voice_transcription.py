#!/usr/bin/env python3
# ABOUTME: Voice transcription with AssemblyAI WebSocket for "may the force be with you" keyword detection
# ABOUTME: Captures speech until keyword is detected, returns transcript content

import pyaudio
import websocket
import json
import threading
import time
from urllib.parse import urlencode
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()
YOUR_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

# Configuration
CONNECTION_PARAMS = {
    "sample_rate": 16000,
    "format_turns": True,
}
API_ENDPOINT_BASE_URL = "wss://streaming.assemblyai.com/v3/ws"
API_ENDPOINT = f"{API_ENDPOINT_BASE_URL}?{urlencode(CONNECTION_PARAMS)}"

# Audio Configuration
FRAMES_PER_BUFFER = 800  # 50ms of audio
SAMPLE_RATE = CONNECTION_PARAMS["sample_rate"]
CHANNELS = 1
FORMAT = pyaudio.paInt16

# Stop keyword
STOP_KEYWORD = "may the force be with you"


def detect_stop_keyword(transcript_text):
    """Detect if the stop keyword is present in transcript"""
    return STOP_KEYWORD.lower() in transcript_text.lower()


def extract_transcript_content(full_transcript):
    """Extract transcript content before the stop keyword"""
    if not detect_stop_keyword(full_transcript):
        return full_transcript

    # Find keyword position and extract content before it
    keyword_pos = full_transcript.lower().find(STOP_KEYWORD.lower())
    content = full_transcript[:keyword_pos].strip()
    return content


class VoiceTranscriber:
    """Real-time voice transcription with keyword detection"""

    def __init__(self):
        self.audio = None
        self.stream = None
        self.ws_app = None
        self.stop_event = threading.Event()
        self.full_transcript = []
        self.raw_transcript = ""
        self.final_content = ""

    def on_open(self, ws):
        """Called when WebSocket connection opens"""
        print("✅ Connected to AssemblyAI")
        print("🎤 Start speaking! Say 'may the force be with you' to end.\n")

        # Start audio streaming thread
        def stream_audio():
            while not self.stop_event.is_set():
                try:
                    audio_data = self.stream.read(
                        FRAMES_PER_BUFFER, exception_on_overflow=False
                    )
                    ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
                except Exception as e:
                    print(f"Audio error: {e}")
                    break

        audio_thread = threading.Thread(target=stream_audio)
        audio_thread.daemon = True
        audio_thread.start()

    def on_message(self, ws, message):
        """Handle incoming messages"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "Begin":
                session_id = data.get("id")
                print(f"Session started: {session_id}")

            elif msg_type == "Turn":
                transcript = data.get("transcript", "")
                formatted = data.get("turn_is_formatted", False)

                if transcript:
                    if formatted:
                        print(f"\n→ {transcript}")
                        self.full_transcript.append(transcript)
                        self.raw_transcript = " ".join(self.full_transcript)
                    else:
                        self.raw_transcript = " ".join(
                            self.full_transcript + [transcript]
                        )
                        print(f"\r... {transcript}", end="")

                    # Check for stop keyword
                    if detect_stop_keyword(self.raw_transcript):
                        print("\n\n🛑 STOP KEYWORD DETECTED!")
                        self.final_content = extract_transcript_content(
                            self.raw_transcript
                        )
                        print(f"\nCaptured content: '{self.final_content}'")
                        self.stop_event.set()
                        ws.close()

        except Exception as e:
            print(f"Message error: {e}")

    def on_error(self, ws, error):
        print(f"\nWebSocket Error: {error}")
        self.stop_event.set()

    def on_close(self, ws, close_status_code, close_msg):
        print(f"\nDisconnected: {close_status_code}")
        self.stop_event.set()

    def start_transcription(self):
        """Start voice transcription and return content when keyword detected"""
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()

        try:
            self.stream = self.audio.open(
                input=True,
                frames_per_buffer=FRAMES_PER_BUFFER,
                channels=CHANNELS,
                format=FORMAT,
                rate=SAMPLE_RATE,
            )
            print("Microphone ready")
        except Exception as e:
            print(f"Microphone error: {e}")
            return None

        # Create WebSocket
        self.ws_app = websocket.WebSocketApp(
            API_ENDPOINT,
            header={"Authorization": YOUR_API_KEY},
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        # Run WebSocket in thread
        ws_thread = threading.Thread(target=self.ws_app.run_forever)
        ws_thread.daemon = True
        ws_thread.start()

        try:
            # Keep alive until stop
            while ws_thread.is_alive() and not self.stop_event.is_set():
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\nStopping...")
            self.stop_event.set()
            if self.ws_app:
                self.ws_app.close()
        finally:
            # Cleanup
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.audio:
                self.audio.terminate()
            print("Cleanup complete")

        return self.final_content


def capture_voice_command():
    """Capture voice input until stop keyword, return transcript content"""
    transcriber = VoiceTranscriber()
    return transcriber.start_transcription()


if __name__ == "__main__":
    print("Starting voice transcription...")
    print("Say 'may the force be with you' to stop recording.")

    content = capture_voice_command()
    if content:
        print(f"\nFinal captured content: '{content}'")
    else:
        print("No content captured")
