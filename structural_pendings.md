# Structural Pending Developments

Core developments to implement after integrating the whole pipeline:

## 1. Extract all prompts to YAML configuration file
- **Files to modify**: `llm_calls.py`, create `prompts.yaml`
- **Description**: Move 3 hardcoded prompts from llm_calls.py to a centralized YAML config:
  - Summarization prompt (lines 37-44)
  - Notification event parsing prompt (lines 95-114)
  - Stop event parsing prompt (lines 117-135)
- **Purpose**: Keep prompts organized, version-controlled, and easier to modify without touching code

## 2. Implement comprehensive end-to-end test
- **Files to create**: `tests/test_end_to_end_pipeline.py`
- **Description**: Create test covering full pipeline: voice capture � transcription � parsing � TMUX control
- **Scope**: Test both notification and stop event flows with real integration points
- **Purpose**: Ensure complete pipeline works correctly across all components

## 3. Add caching layer for transcripts and audio
- **Files to modify**: `get_last_exchange.py`, `audio_generation.py`, `voice_control_hook.py`
- **Description**:
  - Cache parsed transcript results to avoid re-parsing same files
  - Cache generated audio files by content hash to avoid regeneration
  - Implement cache directory management and cleanup policies
- **Purpose**: Improve performance and reduce API costs for repeated operations

## 4. Add 20-second silence timeout to AssemblyAI
- **Files to modify**: `voice_transcription.py` (lines 64-84)
- **Description**:
  - Track silence duration during streaming transcription
  - Auto-terminate session if no speech detected for 20 seconds
  - Add timeout configuration and graceful session cleanup
- **Purpose**: Prevent unnecessary API costs from silent/idle transcription sessions

## 5. Format parsing prompts with bullet points
- **Files to modify**: `llm_calls.py` (lines 95-135)
- **Description**: Convert numbered instruction lists to bullet format in voice command parsing prompts
- **Purpose**: Improve prompt readability and consistency for better LLM parsing



Make it so I can activate this for all my sessions, but also I can deactivate it in each session. 

Create some UI to let the user know that they are speaking to the while this is active or show that this is active. 