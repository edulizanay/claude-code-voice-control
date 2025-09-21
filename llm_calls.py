#!/usr/bin/env python3
# ABOUTME: Unified Groq API interface for LLM calls (summarization and command parsing)
# ABOUTME: Handles transcript summarization and voice command parsing with fallback

import json
import yaml
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()
client = Groq()


# Load prompts and config from YAML files
def _load_prompts():
    """Load prompts from prompts.yaml file"""
    prompts_path = Path(__file__).parent / "prompts.yaml"
    with open(prompts_path, "r") as f:
        return yaml.safe_load(f)


def _load_config():
    """Load configuration from config.yaml file"""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


PROMPTS = _load_prompts()
CONFIG = _load_config()


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

    # Call Groq API with prompt from YAML
    try:
        prompt_template = PROMPTS["transcript_summarization"]["prompt"]
        prompt_content = prompt_template.format(
            context_text=context_text, last_message=last_message
        )
        print("🔍 DEBUG: Using transcript_summarization prompt from prompts.yaml")

        completion = client.chat.completions.create(
            model=CONFIG["models"]["summarization"],
            messages=[
                {
                    "role": "user",
                    "content": prompt_content,
                },
            ],
            **CONFIG["api_params"]["summarization"],
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

    # Get prompt from YAML based on event type
    system_prompt = PROMPTS["voice_command_parsing"][event_type]["prompt"]
    try:
        print(f"🔍 DEBUG: Using event_type='{event_type}'")
        print(
            f"🔍 DEBUG: Using voice_command_parsing.{event_type} prompt from prompts.yaml"
        )
        print(f"🔍 DEBUG: Input speech: '{original_speech}'")

        completion = client.chat.completions.create(
            model=CONFIG["models"]["parsing"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Voice: {original_speech}"},
            ],
            **CONFIG["api_params"]["parsing"],
        )

        # Extract content from response
        full_response = completion.choices[0].message.content
        print(f"🔍 DEBUG: Full LLM response: '{full_response}'")

        # Try to parse JSON from response
        try:
            # Look for JSON in the response
            start_idx = full_response.find("{")
            end_idx = full_response.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = full_response[start_idx:end_idx]
                print(f"🔍 DEBUG: Extracted JSON string: '{json_str}'")
                result = json.loads(json_str)
                result["original_speech"] = original_speech
                print(f"🔍 DEBUG: Parsed result: {result}")
                return result
            else:
                print("🔍 DEBUG: No JSON found in response")
        except json.JSONDecodeError as e:
            print(f"🔍 DEBUG: JSON parsing failed: {e}")

        # Fallback to unclear if JSON parsing fails
        print("🔍 DEBUG: Falling back to unclear")
        return {"action": "unclear", "text": original_speech}

    except Exception as e:
        print(f"🔍 DEBUG: API Error: {e}")
        return {"action": "unclear", "text": original_speech}


# Backward compatibility - keep existing function name
def summarize_claude_actions(transcript_data):
    """Backward compatibility wrapper for existing voice control hook"""
    return summarize_transcript(transcript_data)
