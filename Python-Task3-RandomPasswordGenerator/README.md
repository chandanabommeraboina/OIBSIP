# Oasis Infobyte SIP - Python Programming Internship

## Task 3: Random Password Generator

| Field | Details |
| :--- | :--- |
| **Intern Name** | Chandana |
| **Internship Track** | Python Programming |
| **Task Title** | Task 3 - Random Password Generator |
| **Organization** | Oasis Infobyte (OIBSIP) |
| **Operating System** | Windows 11 |
| **Language** | Python 3 (Standard Library Only) |
| **Repository Name** | `OIBSIP` |
| **Task Folder** | `Python-Task3-PasswordGenerator` |

---

## 1. Project Overview & Objective

The objective of this project is to build a robust, cryptographically secure **Random Password Generator** application developed in Python. The generator allows users to produce custom, high-entropy passwords tailored to specific length, complexity, and character-type requirements.

The application strictly implements every mandatory feature outlined in the **Oasis Infobyte Python Programming Task 3 checklist**, complemented by advanced security and usability features such as cryptographic shuffling, password strength evaluation, ambiguous character exclusion, session-only history tracking, and dual-interface accessibility (CLI and native Tkinter GUI).

---

## 2. Features Implemented

### Required Core Features

- [x] **Configurable Password Length**: Users can define any custom password length.
- [x] **Minimum Length Enforcement**: Enforces a strict minimum password length of **8 characters** to prevent weak, easily crackable passwords.
- [x] **Four Character Type Options**:
  - **Uppercase Letters**: `A–Z`
  - **Lowercase Letters**: `a–z`
  - **Numbers**: `0–9`
  - **Symbols**: `!@#$%^&*()-_=+`
- [x] **Character Diversity Requirement**: Requires the selection of **at least 2 character types** before generation can proceed.
- [x] **Guaranteed Character Inclusion**: Mathematically and programmatically guarantees that every generated password contains at least one character from *each* selected character category.
- [x] **Cryptographic Security**: Employs Python's built-in `secrets` module (`secrets.choice` and `secrets.SystemRandom().shuffle`) instead of pseudorandom `random` to safeguard against predictability and brute-force guessing.
- [x] **Robust Input Validation**: Gracefully handles non-numeric lengths, decimal/negative values, lengths below 8, lengths exceeding safe limits, and insufficient character set selections without crashing.
- [x] **Continuous Session Loop**: Allows users to generate multiple passwords sequentially without having to restart the application.
- [x] **Clear Status & Error Feedback**: Provides informative, user-friendly messages for invalid entries and successful password generation.

### Advanced Features Implemented

- [x] **Password Strength Evaluation**: Classifies generated passwords into `Weak`, `Medium`, or `Strong` based on total length and character diversity.
- [x] **Ambiguous Character Exclusion**: Provides an option to filter out visually confusing characters (`0`, `O`, `1`, `l`, `I`) to prevent transcription errors.
- [x] **In-Memory Session History**: Retains the last five generated passwords during the current active session only.
- [x] **Zero Disk Persistence**: In accordance with privacy and security standards, passwords are never stored in a file, database, or external cache.
- [x] **Dual Interface (CLI & GUI)**: Includes both an interactive Command-Line Interface (CLI) and a native Graphical User Interface (GUI) powered by Python's standard `tkinter` library.
- [x] **Clipboard Integration**: Enables one-click password copying in GUI mode using native window clipboard methods.

### Optional Features Intentionally Not Implemented

- **Persistent Disk / Database Storage**: Storing plain-text passwords permanently on disk is a recognized security vulnerability; hence, persistence was omitted by design.
- **Third-Party Paid API Integration**: Excluded to ensure the project remains lightweight, privacy-preserving, and free of external API key dependencies.

---

## 3. Technologies Used

- **Programming Language**: Python 3.14 (Compatible with Python 3.8+)
- **Cryptographic Engine**: Python standard library `secrets` (OS-level CSPRNG)
- **Character Definitions**: Python standard library `string`
- **Session Management**: Python standard library `collections.deque`
- **Graphical Interface**: Python standard library `tkinter` and `tkinter.ttk`
- **Operating Environment**: Microsoft Windows 11 (64-bit)
- **External Dependencies**: None (100% standard library)

---

## 4. Project Directory Structure

```text
OIBSIP/
└── Python-Task3-PasswordGenerator/
    ├── main.py              # Main application source code (CLI & GUI)
    ├── test_suite.py        # Automated test suite covering all 10 test cases
    ├── README.md            # Comprehensive project documentation
    └── screenshots/
        └── demo-output.png  # Authentic screenshot of application execution
```

---

## 5. Security Architecture & Input Validation

### Cryptographic Security Model

Standard Python `random` uses the Mersenne Twister algorithm, which is completely deterministic and insecure for security credentials. This project strictly relies on `secrets`:

1. **Random Character Selection**: Characters are chosen via `secrets.choice()`, which accesses hardware/OS entropy (`CryptGenRandom` on Windows).
2. **Deterministic Placement Elimination**: After selecting at least one guaranteed character from each chosen type, the remaining positions are filled from the combined pool. The entire character array is then shuffled using `secrets.SystemRandom().shuffle()`. This ensures guaranteed characters do not stay at fixed index positions.
3. **Transient Memory Policy**: History records live inside a fixed-size `collections.deque(maxlen=5)` in RAM. When the program terminates, all generated passwords are automatically wiped.

### Input Validation Rules

