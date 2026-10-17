"""
================================================================================
OASIS INFOBYTE SIP - PYTHON PROGRAMMING INTERNSHIP
Task 3: Random Password Generator
Student Name   : Chandana
Assigned Track : Python Programming
Repository     : OIBSIP
Folder         : Python-Task3-PasswordGenerator
================================================================================

Description:
A secure, feature-rich Random Password Generator developed using Python 3 and
standard library modules (secrets, string, tkinter). Features include length
enforcement (min 8), multiple character type selection (min 2), guaranteed inclusion
of selected types, cryptographic security via `secrets`, strength evaluation,
ambiguous character exclusion, in-memory session history (last 5 passwords),
and both an interactive Command-Line Interface (CLI) and Graphical User Interface (GUI).
"""

import sys
import string
import secrets
from collections import deque
from typing import List, Dict, Tuple, Optional

# ==============================================================================
# PROJECT METADATA & CONSTANTS
# ==============================================================================
STUDENT_NAME = "Chandana"
ASSIGNED_TRACK = "Python Programming"
TASK_TITLE = "Task 3 - Random Password Generator"
ORGANIZATION = "Oasis Infobyte"

# Character set definitions
UPPERCASE_CHARS = string.ascii_uppercase  # A-Z
LOWERCASE_CHARS = string.ascii_lowercase  # a-z
DIGIT_CHARS = string.digits              # 0-9
SYMBOL_CHARS = "!@#$%^&*()-_=+"          # Required symbols from checklist

# Ambiguous characters that can look visually similar (0, O, 1, l, I)
AMBIGUOUS_CHARS = set("0O1lI")

# Validation limits
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 512
MIN_SELECTED_TYPES = 2
MAX_HISTORY_ITEMS = 5


# ==============================================================================
# IN-MEMORY SESSION HISTORY
# ==============================================================================
class SessionHistory:
    """Stores generated passwords in memory during the current session only.
    
    Passwords are never saved to a local file, database, or external storage.
    """

    def __init__(self, max_size: int = MAX_HISTORY_ITEMS) -> None:
        self._history: deque = deque(maxlen=max_size)

    def add(self, password: str, strength: str, length: int) -> None:
        """Add a generated password record to the session history."""
        self._history.append({
            "password": password,
            "strength": strength,
            "length": length
        })

    def get_all(self) -> List[Dict[str, any]]:
        """Return a list of stored password records (most recent last)."""
        return list(self._history)

    def is_empty(self) -> bool:
        """Check if history has any items."""
        return len(self._history) == 0

    def clear(self) -> None:
        """Clear all session history."""
        self._history.clear()


# Global in-memory history instance for the session
session_history = SessionHistory()


# ==============================================================================
# CORE LOGIC: VALIDATION & GENERATION
# ==============================================================================
def filter_ambiguous(chars: str, exclude_ambiguous: bool) -> str:
    """Filter out ambiguous characters (0, O, 1, l, I) if requested."""
    if not exclude_ambiguous:
        return chars
    return "".join(ch for ch in chars if ch not in AMBIGUOUS_CHARS)


def get_character_pools(
    include_upper: bool,
    include_lower: bool,
    include_digits: bool,
    include_symbols: bool,
    exclude_ambiguous: bool = False
) -> Dict[str, str]:
    """Build and return individual character pools for each selected type.
    
    Returns a dictionary mapping type names to their respective character strings.
    """
    pools: Dict[str, str] = {}

    if include_upper:
        chars = filter_ambiguous(UPPERCASE_CHARS, exclude_ambiguous)
        if chars:
            pools["Uppercase"] = chars

    if include_lower:
        chars = filter_ambiguous(LOWERCASE_CHARS, exclude_ambiguous)
        if chars:
            pools["Lowercase"] = chars

    if include_digits:
        chars = filter_ambiguous(DIGIT_CHARS, exclude_ambiguous)
        if chars:
            pools["Numbers"] = chars

    if include_symbols:
        chars = filter_ambiguous(SYMBOL_CHARS, exclude_ambiguous)
        if chars:
            pools["Symbols"] = chars

    return pools


