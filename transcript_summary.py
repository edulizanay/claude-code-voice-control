#!/usr/bin/env python3
# ABOUTME: Summarizes Claude Code transcripts using Grok API for voice control
# ABOUTME: Takes transcript data and returns concise summaries suitable for audio playback

from groq import Groq


client = Groq()


def summarize_claude_actions(transcript_data):
    """Summarize Claude Code actions from transcript data"""

    if not transcript_data:
        return "No recent Claude activity to summarize"

    # Prepare conversation for Grok
    conversation_text = "\n".join(
        [f"{role}: {content}" for role, content in transcript_data]
    )

    # Call Grok API
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
