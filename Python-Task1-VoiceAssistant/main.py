"""
=============================================================================
 Oasis Infobyte Internship - Python Programming
 Task 1: Voice Assistant (Beginner Tier)
 Developed by: Chandana
 Description: A beginner-friendly Python voice assistant that listens to
              spoken voice commands, processes the user's intent, and responds
              using text-to-speech.
=============================================================================
"""

import sys
import webbrowser
import urllib.parse
from datetime import datetime
import speech_recognition as sr
import pyttsx3

# Global variable to hold our text-to-speech engine instance
_tts_engine = None


def init_tts_engine():
    """
    Initializes and configures the pyttsx3 text-to-speech engine.
    Sets speech rate and volume.
    """
    global _tts_engine
    if _tts_engine is None:
        try:
            _tts_engine = pyttsx3.init()
            # Set speed of speech (default is ~200, 175 is clear and natural)
            _tts_engine.setProperty('rate', 175)
            # Set volume level (0.0 to 1.0)
            _tts_engine.setProperty('volume', 1.0)
        except Exception as error:
            print(f"[Warning] Could not initialize voice audio engine: {error}")
            print("[Info] The assistant will still print responses to the console.")
            _tts_engine = False
    return _tts_engine


def speak(text):
    """
    Speaks the given text out loud using pyttsx3 and prints it to the console.
    
    Parameters:
        text (str): The response string the assistant should speak and print.
    """
    # 1. Always display the response clearly in the console
    print(f"\nAssistant: {text}\n")

    # 2. Speak the response aloud using the TTS engine
    engine = init_tts_engine()
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as error:
            print(f"[TTS Error] Voice output failed: {error}")


def greet_user():
    """
    Greets the user warmly when the assistant starts up.
    """
    speak("Hello! I am your Python Voice Assistant. How can I help you today?")


def tell_time():
    """
    Fetches the current local time and speaks it to the user.
    Example output format: "11:30 AM"
    """
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    speak(f"The current time is {current_time}.")


def tell_date():
    """
    Fetches today's date and speaks it to the user.
    Example output format: "Friday, November 13, 2026"
    """
    today = datetime.now()
    current_date = today.strftime("%A, %B %d, %Y")
    speak(f"Today is {current_date}.")


def search_google(query):
    """
    Opens a Google search for the requested query in the default web browser.
    
    Parameters:
        query (str): The topic or keywords to search for.
    """
    # Clean up common phrasing like "search for", "search", or "google"
    cleaned_query = query.strip()
    for prefix in ["search for", "search", "google for", "google"]:
        if cleaned_query.lower().startswith(prefix):
            cleaned_query = cleaned_query[len(prefix):].strip()

    if not cleaned_query:
        speak("What would you like me to search for on Google?")
        return

    speak(f"Searching Google for {cleaned_query}...")
    encoded_query = urllib.parse.quote_plus(cleaned_query)
    search_url = f"https://www.google.com/search?q={encoded_query}"
    webbrowser.open(search_url)


def take_command():
    """
    Listens to speech through the microphone and converts it to text
    using Google Web Speech API. Handles errors gracefully without crashing.
    
    Returns:
        str: The recognized command in lowercase, or an empty string on failure.
    """
    recognizer = sr.Recognizer()

    try:
        # Connect to user microphone
        with sr.Microphone() as source:
            print("-" * 50)
            print("Listening... (Please speak into your microphone)")
            # Calibrate for 0.8 seconds to filter out background ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            # Listen with a 5-second timeout waiting for speech to begin
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)

        print("Recognizing speech...")
        # Convert speech audio into text using Google Speech Recognition
        command = recognizer.recognize_google(audio, language="en-US")
        print(f"You said: \"{command}\"")
        return command.lower().strip()

    except sr.WaitTimeoutError:
        # User did not speak within the 5-second timeout window
        print("[Status] No speech detected within the timeout limit.")
        return ""

    except sr.UnknownValueError:
        # The speech could not be transcribed
        speak("Sorry, I could not understand that. Could you please repeat?")
        return ""

    except sr.RequestError as error:
        # Internet connection or Google Speech API service error
        print(f"[Error] Speech recognition service issue: {error}")
        speak("I cannot connect to the speech recognition service. Please check your internet connection.")
        return ""

    except (AttributeError, OSError) as error:
        # Occurs when microphone is missing or PyAudio is not installed
        print(f"\n[Microphone Error] {error}")
        print("[Tip] Ensure your microphone is plugged in and PyAudio is installed.")
        print("      To install PyAudio: pip install pyaudio")
        # Provide keyboard fallback so testing continues even without a mic
        try:
            typed_input = input("\n[Keyboard Fallback] Type your command (or 'exit' to quit): ").strip()
            return typed_input.lower()
        except (EOFError, KeyboardInterrupt):
            return "exit"

    except Exception as error:
        # Catch-all for any other unexpected system issues
        print(f"[Unexpected Error] {error}")
        return ""


def process_command(command):
    """
    Processes the recognized command string and triggers the appropriate action.
    
    Parameters:
        command (str): The recognized user speech text in lowercase.
        
    Returns:
        bool: True to continue listening in the loop, False to exit the assistant.
    """
    # If no speech was recognized, silently continue listening
    if not command:
        return True

    # Feature 8: Exit / Stop / Goodbye
    if any(exit_word in command for exit_word in ["exit", "stop", "goodbye", "bye", "quit"]):
        speak("Goodbye! Have a great day ahead.")
        return False

    # Feature 2: Greeting ("Hello", "Hi", "Hey")
    elif any(greet in command for greet in ["hello", "hi", "hey"]):
        speak("Hello! How can I help you today?")
        return True

    # Feature 3: Current Time
    elif "time" in command:
        tell_time()
        return True

    # Feature 4: Current Date
    elif "date" in command or "today" in command or "day" in command:
        tell_date()
        return True

    # Feature 5: Google Search
    elif "search" in command or "google" in command:
        search_google(command)
        return True

    # Feature 6: Unrecognized Command Handling
    else:
        speak("I am sorry, I do not understand that command yet. You can ask for time, date, a Google search, or say goodbye to exit.")
        return True


def main():
    """
    Main function that runs the assistant in a continuous listening loop
    until the user says exit, stop, or goodbye.
    """
    print("=" * 60)
    print("         OASIS INFOBYTE PYTHON VOICE ASSISTANT")
    print("=" * 60)
    print("Ready to listen for commands:")
    print(" - 'Hello' / 'Hi'")
    print(" - 'What is the time?'")
    print(" - 'What is today's date?'")
    print(" - 'Search Python programming' / 'Google Artificial Intelligence'")
    print(" - 'Exit' / 'Stop' / 'Goodbye'")
    print("=" * 60)

    # Initial greeting
    greet_user()

    # Continuous listening loop
    is_running = True
    while is_running:
        try:
            user_command = take_command()
            is_running = process_command(user_command)
        except KeyboardInterrupt:
            # Handle Ctrl+C from terminal gracefully
            print("\n")
            speak("Program stopped by user. Goodbye!")
            is_running = False

    print("\nAssistant has shut down successfully.")


if __name__ == "__main__":
    main()
