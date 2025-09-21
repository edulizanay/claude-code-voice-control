# Code Cleanup TODO

## Overview
Cleaning tasks to simplify and reduce the codebase without losing functionality.

## 2. audio_generation.py
### Critical Issues:
- **Lines 43-48**: Remove silent WAV fallback - if TTS fails, fail properly instead of silently playing nothing
- **Lines 19-40**: Extract hardcoded models/voices to config constants at top:
  - `GROQ_MODEL = "playai-tts"`
  - `GROQ_VOICE = "Aaliyah-PlayAI"`
  - `OPENAI_MODEL = "tts-1"`
  - `OPENAI_VOICE = "alloy"`

## 3. get_last_exchange.py
### Refactoring Needs:
- **Lines 21-62**: Extract message parsing into separate functions:
  - `_extract_assistant_message(entry)`
  - `_extract_user_message(entry)`
- **Line 64**: Magic number `3` should be `MESSAGE_WINDOW = 3` constant
- **Lines 19-20**: Define role constants at top: `CLAUDE = "CLAUDE"`, `USER = "USER"`

## 4. llm_calls.py
### Remaining Cleanup:
- **Lines 33, 141**: `"openai/gpt-oss-120b"` hardcoded twice - make constant `DEFAULT_MODEL`
- **Lines 61-83**: DELETE unused `_extract_response_content()` function
- **Lines 137-138, 154, 163-171, 174, 178**: Remove or make debug prints configurable
- **Lines 183-186**: Remove backward compatibility wrapper if unused

## 5. tmux_controller.py
### Code Duplication Issues:
- **Lines 57-116**: Extract repeated subprocess pattern into helper:
  ```python
  def _send_tmux_keys(session, keys):
      result = subprocess.run(["tmux", "send-keys", "-t", session, keys],
                            capture_output=True, check=False)
      return result.returncode == 0
  ```
- **Line 22**: Make `"claude-active"` a constant `CLAUDE_SESSION_NAME`
- **Lines 80, 102**: Document or fix the prepended space hack

## 6. voice_transcription.py
### Configuration Extraction:
- **Line 33**: Make `STOP_KEYWORD` configurable/extractable
- **Lines 19-30**: Move all audio/API config to a config dict/file
- **Lines 36-49**: Could be simplified - these small functions could be inline

## 9. structural_pendings.md
### Already Documents TODOs:
- Aligns with our findings - especially prompt extraction to YAML
- Add: configuration extraction for models, voices, keywords

## 10. Missing: Configuration System
### Create config.yaml or config.py:
```yaml
models:
  summarization: "openai/gpt-oss-120b"
  parsing: "openai/gpt-oss-120b"

tts:
  groq:
    model: "playai-tts"
    voice: "Aaliyah-PlayAI"
  openai:
    model: "tts-1"
    voice: "alloy"

voice:
  stop_keyword: "may the force be with you"

tmux:
  session_name: "claude-active"
```

## Priority Order:
1. **HIGH**: Fix claude_voice_hook.sh line 6 (currently disabled - keeping for dev)
2. ✅ ~~**HIGH**: Extract hardcoded prompts from llm_calls.py~~ **COMPLETED**
3. **MEDIUM**: Create central configuration system
4. ✅ ~~**MEDIUM**: Remove unused code and test snippets~~ **COMPLETED**
5. **LOW**: Refactor duplicated patterns