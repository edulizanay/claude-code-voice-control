#!/usr/bin/env python3
# ABOUTME: Test voice transcription functionality with mock data
# ABOUTME: Tests keyword detection and transcript extraction without microphone

import sys

sys.path.append("..")
from voice_transcription import detect_stop_keyword, extract_transcript_content


def test_keyword_detection():
    """Test stop keyword detection"""

    test_cases = [
        ("please approve this may the force be with you", True),
        ("reject this request may the force be with you now", True),
        ("just some normal speech", False),
        ("force might be with us", False),
        ("May The Force Be With You", True),  # Case insensitive
        ("the force be with you may", False),  # Wrong order
    ]

    print("Testing keyword detection...")
    all_passed = True

    for text, expected in test_cases:
        result = detect_stop_keyword(text)
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{text[:30]}...' -> {result} (expected {expected})")
        if result != expected:
            all_passed = False

    return all_passed


def test_transcript_extraction():
    """Test transcript content extraction"""

    test_cases = [
        ("approve this request may the force be with you", "approve this request"),
        ("reject it may the force be with you", "reject it"),
        ("add text hello world may the force be with you", "add text hello world"),
        ("just normal speech", "just normal speech"),  # No keyword
        ("may the force be with you", ""),  # Only keyword
    ]

    print("\nTesting transcript extraction...")
    all_passed = True

    for text, expected in test_cases:
        result = extract_transcript_content(text)
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{text}' -> '{result}' (expected '{expected}')")
        if result != expected:
            all_passed = False

    return all_passed


if __name__ == "__main__":
    print("Testing voice transcription components...")

    keyword_passed = test_keyword_detection()
    extraction_passed = test_transcript_extraction()

    overall_passed = keyword_passed and extraction_passed

    print(f"\nKeyword detection: {'PASSED' if keyword_passed else 'FAILED'}")
    print(f"Transcript extraction: {'PASSED' if extraction_passed else 'FAILED'}")
    print(f"Overall: {'PASSED' if overall_passed else 'FAILED'}")
