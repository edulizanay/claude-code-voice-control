#!/usr/bin/env python3
# ABOUTME: Unified Groq API interface for LLM calls (summarization and command parsing)
# ABOUTME: Handles transcript summarization and voice command parsing with fallback

import json
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()
client = Groq()


def summarize_transcript(transcript_data):
    """Summarize Claude Code actions using structured transcript data"""

    if not transcript_data:
        return "No recent Claude activity to summarize"

    # Extract structured data
    context = transcript_data.get("context", [])
    last_message_tuple = transcript_data.get("last_message", ("CLAUDE", ""))

    # Build context text
    context_text = "\n".join([f"{role}: {content}" for role, content in context])

    # Extract last message
    _, last_message = last_message_tuple

    # Call Groq API with your prompt template
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": f"""Hey, you are Claude Code. You are working with a user in a project together. Here are the last interactions or the conversation history:

{context_text}

And this is your last message:
{last_message}

Your objective is to summarize your last message in a few words, like "now i need to create  this file X to add the function for Y, or "let me run this bash command to find the missing key", or "great! all tests are passing".""",
                },
            ],
            temperature=0.3,
            max_completion_tokens=300,
            top_p=1,
            stream=False,
        )

        summary = completion.choices[0].message.content
        return summary.strip() if summary else "I completed a task"

    except Exception:
        # Simple fallback
        return "I completed a task"


def _extract_response_content(llm_response):
    """Extract content from <response> tags in LLM output"""
    try:
        # Find content between <response> and </response> tags
        start_tag = "<response>"
        end_tag = "</response>"

        start_idx = llm_response.find(start_tag)
        if start_idx == -1:
            return None

        start_idx += len(start_tag)
        end_idx = llm_response.find(end_tag, start_idx)
        if end_idx == -1:
            return None

        # Extract and clean the content
        content = llm_response[start_idx:end_idx].strip()
        return content.lower() if content else None

    except Exception:
        return None


def parse_voice_command(speech_text, event_type="notification"):
    """Parse voice commands with context-aware prompts for notification and stop events"""

    if not speech_text or not speech_text.strip():
        return {"action": "unclear", "text": speech_text}

    original_speech = speech_text.strip()

    # Choose prompt based on event type
    if event_type == "notification":
        system_prompt = """You are parsing voice commands when Claude Code is waiting for approval/rejection.

Context: Claude just made a suggestion and is waiting for user response.

Categories:
- 'approve': user agrees (→ send Enter key only)
- 'reject': user disagrees and gives alternative (→ send Escape + alternative text + Enter)

<thinking>
1. Is the user agreeing or disagreeing with Claude's suggestion?
2. If disagreeing, what alternative text should be sent to Claude?
3. Remove filler words like "no", "instead", "reject", "actually", "nah" from the actionable text.
4. Ignore any "and then" future commands - focus only on the current approval/rejection.
</thinking>

<response>
Return JSON format:
For approval: {"action": "approve"}
For rejection: {"action": "reject", "text": "clean alternative text"}
For unclear: {"action": "unclear"}
</response>"""

    else:  # event_type == "stop"
        system_prompt = """You are parsing voice commands when Claude Code is ready for new input.

Context: Claude finished a task and is ready for the next command.

Categories:
- 'command': user gives new instruction (→ send text + Enter)

<thinking>
1. What command does the user want to send to Claude?
2. Clean up the text but preserve the core instruction.
3. Remove hesitation words like "hmm", "maybe", "um", "actually", "you know what" but keep the actual command.
4. Remove temporal words like "now", "let's", "go ahead and" but keep the action.
</thinking>

<response>
Return JSON format:
For command: {"action": "command", "text": "clean command text"}
For unclear: {"action": "unclear"}
</response>"""
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Voice: {original_speech}"},
            ],
            temperature=0.1,
            max_completion_tokens=300,
            top_p=1,
            stream=False,
        )

        # Extract content from response
        full_response = completion.choices[0].message.content

        # Try to parse JSON from response
        try:
            # Look for JSON in the response
            start_idx = full_response.find("{")
            end_idx = full_response.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = full_response[start_idx:end_idx]
                result = json.loads(json_str)
                result["original_speech"] = original_speech
                return result
        except json.JSONDecodeError:
            pass

        # Fallback to unclear if JSON parsing fails
        return {"action": "unclear", "text": original_speech}

    except Exception as e:
        print(f"Error: {e}")
        return {"action": "unclear", "text": original_speech}


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
