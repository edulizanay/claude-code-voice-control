#!/usr/bin/env python3
# ABOUTME: Test natural language parsing for voice commands with enhanced prompt
# ABOUTME: Validates improved LLM prompt can handle complex user intent and extract commands

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
client = Groq()


def enhanced_parse_voice_command(speech_text, event_type="notification"):
    """Enhanced voice command parser with context-aware prompts"""

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
3. Remove filler words like "no", "instead", "reject" from the actionable text.
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
3. Remove hesitation words like "hmm", "maybe" but keep the actual command.
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


# Test cases with expected outputs
TEST_CASES = [
    # NOTIFICATION EVENT TESTS (Claude waiting for approval/rejection)
    {
        "event_type": "notification",
        "input": "yes",
        "expected": {"action": "approve"},
        "description": "Simple approval during notification",
    },
    {
        "event_type": "notification",
        "input": "approve this",
        "expected": {"action": "approve"},
        "description": "Direct approval during notification",
    },
    {
        "event_type": "notification",
        "input": "sounds good",
        "expected": {"action": "approve"},
        "description": "Natural approval during notification",
    },
    {
        "event_type": "notification",
        "input": "no, add logging instead",
        "expected": {"action": "reject", "text": "add logging"},
        "description": "Rejection with alternative during notification",
    },
    {
        "event_type": "notification",
        "input": "reject this, I want to refactor the function first",
        "expected": {"action": "reject", "text": "refactor the function first"},
        "description": "Explicit rejection with alternative during notification",
    },
    {
        "event_type": "notification",
        "input": "approve this and then run tests",
        "expected": {"action": "approve"},
        "description": "Approval with ignored future command during notification",
    },
    # STOP EVENT TESTS (Claude ready for new input)
    {
        "event_type": "stop",
        "input": "run the tests",
        "expected": {"action": "command", "text": "run the tests"},
        "description": "Direct command during stop",
    },
    {
        "event_type": "stop",
        "input": "add error handling to this function",
        "expected": {
            "action": "command",
            "text": "add error handling to this function",
        },
        "description": "Detailed command during stop",
    },
    {
        "event_type": "stop",
        "input": "hmm maybe we should add some logging",
        "expected": {"action": "command", "text": "add some logging"},
        "description": "Hesitant command during stop (cleaned up)",
    },
    {
        "event_type": "stop",
        "input": "check if the tests are passing",
        "expected": {"action": "command", "text": "check if the tests are passing"},
        "description": "Instruction command during stop",
    },
]


def run_natural_language_tests():
    """Run all test cases and compare results"""
    from test_tmux_controller import send_enhanced_command

    print("🧪 Testing Enhanced Natural Language Parsing + TMUX Integration")
    print("=" * 70)

    results = []

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Event: {test_case['event_type']}")
        print(f"Input: '{test_case['input']}'")
        print(f"Expected: {json.dumps(test_case['expected'], indent=2)}")

        # Get actual result from enhanced parser
        actual = enhanced_parse_voice_command(
            test_case["input"], test_case["event_type"]
        )
        print(f"Actual: {json.dumps(actual, indent=2)}")

        # Simple comparison (ignoring original_speech field)
        actual_clean = {k: v for k, v in actual.items() if k != "original_speech"}
        parsing_passed = actual_clean == test_case["expected"]

        print(f"Parsing: {'✅ PASS' if parsing_passed else '❌ FAIL'}")

        # Test TMUX integration with mock mode
        print("TMUX Integration:")
        tmux_result = send_enhanced_command(actual_clean, mock_mode=True)
        tmux_passed = tmux_result.get("success", False)

        if tmux_passed:
            commands = tmux_result.get("commands_sent", [])
            print(f"  ✅ Would send: {commands}")
        else:
            error = tmux_result.get("error", "Unknown error")
            print(f"  ❌ TMUX Error: {error}")

        overall_passed = parsing_passed and tmux_passed
        print(f"Overall: {'✅ PASS' if overall_passed else '❌ FAIL'}")

        results.append(
            {
                "test": test_case["description"],
                "passed": overall_passed,
                "parsing_passed": parsing_passed,
                "tmux_passed": tmux_passed,
                "input": test_case["input"],
                "expected": test_case["expected"],
                "actual": actual_clean,
                "tmux_commands": tmux_result.get("commands_sent", []),
            }
        )

        print("-" * 50)

    # Summary
    overall_passed = sum(1 for r in results if r["passed"])
    parsing_passed = sum(1 for r in results if r["parsing_passed"])
    tmux_passed = sum(1 for r in results if r["tmux_passed"])
    total_count = len(results)

    print("\n📊 SUMMARY:")
    print(f"  Overall: {overall_passed}/{total_count} tests passed")
    print(f"  Parsing: {parsing_passed}/{total_count} tests passed")
    print(f"  TMUX Integration: {tmux_passed}/{total_count} tests passed")

    if overall_passed < total_count:
        print("\n❌ Failed tests:")
        for result in results:
            if not result["passed"]:
                print(f"- {result['test']}")
                if not result["parsing_passed"]:
                    print(
                        f"  Parsing Failed - Expected: {result['expected']}, Got: {result['actual']}"
                    )
                if not result["tmux_passed"]:
                    print("  TMUX Integration Failed")

    return results


if __name__ == "__main__":
    # First, show the test cases for review
    print("📋 PROPOSED TEST CASES:")
    print("=" * 50)

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"{i}. {test_case['description']}")
        print(f"   Event: {test_case['event_type']}")
        print(f"   Input: '{test_case['input']}'")
        print(f"   Expected: {json.dumps(test_case['expected'])}")
        print()

    print("\nThese test cases cover:")
    print("- Simple approvals (natural variations)")
    print("- Rejections with alternatives (text extraction)")
    print("- Direct commands (new instructions)")
    print("- Complex sequences (multiple actions)")
    print("- Ambiguous cases (hesitant but actionable)")

    # Run the tests automatically
    print("\n" + "=" * 60)
    print("RUNNING TESTS WITH REAL LLM CALLS...")
    print("=" * 60)
    run_natural_language_tests()
