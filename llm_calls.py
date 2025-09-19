#!/usr/bin/env python3
# ABOUTME: Unified Groq API interface for LLM calls (summarization and command parsing)
# ABOUTME: Handles transcript summarization and voice command parsing with fallback

from groq import Groq
import re


client = Groq()


def summarize_transcript(transcript_data):
    """Summarize Claude Code actions from transcript data (existing functionality)"""

    if not transcript_data:
        return "No recent Claude activity to summarize"

    # Prepare conversation for Groq
    conversation_text = "\n".join(
        [f"{role}: {content}" for role, content in transcript_data]
    )

    # Call Groq API
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": "You are summarizing Claude Code AI assistant actions for voice control. Create a very brief summary (under 20 words) of what Claude just did for the user. Focus on the main action/task completed.",
                },
                {
                    "role": "user",
                    "content": f"Summarize this Claude Code interaction:\n{conversation_text}",
                },
            ],
            temperature=0.3,
            max_completion_tokens=300,
            top_p=1,
            stream=False,
        )

        summary = completion.choices[0].message.content
        if summary:
            return summary.strip()
        else:
            return "Claude completed a task"
    except Exception:
        # Fallback: simple keyword detection
        claude_messages = [
            content for role, content in transcript_data if role == "CLAUDE"
        ]
        if claude_messages:
            first_claude_msg = claude_messages[0].lower()
            if "function" in first_claude_msg:
                return "Claude created a function"
            elif "refactor" in first_claude_msg:
                return "Claude refactored code"
            elif "test" in first_claude_msg:
                return "Claude wrote tests"
            elif "debug" in first_claude_msg:
                return "Claude debugged code"
            else:
                return "Claude completed a task"
        else:
            return "Claude completed a task"


def parse_voice_command(speech_text):
    """Parse voice command into structured action for tmux"""

    if not speech_text or not speech_text.strip():
        return {"action": "unclear", "tmux_command": None, "text": None}

    speech_text = speech_text.strip().lower()

    # Call Groq API for parsing
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": """You parse voice commands for controlling Claude Code via tmux. Return JSON with:
- action: "approve", "reject", "add_text", or "unclear"
- tmux_command: "A" for approve, "R" for reject, the text for add_text, null for unclear
- text: extracted text for add_text actions, null otherwise

Examples:
"approve" -> {"action": "approve", "tmux_command": "A", "text": null}
"no" -> {"action": "reject", "tmux_command": "R", "text": null}
"add text hello" -> {"action": "add_text", "tmux_command": "hello", "text": "hello"}
"I don't know" -> {"action": "unclear", "tmux_command": null, "text": null}""",
                },
                {"role": "user", "content": f"Parse this voice command: {speech_text}"},
            ],
            temperature=0.1,
            max_completion_tokens=200,
            top_p=1,
            stream=False,
        )

        response = completion.choices[0].message.content.strip()

        # Try to extract JSON from response
        import json

        try:
            # Look for JSON in the response
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
        except json.JSONDecodeError:
            pass

        # If JSON parsing fails, fall through to fallback

    except Exception:
        pass

    # Fallback: Simple keyword matching
    return _fallback_command_parsing(speech_text)


def _fallback_command_parsing(speech_text):
    """Fallback command parsing using simple keyword matching"""

    speech_lower = speech_text.lower()

    # Check for approval FIRST if it's a simple approval + action pattern
    if re.match(r"(ok|okay|yes)\s+(write|add|create)", speech_lower):
        return {"action": "approve", "tmux_command": "A", "text": None}

    # Check for text addition patterns (more specific)
    text_patterns = [
        r"add (?:the )?text (.+)",
        r"enter (?:the )?text (.+)",
        r"type (?:the )?(?:message )?(.+)",
        r"write (.+)",
        r"input (.+)",
    ]

    for pattern in text_patterns:
        # Search with case-insensitive but extract from original text
        match = re.search(pattern, speech_lower)
        if match:
            # Find the same pattern in original text to preserve case
            original_match = re.search(pattern, speech_text, re.IGNORECASE)
            if original_match:
                extracted_text = original_match.group(1).strip()
            else:
                extracted_text = match.group(1).strip()
            return {
                "action": "add_text",
                "tmux_command": extracted_text,
                "text": extracted_text,
            }

    # Check for approval keywords as whole words
    approve_keywords = ["approve", "yes", "accept", "ok", "okay"]
    for keyword in approve_keywords:
        # Use word boundaries for exact matching
        if re.search(r"\b" + re.escape(keyword) + r"\b", speech_lower):
            return {"action": "approve", "tmux_command": "A", "text": None}

    # Check for rejection keywords (must be exact words or at start)
    reject_keywords = ["reject", "no", "decline", "cancel", "deny"]
    for keyword in reject_keywords:
        if speech_lower == keyword or speech_lower.startswith(keyword + " "):
            return {"action": "reject", "tmux_command": "R", "text": None}

    # Default to unclear if no patterns match
    return {"action": "unclear", "tmux_command": None, "text": None}


# Backward compatibility - keep existing function name
def summarize_claude_actions(transcript_data):
    """Backward compatibility wrapper for existing voice control hook"""
    return summarize_transcript(transcript_data)


if __name__ == "__main__":
    # Test both functions
    print("Testing transcript summarization...")
    sample_transcript = [
        ("USER", "write a function to calculate fibonacci"),
        ("CLAUDE", "I'll create a fibonacci function using recursion"),
    ]
    summary = summarize_transcript(sample_transcript)
    print(f"Summary: {summary}")

    print("\nTesting command parsing...")
    test_commands = ["approve this", "reject", "add text hello world", "I'm not sure"]

    for cmd in test_commands:
        result = parse_voice_command(cmd)
        print(f"'{cmd}' -> {result}")
