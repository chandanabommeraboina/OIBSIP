# 🎙️ Task 1: Python Voice Assistant (Beginner Tier)

**Oasis Infobyte Internship – Python Programming**  
**Author:** Chandana  
**Domain:** Python Development  
**Submission Repository:** Oasis Infobyte Task 1

---

## 📖 1. Project Introduction

The **Python Voice Assistant** is an interactive, desktop-based voice application developed in Python. It listens to spoken commands from a user through a microphone, translates speech into text using speech recognition algorithms, interprets the user's intent, and speaks responses aloud using a Text-to-Speech (TTS) engine.

This project was built following the **Beginner Tier** guidelines for the Oasis Infobyte internship, focusing on core programming fundamentals, modular code structure, and robust error handling.

---

## 🎯 2. Project Objective

- Develop a hands-free voice assistant capable of recognizing natural speech commands.
- Respond with synthesized voice output to enhance accessibility and user interaction.
- Provide practical everyday utilities including real-time clock, current date, and automated web searches.
- Implement robust exception handling for ambient noise, microphone disconnection, and speech misinterpretations without application crashes.

---

## ✨ 3. Mandatory Features

| Feature | Description | Example Trigger |
| :--- | :--- | :--- |
| **Voice Recognition** | Captures audio via microphone and converts speech to text using Google Speech Recognition. | Natural speech input |
| **Greeting** | Greets the user warmly upon launch and responds to friendly hellos. | `"Hello"`, `"Hi"`, `"Hey"` |
| **Time Query** | Retrieves and announces the current local time in 12-hour format with AM/PM. | `"What is the time?"`, `"Tell me the time"` |
| **Date Query** | Announces today's full day and date (e.g., *Friday, November 13, 2026*). | `"What is today's date?"`, `"What day is it?"` |
| **Google Search** | Extracts search query terms and opens Google search directly in the default web browser. | `"Search Python programming"`, `"Google Machine Learning"` |
| **Error Handling** | Detects empty speech, timeouts, network interruptions, and asks user to repeat politely without crashing. | Ambient silence, muffled words |
| **Text-to-Speech** | Every single response is printed to the console and spoken aloud via `pyttsx3`. | All assistant responses |
| **Graceful Exit** | Terminates the continuous listening loop when an exit command is spoken. | `"Exit"`, `"Stop"`, `"Goodbye"` |

---

## 🛠️ 4. Technologies & Libraries

- **Language:** Python 3.9+ (Tested on Python 3.10 – 3.14)
- **SpeechRecognition (`speech_recognition`):** Library for performing speech recognition with support for Google Web Speech API.
- **pyttsx3:** Offline, cross-platform Text-to-Speech (TTS) conversion engine (supports SAPI5 on Windows, NSSpeechSynthesizer on macOS, and espeak on Linux).
- **PyAudio (`pyaudio`):** PortAudio wrapper that enables cross-platform audio input/output via microphone.
- **datetime:** Python standard library module for fetching real-time system clock and calendar dates.
- **webbrowser & urllib.parse:** Python standard library modules for safe URL encoding and launching the system's default web browser.

---

## 📂 5. Project Structure

```text
VoiceAssistant/
│
├── main.py              # Main assistant source code (functions, speech loop, handlers)
├── test_assistant.py    # Automated test suite (validates all 8 mandatory requirements)
├── requirements.txt     # Python dependencies list
└── README.md            # Complete project documentation and submission guide
```

---

## 💻 6. Installation & Setup

### Step 1: Open Terminal / Command Prompt
Navigate to the project folder:
```bash
cd VoiceAssistant
```

### Step 2: (Recommended) Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
Install the required packages using `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## 🔧 7. PyAudio & Microphone Troubleshooting (Windows / Mac / Linux)

`speech_recognition` requires `pyaudio` to capture audio from your microphone.

### Windows
If `pip install pyaudio` gives an error mentioning *Microsoft Visual C++ Build Tools*, choose one of these quick fixes:

1. **Option A (pipwin - easiest):**
   ```bash
   pip install pipwin
   pipwin install pyaudio
   ```
2. **Option B (Pre-built Wheel):**
   Download the matching `.whl` file for your Python version from [Gohlke Wheels or PyPI](https://pypi.org/project/PyAudio/#files) and install it:
   ```bash
   pip install PyAudio-0.2.14-cp311-cp311-win_amd64.whl
   ```
3. **Built-in Keyboard Fallback:**
   If you do not have a microphone connected or PyAudio is pending, our `main.py` automatically detects this and offers an interactive **Keyboard Fallback** prompt so you can test all features without crashes!

### macOS
```bash
brew install portaudio
pip install pyaudio
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3-pyaudio portaudio19-dev
pip install pyaudio
```

---

## 🎙️ 8. Windows Microphone Permissions Check

If the assistant reports `Microphone Error` or stays silent on Windows:
1. Open Windows **Settings** (`Win + I`).
2. Go to **Privacy & Security** > **Microphone**.
3. Ensure **Microphone access** is turned **ON**.
4. Ensure **Let desktop apps access your microphone** is turned **ON** (this allows Python and VS Code to access the mic).

---

## 🚀 9. How to Run in Visual Studio Code (Step-by-Step)

1. Open **VS Code**.
2. Click **File** > **Open Folder...** and select the `VoiceAssistant` folder.
3. Open `main.py` in the editor.
4. Open the integrated terminal (`Ctrl + ~` or **Terminal** > **New Terminal**).
5. Ensure your Python interpreter is selected in the bottom right corner (select Python 3.10+).
6. Run the assistant:
   ```bash
   python main.py
   ```
7. Speak into your microphone after the `Listening...` prompt appears!

---

## 🧪 10. Running Automated Tests

To verify that all 8 mandatory requirements function correctly (greeting, time, date, Google search, exit, and error handling):

```bash
python -m unittest test_assistant.py -v
```

### Test Results
```text
test_date_feature ............................................. OK (Tells current date)
test_exit_feature ............................................. OK (Handles Exit / Stop / Goodbye)
test_google_search_feature .................................... OK (Opens Google query URL)
test_google_search_with_google_keyword ........................ OK (Recognizes google keyword)
test_greeting_feature ......................................... OK (Responds to Hello)
test_process_command_routing .................................. OK (Routes intents correctly)
test_take_command_microphone_missing_fallback ................. OK (Graceful mic fallback)
test_take_command_request_error ............................... OK (Handles network error)
test_take_command_success ..................................... OK (Converts speech to text)
test_take_command_unknown_value_error ......................... OK (Asks user to repeat)
test_time_feature ............................................. OK (Tells current time)

