"""
================================================================================
OASIS INFOBYTE SIP - PYTHON PROGRAMMING INTERNSHIP
Task 2: BMI Calculator (Desktop GUI & Analytics)
Student Name   : Chandana
Assigned Track : Python Programming
Repository     : OIBSIP
Folder         : Python-Task2-BMICalculator
================================================================================

Description:
A feature-complete, modern desktop Body Mass Index (BMI) Calculator application
built with Python 3, Tkinter GUI, SQLite3 database storage, and Matplotlib trend
analytics.

Features:
- Mandatory Beginner Features:
  * Accepts user's weight in kilograms (kg) and height in meters (m).
  * Calculates BMI using formula: BMI = weight / (height * height).
  * Classifies BMI into Underweight (<18.5), Normal (18.5-24.9),
    Overweight (25-29.9), and Obese (>=30).
  * Displays BMI rounded to two decimal places.
  * Rigorous validation: rejects non-numeric, negative, and zero inputs with clear errors.
  * Crash-proof architecture with structured exception handling.

- Advanced Features:
  * Native desktop GUI with modern visual styling via Tkinter/ttk.
  * Color-coded category feedback (Blue, Green, Amber, Red).
  * Multi-user profile management: save records with user's name and exact timestamp.
  * Local persistent historical storage via SQLite database (`bmi_history.db`).
  * Interactive history viewer with search/filter by username.
  * BMI trend visualization over time using Matplotlib with category reference bands.
  * Parameterized SQL queries preventing SQL injection vulnerabilities.
  * Dual-interface support: Launch GUI by default or run interactive CLI mode.
"""

import os
import sys
import sqlite3
import datetime
from typing import Tuple, List, Dict, Optional, Any

# Graphical interface modules
import tkinter as tk
from tkinter import ttk, messagebox

# Data visualization module
try:
    import matplotlib
    # Use TkAgg backend for embedding or rendering inside Tkinter
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.dates import DateFormatter
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


# ==============================================================================
# PROJECT METADATA & CONSTANTS
# ==============================================================================
STUDENT_NAME = "Chandana"
ASSIGNED_TRACK = "Python Programming"
TASK_TITLE = "Task 2 - BMI Calculator"
ORGANIZATION = "Oasis Infobyte"

# Default local database file name
DEFAULT_DB_NAME = "bmi_history.db"

# Realistic physical validation bounds (for sanity checking beyond > 0)
MIN_WEIGHT_KG = 1.0
MAX_WEIGHT_KG = 500.0
MIN_HEIGHT_M = 0.30
MAX_HEIGHT_M = 2.80

# BMI Category Definitions according to Oasis Infobyte PDF checklist
# Boundary handling rule:
# Standard WHO clinical thresholds use continuous intervals:
#   Underweight: < 18.5
#   Normal: 18.5 to 24.9 (i.e. >= 18.5 and < 25.0)
#   Overweight: 25.0 to 29.9 (i.e. >= 25.0 and < 30.0)
#   Obese: >= 30.0
# The PDF displays ranges to 1 decimal place (18.5-24.9, 25-29.9). When rounded to
# two decimal places, values like 18.49 classify as Underweight, 18.50 as Normal,
# 24.90 as Normal, 25.00 as Overweight, 29.90 as Overweight, and 30.00 as Obese.
CATEGORY_UNDERWEIGHT = "Underweight"
CATEGORY_NORMAL = "Normal"
CATEGORY_OVERWEIGHT = "Overweight"
CATEGORY_OBESE = "Obese"

# Color-coding dictionary for visual category feedback
CATEGORY_COLORS: Dict[str, str] = {
    CATEGORY_UNDERWEIGHT: "#0284c7",  # Vibrant Blue / Sky Blue
    CATEGORY_NORMAL: "#16a34a",       # Rich Forest Green
    CATEGORY_OVERWEIGHT: "#d97706",   # Warm Amber / Orange
    CATEGORY_OBESE: "#dc2626",        # Crisp Crimson Red
}

# Health recommendation advice tailored to category
CATEGORY_RECOMMENDATIONS: Dict[str, str] = {
    CATEGORY_UNDERWEIGHT: (
        "Your BMI is below the healthy range. Consider consulting a healthcare "
        "professional or nutritionist for a balanced, nutrient-dense diet plan."
    ),
    CATEGORY_NORMAL: (
        "Congratulations! Your BMI is within the healthy, normal weight range. "
        "Maintain your current balanced diet and regular physical activity."
    ),
    CATEGORY_OVERWEIGHT: (
        "Your BMI indicates you are in the overweight range. Incorporating moderate "
        "daily aerobic exercise and mindful portion control can help optimize health."
    ),
    CATEGORY_OBESE: (
        "Your BMI falls within the obese range. We recommend speaking with a healthcare "
        "provider for a personalized wellness and lifestyle management strategy."
    ),
}


# ==============================================================================
# SECTION 1: CORE CALCULATION & VALIDATION LOGIC
# ==============================================================================