def validate_generation_params(
    length: int,
    selected_pools: Dict[str, str]
) -> Tuple[bool, Optional[str]]:
    """Validate user inputs against the task requirements.
    
    Returns (is_valid, error_message).
    """
    if not isinstance(length, int):
        return False, "Password length must be a valid whole number (integer)."

    if length < MIN_PASSWORD_LENGTH:
        return (
            False,
            f"Password length ({length}) is too short. "
            f"The minimum allowed length is {MIN_PASSWORD_LENGTH} characters."
        )

    if length > MAX_PASSWORD_LENGTH:
        return (
            False,
            f"Password length ({length}) exceeds maximum limit of {MAX_PASSWORD_LENGTH} characters."
        )

    types_count = len(selected_pools)
    if types_count < MIN_SELECTED_TYPES:
        return (
            False,
            f"You selected {types_count} character type(s). "
            f"A minimum of {MIN_SELECTED_TYPES} character types is required."
        )

    # Ensure no selected pool is empty
    for name, pool in selected_pools.items():
        if not pool:
            return False, f"The selected character pool for '{name}' is empty."

    return True, None


def evaluate_strength(length: int, types_count: int) -> str:
    """Evaluate password strength based on length and character diversity.
    
    Evaluation Criteria:
    - Weak   : Length < 10 OR only 2 character types selected.
    - Strong : (Length >= 14 and >= 3 types) OR (Length >= 12 and all 4 types).
    - Medium : All other valid configurations.
    """
    if length < 10 or types_count <= 2:
        return "Weak"
    elif (length >= 14 and types_count >= 3) or (length >= 12 and types_count == 4):
        return "Strong"
    else:
        return "Medium"


def generate_password(
    length: int,
    include_upper: bool = True,
    include_lower: bool = True,
    include_digits: bool = True,
    include_symbols: bool = True,
    exclude_ambiguous: bool = False
) -> Tuple[str, str]:
    """Generate a cryptographically secure random password.
    
    Algorithm:
    1. Gather character pools for each selected type.
    2. Validate length (>= 8) and character diversity (>= 2 types).
    3. Guarantee at least one character from every selected type using secrets.choice.
    4. Fill remaining length from the unified pool of all selected characters.
    5. Shuffle using secrets.SystemRandom().shuffle to eliminate predictable positions.
    
    Returns (password, strength_label).
    Raises ValueError if validation fails.
    """
    pools = get_character_pools(
        include_upper=include_upper,
        include_lower=include_lower,
        include_digits=include_digits,
        include_symbols=include_symbols,
        exclude_ambiguous=exclude_ambiguous
    )

    is_valid, err_msg = validate_generation_params(length, pools)
    if not is_valid:
        raise ValueError(err_msg)

    password_chars: List[str] = []

    # Step 1: Guarantee at least one character from each selected type
    for pool_chars in pools.values():
        password_chars.append(secrets.choice(pool_chars))

    # Step 2: Combine all selected character pools for remaining slots
    combined_pool = "".join(pools.values())
    remaining_slots = length - len(password_chars)

    # Step 3: Securely select remaining characters
    for _ in range(remaining_slots):
        password_chars.append(secrets.choice(combined_pool))

    # Step 4: Cryptographically secure shuffle so guaranteed characters aren't always first
    secure_random = secrets.SystemRandom()
    secure_random.shuffle(password_chars)

    final_password = "".join(password_chars)
    strength = evaluate_strength(length, len(pools))

    return final_password, strength


# ==============================================================================
# COMMAND LINE INTERFACE (CLI)
# ==============================================================================
def print_banner() -> None:
    """Print the formal Oasis Infobyte internship header banner."""
    print("=" * 80)
    print(f"           {ORGANIZATION.upper()} SIP - PYTHON PROGRAMMING INTERNSHIP")
    print("=" * 80)
    print(f"Full Name      : {STUDENT_NAME}")
    print(f"Assigned Track : {ASSIGNED_TRACK}")
    print(f"Task Title     : {TASK_TITLE}")
    print("=" * 80)


