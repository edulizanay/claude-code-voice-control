import assemblyai as aai
from dotenv import load_dotenv
import os

load_dotenv()
aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')

# Test with your WAV file first
transcriber = aai.Transcriber()
transcript = transcriber.transcribe("test2.wav")

if transcript.status == aai.TranscriptStatus.error:
    print(f"Error: {transcript.error}")
else:
    print(f"Transcription: {transcript.text}")