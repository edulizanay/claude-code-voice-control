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
YOUR_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')

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

# Global variables
audio = None
stream = None
ws_app = None
stop_event = threading.Event()
full_transcript = []

def on_open(ws):
    """Called when WebSocket connection opens"""
    print("✅ Connected to AssemblyAI")
    print("🎤 Start speaking! Say 'over sargent' to end.\n")
    
    # Start audio streaming thread
    def stream_audio():
        global stream
        while not stop_event.is_set():
            try:
                audio_data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                # Send raw audio bytes (not JSON)
                ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
            except Exception as e:
                print(f"Audio error: {e}")
                break
    
    audio_thread = threading.Thread(target=stream_audio)
    audio_thread.daemon = True
    audio_thread.start()

def on_message(ws, message):
    """Handle incoming messages"""
    global full_transcript
    
    try:
        data = json.loads(message)
        msg_type = data.get('type')
        
        if msg_type == "Begin":
            session_id = data.get('id')
            print(f"Session started: {session_id}")
            
        elif msg_type == "Turn":
            transcript = data.get('transcript', '')
            formatted = data.get('turn_is_formatted', False)
            
            if transcript:
                if formatted:
                    print(f"\n→ {transcript}")
                    full_transcript.append(transcript)
                else:
                    print(f"\r... {transcript}", end='')
                
                # Check for stop keyword
                if "over sargent" in transcript.lower():
                    print("\n\n🛑 STOP KEYWORD DETECTED!")
                    print(f"\nFull transcript:\n{' '.join(full_transcript)}")
                    stop_event.set()
                    ws.close()
                    
    except Exception as e:
        print(f"Message error: {e}")

def on_error(ws, error):
    print(f"\nWebSocket Error: {error}")
    stop_event.set()

def on_close(ws, close_status_code, close_msg):
    print(f"\nDisconnected: {close_status_code}")
    stop_event.set()

def run():
    global audio, stream, ws_app
    
    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    
    try:
        stream = audio.open(
            input=True,
            frames_per_buffer=FRAMES_PER_BUFFER,
            channels=CHANNELS,
            format=FORMAT,
            rate=SAMPLE_RATE,
        )
        print("Microphone ready")
    except Exception as e:
        print(f"Microphone error: {e}")
        return
    
    # Create WebSocket
    ws_app = websocket.WebSocketApp(
        API_ENDPOINT,
        header={"Authorization": YOUR_API_KEY},
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    
    # Run WebSocket in thread
    ws_thread = threading.Thread(target=ws_app.run_forever)
    ws_thread.daemon = True
    ws_thread.start()
    
    try:
        # Keep alive until stop
        while ws_thread.is_alive() and not stop_event.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        stop_event.set()
        if ws_app:
            ws_app.close()
    finally:
        # Cleanup
        if stream:
            stream.stop_stream()
            stream.close()
        if audio:
            audio.terminate()
        print("Cleanup complete")

if __name__ == "__main__":
    print("Connecting to AssemblyAI v3...")
    run()