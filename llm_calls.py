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
    """Classify voice command into simple action categories"""

    if not speech_text or not speech_text.strip():
        return ("unclear", speech_text)

    original_speech = speech_text.strip()

    # Call Groq API for simple classification
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": "Return only: 'approve', 'approve_all', 'reject', or 'unclear'",
                },
                {"role": "user", "content": f"Voice: {original_speech}"},
            ],
            temperature=0.1,
            max_completion_tokens=50,
            top_p=1,
            stream=False,
        )

        response = completion.choices[0].message.content.strip().lower()

        # Validate response is one of expected categories
        if response in ["approve", "approve_all", "reject", "unclear"]:
            return (response, original_speech)
        else:
            # If unexpected response, fall through to fallback
            pass

    except Exception:
        pass

    # Fallback: Simple keyword matching
    return _fallback_classification(original_speech)


def _fallback_classification(speech_text):
    """Fallback classification using simple keyword matching"""

    speech_lower = speech_text.lower()

    # Check for approve_all keywords
    approve_all_keywords = ["approve all", "accept all", "ok all", "yes all"]
    for keyword in approve_all_keywords:
        if keyword in speech_lower:
            return ("approve_all", speech_text)

    # Check for approval keywords as whole words
    approve_keywords = ["approve", "yes", "accept", "ok", "okay"]
    for keyword in approve_keywords:
        # Use word boundaries for exact matching
        if re.search(r"\b" + re.escape(keyword) + r"\b", speech_lower):
            return ("approve", speech_text)

    # Check for rejection keywords (must be exact words or at start)
    reject_keywords = ["reject", "no", "decline", "cancel", "deny"]
    for keyword in reject_keywords:
        if speech_lower == keyword or speech_lower.startswith(keyword + " "):
            return ("reject", speech_text)

    # Default to unclear if no patterns match
    return ("unclear", speech_text)


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
    test_commands = [
        "approve this",
        "approve all changes",
        "reject",
        "no this is wrong",
        "I'm not sure",
    ]

    for cmd in test_commands:
        classification, original_speech = parse_voice_command(cmd)
        print(
            f"'{cmd}' -> classification: '{classification}', original: '{original_speech}'"
        )