def validate_input(
    name_str: str,
    weight_str: str,
    height_str: str
) -> Tuple[bool, str, str, float, float]:
    """
    Validate user input fields for name, weight, and height.

    Parameters:
        name_str   : Raw string for user's name
        weight_str : Raw string for weight (kg)
        height_str : Raw string for height (m)

    Returns:
        Tuple of (is_valid, error_message, cleaned_name, weight_float, height_float)
    """
    cleaned_name = name_str.strip()
    if not cleaned_name:
        return False, "Name field cannot be empty. Please enter the person's name.", "", 0.0, 0.0

    # Validate weight presence
    cleaned_weight = weight_str.strip()
    if not cleaned_weight:
        return False, "Weight field cannot be empty. Please enter weight in kilograms (kg).", "", 0.0, 0.0

    # Validate height presence
    cleaned_height = height_str.strip()
    if not cleaned_height:
        return False, "Height field cannot be empty. Please enter height in meters (m).", "", 0.0, 0.0

    # Parse and validate weight value
    try:
        weight = float(cleaned_weight)
    except ValueError:
        return (
            False,
            f"Invalid weight '{cleaned_weight}'. Weight must be a valid positive number (e.g., 68.5).",
            "",
            0.0,
            0.0
        )

    if weight <= 0:
        return (
            False,
            f"Weight must be greater than zero. You entered: {weight} kg.",
            "",
            0.0,
            0.0
        )

    if weight < MIN_WEIGHT_KG or weight > MAX_WEIGHT_KG:
        return (
            False,
            f"Weight {weight} kg is outside realistic human limits ({MIN_WEIGHT_KG}-{MAX_WEIGHT_KG} kg).",
            "",
            0.0,
            0.0
        )

    # Parse and validate height value
    try:
        height = float(cleaned_height)
    except ValueError:
        return (
            False,
            f"Invalid height '{cleaned_height}'. Height must be a valid positive number in meters (e.g., 1.75).",
            "",
            0.0,
            0.0
        )

    if height <= 0:
        return (
            False,
            f"Height must be greater than zero. You entered: {height} m.",
            "",
            0.0,
            0.0
        )

    if height < MIN_HEIGHT_M or height > MAX_HEIGHT_M:
        return (
            False,
            f"Height {height} m is outside realistic human limits ({MIN_HEIGHT_M}-{MAX_HEIGHT_M} m). "
            f"Note: Enter height in meters (e.g., 1.75 m instead of 175 cm).",
            "",
            0.0,
            0.0
        )

    return True, "", cleaned_name, weight, height


def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """
    Calculate Body Mass Index using the standard formula:
        BMI = weight / (height * height)

    Parameters:
        weight_kg : Weight in kilograms (kg)
        height_m  : Height in meters (m)

    Returns:
        Calculated raw BMI as a float.
    """
    if height_m <= 0:
        raise ValueError("Height must be strictly positive to calculate BMI.")
    return weight_kg / (height_m * height_m)


def classify_bmi(bmi_value: float) -> Tuple[str, str, str]:
    """
    Classify a BMI value into its official category according to the Oasis Infobyte PDF:
      - Underweight: BMI below 18.5
      - Normal: BMI from 18.5 to 24.9
      - Overweight: BMI from 25 to 29.9
      - Obese: BMI 30 or above

    Parameters:
        bmi_value : Raw or rounded float BMI value

    Returns:
        Tuple of (category_name, color_hex_code, health_recommendation)
    """
    rounded_bmi = round(bmi_value, 2)

    if rounded_bmi < 18.5:
        category = CATEGORY_UNDERWEIGHT
    elif rounded_bmi < 25.0:
        category = CATEGORY_NORMAL
    elif rounded_bmi < 30.0:
        category = CATEGORY_OVERWEIGHT
    else:
        category = CATEGORY_OBESE

    color = CATEGORY_COLORS[category]
    recommendation = CATEGORY_RECOMMENDATIONS[category]
    return category, color, recommendation


def format_bmi(bmi_value: float) -> str:
    """Format BMI rounded to two decimal places."""
    return f"{bmi_value:.2f}"


# ==============================================================================
# SECTION 2: SQLITE DATABASE OPERATIONS (sqlite3)
# ==============================================================================

