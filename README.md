# Oasis Infobyte (OIBSIP) — Python Programming Internship

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg?logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Completed-success.svg)
![Track](https://img.shields.io/badge/Internship-Python%20Programming-orange.svg)
![Organization](https://img.shields.io/badge/Organization-Oasis%20Infobyte-brightgreen.svg)
![Verified Tests](https://img.shields.io/badge/Tests-54%2F54%20Passing%20(100%25)-success.svg)

Welcome to the official repository for the **Oasis Infobyte Internship in Python Programming (OIBSIP)**. This repository contains the complete source code, documentation, test suites, and deliverables for all **five internship tasks**, structured in accordance with the official Oasis Infobyte submission guidelines.

---

## 👨‍💻 Intern Profile

| Field | Details |
| :--- | :--- |
| **Intern Name** | Chandana |
| **Internship Track** | Python Programming |
| **Internship Domain** | Software Development / Python |
| **Host Organization** | Oasis Infobyte |
| **Submission Repository** | [OIBSIP](https://github.com/chandanabommeraboina/OIBSIP) |
| **Operating System** | Microsoft Windows 11 (64-bit) |
| **Primary Language** | Python 3 (Python 3.10 – 3.14) |

---

## 📂 Repository Structure

The projects are organized into dedicated task folders with clean modular code, automated test suites, requirements specifications, and comprehensive documentation:

```text
OIBSIP/
│
├── Python-Task1-VoiceAssistant/
│   ├── main.py                     # Core voice assistant application
│   ├── test_assistant.py           # Automated test suite (11 test cases)
│   ├── requirements.txt            # Dependency list (SpeechRecognition, pyttsx3, pyaudio)
│   └── README.md                   # Full documentation & usage guide
│
├── Python-Task2-BMICalculator/
│   ├── main.py                     # Modern Tkinter GUI & BMI analytics engine
│   ├── test_suite.py               # Automated test suite (11 test cases)
│   ├── requirements.txt            # Dependencies (matplotlib, sqlite3)
│   ├── bmi_history.db              # SQLite historical database seed
│   ├── screenshots/                # Application output & trend visualizations
│   │   ├── demo-output.png
│   │   └── trend-graph.png
│   └── README.md                   # Detailed project report
│
├── Python-Task3-RandomPasswordGenerator/
│   ├── main.py                     # Dual-mode (CLI & Tkinter GUI) password generator
│   ├── test_suite.py               # Automated test suite (10 test cases)
│   ├── requirements.txt            # Standard library specification
│   ├── screenshots/                # Application output demonstration
│   │   └── demo-output.png
│   └── README.md                   # Comprehensive security & design documentation
│
├── Python-Task4-WeatherApp/
│   ├── main.py                     # OpenWeatherMap CLI client with live weather lookup
│   ├── test_weather.py             # Automated unit test suite (10 test cases)
│   ├── requirements.txt            # Dependencies (requests, python-dotenv)
│   ├── .env.example                # Safe environment variable configuration template
│   └── README.md                   # Detailed API documentation & execution guide
│
└── Python-Task5-ChatApplication/
    ├── server.py                   # Multi-threaded TCP socket chat server
    ├── client.py                   # Tkinter GUI real-time chat client
    ├── database.py                 # SQLite ACID storage engine (users, rooms, messages)
    ├── main.py                     # Unified entry point launcher
    ├── test_chat.py                # Automated integration test suite (12 test cases)
    ├── requirements.txt            # Standard library networking specification
    ├── chat_app.db                 # Seed database with sample rooms and users
    └── README.md                   # Complete protocol & architecture documentation
```

---

## 🚀 Tasks Overview & Deliverables

### [Task 1: Voice Assistant](file:///./Python-Task1-VoiceAssistant)
- **Folder:** [`Python-Task1-VoiceAssistant/`](./Python-Task1-VoiceAssistant/)
- **Description:** An interactive desktop voice assistant that captures voice commands via microphone, translates speech to text with Google Speech Recognition, and responds with synthetic voice output via `pyttsx3`.
- **Key Features:**
  - Real-time natural speech recognition with ambient noise adjustment.
  - Text-to-speech audio feedback for all interactions.
  - Live clock and current calendar date announcements.
  - Automated Google search browser integration.
  - Interactive keyboard fallback when microphone hardware is unavailable.
- **Technologies:** `Python 3`, `speech_recognition`, `pyttsx3`, `pyaudio`, `webbrowser`.
- **Test Status:** 11 / 11 automated unit tests passed (100%).

---

### [Task 2: BMI Calculator](file:///./Python-Task2-BMICalculator)
- **Folder:** [`Python-Task2-BMICalculator/`](./Python-Task2-BMICalculator/)
- **Description:** A modern Graphical User Interface (GUI) desktop application for calculating Body Mass Index (BMI), categorizing health status according to WHO standards, and visualizing longitudinal weight/BMI trends.
- **Key Features:**
  - Metric and Imperial unit calculation support.
  - WHO health category categorization (Underweight, Normal, Overweight, Obese).
  - Embedded SQLite database for historical entry logging.
  - Visual trend analytics with Matplotlib charting and color-coded BMI zones.
- **Technologies:** `Python 3`, `tkinter`, `sqlite3`, `matplotlib`.
- **Test Status:** 11 / 11 automated tests passed (100%).

---

### [Task 3: Random Password Generator](file:///./Python-Task3-RandomPasswordGenerator)
- **Folder:** [`Python-Task3-RandomPasswordGenerator/`](./Python-Task3-RandomPasswordGenerator/)
- **Description:** A cryptographically secure random password generator offering both an interactive Command-Line Interface (CLI) and an intuitive Graphical User Interface (GUI).
- **Key Features:**
  - Cryptographically secure randomness powered by the OS-level `secrets` module.
  - Guaranteed inclusion of all selected character types (uppercase, lowercase, numbers, symbols).
  - Minimum length enforcement ($\ge 8$ characters) and strength scoring (Weak, Medium, Strong).
  - Ambiguous character exclusion filter (`0`, `O`, `1`, `l`, `I`).
  - One-click clipboard copy integration in GUI mode.
- **Technologies:** `Python 3`, `secrets`, `string`, `tkinter`, `collections`.
- **Test Status:** 10 / 10 automated test cases passed (100%).

---

### [Task 4: Basic Weather App](file:///./Python-Task4-WeatherApp)
- **Folder:** [`Python-Task4-WeatherApp/`](./Python-Task4-WeatherApp/)
- **Description:** A reliable command-line weather application that connects to the OpenWeatherMap REST API to fetch real-time atmospheric data by city name or ZIP code.
- **Key Features:**
  - Real-time weather data retrieval: temperature, feels-like, humidity, wind speed, pressure, and descriptions.
  - Dual temperature scale support (Celsius and Fahrenheit).
  - Robust error handling for network dropouts, rate limits, and invalid city queries.
  - Secure credential management using `.env` environment variables via `python-dotenv`.
- **Technologies:** `Python 3`, `requests`, `python-dotenv`, `OpenWeatherMap REST API`.
- **Test Status:** 10 / 10 automated unit tests passed (100%).

---

### [Task 5: Real-Time Chat Application](file:///./Python-Task5-ChatApplication)
- **Folder:** [`Python-Task5-ChatApplication/`](./Python-Task5-ChatApplication/)
- **Description:** A full-stack, real-time multi-room client-server desktop chat application built with TCP sockets, multi-threading, SQLite database persistence, and Tkinter GUI.
- **Key Features:**
  - Multi-threaded TCP socket server supporting concurrent connected clients.
  - Secure user registration and authentication with salted PBKDF2-SHA256 password hashing.
  - Dynamic chat room creation, room joining, and broadcast isolation.
  - Persistent chat history restored from SQLite upon joining rooms.
  - Modern desktop chat window with emoji support, live user list, and formatted timestamps.
- **Technologies:** `Python 3`, `socket`, `threading`, `sqlite3`, `hashlib`, `tkinter`.
- **Test Status:** 12 / 12 automated integration tests passed (100%).

---

## 🧪 Comprehensive Test Summary

All projects include comprehensive automated test suites using Python's `unittest` framework:

| Task Folder | Project | Test Runner | Total Tests | Passed | Success Rate |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `Python-Task1-VoiceAssistant` | Voice Assistant | `test_assistant.py` | 11 | 11 | **100%** |
| `Python-Task2-BMICalculator` | BMI Calculator | `test_suite.py` | 11 | 11 | **100%** |
| `Python-Task3-RandomPasswordGenerator` | Password Generator | `test_suite.py` | 10 | 10 | **100%** |
| `Python-Task4-WeatherApp` | Weather App | `test_weather.py` | 10 | 10 | **100%** |
| `Python-Task5-ChatApplication` | Chat Application | `test_chat.py` | 12 | 12 | **100%** |
| **TOTAL** | **All 5 Tasks** | — | **54** | **54** | **100%** |

---

## 🔒 Security Best Practices & Compliance

- **No Secrets or Credentials Uploaded:** All sensitive configuration values and private keys (such as OpenWeatherMap API keys) are strictly loaded via `.env` files and excluded from version control via `.gitignore`.
- **Templates Included:** Each task requiring configuration includes a `.env.example` file outlining required parameters with safe placeholder values.
- **Clean Repository:** No build artifacts, cache folders (`__pycache__`), virtual environments (`.venv`), or temporary IDE configs (`.vscode`, `.idea`) are tracked.
- **Database Privacy:** Embedded SQLite databases only contain mock testing data and public seed records.

---

## 🛠️ Getting Started & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/chandanabommeraboina/OIBSIP.git
cd OIBSIP
```

### 2. Run Any Task
Navigate into the desired project folder and follow the instructions in its respective `README.md`:

```bash
# Example: Running Task 3 Password Generator
cd Python-Task3-RandomPasswordGenerator
python main.py

# Example: Running Task 2 BMI Calculator GUI
cd ../Python-Task2-BMICalculator
pip install -r requirements.txt
python main.py

# Example: Running Task 4 Weather App
cd ../Python-Task4-WeatherApp
pip install -r requirements.txt
cp .env.example .env   # Add your OpenWeatherMap API key
python main.py

# Example: Running Task 5 Chat Application
cd ../Python-Task5-ChatApplication
python server.py       # In terminal 1
python client.py       # In terminal 2
```

---

## 📜 Acknowledgments

Developed by **Chandana** as part of the **Oasis Infobyte Python Programming Internship (OIBSIP)**. Special thanks to the mentors and coordinators at Oasis Infobyte for providing a structured learning experience and practical hands-on challenges.
