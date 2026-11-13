"""
client.py - Modern Tkinter GUI Chat Client
Oasis Infobyte Python Internship - Task 5

Features:
- Authentication GUI: Login & Registration with input validation and show/hide password
- Multi-Room Chat: Room browsing, room creation modal, and active room participant list
- Real-Time Messaging: Thread-safe queue architecture prevents GUI freezing
- Message History: Automatically displays room history when switching rooms
- Visual Styling: Message cards/bubbles, distinct sent/received tags, timestamps
- Unicode Emoji Toolbar: Quick-insert popular emojis into the chat field
- Desktop Notifications: In-app notification banner, window focus tracking, audio bell
- Graceful Disconnection: Handles window closing and sudden server dropouts safely
"""

import socket
import threading
import queue
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

# =============================================================================
# COLOR THEME & STYLES (Modern Deep Slate / Indigo Theme)
# =============================================================================
THEME = {
    "bg_dark": "#13141f",         # Deep dark app background
    "bg_card": "#1e1f2e",         # Card / container background
    "bg_sidebar": "#181926",      # Sidebar background
    "bg_chat": "#161724",         # Chat history background
    "bg_input": "#252739",        # Entry field background
    "primary": "#6366f1",         # Modern Indigo Accent
    "primary_hover": "#4f46e5",   # Indigo Dark Hover
    "secondary": "#3b82f6",       # Blue accent
    "success": "#10b981",         # Emerald Green
    "danger": "#ef4444",          # Red error
    "warning": "#f59e0b",         # Amber notice
    "text_main": "#f8fafc",       # Bright text
    "text_muted": "#94a3b8",      # Slate muted text
    "bubble_sent": "#4f46e5",     # Sent message bubble
    "bubble_recv": "#282a3c",     # Received message bubble
    "border": "#2d3148",          # Subtle border
}

FONT_FAMILY = "Segoe UI"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5555


