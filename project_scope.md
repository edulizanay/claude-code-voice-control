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

**Two Groq Prompts Needed** ideally in the same .yaml for simplicity. One for summarization of Claude's actions ad another to parse the user's input. Exact API call examples for Groq can be found in @groq_examples.py. Use those models. 

So far we've been able to test:
1. TMUX messages with claude code. An example can be found in @tmux_context.md
2. Recording with my voice. An example can be found in @audio_switch_test.sh
3. **Hook Data Differences:**
    - **Stop hook**: Receives full JSON with session_id, transcript_path, cwd, hook_event_name
    - **Notification hook**: Receives EMPTY stdin (no data at all) - this is why we can't get session_id
4. **Working Symlink:** /tmp/test_hook.sh -> /Users/eduardolizana/Desktop/2. python-projects/15. tmux-test/test_hook.sh
(Using symlink to avoid space-in-path issues)
5. AssemblyAI Configuration: **Speech-to-text working**, AssemblyAI v3 WebSocket API configured and tested
   - Using real-time transcription 
   - Keyword detection "stop recording" to end capture
   - Tested with recordings up to 30 seconds
   - An example can be found in /Users/eduardolizana/Desktop/2. python-projects/15. tmux-test/older/streaming_example.py


### Current focus:

**Hooks Setup:**
- Configured in .claude/settings.local.json for project-specific hooks
- Both Stop and Notification hooks are firing correctly
- Using symlink at /tmp/test_hook.sh to avoid path spacing issues


### The Core Problem:

**BLOCKER**: Cannot identify which transcript to read during Notification events because:
- Multiple Claude Code sessions could be running
- Notification hook receives no session_id
- Need alternative method to link notification to correct transcript file

