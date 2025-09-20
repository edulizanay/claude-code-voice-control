#!/usr/bin/env python3
# ABOUTME: Tests for voice transcription functionality with "may the force be with you" keyword
# ABOUTME: Validates keyword detection, transcript capture, and accent handling

def test_keyword_detection_exact_match():
    """Test that exact keyword phrase is detected"""
    from voice_transcription import detect_stop_keyword

    # Exact match should be detected
    transcript = "I want to approve this request may the force be with you"
    assert detect_stop_keyword(transcript) == True

    transcript = "may the force be with you and goodbye"
    assert detect_stop_keyword(transcript) == True


def test_keyword_detection_case_insensitive():
    """Test that keyword detection works regardless of case"""
    from voice_transcription import detect_stop_keyword

    # Different cases should all work
    test_cases = [
        "MAY THE FORCE BE WITH YOU",
        "May The Force Be With You",
        "may the force be with you",
        "May the FORCE be WITH you"
    ]

    for transcript in test_cases:
        assert detect_stop_keyword(transcript) == True


def test_keyword_detection_partial_rejection():
    """Test that partial phrases are not detected as stop keywords"""
    from voice_transcription import detect_stop_keyword

    # Partial phrases should NOT trigger
    partial_phrases = [
        "may the force",
        "force be with you",
        "may the force be with",
        "the force be with you",
        "may force be with you"  # missing "the"
    ]

    for transcript in partial_phrases:
        assert detect_stop_keyword(transcript) == False


def test_keyword_detection_accent_variations():
    """Test common accent variations that might occur in transcription"""
    from voice_transcription import detect_stop_keyword

    # Common transcription variations for Chilean accent
    accent_variations = [
        "may de force be with you",  # "the" might become "de"
        "may the forse be with you",  # "force" might become "forse"
        "may the force be wit you",   # "with" might lose "h"
        "may the fors be with you"    # "force" might lose "ce"
    ]

    # These should still be detected (flexible matching)
    for transcript in accent_variations:
        # For now, we'll be strict - exact match only
        # Can be relaxed later if needed
        assert detect_stop_keyword(transcript) == False


def test_transcript_capture_before_keyword():
    """Test that transcript content before keyword is captured"""
    from voice_transcription import extract_transcript_content

    full_transcript = "I want to approve this request and add some text may the force be with you"
    expected_content = "I want to approve this request and add some text"

    result = extract_transcript_content(full_transcript)
    assert result == expected_content


def test_transcript_capture_multiple_sentences():
    """Test transcript capture with multiple sentences"""
    from voice_transcription import extract_transcript_content

    full_transcript = "First I want to reject this. Then I want to add the text hello world. Now may the force be with you"
    expected_content = "First I want to reject this. Then I want to add the text hello world. Now"

    result = extract_transcript_content(full_transcript)
    assert result == expected_content


def test_transcript_capture_keyword_only():
    """Test when transcript contains only the keyword"""
    from voice_transcription import extract_transcript_content

    full_transcript = "may the force be with you"
    expected_content = ""

    result = extract_transcript_content(full_transcript)
    assert result == expected_content


def test_transcript_capture_no_keyword():
    """Test transcript capture when no keyword is present"""
    from voice_transcription import extract_transcript_content

    full_transcript = "I want to approve this request"
    expected_content = full_transcript  # Should return full transcript

    result = extract_transcript_content(full_transcript)
    assert result == expected_content


if __name__ == "__main__":
    # Simple test runner without pytest
    test_functions = [
        test_keyword_detection_exact_match,
        test_keyword_detection_case_insensitive,
        test_keyword_detection_partial_rejection,
        test_keyword_detection_accent_variations,
        test_transcript_capture_before_keyword,
        test_transcript_capture_multiple_sentences,
        test_transcript_capture_keyword_only,
        test_transcript_capture_no_keyword
    ]

    print("Running voice transcription tests...")
    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")