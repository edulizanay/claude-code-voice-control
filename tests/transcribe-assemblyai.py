import assemblyai as aai
from dotenv import load_dotenv
import os
import signal
import sys

load_dotenv()
aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')

# Global transcriber for clean shutdown
transcriber = None
full_text = []

def signal_handler(sig, frame):
    print('\nStopping transcription...')
    if transcriber:
        transcriber.close()
    print(f"Full transcription: {' '.join(full_text)}")
    sys.exit(0)

def on_data(transcript: aai.RealtimeTranscript):
    if not transcript.text:
        return
    
    text = transcript.text
    full_text.append(text)
    print(f"Heard: {text}")
    
    # Check for stop keyword
    if "stop recording" in text.lower():
        print("\n🛑 Stop keyword detected!")
        transcriber.close()
        print(f"\nFull transcription: {' '.join(full_text)}")
        sys.exit(0)

# Handle Ctrl+C gracefully
signal.signal(signal.SIGINT, signal_handler)

# Start streaming
transcriber = aai.RealtimeTranscriber(
    on_data=on_data,
    sample_rate=16000
)

print("Connecting to AssemblyAI...")
transcriber.connect()

print("Start speaking! Say 'stop recording' to end, or press Ctrl+C")
microphone_stream = aai.extras.MicrophoneStream(sample_rate=16000)
transcriber.stream(microphone_stream)