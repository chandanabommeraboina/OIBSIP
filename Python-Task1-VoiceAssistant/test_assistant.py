"""
=============================================================================
 Unit Tests for Voice Assistant
 Verifies all mandatory requirements for Oasis Infobyte Task 1:
 1. Voice Recognition
 2. Greeting
 3. Time
 4. Date
 5. Google Search
 6. Error Handling
 7. Text-to-Speech
 8. Exit / Stop
=============================================================================
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import speech_recognition as sr

# Import functions from main module
import main


class TestVoiceAssistant(unittest.TestCase):

    @patch("main.speak")
    def test_greeting_feature(self, mock_speak):
        """Requirement 2: Respond when the user says Hello / starts up."""
        main.greet_user()
        mock_speak.assert_called_once()
        self.assertIn("Hello", mock_speak.call_args[0][0])

    @patch("main.speak")
    def test_time_feature(self, mock_speak):
        """Requirement 3: Tell current time when requested."""
        main.tell_time()
        mock_speak.assert_called_once()
        spoken_text = mock_speak.call_args[0][0]
        self.assertIn("The current time is", spoken_text)
        expected_time_str = datetime.now().strftime("%I:%M")
        self.assertIn(expected_time_str, spoken_text)

    @patch("main.speak")
    def test_date_feature(self, mock_speak):
        """Requirement 4: Tell today's date when requested."""
        main.tell_date()
        mock_speak.assert_called_once()
        spoken_text = mock_speak.call_args[0][0]
        self.assertIn("Today is", spoken_text)
        expected_date_str = datetime.now().strftime("%B")
        self.assertIn(expected_date_str, spoken_text)

    @patch("main.webbrowser.open")
    @patch("main.speak")
    def test_google_search_feature(self, mock_speak, mock_web_open):
        """Requirement 5: Recognize commands like 'Search Python programming' and open Google."""
        main.search_google("search Python programming")
        mock_web_open.assert_called_once_with("https://www.google.com/search?q=Python+programming")
        mock_speak.assert_called_with("Searching Google for Python programming...")

    @patch("main.webbrowser.open")
    @patch("main.speak")
    def test_google_search_with_google_keyword(self, mock_speak, mock_web_open):
        """Requirement 5: Recognize search with 'google' keyword."""
        main.search_google("google machine learning")
        mock_web_open.assert_called_once_with("https://www.google.com/search?q=machine+learning")

    @patch("main.speak")
    def test_exit_feature(self, mock_speak):
        """Requirement 8: Stop assistant when user says Exit, Stop, or Goodbye."""
        for exit_cmd in ["exit", "stop", "goodbye", "bye", "quit"]:
            with self.subTest(command=exit_cmd):
                result = main.process_command(exit_cmd)
                self.assertFalse(result, f"Expected {exit_cmd} to return False (exit loop)")
                self.assertIn("Goodbye", mock_speak.call_args[0][0])

    @patch("main.speak")
    def test_process_command_routing(self, mock_speak):
        """Test routing for greetings, time, and unrecognized commands."""
        # Test greeting
        self.assertTrue(main.process_command("hello"))
        self.assertIn("Hello", mock_speak.call_args[0][0])

        # Test time
        self.assertTrue(main.process_command("what is the time"))
        self.assertIn("The current time is", mock_speak.call_args[0][0])

        # Test date
        self.assertTrue(main.process_command("what is the date"))
        self.assertIn("Today is", mock_speak.call_args[0][0])

        # Test unrecognized command (Requirement 6)
        self.assertTrue(main.process_command("random unrecognized speech"))
        self.assertIn("do not understand", mock_speak.call_args[0][0])

    @patch("main.sr.Recognizer")
    @patch("main.sr.Microphone")
    def test_take_command_success(self, mock_mic, mock_recog_class):
        """Requirement 1: Listen to voice and convert speech to text."""
        mock_recog_instance = MagicMock()
        mock_recog_instance.recognize_google.return_value = "Hello Assistant"
        mock_recog_class.return_value = mock_recog_instance

        command = main.take_command()
        self.assertEqual(command, "hello assistant")

    @patch("main.speak")
    @patch("main.sr.Recognizer")
    @patch("main.sr.Microphone")
    def test_take_command_unknown_value_error(self, mock_mic, mock_recog_class, mock_speak):
        """Requirement 6: Handle unrecognized speech and ask user to repeat."""
        mock_recog_instance = MagicMock()
        mock_recog_instance.recognize_google.side_effect = sr.UnknownValueError()
        mock_recog_class.return_value = mock_recog_instance

        command = main.take_command()
        self.assertEqual(command, "")
        mock_speak.assert_called_with("Sorry, I could not understand that. Could you please repeat?")

    @patch("main.speak")
    @patch("main.sr.Recognizer")
    @patch("main.sr.Microphone")
    def test_take_command_request_error(self, mock_mic, mock_recog_class, mock_speak):
        """Requirement 6: Handle speech recognition network/service request error without crashing."""
        mock_recog_instance = MagicMock()
        mock_recog_instance.recognize_google.side_effect = sr.RequestError("Connection dropped")
        mock_recog_class.return_value = mock_recog_instance

        command = main.take_command()
        self.assertEqual(command, "")
        mock_speak.assert_called_with(
            "I cannot connect to the speech recognition service. Please check your internet connection."
        )

    @patch("builtins.input", return_value="exit")
    @patch("main.sr.Microphone", side_effect=OSError("No default input device available"))
    def test_take_command_microphone_missing_fallback(self, mock_mic, mock_input):
        """Requirement 6: Handle microphone hardware missing gracefully without crashing."""
        command = main.take_command()
        self.assertEqual(command, "exit")


if __name__ == "__main__":
    unittest.main()