| User Input | Validation Rule | Application Behavior |
| :--- | :--- | :--- |
| **Password Length** | Must be an integer $\ge 8$ | Rejects non-numbers, negatives, decimals, and values $< 8$ with a clear explanatory error. |
| **Maximum Length** | Capped at $512$ | Prevents denial-of-service / memory exhaustion. |
| **Character Types** | Minimum of $2$ types | Prevents generation if fewer than $2$ types are checked. Prompts user to select more. |
| **Empty Pool Check** | Pool size $> 0$ | Ensures ambiguous exclusion does not leave any selected pool empty. |

### Strength Evaluation Rubric

- **Weak**: Length $< 10$ characters OR only $2$ character types selected.
- **Medium**: Length $10$–$13$ characters with $\ge 3$ types, OR length $\ge 14$ with $2$ types.
- **Strong**: Length $\ge 14$ characters with $\ge 3$ types, OR length $\ge 12$ characters with all $4$ types.

---

## 6. Execution Instructions (Windows 11)

### Prerequisites

Ensure Python 3 is installed on your Windows 11 system. You can verify by opening PowerShell or Command Prompt and running:

```powershell
py --version
# or
python --version
```

### Steps to Run

1. Open **Windows PowerShell** or **Command Prompt**.
2. Navigate to the task directory:
   ```powershell
   cd "C:\Users\Chandana\OneDrive\Desktop\OIBSIP\Python-Task3-PasswordGenerator"
   ```

3. **To run the Interactive Command-Line Interface (CLI):**
   ```powershell
   py main.py
   # or
   python main.py
   ```

4. **To launch the Graphical User Interface (GUI) directly:**
   ```powershell
   py main.py --gui
   # or
   python main.py --gui
   ```

5. **To view help and CLI options:**
   ```powershell
   py main.py --help
   ```

6. **To execute the automated test suite:**
   ```powershell
   py test_suite.py
   ```

---

## 7. Sample CLI Output & Demo Screenshot

### Terminal Output Sample

```text
================================================================================
           OASIS INFOBYTE SIP - PYTHON PROGRAMMING INTERNSHIP
================================================================================
Full Name      : Chandana
Assigned Track : Python Programming
Task Title     : Task 3 - Random Password Generator
================================================================================

MAIN MENU:
  [1] Generate a Secure Password
  [2] View Session History (Last 5 Passwords)
  [3] Launch Graphical User Interface (GUI)
  [4] Exit Application

Enter your choice (1-4) [1]: 1

--- NEW PASSWORD GENERATION ---
Enter desired password length (minimum 8): 14

Select character types to include (Select at least 2):
  1. Include Uppercase letters (A-Z)? [Y/n]: Y
  2. Include Lowercase letters (a-z)? [Y/n]: Y
  3. Include Numbers (0-9)? [Y/n]: Y
  4. Include Symbols (!@#$%^&*()-_=+)? [Y/n]: Y

Optional feature:
  Exclude ambiguous characters (0, O, 1, l, I)? [y/N]: N

================================================================================
                 PASSWORD GENERATED SUCCESSFULLY
================================================================================
 Generated Password : k7@M9=xP2$wV8#
 Password Length    : 14 characters
 Strength Rating    : [STRONG]
 Character Types    : Uppercase (A-Z), Lowercase (a-z), Numbers (0-9), Symbols (!@#$%^&*()-_=+)
 Ambiguous Excluded : No
================================================================================
```

### Application Screenshot

![Application Output](screenshots/demo-output.png)

---

## 8. Verification & Test Suite Results

All 10 required test cases from the Oasis Infobyte specification were executed against the code using `test_suite.py`:

| # | Test Scenario | Input / Condition | Expected Result | Actual Result | Status |
| :-: | :--- | :--- | :--- | :--- | :-: |
| **1** | Valid password length | `length=12` | Generates 12-char password | Length 12 verified | **PASS** |
| **2** | Password length below 8 | `length=7` | Raises `ValueError` | Rejected with error | **PASS** |
| **3** | Non-numeric length | `length="twelve"` | Raises `ValueError` | Rejected with error | **PASS** |
| **4** | No character types selected | 0 types enabled | Raises `ValueError` | Rejected with error | **PASS** |
| **5** | Only one character type selected | Uppercase only | Raises `ValueError` | Rejected with error | **PASS** |
| **6** | Two character types selected | Uppercase + Numbers | Passwords contain both, none other | 100% compliant | **PASS** |
| **7** | All four character types selected | All 4 enabled | Passwords contain all 4 sets | 100% compliant | **PASS** |
| **8** | Guarantee inclusion on boundary | `length=8`, 3 types | Each type present in 8 chars | Verified across 25 runs | **PASS** |
| **9** | Multi-generation session loop | 7 sequential passwords | In-memory history capped at 5 | FIFO rolling verified | **PASS** |
| **10** | Ambiguous exclusion | Exclude `0, O, 1, l, I` | Zero ambiguous chars in 50 runs | Verified 0 present | **PASS** |

**Summary: 10/10 Tests Passed (100% Success Rate).**

---

## 9. Limitations & Design Considerations

1. **Transient History**: In-memory session history resets when the application exits. This is intentional to adhere to security best practices.
2. **Terminal Encoding**: Standard ASCII symbols and hyphens are utilized throughout the CLI to prevent character-page rendering issues on localized Windows consoles.

---

## 10. Submission Checklist Compliance

- [x] Workspace repository named `OIBSIP`.
- [x] Task directory named `Python-Task3-PasswordGenerator`.
- [x] Clean source code in `main.py` with beginner-friendly modular structure and comments.
- [x] Automated test runner in `test_suite.py`.
- [x] Professional `README.md` with full documentation and screenshot reference.
- [x] Verified screenshot in `screenshots/demo-output.png`.
- [x] Student header banner displaying:
  - **Full Name**: Chandana
  - **Assigned Track**: Python Programming
  - **Task Title**: Task 3 - Random Password Generator
