#!/usr/bin/env python3
# ABOUTME: Unified Groq API interface for LLM calls (summarization and command parsing)
# ABOUTME: Handles transcript summarization and voice command parsing with fallback

from groq import Groq


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
                    "content": """You are a voice command classifier. You are listening to a conversation between a user and a Claude Code AI assistant. You are given a voice command and you need to classify it into one of the following categories:
- 'approve': when the user agrees with the current suggestion
- 'approve_all': when the user agrees with all suggestions
- 'reject': when the user disagrees with the current suggestion

<thinking>
Analyze the voice command here. Consider:
- Is the user expressing agreement or disagreement?
- What keywords or phrases indicate their intent?
</thinking>

<response>
[Return ONLY one of: approve, approve_all, or reject]
</response>""",
                },
                {"role": "user", "content": f"Voice: {original_speech}"},
            ],
            temperature=0.1,
            max_completion_tokens=250,
            top_p=1,
            stream=False,
        )

        # Extract content from <response> tags, or use direct response
        full_response = completion.choices[0].message.content
        response = _extract_response_content(full_response)

        # If no structured response found, try using the raw response
        if not response:
            response = full_response.strip().lower()

        # Trust the LLM response - if it's not a valid category, mark as unclear
        if response and response in ["approve", "approve_all", "reject"]:
            return (response, original_speech)
        else:
            return ("unclear", original_speech)

    except Exception:
        return ("unclear", original_speech)


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
