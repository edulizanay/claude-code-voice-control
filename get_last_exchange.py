#!/usr/bin/env python3
# ABOUTME: Gets the last Claude-User-Claude exchange from transcript in minimal format
# ABOUTME: Returns exactly 3 messages with just the content, no fluff

import json
import sys
from pathlib import Path


def get_interactions(transcript_path):
    transcript_path = Path(transcript_path)

    entries = []
    with open(transcript_path, "r") as f:
        for line in f:
            entries.append(json.loads(line.strip()))

    messages = []
    for entry in reversed(entries):
        if (
            entry.get("type") == "assistant"
            and entry.get("message", {}).get("role") == "assistant"
        ):
            content = entry.get("message", {}).get("content", [])
            if isinstance(content, list):
                text = " ".join(
                    [
                        item.get("text", "")
                        for item in content
                        if item.get("type") == "text" and item.get("text", "").strip()
                    ]
                )
                if text:
                    messages.append(("CLAUDE", text))

        elif (
            entry.get("type") == "user"
            and entry.get("message", {}).get("role") == "user"
        ):
            content = entry.get("message", {}).get("content", "")
            user_text = ""

            if isinstance(content, str) and content.strip():
                # Direct string content
                user_text = content
            elif isinstance(content, list):
                # Extract text from tool results or other content items
                for item in content:
                    if item.get("type") == "tool_result":
                        tool_content = item.get("content", "")
                        if tool_content and tool_content.strip():
                            user_text = tool_content
                            break
                    elif item.get("type") == "text":
                        text_content = item.get("text", "")
                        if text_content and text_content.strip():
                            user_text = text_content
                            break

            if user_text:
                messages.append(("USER", user_text))

        if len(messages) >= 3:
            break

    messages.reverse()
    return messages[-3:]


if __name__ == "__main__":
    transcript_path = sys.argv[1]
    for role, content in get_interactions(transcript_path):
        print(f"{role}:")
        print(f"   {content}")
        print()