def prompt_int(prompt_text: str, min_val: int = MIN_PASSWORD_LENGTH) -> int:
    """Prompt the user for a valid integer meeting the minimum requirement."""
    while True:
        user_input = input(prompt_text).strip()
        if not user_input:
            print("[!] Input cannot be empty. Please enter a valid number.")
            continue
        try:
            val = int(user_input)
            if val < min_val:
                print(f"[!] Length too short! Must be at least {min_val} characters. Please try again.")
                continue
            if val > MAX_PASSWORD_LENGTH:
                print(f"[!] Length too large! Maximum limit is {MAX_PASSWORD_LENGTH}. Please try again.")
                continue
            return val
        except ValueError:
            print(f"[!] Invalid input '{user_input}'. Please enter a whole number (e.g., 12).")


def prompt_bool(prompt_text: str, default: bool = True) -> bool:
    """Prompt the user for a Yes/No answer with a default value."""
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        resp = input(prompt_text + suffix).strip().lower()
        if resp == "":
            return default
        if resp in ("y", "yes"):
            return True
        if resp in ("n", "no"):
            return False
        print("[!] Please enter 'y' for Yes or 'n' for No.")


def run_cli_password_generation() -> None:
    """Interactive password generation workflow for CLI."""
    print("\n--- NEW PASSWORD GENERATION ---")

    # 1. Ask for desired password length
    length = prompt_int(f"Enter desired password length (minimum {MIN_PASSWORD_LENGTH}): ")

    # 2. Select character types (enforcing at least 2)
    while True:
        print("\nSelect character types to include (Select at least 2):")
        inc_upper = prompt_bool("  1. Include Uppercase letters (A-Z)?", default=True)
        inc_lower = prompt_bool("  2. Include Lowercase letters (a-z)?", default=True)
        inc_digits = prompt_bool("  3. Include Numbers (0-9)?", default=True)
        inc_symbols = prompt_bool("  4. Include Symbols (!@#$%^&*()-_=+)?", default=True)

        selected_count = sum([inc_upper, inc_lower, inc_digits, inc_symbols])
        if selected_count >= MIN_SELECTED_TYPES:
            break
        print(f"\n[!] ERROR: You selected only {selected_count} character type(s).")
        print(f"    Task requirement: Select at least {MIN_SELECTED_TYPES} character types. Please re-select.")

    # 3. Option to exclude ambiguous characters
    print("\nOptional feature:")
    exc_ambiguous = prompt_bool("  Exclude ambiguous characters (0, O, 1, l, I)?", default=False)

    # 4. Generate password
    try:
        password, strength = generate_password(
            length=length,
            include_upper=inc_upper,
            include_lower=inc_lower,
            include_digits=inc_digits,
            include_symbols=inc_symbols,
            exclude_ambiguous=exc_ambiguous
        )

        # Record in session history
        session_history.add(password, strength, length)

        # 5. Display result clearly
        types_used = []
        if inc_upper: types_used.append("Uppercase (A-Z)")
        if inc_lower: types_used.append("Lowercase (a-z)")
        if inc_digits: types_used.append("Numbers (0-9)")
        if inc_symbols: types_used.append("Symbols (!@#$%^&*()-_=+)")

        print("\n" + "=" * 80)
        print("                 PASSWORD GENERATED SUCCESSFULLY")
        print("=" * 80)
        print(f" Generated Password : {password}")
        print(f" Password Length    : {len(password)} characters")
        print(f" Strength Rating    : [{strength.upper()}]")
        print(f" Character Types    : {', '.join(types_used)}")
        print(f" Ambiguous Excluded : {'Yes (0, O, 1, l, I excluded)' if exc_ambiguous else 'No'}")
        print("=" * 80)

    except ValueError as e:
        print(f"\n[!] Generation failed: {e}")