def get_default_db_path() -> str:
    """Get the absolute filepath for the SQLite history database."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, DEFAULT_DB_NAME)


def init_db(db_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    Initialize SQLite database and create `bmi_records` table if it doesn't exist.
    Uses safe schema definition and indexed fields.

    Parameters:
        db_path : Optional custom database path (defaults to get_default_db_path())

    Returns:
        Tuple of (success_boolean, status_message)
    """
    path = db_path or get_default_db_path()
    try:
        with sqlite3.connect(path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bmi_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    weight REAL NOT NULL,
                    height REAL NOT NULL,
                    bmi REAL NOT NULL,
                    category TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            # Create index on name for fast multi-user history queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bmi_name ON bmi_records (name)
            """)
            conn.commit()
        return True, "Database initialized successfully."
    except sqlite3.Error as e:
        return False, f"Database initialization failed: {e}"


def save_bmi_record(
    name: str,
    weight: float,
    height: float,
    bmi: float,
    category: str,
    timestamp: Optional[str] = None,
    db_path: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Save a new BMI record into the SQLite database using parameterized queries.

    Parameters:
        name      : User's name
        weight    : Weight in kg
        height    : Height in m
        bmi       : Calculated BMI (rounded to 2 decimal places)
        category  : Classified BMI category
        timestamp : Optional ISO formatted datetime string (defaults to current time)
        db_path   : Optional custom database path

    Returns:
        Tuple of (success_boolean, status_message)
    """
    path = db_path or get_default_db_path()
    record_time = timestamp or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with sqlite3.connect(path) as conn:
            cursor = conn.cursor()
            # Parameterized query protects against SQL injection
            cursor.execute("""
                INSERT INTO bmi_records (name, weight, height, bmi, category, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name.strip(), round(weight, 2), round(height, 2), round(bmi, 2), category, record_time))
            conn.commit()
        return True, f"Record for '{name.strip()}' saved successfully."
    except sqlite3.Error as e:
        return False, f"Failed to save record to database: {e}"


def fetch_all_records(db_path: Optional[str] = None) -> Tuple[bool, List[Dict[str, Any]], str]:
    """
    Fetch all historical records ordered chronologically by timestamp (newest first).

    Returns:
        Tuple of (success_boolean, list_of_records_dict, status_message)
    """
    path = db_path or get_default_db_path()
    try:
        with sqlite3.connect(path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, bmi, category, timestamp
                FROM bmi_records
                ORDER BY timestamp DESC, id DESC
            """)
            rows = cursor.fetchall()
            records = [dict(row) for row in rows]
        return True, records, f"Fetched {len(records)} records."
    except sqlite3.Error as e:
        return False, [], f"Database query failed: {e}"


def fetch_records_by_user(name: str, db_path: Optional[str] = None) -> Tuple[bool, List[Dict[str, Any]], str]:
    """
    Fetch all historical records for a specific named user, ordered chronologically
    from oldest to newest (ideal for chronological trend graphing).

    Returns:
        Tuple of (success_boolean, list_of_records_dict, status_message)
    """
    path = db_path or get_default_db_path()
    try:
        with sqlite3.connect(path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, bmi, category, timestamp
                FROM bmi_records
                WHERE LOWER(name) = LOWER(?)
                ORDER BY timestamp ASC, id ASC
            """, (name.strip(),))
            rows = cursor.fetchall()
            records = [dict(row) for row in rows]
        return True, records, f"Fetched {len(records)} records for user '{name}'."
    except sqlite3.Error as e:
        return False, [], f"Failed to fetch user records: {e}"


def fetch_distinct_users(db_path: Optional[str] = None) -> Tuple[bool, List[str], str]:
    """Fetch a sorted list of unique usernames recorded in the database."""
    path = db_path or get_default_db_path()
    try:
        with sqlite3.connect(path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT name
                FROM bmi_records
                ORDER BY name COLLATE NOCASE ASC
            """)
            rows = cursor.fetchall()
            users = [row[0] for row in rows]
        return True, users, "User list retrieved."
    except sqlite3.Error as e:
        return False, [], f"Failed to retrieve user list: {e}"


def delete_record_by_id(record_id: int, db_path: Optional[str] = None) -> Tuple[bool, str]:
    """Delete a specific BMI record by its primary key ID."""
    path = db_path or get_default_db_path()
    try:
        with sqlite3.connect(path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bmi_records WHERE id = ?", (record_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return False, f"Record with ID #{record_id} not found."
        return True, f"Record #{record_id} deleted successfully."
    except sqlite3.Error as e:
        return False, f"Failed to delete record: {e}"


# ==============================================================================
# SECTION 3: MATPLOTLIB BMI TREND GRAPH
# ==============================================================================

def open_bmi_trend_window(
    user_name: str,
    parent_window: Optional[tk.Tk] = None,
    db_path: Optional[str] = None
) -> Optional[tk.Toplevel]:
    """
    Open a dedicated top-level desktop window displaying the user's BMI trend
    over time using Matplotlib embedded in Tkinter.

    Parameters:
        user_name     : Name of user whose historical trend is plotted
        parent_window : Parent Tkinter root window
        db_path       : Optional custom SQLite database path
    """
    if not MATPLOTLIB_AVAILABLE:
        messagebox.showerror(
            "Matplotlib Missing",
            "The 'matplotlib' library is required to render the BMI trend graph.\n\n"
            "Please install it using:\n  py -m pip install matplotlib"
        )
        return None

    success, records, msg = fetch_records_by_user(user_name, db_path)
    if not success:
        messagebox.showerror("Database Error", msg)
        return None

    if not records:
        messagebox.showinfo(
            "No Records Found",
            f"No historical records found for '{user_name}'.\n\n"
            f"Please calculate and save at least one measurement for '{user_name}' first."
        )
        return None

    # Parse timestamps and BMI values
    dates = []
    bmis = []
    for rec in records:
        try:
            dt = datetime.datetime.strptime(rec["timestamp"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # Fallback for date-only format if present
            try:
                dt = datetime.datetime.strptime(rec["timestamp"], "%Y-%m-%d")
            except ValueError:
                dt = datetime.datetime.now()
        dates.append(dt)
        bmis.append(rec["bmi"])

    # Create Toplevel Window
    trend_win = tk.Toplevel(parent_window)
    trend_win.title(f"BMI Trend Analysis — {user_name}")
    trend_win.geometry("820x620")
    trend_win.minsize(700, 500)
    trend_win.configure(bg="#f8fafc")

    # Header Card inside TopLevel
    header_frame = tk.Frame(trend_win, bg="#0f172a", padx=16, pady=12)
    header_frame.pack(fill="x")

    title_lbl = tk.Label(
        header_frame,
        text=f"📊 BMI Historical Trend Analysis — {user_name}",
        font=("Segoe UI", 13, "bold"),
        fg="#ffffff",
        bg="#0f172a"
    )
    title_lbl.pack(anchor="w")

    subtitle_lbl = tk.Label(
        header_frame,
        text=f"Total Records: {len(records)} | Latest BMI: {bmis[-1]:.2f} ({records[-1]['category']})",
        font=("Segoe UI", 9),
        fg="#94a3b8",
        bg="#0f172a"
    )
    subtitle_lbl.pack(anchor="w")

    # Matplotlib Figure
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=100)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#fafafa")

    # Reference bands and horizontal threshold lines
    # Underweight (<18.5), Normal (18.5 - 24.9), Overweight (25 - 29.9), Obese (>=30)
    y_min = max(10.0, min(bmis) - 3.0)
    y_max = max(35.0, max(bmis) + 4.0)
    ax.set_ylim(y_min, y_max)

    # Shaded visual regions
    ax.axhspan(10.0, 18.5, color="#0284c7", alpha=0.08, label="Underweight Zone (<18.5)")
    ax.axhspan(18.5, 25.0, color="#16a34a", alpha=0.10, label="Normal Weight Zone (18.5-24.9)")
    ax.axhspan(25.0, 30.0, color="#d97706", alpha=0.08, label="Overweight Zone (25-29.9)")
    ax.axhspan(30.0, max(50.0, y_max + 5), color="#dc2626", alpha=0.08, label="Obese Zone (≥30)")

    # Threshold guideline lines
    ax.axhline(18.5, color="#0284c7", linestyle="--", linewidth=1.1, alpha=0.7)
    ax.axhline(25.0, color="#16a34a", linestyle="--", linewidth=1.1, alpha=0.7)
    ax.axhline(30.0, color="#dc2626", linestyle="--", linewidth=1.1, alpha=0.7)

    # Plot Trend Line & Data Points
    if len(dates) == 1:
        # Single record case: highlight single point clearly
        ax.plot(dates, bmis, marker='o', markersize=10, color='#2563eb', label=f"Measurement: {bmis[0]:.2f}")
        ax.annotate(
            f"BMI: {bmis[0]:.2f}\n({records[0]['category']})",
            (dates[0], bmis[0]),
            textcoords="offset points",
            xytext=(0, 15),
            ha='center',
            fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.4", fc="#ffffff", ec="#2563eb", lw=1.5)
        )
    else:
        # Multiple records
        ax.plot(
            dates,
            bmis,
            marker='o',
            markersize=7,
            color='#2563eb',
            linewidth=2.2,
            label="User BMI Progression"
        )
        # Annotate each point with its rounded value
        for dt, val, rec in zip(dates, bmis, records):
            cat_color = CATEGORY_COLORS.get(rec["category"], "#2563eb")
            ax.annotate(
                f"{val:.2f}",
                (dt, val),
                textcoords="offset points",
                xytext=(0, 10),
                ha='center',
                fontsize=8.5,
                fontweight='bold',
                color=cat_color,
                bbox=dict(boxstyle="round,pad=0.25", fc="#ffffff", ec=cat_color, lw=1)
            )

    # Date formatting on X-axis
    if len(dates) > 1 and (dates[-1] - dates[0]).days > 3:
        ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
    else:
        ax.xaxis.set_major_formatter(DateFormatter("%m-%d %H:%M"))
    fig.autofmt_xdate(rotation=30)

    ax.set_title(f"Progressive BMI Trend for {user_name}", fontsize=12, fontweight="bold", pad=12, color="#0f172a")
    ax.set_xlabel("Measurement Timestamp (Chronological)", fontsize=9.5, fontweight="bold", labelpad=8, color="#334155")
    ax.set_ylabel("Body Mass Index (BMI)", fontsize=9.5, fontweight="bold", labelpad=8, color="#334155")
    ax.grid(True, linestyle=":", alpha=0.5, color="#94a3b8")
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)

    plt.tight_layout()

    # Embed FigureCanvasTkAgg into Tkinter TopLevel
    canvas = FigureCanvasTkAgg(fig, master=trend_win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=8)

    # Embed Navigation Toolbar
    toolbar = NavigationToolbar2Tk(canvas, trend_win)
    toolbar.update()
    toolbar.pack(side="bottom", fill="x")

    def on_close():
        plt.close(fig)
        trend_win.destroy()

    trend_win.protocol("WM_DELETE_WINDOW", on_close)
    return trend_win


# ==============================================================================
# SECTION 4: MODERN TKINTER GRAPHICAL USER INTERFACE (GUI)
# ==============================================================================

class BMICalculatorGUI:
    """
    Tkinter Graphical User Interface for Oasis Infobyte Task 2 BMI Calculator.
    Designed with modern typography, responsive cards, color-coded feedback,
    and integrated SQLite history and trend graphing.
    """

    def __init__(self, root: tk.Tk, db_path: Optional[str] = None):
        self.root = root
        self.db_path = db_path or get_default_db_path()

        # Initialize SQLite database
        init_ok, init_msg = init_db(self.db_path)
        if not init_ok:
            messagebox.showwarning("Database Warning", f"{init_msg}\nSome database features may be unavailable.")

        # Window configuration
        self.root.title("BMI Calculator — Oasis Infobyte")
        self.root.geometry("1020x680")
        self.root.minsize(920, 620)
        self.root.configure(bg="#f1f5f9")

        # Runtime state
        self.last_calculated_result: Optional[Dict[str, Any]] = None

        # Build styles and UI
        self._setup_styles()
        self._build_header_card()
        self._build_main_layout()
        self._load_history_table()
        self._refresh_user_dropdown()

    def _setup_styles(self) -> None:
        """Configure ttk modern styling tokens."""
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # Global base font
        default_font = ("Segoe UI", 10)
        self.root.option_add("*Font", default_font)

        # Custom ttk configurations
        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("TLabelframe", background="#ffffff", relief="flat")
        self.style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"), foreground="#1e293b", background="#ffffff")
        self.style.configure("TFrame", background="#f1f5f9")
        self.style.configure("White.TFrame", background="#ffffff")

        # Treeview styling for history
        self.style.configure(
            "Treeview",
            background="#ffffff",
            foreground="#0f172a",
            rowheight=26,
            fieldbackground="#ffffff",
            font=("Segoe UI", 9)
        )
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), foreground="#0f172a", background="#e2e8f0")
        self.style.map("Treeview", background=[("selected", "#cbd5e1")], foreground=[("selected", "#0f172a")])

    def _build_header_card(self) -> None:
        """
        Build top metadata banner displaying student information.
        Complies strictly with video demo requirements:
        Full Name: Chandana | Assigned Track: Python Programming | Task Title: Task 2 – BMI Calculator
        """
        header = tk.Frame(self.root, bg="#0f172a", padx=20, pady=12)
        header.pack(fill="x", side="top")

        # Top row: Organization & Task
        top_row = tk.Frame(header, bg="#0f172a")
        top_row.pack(fill="x")

        org_label = tk.Label(
            top_row,
            text=f"✨ {ORGANIZATION} SIP INTERNSHIP",
            font=("Segoe UI", 9, "bold"),
            fg="#38bdf8",
            bg="#0f172a"
        )
        org_label.pack(side="left")

        track_badge = tk.Label(
            top_row,
            text=f"Track: {ASSIGNED_TRACK}",
            font=("Segoe UI", 8, "bold"),
            fg="#94a3b8",
            bg="#1e293b",
            padx=8,
            pady=2
        )
        track_badge.pack(side="right")

        # Main Title & Student Identity Banner
        title_label = tk.Label(
            header,
            text="Body Mass Index (BMI) Calculator",
            font=("Segoe UI", 16, "bold"),
            fg="#ffffff",
            bg="#0f172a"
        )
        title_label.pack(anchor="w", pady=(2, 1))

        # Identity Card details explicitly presented for screen recording
        id_frame = tk.Frame(header, bg="#1e293b", padx=10, pady=5)
        id_frame.pack(fill="x", pady=(4, 0))

        demo_info = (
            f"👤 Full Name: {STUDENT_NAME}    |    "
            f"🎯 Assigned Track: {ASSIGNED_TRACK}    |    "
            f"📋 Task Title: {TASK_TITLE}"
        )
        id_label = tk.Label(
            id_frame,
            text=demo_info,
            font=("Segoe UI", 9, "bold"),
            fg="#38bdf8",
            bg="#1e293b"
        )
        id_label.pack(anchor="w")

    def _build_main_layout(self) -> None:
        """Create split two-column card layout: Input/Result on Left, History/Trends on Right."""
        body = tk.Frame(self.root, bg="#f1f5f9", padx=16, pady=12)
        body.pack(fill="both", expand=True)

        # ----------------------------------------------------------------------
        # LEFT COLUMN: Calculator Controls & BMI Result Card
        # ----------------------------------------------------------------------
        left_col = tk.Frame(body, bg="#f1f5f9", width=420)
        left_col.pack(side="left", fill="both", padx=(0, 10))

        # Input Card
        input_frame = tk.LabelFrame(
            left_col,
            text=" 1. Enter Measurements ",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#0f172a",
            padx=14,
            pady=12,
            relief="solid",
            bd=1
        )
        input_frame.pack(fill="x", pady=(0, 10))

        # Name Field
        tk.Label(input_frame, text="Person's Name:", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#334155").grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.entry_name = ttk.Entry(input_frame, font=("Segoe UI", 10))
        self.entry_name.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.entry_name.insert(0, STUDENT_NAME)  # Pre-fill intern name for quick demonstration

        # Weight Field (kg)
        tk.Label(input_frame, text="Weight in Kilograms (kg):", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#334155").grid(row=2, column=0, sticky="w", pady=(0, 2))
        self.entry_weight = ttk.Entry(input_frame, font=("Segoe UI", 10))
        self.entry_weight.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        tk.Label(input_frame, text="kg", font=("Segoe UI", 9, "bold"), bg="#e2e8f0", fg="#475569", padx=8, pady=4).grid(row=3, column=1, sticky="w", padx=(4, 0), pady=(0, 10))

        # Height Field (m)
        tk.Label(input_frame, text="Height in Meters (m):", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#334155").grid(row=4, column=0, sticky="w", pady=(0, 2))
        self.entry_height = ttk.Entry(input_frame, font=("Segoe UI", 10))
        self.entry_height.grid(row=5, column=0, sticky="ew", pady=(0, 4))
        tk.Label(input_frame, text="meters", font=("Segoe UI", 9, "bold"), bg="#e2e8f0", fg="#475569", padx=8, pady=4).grid(row=5, column=1, sticky="w", padx=(4, 0), pady=(0, 4))

        # Helper hint for height
        hint_label = tk.Label(
            input_frame,
            text="💡 Example: Weight = 68.5 kg, Height = 1.75 m (use meters, not cm)",
            font=("Segoe UI", 8),
            fg="#64748b",
            bg="#ffffff"
        )
        hint_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(2, 10))

        # Action Buttons
        btn_box = tk.Frame(input_frame, bg="#ffffff")
        btn_box.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        self.btn_calc = tk.Button(
            btn_box,
            text="⚡ Calculate BMI",
            command=self.on_calculate_bmi,
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2"
        )
        self.btn_calc.pack(side="left", expand=True, fill="x", padx=(0, 4))

        self.btn_reset = tk.Button(
            btn_box,
            text="🔄 Reset",
            command=self.on_reset_inputs,
            bg="#f1f5f9",
            fg="#475569",
            activebackground="#e2e8f0",
            activeforeground="#0f172a",
            font=("Segoe UI", 9),
            relief="solid",
            bd=1,
            padx=10,
            pady=6,
            cursor="hand2"
        )
        self.btn_reset.pack(side="right", padx=(4, 0))

        input_frame.columnconfigure(0, weight=1)

        # Result Display Card
        self.result_card = tk.LabelFrame(
            left_col,
            text=" 2. BMI Calculation Result ",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#0f172a",
            padx=14,
            pady=12,
            relief="solid",
            bd=1
        )
        self.result_card.pack(fill="both", expand=True)

        self.lbl_bmi_display = tk.Label(
            self.result_card,
            text="--.--",
            font=("Segoe UI", 32, "bold"),
            fg="#94a3b8",
            bg="#ffffff"
        )
        self.lbl_bmi_display.pack(pady=(4, 2))

        self.lbl_category_badge = tk.Label(
            self.result_card,
            text="Awaiting Calculation",
            font=("Segoe UI", 10, "bold"),
            fg="#64748b",
            bg="#f1f5f9",
            padx=12,
            pady=4,
            relief="flat"
        )
        self.lbl_category_badge.pack(pady=(0, 8))

        # Health tip box
        self.lbl_health_tip = tk.Label(
            self.result_card,
            text="Enter weight and height above, then click 'Calculate BMI' to see your score and category classification.",
            font=("Segoe UI", 9),
            fg="#475569",
            bg="#f8fafc",
            wraplength=340,
            justify="center",
            padx=8,
            pady=8,
            relief="solid",
            bd=1
        )
        self.lbl_health_tip.pack(fill="x", pady=(0, 10))

        # Save Button
        self.btn_save = tk.Button(
            self.result_card,
            text="💾 Save Record to Database",
            command=self.on_save_record,
            state="disabled",
            bg="#16a34a",
            fg="#ffffff",
            activebackground="#15803d",
            activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2"
        )
        self.btn_save.pack(fill="x")

        # ----------------------------------------------------------------------
        # RIGHT COLUMN: Historical Database Records & BMI Trend Graph
        # ----------------------------------------------------------------------
        right_col = tk.Frame(body, bg="#f1f5f9")
        right_col.pack(side="right", fill="both", expand=True)

        history_card = tk.LabelFrame(
            right_col,
            text=" 3. Historical Records & Trends (SQLite Local Storage) ",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#0f172a",
            padx=12,
            pady=10,
            relief="solid",
            bd=1
        )
        history_card.pack(fill="both", expand=True)

        # Filter & Action Toolbar
        toolbar = tk.Frame(history_card, bg="#ffffff")
        toolbar.pack(fill="x", pady=(0, 8))

        tk.Label(toolbar, text="Filter by User:", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#334155").pack(side="left", padx=(0, 6))

        self.combo_user_filter = ttk.Combobox(toolbar, state="readonly", width=18, font=("Segoe UI", 9))
        self.combo_user_filter.pack(side="left", padx=(0, 6))
        self.combo_user_filter.bind("<<ComboboxSelected>>", self.on_filter_changed)

        btn_show_all = tk.Button(
            toolbar,
            text="Show All",
            command=self.on_show_all_records,
            bg="#f1f5f9",
            fg="#334155",
            font=("Segoe UI", 9),
            relief="solid",
            bd=1,
            padx=6,
            pady=2,
            cursor="hand2"
        )
        btn_show_all.pack(side="left")

        # History Treeview Table
        table_frame = tk.Frame(history_card, bg="#ffffff")
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "timestamp", "name", "weight", "height", "bmi", "category")
        self.tree_history = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.tree_history.heading("id", text="# ID")
        self.tree_history.heading("timestamp", text="Date & Time")
        self.tree_history.heading("name", text="Name")
        self.tree_history.heading("weight", text="Weight (kg)")
        self.tree_history.heading("height", text="Height (m)")
        self.tree_history.heading("bmi", text="BMI")
        self.tree_history.heading("category", text="Category")

        self.tree_history.column("id", width=45, anchor="center")
        self.tree_history.column("timestamp", width=130, anchor="center")
        self.tree_history.column("name", width=95, anchor="w")
        self.tree_history.column("weight", width=75, anchor="center")
        self.tree_history.column("height", width=75, anchor="center")
        self.tree_history.column("bmi", width=65, anchor="center")
        self.tree_history.column("category", width=95, anchor="center")

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_history.yview)
        self.tree_history.configure(yscrollcommand=scrollbar_y.set)
        self.tree_history.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")

        # Bottom Action Bar
        bottom_bar = tk.Frame(history_card, bg="#ffffff")
        bottom_bar.pack(fill="x", pady=(10, 0))

        self.btn_trend_graph = tk.Button(
            bottom_bar,
            text="📈 View BMI Trend Graph",
            command=self.on_view_trend_graph,
            bg="#7c3aed",
            fg="#ffffff",
            activebackground="#6d28d9",
            activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2"
        )
        self.btn_trend_graph.pack(side="left", padx=(0, 6))

        self.btn_delete_rec = tk.Button(
            bottom_bar,
            text="🗑️ Delete Selected",
            command=self.on_delete_selected_record,
            bg="#fee2e2",
            fg="#dc2626",
            activebackground="#fecaca",
            activeforeground="#991b1b",
            font=("Segoe UI", 9, "bold"),
            relief="solid",
            bd=1,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.btn_delete_rec.pack(side="right")

    # --------------------------------------------------------------------------
    # Event Handlers & Controller Methods
    # --------------------------------------------------------------------------

    def on_calculate_bmi(self) -> None:
        """Handle BMI calculation with comprehensive input validation."""
        raw_name = self.entry_name.get()
        raw_weight = self.entry_weight.get()
        raw_height = self.entry_height.get()

        is_valid, err_msg, name, weight, height = validate_input(raw_name, raw_weight, raw_height)
        if not is_valid:
            messagebox.showerror("Input Validation Error", err_msg)
            return

        try:
            bmi = calculate_bmi(weight, height)
            category, color_hex, recommendation = classify_bmi(bmi)
            formatted_bmi = format_bmi(bmi)

            # Update GUI elements with calculated values
            self.lbl_bmi_display.config(text=formatted_bmi, fg=color_hex)
            self.lbl_category_badge.config(
                text=f"● Category: {category}",
                fg="#ffffff",
                bg=color_hex
            )
            self.lbl_health_tip.config(
                text=recommendation,
                fg="#0f172a",
                bg="#f8fafc"
            )

            # Store calculation in memory and enable Save button
            self.last_calculated_result = {
                "name": name,
                "weight": weight,
                "height": height,
                "bmi": float(formatted_bmi),
                "category": category
            }
            self.btn_save.config(state="normal", bg="#16a34a", cursor="hand2")

        except Exception as e:
            messagebox.showerror("Calculation Error", f"An unexpected error occurred during calculation:\n{e}")

    def on_save_record(self) -> None:
        """Save the currently calculated BMI record to SQLite database."""
        if not self.last_calculated_result:
            messagebox.showinfo("Nothing to Save", "Please calculate a BMI first before saving.")
            return

        rec = self.last_calculated_result
        success, msg = save_bmi_record(
            name=rec["name"],
            weight=rec["weight"],
            height=rec["height"],
            bmi=rec["bmi"],
            category=rec["category"],
            db_path=self.db_path
        )

        if success:
            messagebox.showinfo("Record Saved", msg)
            self._load_history_table()
            self._refresh_user_dropdown()
            # Disable save button until next new calculation to prevent duplicate double-click
            self.btn_save.config(state="disabled", bg="#94a3b8", cursor="arrow")
        else:
            messagebox.showerror("Database Error", msg)

    def on_reset_inputs(self) -> None:
        """Reset inputs and result cards to fresh state."""
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, STUDENT_NAME)
        self.entry_weight.delete(0, tk.END)
        self.entry_height.delete(0, tk.END)

        self.lbl_bmi_display.config(text="--.--", fg="#94a3b8")
        self.lbl_category_badge.config(
            text="Awaiting Calculation",
            fg="#64748b",
            bg="#f1f5f9"
        )
        self.lbl_health_tip.config(
            text="Enter weight and height above, then click 'Calculate BMI' to see your score and category classification.",
            fg="#475569",
            bg="#f8fafc"
        )
        self.last_calculated_result = None
        self.btn_save.config(state="disabled", bg="#94a3b8", cursor="arrow")

    def _load_history_table(self, user_filter: Optional[str] = None) -> None:
        """Reload historical records into the Treeview widget."""
        for item in self.tree_history.get_children():
            self.tree_history.delete(item)

        if user_filter and user_filter != "All Users":
            success, records, msg = fetch_records_by_user(user_filter, self.db_path)
            # Reverse to show newest at top of table
            records = list(reversed(records))
        else:
            success, records, msg = fetch_all_records(self.db_path)

        if not success:
            return

        for rec in records:
            self.tree_history.insert(
                "",
                "end",
                values=(
                    rec["id"],
                    rec["timestamp"],
                    rec["name"],
                    f"{rec['weight']:.2f}",
                    f"{rec['height']:.2f}",
                    f"{rec['bmi']:.2f}",
                    rec["category"]
                )
            )

    def _refresh_user_dropdown(self) -> None:
        """Refresh user filter options in the Combobox."""
        success, users, _ = fetch_distinct_users(self.db_path)
        options = ["All Users"] + users if success and users else ["All Users"]
        self.combo_user_filter["values"] = options
        if not self.combo_user_filter.get():
            self.combo_user_filter.set("All Users")

    def on_filter_changed(self, event=None) -> None:
        """Filter table records based on combobox selection."""
        selected = self.combo_user_filter.get()
        self._load_history_table(selected)

    def on_show_all_records(self) -> None:
        """Clear filter and display all records."""
        self.combo_user_filter.set("All Users")
        self._load_history_table("All Users")

    def on_view_trend_graph(self) -> None:
        """Open Matplotlib trend graph for the active or selected user."""
        selected_user = self.combo_user_filter.get()
        if not selected_user or selected_user == "All Users":
            # If not selected in filter, check current name entry field
            current_name = self.entry_name.get().strip()
            if current_name:
                selected_user = current_name
            else:
                messagebox.showinfo(
                    "Select User",
                    "Please select a user from the 'Filter by User' dropdown or type a name in the Name input field."
                )
                return

        open_bmi_trend_window(selected_user, self.root, self.db_path)

    def on_delete_selected_record(self) -> None:
        """Delete selected record from database after user confirmation."""
        selected_item = self.tree_history.selection()
        if not selected_item:
            messagebox.showinfo("Selection Required", "Please click on a record in the table to select it for deletion.")
            return

        record_values = self.tree_history.item(selected_item[0])["values"]
        record_id = record_values[0]
        person_name = record_values[2]

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete record #{record_id} for '{person_name}'?"
        )
        if confirm:
            success, msg = delete_record_by_id(record_id, self.db_path)
            if success:
                messagebox.showinfo("Deleted", msg)
                self._load_history_table(self.combo_user_filter.get())
                self._refresh_user_dropdown()
            else:
                messagebox.showerror("Error", msg)