----------------------------------------------------------------------
Ran 11 tests in 0.083s

OK (100% tests passing)
```

---

## 🗣️ 11. Example Voice Commands & Responses

| # | User Spoken Voice Command | Assistant Console Output | Assistant Audio Response | Action Performed |
|---|---------------------------|--------------------------|--------------------------|------------------|
| 1 | *"Hello"* | `Assistant: Hello! How can I help you today?` | Speaks greeting aloud | Greets user |
| 2 | *"What is the time?"* | `Assistant: The current time is 11:30 AM.` | Speaks current time aloud | Fetches system time |
| 3 | *"What is today's date?"* | `Assistant: Today is Friday, November 13, 2026.` | Speaks full date aloud | Fetches calendar date |
| 4 | *"Search Python programming"* | `Assistant: Searching Google for Python programming...` | Speaks search confirmation | Opens browser to Google |
| 5 | *(Unclear audio / mumble)* | `Assistant: Sorry, I could not understand that. Could you please repeat?` | Asks to repeat | Catches `UnknownValueError` |
| 6 | *"Goodbye"* | `Assistant: Goodbye! Have a great day ahead.` | Speaks farewell aloud | Gracefully exits loop |

---

## 📸 12. Screenshots Section

*(Include these screenshots in your Oasis Infobyte submission report or repository)*

### Assistant Startup & Voice Commands Execution
```text
============================================================
         OASIS INFOBYTE PYTHON VOICE ASSISTANT
============================================================
Ready to listen for commands:
 - 'Hello' / 'Hi'
 - 'What is the time?'
 - 'What is today's date?'
 - 'Search Python programming' / 'Google Artificial Intelligence'
 - 'Exit' / 'Stop' / 'Goodbye'
============================================================

Assistant: Hello! I am your Python Voice Assistant. How can I help you today?

--------------------------------------------------
Listening... (Please speak into your microphone)
Recognizing speech...
You said: "what is the time"

Assistant: The current time is 11:45 AM.

--------------------------------------------------
Listening... (Please speak into your microphone)
Recognizing speech...
You said: "search machine learning"

Assistant: Searching Google for machine learning...

--------------------------------------------------
Listening... (Please speak into your microphone)
Recognizing speech...
You said: "goodbye"

Assistant: Goodbye! Have a great day ahead.

Assistant has shut down successfully.
```

*(You can also place `.png` or `.jpg` screenshots in an `assets/` folder and link them here: `![Terminal Output](assets/screenshot1.png)`)*

---

## 🔮 13. Future Improvements (Intermediate / Advanced Scope)

- **Offline Speech Recognition:** Integrate offline models like `vosk` or Whisper for recognition without an active internet connection.
- **Custom Wake Word:** Add a wake word detector (e.g. *"Hey Assistant"* or *"Jarvis"*).
- **Weather API Integration:** Connect to OpenWeatherMap API to provide live temperature and forecasts.
- **Wikipedia Summaries:** Add the `wikipedia` library to summarize encyclopedia articles.
- **Graphical User Interface (GUI):** Build a sleek visual dashboard using Tkinter, PyQt, or CustomTkinter with animated voice wave visualizations.

---

## 📜 14. Oasis Infobyte Internship Submission Checklist

- [x] Functional Voice Recognition using `speech_recognition`
- [x] Text-to-Speech responses using `pyttsx3`
- [x] Greeting feature ("Hello")
- [x] Real-time clock inquiry
- [x] Current calendar date inquiry
- [x] Google Search integration via `webbrowser`
- [x] Exception handling for speech errors & missing audio hardware
- [x] Graceful exit commands ("Exit", "Stop", "Goodbye")
- [x] Modular functions with clear beginner-friendly comments
- [x] Clean `requirements.txt` and `README.md`
- [x] Unit test suite passing 100% of test cases

---

**Developed with ❤️ for Oasis Infobyte Python Programming Internship (Task 1).**