def display_session_history() -> None:
    """Display the last five generated passwords during the current session."""
    print("\n--- SESSION HISTORY (LAST 5 PASSWORDS) ---")
    history = session_history.get_all()
    if not history:
        print("No passwords generated in this session yet.")
        return

    print(f"Total in memory: {len(history)} (Session-only, not saved to disk)")
    print("-" * 80)
    for idx, item in enumerate(history, 1):
        print(f" {idx}. [{item['strength']}] (len={item['length']}) : {item['password']}")
    print("-" * 80)


def cli_main() -> None:
    """Main CLI menu loop allowing repeated generation without application restart."""
    print_banner()

    while True:
        print("\nMAIN MENU:")
        print("  [1] Generate a Secure Password")
        print("  [2] View Session History (Last 5 Passwords)")
        print("  [3] Launch Graphical User Interface (GUI)")
        print("  [4] Exit Application")

        choice = input("\nEnter your choice (1-4) [1]: ").strip()
        if choice in ("", "1"):
            while True:
                run_cli_password_generation()
                repeat = prompt_bool("\nWould you like to generate another password?", default=True)
                if not repeat:
                    break
        elif choice == "2":
            display_session_history()
        elif choice == "3":
            print("\nLaunching Graphical Interface (Tkinter)...")
            launch_gui()
            print("\nReturned from Graphical Interface to CLI.")
        elif choice == "4":
            print(f"\nThank you for using the {TASK_TITLE} by {STUDENT_NAME}!")
            print("Session closed. In-memory history discarded securely.\n")
            break
        else:
            print("[!] Invalid menu selection. Please choose an option from 1 to 4.")