# ==============================================================================
# SECTION 5: COMMAND-LINE INTERFACE (CLI) & BANNER
# ==============================================================================

def print_banner() -> None:
    """Print student and project metadata banner."""
    print("=" * 72)
    print(f"  {ORGANIZATION.upper()} SIP - PYTHON PROGRAMMING INTERNSHIP")
    print(f"  {TASK_TITLE.upper()}")
    print("-" * 72)
    print(f"  Full Name     : {STUDENT_NAME}")
    print(f"  Assigned Track: {ASSIGNED_TRACK}")
    print(f"  Task Title    : {TASK_TITLE}")
    print(f"  Organization  : {ORGANIZATION}")
    print("=" * 72)


def cli_main(db_path: Optional[str] = None) -> None:
    """Run interactive Command-Line Interface."""
    path = db_path or get_default_db_path()
    init_db(path)
    print_banner()
    print("\nWelcome to the Body Mass Index (BMI) Calculator CLI!")

    while True:
        print("\n--- Main Menu ---")
        print("1. Calculate BMI & Classify Category")
        print("2. View All Saved Historical Records")
        print("3. View BMI Trend Graph for a User")
        print("4. Launch Graphical User Interface (GUI)")
        print("5. Exit Application")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            print("\n[BMI Calculation]")
            name = input("Enter person's name: ")
            weight_str = input("Enter weight in kilograms (kg): ")
            height_str = input("Enter height in meters (m) [e.g. 1.75]: ")

            is_valid, err_msg, clean_name, weight, height = validate_input(name, weight_str, height_str)
            if not is_valid:
                print(f"\n❌ Error: {err_msg}")
                continue

            bmi = calculate_bmi(weight, height)
            category, color, advice = classify_bmi(bmi)
            formatted_bmi = format_bmi(bmi)

            print("\n" + "-" * 50)
            print(f"Result for   : {clean_name}")
            print(f"Weight       : {weight:.2f} kg")
            print(f"Height       : {height:.2f} m")
            print(f"BMI Score    : {formatted_bmi}")
            print(f"Category     : {category}")
            print(f"Health Note  : {advice}")
            print("-" * 50)

            save_choice = input("Do you want to save this record to database? (y/n): ").strip().lower()
            if save_choice in ("y", "yes"):
                ok, msg = save_bmi_record(clean_name, weight, height, float(formatted_bmi), category, db_path=path)
                if ok:
                    print(f"✅ {msg}")
                else:
                    print(f"❌ {msg}")

        elif choice == "2":
            print("\n[Historical Records]")
            ok, records, msg = fetch_all_records(path)
            if not ok:
                print(f"❌ {msg}")
            elif not records:
                print("No records currently saved in the database.")
            else:
                print(f"\n{'ID':<5} {'Timestamp':<20} {'Name':<15} {'Weight':<10} {'Height':<10} {'BMI':<8} {'Category':<12}")
                print("-" * 84)
                for r in records:
                    print(f"{r['id']:<5} {r['timestamp']:<20} {r['name']:<15} {r['weight']:<10.2f} {r['height']:<10.2f} {r['bmi']:<8.2f} {r['category']:<12}")

        elif choice == "3":
            if not MATPLOTLIB_AVAILABLE:
                print("\n❌ Error: 'matplotlib' is required for trend graphs. Please run: py -m pip install matplotlib")
                continue
            name = input("\nEnter user's name to plot BMI trend: ").strip()
            if not name:
                print("❌ Name cannot be empty.")
                continue
            print(f"Opening BMI trend graph window for '{name}'...")
            open_bmi_trend_window(name, db_path=path)
            # Matplotlib event loop in CLI mode
            try:
                plt.show()
            except Exception as e:
                print(f"Graph display note: {e}")

        elif choice == "4":
            print("\nLaunching Desktop Graphical User Interface (GUI)...")
            launch_gui(path)
            break

        elif choice == "5":
            print(f"\nThank you for using the Oasis Infobyte BMI Calculator. Goodbye!\n")
            break
        else:
            print("Invalid selection. Please choose an option from 1 to 5.")


def launch_gui(db_path: Optional[str] = None) -> None:
    """Initialize and run Tkinter main event loop."""
    root = tk.Tk()
    app = BMICalculatorGUI(root, db_path)
    root.mainloop()


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================
def main() -> None:
    """
    Main dispatching entry point:
    - If '--cli' passed: starts Command-Line Interface
    - If '--help' or '-h' passed: displays usage information
    - Default behavior: launches Tkinter Desktop GUI
    """
    if "--cli" in sys.argv:
        cli_main()
    elif "--help" in sys.argv or "-h" in sys.argv:
        print_banner()
        print("\nUsage:")
        print("  py main.py          : Launch Desktop Graphical User Interface (Default)")
        print("  py main.py --gui    : Explicitly launch Graphical User Interface")
        print("  py main.py --cli    : Launch Interactive Command-Line Interface")
        print("  py main.py --help   : Display this help message")
    else:
        # Default behavior: Launch modern Tkinter Desktop GUI
        launch_gui()


if __name__ == "__main__":
    main()