class ChatClientApp:
    """
    Main Tkinter Chat Application Controller.
    Manages socket communication, GUI view switching, and incoming message queues.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Oasis Chat Application — Task 5")
        self.root.geometry("980x680")
        self.root.minsize(800, 560)
        self.root.configure(bg=THEME["bg_dark"])

        # Network State
        self.sock = None
        self.is_connected = False
        self.current_user = None
        self.current_room = None
        self.available_rooms = []
        self.room_users = []
        self.unread_count = 0
        self.window_has_focus = True

        # Thread-safe queue for incoming network messages
        self.msg_queue = queue.Queue()

        # Track window focus for notifications
        self.root.bind("<FocusIn>", self._on_focus_in)
        self.root.bind("<FocusOut>", self._on_focus_out)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Build Container for switching views
        self.container = tk.Frame(self.root, bg=THEME["bg_dark"])
        self.container.pack(fill="both", expand=True)

        # Show Authentication Screen by default
        self.auth_frame = None
        self.chat_frame = None
        self.show_auth_screen()

        # Start background queue processor loop in Tkinter main thread
        self.root.after(50, self.process_incoming_queue)

    # =========================================================================
    # VIEW SWITCHING: AUTHENTICATION SCREEN
    # =========================================================================

    def show_auth_screen(self):
        """Builds and displays the Login & Registration screen."""
        if self.chat_frame:
            self.chat_frame.destroy()
            self.chat_frame = None

        self.auth_frame = tk.Frame(self.container, bg=THEME["bg_dark"])
        self.auth_frame.pack(fill="both", expand=True)

        # Centered Login Card
        card = tk.Frame(
            self.auth_frame,
            bg=THEME["bg_card"],
            highlightbackground=THEME["border"],
            highlightthickness=1,
            padx=35,
            pady=30
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Header Badge
        badge = tk.Label(
            card,
            text="⚡ OASIS INFOBYTE PYTHON INTERNSHIP",
            font=(FONT_FAMILY, 9, "bold"),
            fg=THEME["primary"],
            bg=THEME["bg_card"]
        )
        badge.pack(pady=(0, 4))

        title = tk.Label(
            card,
            text="Real-Time Chat Application",
            font=(FONT_FAMILY, 18, "bold"),
            fg=THEME["text_main"],
            bg=THEME["bg_card"]
        )
        title.pack(pady=(0, 4))

        subtitle = tk.Label(
            card,
            text="Connect, create rooms, and chat in real time",
            font=(FONT_FAMILY, 10),
            fg=THEME["text_muted"],
            bg=THEME["bg_card"]
        )
        subtitle.pack(pady=(0, 20))

        # Mode Selector (Login vs Register)
        self.auth_mode = tk.StringVar(value="login")

        tab_bar = tk.Frame(card, bg=THEME["bg_input"], padx=4, pady=4)
        tab_bar.pack(fill="x", pady=(0, 18))

        self.login_tab_btn = tk.Button(
            tab_bar,
            text="Log In",
            font=(FONT_FAMILY, 10, "bold"),
            bg=THEME["primary"],
            fg="white",
            relief="flat",
            activebackground=THEME["primary_hover"],
            activeforeground="white",
            cursor="hand2",
            padx=20,
            pady=6,
            command=lambda: self._set_auth_mode("login")
        )
        self.login_tab_btn.pack(side="left", expand=True, fill="x")

        self.reg_tab_btn = tk.Button(
            tab_bar,
            text="Register",
            font=(FONT_FAMILY, 10, "bold"),
            bg=THEME["bg_input"],
            fg=THEME["text_muted"],
            relief="flat",
            activebackground=THEME["border"],
            activeforeground="white",
            cursor="hand2",
            padx=20,
            pady=6,
            command=lambda: self._set_auth_mode("register")
        )
        self.reg_tab_btn.pack(side="right", expand=True, fill="x")

        # Server Host & Port Row
        conn_frame = tk.Frame(card, bg=THEME["bg_card"])
        conn_frame.pack(fill="x", pady=(0, 12))

        host_label = tk.Label(conn_frame, text="Server Host & Port:", font=(FONT_FAMILY, 9, "bold"), fg=THEME["text_muted"], bg=THEME["bg_card"])
        host_label.pack(anchor="w", pady=(0, 2))

        conn_inputs = tk.Frame(conn_frame, bg=THEME["bg_card"])
        conn_inputs.pack(fill="x")

        self.host_entry = tk.Entry(
            conn_inputs,
            font=(FONT_FAMILY, 10),
            bg=THEME["bg_input"],
            fg=THEME["text_main"],
            insertbackground="white",
            relief="flat",
            highlightbackground=THEME["border"],
            highlightthickness=1
        )
        self.host_entry.insert(0, DEFAULT_HOST)
        self.host_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 6))

        self.port_entry = tk.Entry(
            conn_inputs,
            font=(FONT_FAMILY, 10),
            bg=THEME["bg_input"],
            fg=THEME["text_main"],
            insertbackground="white",
            relief="flat",
            highlightbackground=THEME["border"],
            highlightthickness=1,
            width=8
        )
        self.port_entry.insert(0, str(DEFAULT_PORT))
        self.port_entry.pack(side="right", ipady=6)

        # Username Field
        u_label = tk.Label(card, text="Username:", font=(FONT_FAMILY, 9, "bold"), fg=THEME["text_muted"], bg=THEME["bg_card"])
        u_label.pack(anchor="w", pady=(0, 2))

        self.username_entry = tk.Entry(
            card,
            font=(FONT_FAMILY, 10),
            bg=THEME["bg_input"],
            fg=THEME["text_main"],
            insertbackground="white",
            relief="flat",
            highlightbackground=THEME["border"],
            highlightthickness=1
        )
        self.username_entry.pack(fill="x", ipady=6, pady=(0, 12))
        self.username_entry.focus_set()

        # Password Field with Show/Hide Toggle
        p_label = tk.Label(card, text="Password:", font=(FONT_FAMILY, 9, "bold"), fg=THEME["text_muted"], bg=THEME["bg_card"])
        p_label.pack(anchor="w", pady=(0, 2))

        pwd_frame = tk.Frame(card, bg=THEME["bg_input"], highlightbackground=THEME["border"], highlightthickness=1)
        pwd_frame.pack(fill="x", pady=(0, 16))

        self.password_entry = tk.Entry(
            pwd_frame,
            show="•",
            font=(FONT_FAMILY, 10),
            bg=THEME["bg_input"],
            fg=THEME["text_main"],
            insertbackground="white",
            relief="flat",
            bd=0
        )
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(8, 0))
        self.password_entry.bind("<Return>", lambda e: self._submit_auth())

        self.show_pwd_var = tk.BooleanVar(value=False)
        self.toggle_pwd_btn = tk.Button(
            pwd_frame,
            text="👁",
            font=(FONT_FAMILY, 9),
            bg=THEME["bg_input"],
            fg=THEME["text_muted"],
            relief="flat",
            bd=0,
            activebackground=THEME["bg_input"],
            cursor="hand2",
            command=self._toggle_password_visibility
        )
        self.toggle_pwd_btn.pack(side="right", padx=6)

        # Status / Feedback Label
        self.auth_feedback_label = tk.Label(
            card,
            text="",
            font=(FONT_FAMILY, 9),
            fg=THEME["danger"],
            bg=THEME["bg_card"],
            wraplength=320,
            justify="center"
        )
        self.auth_feedback_label.pack(fill="x", pady=(0, 10))

        # Submit Button
        self.auth_submit_btn = tk.Button(
            card,
            text="Log In to Chat",
            font=(FONT_FAMILY, 11, "bold"),
            bg=THEME["primary"],
            fg="white",
            activebackground=THEME["primary_hover"],
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            pady=8,
            command=self._submit_auth
        )
        self.auth_submit_btn.pack(fill="x")

    def _set_auth_mode(self, mode: str):
        """Switches between Login and Register tabs in the Auth view."""
        self.auth_mode.set(mode)
        self.auth_feedback_label.config(text="")
        if mode == "login":
            self.login_tab_btn.config(bg=THEME["primary"], fg="white")
            self.reg_tab_btn.config(bg=THEME["bg_input"], fg=THEME["text_muted"])
            self.auth_submit_btn.config(text="Log In to Chat")
        else:
            self.login_tab_btn.config(bg=THEME["bg_input"], fg=THEME["text_muted"])
            self.reg_tab_btn.config(bg=THEME["primary"], fg="white")
            self.auth_submit_btn.config(text="Create Account")

    def _toggle_password_visibility(self):
        """Toggles password masking between bullets and plain text."""
        if self.show_pwd_var.get():
            self.password_entry.config(show="•")
            self.show_pwd_var.set(False)
            self.toggle_pwd_btn.config(fg=THEME["text_muted"])
        else:
            self.password_entry.config(show="")
            self.show_pwd_var.set(True)
            self.toggle_pwd_btn.config(fg=THEME["primary"])

    # =========================================================================
    # VIEW SWITCHING: MAIN CHAT SCREEN
    # =========================================================================

    def show_chat_screen(self):
        """Constructs and renders the modern multi-room chat dashboard."""
        if self.auth_frame:
            self.auth_frame.destroy()
            self.auth_frame = None

        self.chat_frame = tk.Frame(self.container, bg=THEME["bg_dark"])
        self.chat_frame.pack(fill="both", expand=True)

        # ---------------- TOP NAVIGATION BAR ----------------
        top_bar = tk.Frame(self.chat_frame, bg=THEME["bg_card"], height=52, padx=16, pady=8)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        # Brand Title
        app_logo = tk.Label(
            top_bar,
            text="⚡ OASIS CHAT",
            font=(FONT_FAMILY, 12, "bold"),
            fg=THEME["primary"],
            bg=THEME["bg_card"]
        )
        app_logo.pack(side="left")

        # Current Room Indicator in Top Bar
        self.top_room_label = tk.Label(
            top_bar,
            text="# General",
            font=(FONT_FAMILY, 12, "bold"),
            fg=THEME["text_main"],
            bg=THEME["bg_card"],
            padx=12
        )
        self.top_room_label.pack(side="left")

        # In-App Notification Toast
        self.toast_label = tk.Label(
            top_bar,
            text="",
            font=(FONT_FAMILY, 9, "italic"),
            fg=THEME["warning"],
            bg=THEME["bg_card"]
        )
        self.toast_label.pack(side="left", padx=16)

        # Right-side user badge & Logout Button
        logout_btn = tk.Button(
            top_bar,
            text="Logout",
            font=(FONT_FAMILY, 9, "bold"),
            bg="#2e1a22",
            fg="#f87171",
            relief="flat",
            activebackground=THEME["danger"],
            activeforeground="white",
            cursor="hand2",
            padx=12,
            pady=3,
            command=self.logout
        )
        logout_btn.pack(side="right")

        self.user_badge = tk.Label(
            top_bar,
            text=f"🟢 {self.current_user}",
            font=(FONT_FAMILY, 10, "bold"),
            fg=THEME["success"],
            bg=THEME["bg_card"],
            padx=10
        )
        self.user_badge.pack(side="right")

        # ---------------- MAIN CONTENT SPLIT ----------------
        main_body = tk.Frame(self.chat_frame, bg=THEME["bg_dark"])
        main_body.pack(fill="both", expand=True)

        # ---------------- LEFT SIDEBAR: ROOMS & USERS ----------------
        sidebar = tk.Frame(
            main_body,
            bg=THEME["bg_sidebar"],
            width=230,
            padx=12,
            pady=12,
            highlightbackground=THEME["border"],
            highlightthickness=1
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Rooms Header & Create Button
        room_header_row = tk.Frame(sidebar, bg=THEME["bg_sidebar"])
        room_header_row.pack(fill="x", pady=(0, 8))

        rooms_title = tk.Label(
            room_header_row,
            text="CHAT ROOMS",
            font=(FONT_FAMILY, 9, "bold"),
            fg=THEME["text_muted"],
            bg=THEME["bg_sidebar"]
        )
        rooms_title.pack(side="left")

        new_room_btn = tk.Button(
            room_header_row,
            text="+ New",
            font=(FONT_FAMILY, 8, "bold"),
            bg=THEME["primary"],
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=6,
            pady=1,
            activebackground=THEME["primary_hover"],
            command=self._prompt_create_room
        )
        new_room_btn.pack(side="right")

        # Scrollable Room Listbox
        rooms_container = tk.Frame(sidebar, bg=THEME["bg_input"])
        rooms_container.pack(fill="both", expand=True, pady=(0, 10))

        self.room_listbox = tk.Listbox(
            rooms_container,
            bg=THEME["bg_sidebar"],
            fg=THEME["text_main"],
            selectbackground=THEME["primary"],
            selectforeground="white",
            font=(FONT_FAMILY, 10),
            relief="flat",
            bd=0,
            highlightthickness=0,
            activestyle="none"
        )
        self.room_listbox.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        self.room_listbox.bind("<<ListboxSelect>>", self._on_room_selected)

        room_scrollbar = ttk.Scrollbar(rooms_container, orient="vertical", command=self.room_listbox.yview)
        room_scrollbar.pack(side="right", fill="y")
        self.room_listbox.config(yscrollcommand=room_scrollbar.set)

        # Active Users in Room Header
        users_title = tk.Label(
            sidebar,
            text="ONLINE IN ROOM",
            font=(FONT_FAMILY, 9, "bold"),
            fg=THEME["text_muted"],
            bg=THEME["bg_sidebar"]
        )
        users_title.pack(anchor="w", pady=(6, 4))

        # Active Users Listbox
        users_container = tk.Frame(sidebar, bg=THEME["bg_sidebar"], height=160)
        users_container.pack(fill="x", side="bottom")
        users_container.pack_propagate(False)

        self.users_listbox = tk.Listbox(
            users_container,
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            font=(FONT_FAMILY, 9),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=THEME["border"],
            activestyle="none"
        )
        self.users_listbox.pack(fill="both", expand=True)

        # ---------------- RIGHT: CHAT FEED & INPUT AREA ----------------
        chat_area_frame = tk.Frame(main_body, bg=THEME["bg_dark"])
        chat_area_frame.pack(side="right", fill="both", expand=True)

        # Chat Message View (Text widget with Rich Tags)
        msg_container = tk.Frame(chat_area_frame, bg=THEME["bg_chat"])
        msg_container.pack(fill="both", expand=True, padx=12, pady=(10, 6))

        self.chat_display = tk.Text(
            msg_container,
            bg=THEME["bg_chat"],
            fg=THEME["text_main"],
            font=(FONT_FAMILY, 10),
            wrap="word",
            state="disabled",
            relief="flat",
            bd=0,
            padx=14,
            pady=12
        )
        self.chat_display.pack(side="left", fill="both", expand=True)

        chat_scroll = ttk.Scrollbar(msg_container, orient="vertical", command=self.chat_display.yview)
        chat_scroll.pack(side="right", fill="y")
        self.chat_display.config(yscrollcommand=chat_scroll.set)

        # Configure rich visual tags in Text widget
        self.chat_display.tag_configure("timestamp", foreground=THEME["text_muted"], font=(FONT_FAMILY, 8))
        self.chat_display.tag_configure("sender_self", foreground="#818cf8", font=(FONT_FAMILY, 10, "bold"))
        self.chat_display.tag_configure("sender_other", foreground="#38bdf8", font=(FONT_FAMILY, 10, "bold"))
        self.chat_display.tag_configure("msg_text", foreground=THEME["text_main"], font=(FONT_FAMILY, 10))
        self.chat_display.tag_configure("bubble_self", background="#232438", lmargin1=40, lmargin2=40, rmargin=10)
        self.chat_display.tag_configure("bubble_other", background="#1e202f", lmargin1=10, lmargin2=10, rmargin=40)
        self.chat_display.tag_configure("system_notice", foreground=THEME["warning"], font=(FONT_FAMILY, 9, "italic"), justify="center")
        self.chat_display.tag_configure("system_join", foreground=THEME["success"], font=(FONT_FAMILY, 9, "italic"), justify="center")
        self.chat_display.tag_configure("history_header", foreground=THEME["text_muted"], font=(FONT_FAMILY, 9, "bold"), justify="center")

        # ---------------- EMOJI TOOLBAR ----------------
        emoji_frame = tk.Frame(chat_area_frame, bg=THEME["bg_dark"], padx=12)
        emoji_frame.pack(fill="x", pady=(0, 4))

        quick_emojis = ["😀", "😂", "😍", "👍", "🎉", "🔥", "❤️", "🚀", "👏", "🙌", "😎", "🤔", "💡", "💻", "🐍", "✨"]
        for emo in quick_emojis:
            b = tk.Button(
                emoji_frame,
                text=emo,
                font=(FONT_FAMILY, 10),
                bg=THEME["bg_card"],
                fg="white",
                relief="flat",
                bd=0,
                padx=4,
                pady=1,
                cursor="hand2",
                activebackground=THEME["border"],
                command=lambda e=emo: self._insert_emoji(e)
            )
            b.pack(side="left", padx=2)

        # ---------------- MESSAGE INPUT ROW ----------------
        input_row = tk.Frame(chat_area_frame, bg=THEME["bg_card"], padx=12, pady=10)
        input_row.pack(fill="x", side="bottom", padx=12, pady=(0, 10))

        self.msg_entry = tk.Entry(
            input_row,
            font=(FONT_FAMILY, 11),
            bg=THEME["bg_input"],
            fg=THEME["text_main"],
            insertbackground="white",
            relief="flat",
            bd=0,
            highlightbackground=THEME["border"],
            highlightthickness=1
        )
        self.msg_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.msg_entry.bind("<Return>", lambda e: self.send_chat_message())
        self.msg_entry.focus_set()

        send_btn = tk.Button(
            input_row,
            text="➤ Send",
            font=(FONT_FAMILY, 10, "bold"),
            bg=THEME["primary"],
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=6,
            activebackground=THEME["primary_hover"],
            activeforeground="white",
            command=self.send_chat_message
        )
        send_btn.pack(side="right")

        # Refresh rooms listbox
        self._refresh_room_listbox()

        # Automatically join default room ('General')
        if "General" in self.available_rooms:
            self.join_room("General")
        elif self.available_rooms:
            self.join_room(self.available_rooms[0])

    def _insert_emoji(self, emoji_char: str):
        """Inserts selected emoji at current cursor position in message entry."""
        if hasattr(self, "msg_entry") and self.msg_entry:
            self.msg_entry.insert(tk.INSERT, emoji_char)
            self.msg_entry.focus_set()

    # =========================================================================
    # AUTHENTICATION LOGIC (LOGIN / REGISTER)
    # =========================================================================

    def _submit_auth(self):
        """Handles submission of either Login or Registration form."""
        host = self.host_entry.get().strip() or DEFAULT_HOST
        port_str = self.port_entry.get().strip() or str(DEFAULT_PORT)
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        try:
            port = int(port_str)
        except ValueError:
            self.auth_feedback_label.config(text="Port must be a valid integer.", fg=THEME["danger"])
            return

        if not username:
            self.auth_feedback_label.config(text="Please enter a username.", fg=THEME["danger"])
            return

        if not password:
            self.auth_feedback_label.config(text="Please enter a password.", fg=THEME["danger"])
            return

        self.auth_feedback_label.config(text="Connecting to server...", fg=THEME["warning"])
        self.auth_submit_btn.config(state="disabled")

        # Connect to server if not connected
        if not self.is_connected:
            connected = self.connect_to_server(host, port)
            if not connected:
                self.auth_submit_btn.config(state="normal")
                return

        mode = self.auth_mode.get()
        if mode == "register":
            self.send_packet({
                "action": "register",
                "username": username,
                "password": password
            })
        else:
            self.send_packet({
                "action": "login",
                "username": username,
                "password": password
            })

    def connect_to_server(self, host: str, port: int) -> bool:
        """Establishes a TCP connection to the chat server."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            self.is_connected = True

            # Start listener background thread
            listener_thread = threading.Thread(target=self.receive_loop, daemon=True)
            listener_thread.start()
            return True
        except Exception as e:
            self.is_connected = False
            self.sock = None
            self.auth_feedback_label.config(
                text=f"Connection failed: Could not connect to {host}:{port}.\nMake sure server.py is running!",
                fg=THEME["danger"]
            )
            return False

    # =========================================================================
    # NETWORKING: SEND & RECEIVE LOOPS
    # =========================================================================

    def send_packet(self, payload: dict):
        """Sends a newline-delimited JSON packet across the socket."""
        if not self.sock or not self.is_connected:
            return False
        try:
            data = (json.dumps(payload) + "\n").encode("utf-8")
            self.sock.sendall(data)
            return True
        except Exception as e:
            self.handle_server_disconnect("Connection error while sending data.")
            return False

    def receive_loop(self):
        """
        Background listener loop. Reads from socket, parses newline-delimited
        JSON messages, and enqueues them into the thread-safe msg_queue.
        """
        buffer = ""
        while self.is_connected:
            try:
                data = self.sock.recv(4096)
                if not data:
                    # Server closed connection
                    break
                buffer += data.decode("utf-8", errors="replace")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line:
                        try:
                            packet = json.loads(line)
                            self.msg_queue.put(packet)
                        except json.JSONDecodeError:
                            pass
            except (ConnectionResetError, ConnectionAbortedError):
                break
            except Exception:
                break

        if self.is_connected:
            self.msg_queue.put({"action": "server_shutdown", "message": "Connection to chat server was lost."})

    def process_incoming_queue(self):
        """
        Called repeatedly on the Tkinter main event thread via root.after().
        Pulls packets from the queue and updates the GUI safely.
        """
        try:
            while not self.msg_queue.empty():
                packet = self.msg_queue.get_nowait()
                self.dispatch_packet(packet)
        except queue.Empty:
            pass
        finally:
            self.root.after(50, self.process_incoming_queue)

    def dispatch_packet(self, packet: dict):
        """Dispatches an incoming packet to its dedicated GUI handler."""
        action = packet.get("action")

        if action == "register_response":
            self.on_register_response(packet)
        elif action == "login_response":
            self.on_login_response(packet)
        elif action == "rooms_list":
            self.on_rooms_list(packet)
        elif action == "join_room_response":
            self.on_join_room_response(packet)
        elif action == "new_message":
            self.on_new_message(packet)
        elif action == "user_joined":
            self.on_user_joined(packet)
        elif action == "user_left":
            self.on_user_left(packet)
        elif action == "server_shutdown":
            self.handle_server_disconnect(packet.get("message", "Server disconnected."))
        elif action == "error":
            self.show_toast(packet.get("message", "Error occurred"), is_error=True)

    # =========================================================================
    # PACKET HANDLERS
    # =========================================================================

    def on_register_response(self, packet: dict):
        status = packet.get("status")
        msg = packet.get("message", "")
        if hasattr(self, "auth_submit_btn") and self.auth_submit_btn:
            self.auth_submit_btn.config(state="normal")

        if status == "ok":
            self.auth_feedback_label.config(text=f"{msg}\nYou can now log in!", fg=THEME["success"])
            self._set_auth_mode("login")
        else:
            self.auth_feedback_label.config(text=msg, fg=THEME["danger"])

    def on_login_response(self, packet: dict):
        status = packet.get("status")
        msg = packet.get("message", "")
        if hasattr(self, "auth_submit_btn") and self.auth_submit_btn:
            self.auth_submit_btn.config(state="normal")

        if status == "ok":
            self.current_user = packet.get("username")
            self.available_rooms = packet.get("rooms", [])
            self.show_chat_screen()
        else:
            self.auth_feedback_label.config(text=msg, fg=THEME["danger"])

    def on_rooms_list(self, packet: dict):
        self.available_rooms = packet.get("rooms", [])
        self._refresh_room_listbox()
        notice = packet.get("notice")
        if notice:
            self.show_toast(notice)

    def on_join_room_response(self, packet: dict):
        status = packet.get("status")
        if status == "ok":
            self.current_room = packet.get("room_name")
            self.room_users = packet.get("users", [])
            history = packet.get("history", [])

            # Update top label
            if hasattr(self, "top_room_label"):
                self.top_room_label.config(text=f"# {self.current_room}")

            # Update online users list
            self._refresh_users_listbox()

            # Clear chat and render history
            self._clear_chat_display()
            self._append_system_message(f"--- Welcome to #{self.current_room} ---", tag="history_header")

            if history:
                self._append_system_message("─── Previous Message History ───", tag="history_header")
                for item in history:
                    self._render_message(
                        sender=item.get("username", "Unknown"),
                        message=item.get("message", ""),
                        timestamp=item.get("timestamp", ""),
                        is_history=True
                    )
                self._append_system_message("─── Live Messages Below ───", tag="history_header")
            else:
                self._append_system_message("No previous messages in this room. Be the first to say hi!", tag="system_notice")

    def on_new_message(self, packet: dict):
        room = packet.get("room_name")
        sender = packet.get("username")
        text = packet.get("message")
        ts = packet.get("timestamp")

        # Only display if the message belongs to current room
        if room == self.current_room:
            self._render_message(sender, text, ts)

            # Trigger notification if received from someone else
            if sender != self.current_user:
                self._trigger_incoming_notification(sender, room, text)

    def on_user_joined(self, packet: dict):
        room = packet.get("room_name")
        username = packet.get("username")
        ts = packet.get("timestamp")
        users = packet.get("users", [])

        if room == self.current_room:
            self.room_users = users
            self._refresh_users_listbox()
            self._append_system_message(f"{ts} → {username} joined #{room}", tag="system_join")

    def on_user_left(self, packet: dict):
        room = packet.get("room_name")
        username = packet.get("username")
        ts = packet.get("timestamp")
        users = packet.get("users", [])

        if room == self.current_room:
            self.room_users = users
            self._refresh_users_listbox()
            self._append_system_message(f"{ts} ← {username} left #{room}", tag="system_notice")

    # =========================================================================
    # CHAT ACTIONS: SENDING, ROOM CREATION & JOINING
    # =========================================================================

    def send_chat_message(self):
        """Validates and sends the current typed message."""
        if not hasattr(self, "msg_entry") or not self.msg_entry:
            return

        text = self.msg_entry.get().strip()
        if not text:
            return

        if not self.current_room:
            messagebox.showwarning("No Room", "Please select or join a room first.")
            return

        success = self.send_packet({
            "action": "send_message",
            "room_name": self.current_room,
            "message": text
        })

        if success:
            self.msg_entry.delete(0, tk.END)

    def join_room(self, room_name: str):
        """Sends request to join the chosen room."""
        if not room_name or room_name == self.current_room:
            return
        self.send_packet({
            "action": "join_room",
            "room_name": room_name
        })

    def _prompt_create_room(self):
        """Opens a clean dialog prompting user for a new room name."""
        room_name = simpledialog.askstring("Create Chat Room", "Enter new room name (alphanumeric, -, _):", parent=self.root)
        if room_name and room_name.strip():
            self.send_packet({
                "action": "create_room",
                "room_name": room_name.strip()
            })

    def _on_room_selected(self, event):
        """Handles user clicking a room in the rooms listbox."""
        selection = self.room_listbox.curselection()
        if selection:
            index = selection[0]
            selected_room = self.available_rooms[index]
            if selected_room != self.current_room:
                self.join_room(selected_room)

    # =========================================================================
    # GUI RENDERING HELPERS
    # =========================================================================

    def _render_message(self, sender: str, message: str, timestamp: str, is_history: bool = False):
        """Appends a styled message card into the chat Text widget."""
        self.chat_display.config(state="normal")

        is_self = (sender == self.current_user)
        bubble_tag = "bubble_self" if is_self else "bubble_recv"
        sender_tag = "sender_self" if is_self else "sender_other"
        display_sender = "You" if is_self else sender

        # Header: Timestamp + Sender
        self.chat_display.insert(tk.END, f"\n{timestamp} ", "timestamp")
        self.chat_display.insert(tk.END, f"{display_sender}\n", sender_tag)

        # Message body
        self.chat_display.insert(tk.END, f"  {message}\n", ("msg_text", bubble_tag))

        self.chat_display.config(state="disabled")
        self.chat_display.see(tk.END)

    def _append_system_message(self, text: str, tag: str = "system_notice"):
        """Inserts a centered system notice into the chat."""
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, f"\n{text}\n", tag)
        self.chat_display.config(state="disabled")
        self.chat_display.see(tk.END)

    def _clear_chat_display(self):
        """Clears all text from the chat feed."""
        self.chat_display.config(state="normal")
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state="disabled")

    def _refresh_room_listbox(self):
        """Populates the room listbox with current available rooms."""
        if not hasattr(self, "room_listbox") or not self.room_listbox:
            return

        self.room_listbox.delete(0, tk.END)
        for i, room in enumerate(self.available_rooms):
            prefix = "▶ " if room == self.current_room else "  # "
            self.room_listbox.insert(tk.END, f"{prefix}{room}")
            if room == self.current_room:
                self.room_listbox.selection_set(i)

    def _refresh_users_listbox(self):
        """Populates the users listbox with online participants."""
        if not hasattr(self, "users_listbox") or not self.users_listbox:
            return

        self.users_listbox.delete(0, tk.END)
        for user in self.room_users:
            marker = " (You)" if user == self.current_user else ""
            self.users_listbox.insert(tk.END, f"  🟢 {user}{marker}")

    # =========================================================================
    # NOTIFICATIONS & FOCUS MANAGEMENT
    # =========================================================================

    def _trigger_incoming_notification(self, sender: str, room: str, text: str):
        """Produces in-app notification toast and window alert."""
        # Audio alert
        try:
            self.root.bell()
        except Exception:
            pass

        # In-app toast banner
        preview = (text[:28] + "...") if len(text) > 28 else text
        self.show_toast(f"💬 {sender} in #{room}: {preview}")

        # If window is unfocused, update window title
        if not self.window_has_focus:
            self.unread_count += 1
            self.root.title(f"({self.unread_count} New Messages) Oasis Chat — #{self.current_room}")

    def show_toast(self, message: str, is_error: bool = False):
        """Shows temporary notice on the top navigation bar."""
        if hasattr(self, "toast_label") and self.toast_label:
            color = THEME["danger"] if is_error else THEME["warning"]
            self.toast_label.config(text=message, fg=color)
            self.root.after(4500, self._clear_toast)

    def _clear_toast(self):
        if hasattr(self, "toast_label") and self.toast_label:
            self.toast_label.config(text="")

    def _on_focus_in(self, event):
        self.window_has_focus = True
        self.unread_count = 0
        room_title = f" — #{self.current_room}" if self.current_room else ""
        self.root.title(f"Oasis Chat Application{room_title}")

    def _on_focus_out(self, event):
        self.window_has_focus = False

    # =========================================================================
    # LOGOUT & DISCONNECTION
    # =========================================================================

    def logout(self):
        """Logs out of the current session and returns to login screen."""
        if self.sock and self.is_connected:
            self.send_packet({"action": "leave_room"})
            self.send_packet({"action": "disconnect"})
            try:
                self.sock.close()
            except Exception:
                pass
        self.sock = None
        self.is_connected = False
        self.current_user = None
        self.current_room = None
        self.show_auth_screen()

    def handle_server_disconnect(self, message: str):
        """Handles server connection drops gracefully without crashing."""
        self.is_connected = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

        if self.chat_frame:
            self._append_system_message(f"⚠️ {message}", tag="system_notice")
            if hasattr(self, "msg_entry"):
                self.msg_entry.config(state="disabled")
            messagebox.showwarning("Connection Lost", f"{message}\nPlease restart the application or reconnect.")
        elif self.auth_frame:
            self.auth_feedback_label.config(text=message, fg=THEME["danger"])
            if hasattr(self, "auth_submit_btn"):
                self.auth_submit_btn.config(state="normal")

    def on_closing(self):
        """Gracefully closes socket and cleans up upon window closing."""
        if self.is_connected and self.sock:
            try:
                self.send_packet({"action": "disconnect"})
                self.sock.close()
            except Exception:
                pass
        self.is_connected = False
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ChatClientApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
