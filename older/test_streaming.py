import assemblyai as aai
from dotenv import load_dotenv
import os
import signal
import sys

load_dotenv()
aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')

# Global variables
transcriber = None
full_transcript = []

def signal_handler(sig, frame):
    print('\n\nStopping transcription...')
    if transcriber:
        transcriber.close()
    print(f"Final transcript: {' '.join(full_transcript)}")
    sys.exit(0)

def on_data(transcript: aai.RealtimeTranscript):
    if not transcript.text:
        return
    
    text = transcript.text
    full_transcript.append(text)
    print(f"→ {text}")
    
    # Check for stop keyword
    if "stop recording" in text.lower():
        print("\n🛑 STOP KEYWORD DETECTED!")
        transcriber.close()
        print(f"\nComplete transcript:\n{' '.join(full_transcript)}")
        sys.exit(0)

def on_error(error: aai.RealtimeError):
    print(f"Error: {error}")

# Handle Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

print("Connecting to AssemblyAI WebSocket...")
transcriber = aai.RealtimeTranscriber(
    on_data=on_data,
    on_error=on_error,
    sample_rate=16000
)

transcriber.connect()
print("✅ Connected! Start speaking...")
print("Say 'stop recording' to end, or press Ctrl+C\n")

try:
    microphone_stream = aai.extras.MicrophoneStream(sample_rate=16000)
    transcriber.stream(microphone_stream)
except Exception as e:
    print(f"Microphone error: {e}")
    transcriber.close()