# ==============================================================================
# GRAPHICAL USER INTERFACE (GUI) VIA TKINTER
# ==============================================================================
def launch_gui() -> None:
    """Launch the Tkinter Graphical User Interface for the password generator."""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except ImportError:
        print("[!] Tkinter is not installed or available on this Python installation.")
        return

    root = tk.Tk()
    root.title(f"{TASK_TITLE} - {STUDENT_NAME} ({ORGANIZATION})")
    root.geometry("640x720")
    root.minsize(580, 680)

    # Style configuration
    style = ttk.Style(root)
    # Use available theme if possible
    available_themes = style.theme_names()
    if "clam" in available_themes:
        style.theme_use("clam")

    # Top Header Banner
    header_frame = tk.Frame(root, bg="#1e293b", pady=12)
    header_frame.pack(fill="x")

    lbl_org = tk.Label(
        header_frame,
        text=f"{ORGANIZATION.upper()} SIP - {ASSIGNED_TRACK.upper()}",
        font=("Segoe UI", 10, "bold"),
        fg="#94a3b8",
        bg="#1e293b"
    )
    lbl_org.pack()

    lbl_title = tk.Label(
        header_frame,
        text=TASK_TITLE,
        font=("Segoe UI", 15, "bold"),
        fg="#ffffff",
        bg="#1e293b"
    )
    lbl_title.pack(pady=2)

    lbl_student = tk.Label(
        header_frame,
        text=f"Student Name: {STUDENT_NAME} | Track: {ASSIGNED_TRACK}",
        font=("Segoe UI", 9),
        fg="#38bdf8",
        bg="#1e293b"
    )
    lbl_student.pack()

    # Main Scrollable / Padded Container
    container = ttk.Frame(root, padding="16")
    container.pack(fill="both", expand=True)

    # Section 1: Password Length
    length_frame = ttk.LabelFrame(container, text=" 1. Password Length ", padding="10")
    length_frame.pack(fill="x", pady=6)

    lbl_len_info = ttk.Label(
        length_frame,
        text=f"Desired Length (Minimum {MIN_PASSWORD_LENGTH} characters required):"
    )
    lbl_len_info.pack(anchor="w")

    length_ctrl_frame = ttk.Frame(length_frame)
    length_ctrl_frame.pack(fill="x", pady=4)

    length_var = tk.IntVar(value=12)
    length_spin = ttk.Spinbox(
        length_ctrl_frame,
        from_=MIN_PASSWORD_LENGTH,
        to=MAX_PASSWORD_LENGTH,
        textvariable=length_var,
        width=8,
        font=("Segoe UI", 11)
    )
    length_spin.pack(side="left", padx=(0, 10))

    length_slider = ttk.Scale(
        length_ctrl_frame,
        from_=MIN_PASSWORD_LENGTH,
        to=64,
        orient="horizontal",
        variable=length_var
    )
    length_slider.pack(side="left", fill="x", expand=True)

    # Section 2: Character Types (Require at least 2)
    types_frame = ttk.LabelFrame(
        container,
        text=" 2. Character Criteria (Select at least 2) ",
        padding="10"
    )
    types_frame.pack(fill="x", pady=6)

    var_upper = tk.BooleanVar(value=True)
    var_lower = tk.BooleanVar(value=True)
    var_digits = tk.BooleanVar(value=True)
    var_symbols = tk.BooleanVar(value=True)

    chk_upper = ttk.Checkbutton(types_frame, text="Uppercase Letters (A – Z)", variable=var_upper)
    chk_upper.pack(anchor="w", pady=2)

    chk_lower = ttk.Checkbutton(types_frame, text="Lowercase Letters (a – z)", variable=var_lower)
    chk_lower.pack(anchor="w", pady=2)

    chk_digits = ttk.Checkbutton(types_frame, text="Numbers (0 – 9)", variable=var_digits)
    chk_digits.pack(anchor="w", pady=2)

    chk_symbols = ttk.Checkbutton(types_frame, text="Symbols (!@#$%^&*()-_=+)", variable=var_symbols)
    chk_symbols.pack(anchor="w", pady=2)

    # Section 3: Advanced Options
    adv_frame = ttk.LabelFrame(container, text=" 3. Advanced Options ", padding="10")
    adv_frame.pack(fill="x", pady=6)

    var_ambiguous = tk.BooleanVar(value=False)
    chk_ambiguous = ttk.Checkbutton(
        adv_frame,
        text="Exclude Ambiguous Characters (0, O, 1, l, I)",
        variable=var_ambiguous
    )
    chk_ambiguous.pack(anchor="w")

    # Section 4: Result & Strength
    result_frame = ttk.LabelFrame(container, text=" 4. Generated Password & Security ", padding="10")
    result_frame.pack(fill="x", pady=6)

    password_var = tk.StringVar(value="")
    entry_pwd = ttk.Entry(
        result_frame,
        textvariable=password_var,
        font=("Consolas", 13, "bold"),
        justify="center"
    )
    entry_pwd.pack(fill="x", pady=4)

    status_row = ttk.Frame(result_frame)
    status_row.pack(fill="x", pady=2)

    lbl_strength_title = ttk.Label(status_row, text="Strength: ", font=("Segoe UI", 9, "bold"))
    lbl_strength_title.pack(side="left")

    lbl_strength_val = tk.Label(
        status_row,
        text="None",
        font=("Segoe UI", 9, "bold"),
        fg="#64748b",
        bg="#f1f5f9",
        padx=8,
        pady=2
    )
    lbl_strength_val.pack(side="left", padx=4)

    lbl_msg = ttk.Label(result_frame, text="", foreground="red")
    lbl_msg.pack(anchor="w", pady=2)

    # Section 5: Session History Display
    hist_frame = ttk.LabelFrame(container, text=" Session History (Last 5 - Current Session Only) ", padding="6")
    hist_frame.pack(fill="both", expand=True, pady=6)

    hist_listbox = tk.Listbox(
        hist_frame,
        height=4,
        font=("Consolas", 9),
        bg="#f8fafc",
        fg="#0f172a",
        selectbackground="#cbd5e1"
    )
    hist_listbox.pack(fill="both", expand=True)

    def refresh_history_ui() -> None:
        """Refresh the GUI history listbox from in-memory session records."""
        hist_listbox.delete(0, tk.END)
        for idx, rec in enumerate(session_history.get_all(), 1):
            hist_listbox.insert(
                tk.END,
                f" {idx}. [{rec['strength']}] (len={rec['length']}) {rec['password']}"
            )

    # Initial history population
    refresh_history_ui()

    # Handlers
    def on_generate() -> None:
        """Handle Generate Password button click."""
        lbl_msg.config(text="")
        try:
            try:
                length = int(length_var.get())
            except (ValueError, tk.TclError):
                lbl_msg.config(text="Error: Password length must be a valid integer.", foreground="red")
                return

            pwd, strength = generate_password(
                length=length,
                include_upper=var_upper.get(),
                include_lower=var_lower.get(),
                include_digits=var_digits.get(),
                include_symbols=var_symbols.get(),
                exclude_ambiguous=var_ambiguous.get()
            )

            password_var.set(pwd)
            session_history.add(pwd, strength, length)
            refresh_history_ui()

            # Update strength badge color
            strength_colors = {
                "Strong": ("#16a34a", "#dcfce7"),  # Green text / light green bg
                "Medium": ("#d97706", "#fef3c7"),  # Amber text / light yellow bg
                "Weak":   ("#dc2626", "#fee2e2"),  # Red text / light red bg
            }
            fg_col, bg_col = strength_colors.get(strength, ("#0f172a", "#f1f5f9"))
            lbl_strength_val.config(text=strength.upper(), fg=fg_col, bg=bg_col)
            lbl_msg.config(text="Password generated securely!", foreground="#16a34a")

        except ValueError as err:
            lbl_msg.config(text=f"Error: {err}", foreground="red")

    def on_copy() -> None:
        """Copy the generated password to system clipboard."""
        current_pwd = password_var.get()
        if not current_pwd:
            lbl_msg.config(text="Nothing to copy. Generate a password first.", foreground="red")
            return
        root.clipboard_clear()
        root.clipboard_append(current_pwd)
        lbl_msg.config(text="Copied to clipboard successfully!", foreground="#0284c7")

    # Action Buttons Bar
    btn_bar = ttk.Frame(container)
    btn_bar.pack(fill="x", pady=6)

    btn_generate = tk.Button(
        btn_bar,
        text="Generate Password",
        command=on_generate,
        font=("Segoe UI", 10, "bold"),
        bg="#2563eb",
        fg="#ffffff",
        activebackground="#1d4ed8",
        activeforeground="#ffffff",
        padx=14,
        pady=6,
        relief="flat",
        cursor="hand2"
    )
    btn_generate.pack(side="left", padx=4)

    btn_copy = tk.Button(
        btn_bar,
        text="Copy to Clipboard",
        command=on_copy,
        font=("Segoe UI", 10),
        bg="#e2e8f0",
        fg="#0f172a",
        activebackground="#cbd5e1",
        padx=12,
        pady=6,
        relief="flat",
        cursor="hand2"
    )
    btn_copy.pack(side="left", padx=4)

    btn_close = tk.Button(
        btn_bar,
        text="Close Window",
        command=root.destroy,
        font=("Segoe UI", 10),
        bg="#f1f5f9",
        fg="#475569",
        padx=10,
        pady=6,
        relief="flat",
        cursor="hand2"
    )
    btn_close.pack(side="right", padx=4)

    # Generate an initial password when window opens
    on_generate()

    root.mainloop()


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================
def main() -> None:
    """Entry point dispatching CLI or GUI based on command-line arguments."""
    if "--gui" in sys.argv:
        launch_gui()
    elif "--help" in sys.argv or "-h" in sys.argv:
        print_banner()
        print("\nUsage:")
        print("  py main.py          : Launch interactive Command-Line Interface (CLI)")
        print("  py main.py --cli    : Launch Command-Line Interface explicitly")
        print("  py main.py --gui    : Launch Graphical User Interface (Tkinter)")
        print("  py main.py --help   : Display this help message")
    else:
        # Default behavior: run CLI with seamless option to launch GUI
        cli_main()


if __name__ == "__main__":
    main()
