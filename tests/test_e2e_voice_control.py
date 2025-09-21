#!/usr/bin/env python3
# ABOUTME: End-to-end tests for voice control pipeline using scenario-based data
# ABOUTME: Tests complete pipeline flow while skipping audio playback to avoid hanging

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestVoiceControlE2E(unittest.TestCase):
    """End-to-end tests for voice control system"""

    def setUp(self):
        """Set up test environment with proper mock isolation"""
        # Load scenarios from fixtures
        fixtures_path = Path(__file__).parent / "fixtures" / "scenarios.json"
        with open(fixtures_path) as f:
            self.scenarios = json.load(f)

        # Create temporary transcript file template
        self.temp_dir = tempfile.mkdtemp()
        self.transcript_path = Path(self.temp_dir) / "transcript.jsonl"

        # Sample transcript data (Claude-User-Claude exchange)
        transcript_entries = [
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "I'll help you create a test file for the project.",
                        }
                    ],
                },
            },
            {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": "Yes, create a comprehensive test",
                },
            },
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "Creating test_example.py with comprehensive test coverage...",
                        }
                    ],
                },
            },
        ]

        # Write transcript entries as JSONL
        with open(self.transcript_path, "w") as f:
            for entry in transcript_entries:
                f.write(json.dumps(entry) + "\n")

        # Store original subprocess.run for restoration
        import subprocess

        self.original_subprocess_run = subprocess.run

        # Reset any module-level imports that might cause contamination
        if "voice_control_main" in sys.modules:
            del sys.modules["voice_control_main"]

    def tearDown(self):
        """Clean up test environment and restore original state"""
        import shutil
        import subprocess

        # Clean up temporary files
        shutil.rmtree(self.temp_dir, ignore_errors=True)

        # Restore original subprocess.run
        subprocess.run = self.original_subprocess_run

        # Clear module imports to prevent contamination
        modules_to_clear = [
            "voice_control_main",
            "voice_transcription",
            "llm_calls",
            "audio_generation",
            "tmux_controller",
        ]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]

    def run_scenario_test(self, scenario_name):
        """Run a scenario test using the proven working pattern with proper isolation"""
        scenario = self.scenarios[scenario_name]
        print(f"\n--- Testing scenario: {scenario_name} ---")
        print(f"Description: {scenario['description']}")

        # Prepare hook data
        hook_data = scenario["hook_data"].copy()
        hook_data["transcript_path"] = str(self.transcript_path)

        # Track subprocess calls for this test only
        subprocess_calls = []

        def smart_subprocess_mock(cmd, *args, **kwargs):
            subprocess_calls.append(cmd)

            if "afplay" in cmd:
                return MagicMock(returncode=0)
            elif "tmux" in cmd:
                if "list-sessions" in cmd:
                    returncode = scenario.get("tmux_list_sessions_returncode", 0)
                    stdout = scenario.get(
                        "tmux_list_sessions_stdout", "claude-active: 1 windows\n"
                    )
                    return MagicMock(returncode=returncode, stdout=stdout, stderr="")
                elif "send-keys" in cmd:
                    return MagicMock(returncode=0, stdout="", stderr="")
                else:
                    return MagicMock(returncode=0, stdout="", stderr="")
            else:
                raise Exception(f"Unexpected subprocess call: {cmd}")

        # Use consistent patching pattern - all context managers
        with (
            patch("voice_transcription.capture_voice_command") as mock_voice,
            patch("llm_calls.client.chat.completions.create") as mock_llm,
            patch("audio_generation.generate_audio") as mock_audio_gen,
        ):
            # Configure mocks with scenario data
            mock_voice.return_value = scenario["voice_input"]

            # Configure LLM mock responses
            mock_summary_response = MagicMock()
            mock_summary_response.choices = [
                MagicMock(message=MagicMock(content=scenario["llm_summary_response"]))
            ]

            if "llm_parse_response" in scenario:
                mock_parse_response = MagicMock()
                mock_parse_response.choices = [
                    MagicMock(message=MagicMock(content=scenario["llm_parse_response"]))
                ]
                mock_llm.side_effect = [mock_summary_response, mock_parse_response]
            else:
                mock_llm.return_value = mock_summary_response

            # Configure audio generation mock
            mock_audio_file = MagicMock()
            mock_audio_file.unlink = MagicMock()
            mock_audio_gen.return_value = mock_audio_file

            # Use subprocess patching at module level for this test
            import subprocess

            subprocess.run = smart_subprocess_mock

            try:
                # Import after subprocess patching
                from voice_control_main import run_voice_pipeline

                # Additional patch for tmux_controller subprocess calls
                with patch(
                    "tmux_controller.subprocess.run", side_effect=smart_subprocess_mock
                ):
                    if scenario["should_succeed"]:
                        # Should complete successfully
                        run_voice_pipeline(hook_data, hook_data["hook_event_name"])

                        # Verify expectations
                        self.assertEqual(
                            mock_llm.call_count, scenario["expected_llm_calls"]
                        )

                        if scenario["voice_input"] is not None:
                            mock_voice.assert_called_once()

                        # Verify subprocess calls
                        self._verify_subprocess_calls(
                            subprocess_calls, scenario["expected_subprocess_calls"]
                        )

                    else:
                        # Should raise an exception
                        with self.assertRaises(Exception) as context:
                            run_voice_pipeline(hook_data, hook_data["hook_event_name"])

                        if "expected_error" in scenario:
                            self.assertIn(
                                scenario["expected_error"], str(context.exception)
                            )

                        # Still verify subprocess calls that happened before error
                        self._verify_subprocess_calls(
                            subprocess_calls, scenario["expected_subprocess_calls"]
                        )

            finally:
                # Restore subprocess.run for this test
                subprocess.run = self.original_subprocess_run

    def _verify_subprocess_calls(self, actual_calls, expected_calls):
        """Verify subprocess calls match expectations"""
        for expected in expected_calls:
            cmd_contains = expected["cmd_contains"]
            expected_count = expected["count"]

            if isinstance(cmd_contains, str):
                # Single string to match anywhere in the command
                matching_calls = [
                    call for call in actual_calls if cmd_contains in str(call)
                ]
            else:
                # List of strings - all must be present in the same call
                matching_calls = []
                for call in actual_calls:
                    # Convert call to list if it's already a list, or str if it's a string
                    if isinstance(call, list):
                        call_parts = call
                    else:
                        call_parts = str(call).split()

                    # Check if all required parts are in this call
                    if all(part in call_parts for part in cmd_contains):
                        matching_calls.append(call)

            actual_count = len(matching_calls)
            self.assertEqual(
                actual_count,
                expected_count,
                f"Expected {expected_count} calls containing {cmd_contains}, got {actual_count}. "
                f"Actual calls: {actual_calls}",
            )

    def test_notification_approve(self):
        """Test notification approval scenario"""
        self.run_scenario_test("notification_approve")

    def test_notification_reject(self):
        """Test notification rejection scenario"""
        self.run_scenario_test("notification_reject")

    def test_stop_event_command(self):
        """Test stop event command scenario"""
        self.run_scenario_test("stop_event_command")

    def test_tmux_session_not_found(self):
        """Test TMUX session not found error scenario"""
        self.run_scenario_test("tmux_session_not_found")

    def test_voice_capture_failure(self):
        """Test voice capture failure error scenario"""
        self.run_scenario_test("voice_capture_failure")

    def test_unclear_voice_command(self):
        """Test unclear voice command error scenario"""
        self.run_scenario_test("unclear_voice_command")


if __name__ == "__main__":
    # Run tests with unittest
    unittest.main(verbosity=2)
