# Integration Todo: Enhanced Voice Parsing + TMUX Controller

## Overview
Move enhanced voice parsing and TMUX controller from tests to production. Test integration in `/tests/` first, then implement in root directory.

## Current Status
- ✅ Enhanced parsing works in `tests/test_natural_language_prompt.py`
- ✅ Enhanced TMUX controller works in `tests/test_tmux_controller.py`
- ❌ No integration test between enhanced parsing and TMUX controller
- ❌ Production files still use old tuple-based interface

## Key Changes We're Making

### 1. Enhanced Voice Parsing
- **Old:** `parse_voice_command(speech) → (classification, original_speech)`
- **New:** `enhanced_parse_voice_command(speech, event_type) → {"action": "approve/reject/command", "text": "cleaned_text"}`
- **Context-aware prompts:** Different behavior for notification vs stop events

### 2. Enhanced TMUX Controller
- **Old:** `send_classified_command(classification, original_speech)` - sends raw speech
- **New:** `send_enhanced_command(parsed_result)` - uses cleaned text
- **New action type:** "command" for STOP events (sends text + Enter)

## Files Involved

### Test Files (Working)
- `tests/test_natural_language_prompt.py` - Enhanced parsing with context awareness
- `tests/test_natural_language_prompt_harder.py` - Harder conversational test cases
- `tests/test_tmux_controller.py` - Enhanced TMUX controller with JSON structure

### Root Files (Need Update)
- `llm_calls.py` - Add `enhanced_parse_voice_command()` function
- `tmux_controller.py` - Add `send_enhanced_command()` function

## Integration Tasks

### Phase 1: Test Integration (CURRENT)
- [ ] Create `tests/test_integration_complete.py`
- [ ] Test enhanced parsing → enhanced TMUX flow
- [ ] Validate all scenarios:
  - Notification approval → Enter only
  - Notification rejection → Escape + cleaned_text + Enter
  - Stop command → cleaned_text + Enter
- [ ] Ensure cleaned text is used (not original speech)

### Phase 2: Production Implementation (AFTER TESTS PASS)
- [ ] Add `enhanced_parse_voice_command()` to `llm_calls.py`
- [ ] Add `send_enhanced_command()` to `tmux_controller.py`
- [ ] Keep old functions for backward compatibility
- [ ] Test production functions match test versions

## Test Scenarios to Validate

### Notification Events
1. **Approval:** "yes" → `{"action": "approve"}` → `["Enter"]`
2. **Rejection:** "no, add logging instead" → `{"action": "reject", "text": "add logging"}` → `["Escape", "text: add logging", "Enter"]`

### Stop Events
1. **Command:** "run the tests" → `{"action": "command", "text": "run the tests"}` → `["text: run the tests", "Enter"]`
2. **Cleaned command:** "hmm maybe add logging" → `{"action": "command", "text": "add logging"}` → `["text: add logging", "Enter"]`

## Success Criteria
- ✅ Integration test passes all scenarios
- ✅ Cleaned text is used instead of original speech for reject/command actions
- ✅ Context switching works (same input behaves differently for notification vs stop)
- ✅ Production functions work identically to test versions
- ✅ Old functions still work (backward compatibility)

## Risk Mitigation
- Test everything in `/tests/` folder first
- Only touch production files after tests prove integration works
- Keep old functions working to avoid breaking existing code
- Use separate branch (`integrate-enhanced-parsing`) for safety