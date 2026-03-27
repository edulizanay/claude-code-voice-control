<!-- ABOUTME: README for claude-code-voice-control, a hands-free voice interface for Claude Code. -->
<!-- ABOUTME: Chains 4 AI services (LLM x2, TTS, streaming STT) in a real-time bidirectional voice loop. -->

# Claude Code Voice Control

**Voice interface for Claude Code -- Claude speaks what it just did, you respond by voice, and it sends your decision back. No keyboard needed.**

Built before Claude Code had any voice features.

---

## What It Does

When Claude Code finishes a task or asks for approval, this tool:

1. Reads the live conversation to understand what just happened
2. Summarizes it out loud in natural language
3. Listens to your voice response in real-time
4. Figures out if you're approving, rejecting, or giving a new command
5. Sends the right input back to Claude Code

You stay hands-free the entire time. Say "May the Force be with you" when you're done talking -- the system detects it in the live audio stream and stops listening.

---

## How It Works

```
Claude Code Hook Event
(notification or stop)
         |
         v
+--------------------+
| 1. Read Transcript  |  Parses the JSONL conversation log
|    (last 3 msgs)    |  to understand what Claude just did
+--------------------+
         |
         v
+--------------------+
| 2. Summarize        |  LLM generates a natural sentence:
|    (LLM)            |  "I just created test_utils.py
|                     |   with 12 test cases"
+--------------------+
         |
         v
+--------------------+
| 3. Speak            |  TTS converts summary to audio
|    (Groq / OpenAI)  |  and plays it through speakers
+--------------------+
         |
         v
+--------------------+
| 4. Listen           |  Streaming STT via AssemblyAI WebSocket
|    (AssemblyAI)     |  Real-time partials displayed as you talk
|                     |  "May the Force be with you" = stop
+--------------------+
         |
         v
+--------------------+
| 5. Parse Intent     |  LLM classifies your speech:
|    (LLM)            |  approve / reject + alternative / new command
|                     |  Strips filler words, outputs structured JSON
+--------------------+
         |
         v
+--------------------+
| 6. Execute          |  Sends keystrokes to Claude Code via tmux
|    (tmux)           |  Enter (approve), Esc+text (reject),
|                     |  or text+Enter (new command)
+--------------------+
```

Four AI services chained in a single real-time loop: LLM (summarization) -> TTS (speech) -> streaming STT (listening) -> LLM (intent parsing).

---

## Design Decisions

**Streaming STT with keyword detection** -- The stop keyword ("May the Force be with you") is detected in the live audio stream via AssemblyAI's WebSocket API, not after recording finishes. This means you never touch the keyboard -- the system knows you're done talking the moment you say the phrase.

**Context-aware intent parsing** -- The LLM receives different prompts depending on the event type. Notification events (Claude is waiting for approval) parse into approve/reject. Stop events (Claude finished a task) parse into new commands. Filler words ("um", "actually", "you know what") are stripped automatically.

**Non-blocking hook architecture** -- The shell hook captures stdin, spawns the voice pipeline as a background process, and immediately returns control to Claude Code. Claude keeps working while the voice system processes in parallel.

**Multi-provider fallbacks** -- TTS falls back from Groq to OpenAI to silent WAV. LLM routing is configurable via YAML (OpenRouter primary, Groq fallback). The system degrades gracefully instead of crashing.

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| STT | AssemblyAI (real-time WebSocket, streaming partials) |
| TTS | Groq PlayAI (primary), OpenAI TTS (fallback) |
| LLM | OpenRouter / Groq (summarization + intent parsing) |
| Prompts | YAML-based templates, context-aware per event type |
| Integration | Claude Code hooks, tmux keystroke injection |
| Audio | PyAudio (microphone capture, 16kHz mono) |
| Testing | Scenario-based e2e tests with fixture data |

---

## Project Structure

```
voice_control_main.py      # Pipeline orchestrator (hook event -> voice loop -> tmux)
voice_transcription.py     # Streaming STT with AssemblyAI WebSocket + keyword detection
llm_calls.py               # LLM interface (summarization + intent parsing)
audio_generation.py        # TTS with Groq/OpenAI/silent fallback chain
get_last_exchange.py       # Transcript parser (extracts last 3 messages from JSONL)
tmux_controller.py         # Sends classified commands to Claude Code via tmux
claude_voice_hook.sh       # Shell hook (captures stdin, runs pipeline in background)
config.yaml                # All configuration (providers, models, audio, tmux)
prompts.yaml               # LLM prompts for summarization and intent parsing
tests/                     # E2E tests with scenario fixtures
```

---

## Setup

```bash
pip install groq openai pyaudio websocket-client pyyaml python-dotenv assemblyai
cp .env.example .env       # Add API keys: GROQ, OPENROUTER, ASSEMBLYAI, OPENAI
```

Configure Claude Code to use the hook by pointing to `claude_voice_hook.sh` in your Claude Code settings.

---

## Requirements

- macOS (uses `afplay` for audio playback)
- tmux session named `claude-active` running Claude Code
- API keys: AssemblyAI, Groq, OpenRouter (and optionally OpenAI for TTS fallback)
