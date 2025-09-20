## Complete Project Summary: Hands-Free Claude Code Voice Control

### Objective
Hey I'm trying to build a voice control system to operate Claude Code hands-free while away from my computer.


### Complete Flow

1. **Claude asks permission or stops** → Notification hook fires
2. **Fetch Claude's transcript for that last interaction** (need session_id somehow, apparently for stop actions works, but notifications return fewer variables)
3. **Send transcript to Groq** → Summarize what Claude did
4. **Groq generates audio summary** → Play through AirPods
5. **When audio ends** → Start recording your voice (sox)
6. **You speak response** → AssemblyAI WebSocket transcribes
7. **Say "stop recording"** → WebSocket closes, get transcription
8. **Send to Groq for parsing** → Extract action (approve/reject) + any text
9. **Send to tmux** → Type "1" for approve, "3" for reject, plus any text
10. **Claude finishes** → Stop hook fires → Could summarize again
