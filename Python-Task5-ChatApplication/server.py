"""
server.py - Multi-Threaded Real-Time Chat Server
Oasis Infobyte Python Internship - Task 5

Handles TCP socket connections, JSON protocol message framing,
user authentication, room isolation, message routing, persistence,
and graceful disconnection handling.
"""

import socket
import threading
import json
import os
import sys
from datetime import datetime
import database

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5555
BUFFER_SIZE = 4096


class ChatServer:
    """
    Multi-threaded TCP Chat Server that routes messages between clients,
    maintains room isolation, and persists history in SQLite.
    """

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, db_path=database.DEFAULT_DB_PATH):
        self.host = host
        self.port = port
        self.db_path = db_path
        self.server_socket = None
        self.is_running = False

        # Lock for thread-safe access to client state
        self.lock = threading.Lock()

        # {socket: {"username": str, "current_room": str or None}}
        self.clients = {}

        # {room_name: set(socket)}
        self.rooms = {}

        # Initialize the database schema and default rooms
        database.init_db(self.db_path)

    def log(self, tag: str, message: str):
        """Prints a clean formatted server console log with timestamp."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] [{tag.upper()}] {message}", flush=True)

    def start(self):
        """Starts the TCP server socket and the client listener loop."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(50)
            self.is_running = True
            self.log("INFO", f"Chat Server running on {self.host}:{self.port}")
            self.log("INFO", "Waiting for incoming client connections...")

            while self.is_running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    self.log("CONN", f"New connection from {client_address[0]}:{client_address[1]}")

                    with self.lock:
                        self.clients[client_socket] = {"username": None, "current_room": None}

                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                except socket.error:
                    if not self.is_running:
                        break
        except Exception as e:
            self.log("ERROR", f"Server error: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        """Gracefully shuts down the server and notifies all connected clients."""
        with self.lock:
            if not self.is_running and self.server_socket is None:
                return
            self.is_running = False
            sock_to_close = self.server_socket
            self.server_socket = None
            client_socks = list(self.clients.keys())
            self.clients.clear()
            self.rooms.clear()

        self.log("INFO", "Shutting down chat server...")

        # Notify all connected clients of shutdown
        for sock in client_socks:
            try:
                self.send_json(sock, {
                    "action": "server_shutdown",
                    "message": "The server has been shut down by the administrator."
                })
                sock.close()
            except Exception:
                pass

        if sock_to_close:
            try:
                sock_to_close.close()
            except Exception:
                pass

        self.log("INFO", "Server stopped cleanly.")

    def send_json(self, sock: socket.socket, payload: dict):
        """
        Encodes a python dict into a newline-delimited JSON UTF-8 byte stream.
        """
        try:
            raw_data = (json.dumps(payload) + "\n").encode("utf-8")
            sock.sendall(raw_data)
            return True
        except Exception as e:
            # Client socket may have closed unexpectedly
            return False

    def broadcast_to_room(self, room_name: str, payload: dict, exclude_sock=None):
        """
        Sends a JSON payload to every client currently joined to room_name.
        """
        with self.lock:
            target_sockets = list(self.rooms.get(room_name, set()))

        for sock in target_sockets:
            if sock != exclude_sock:
                self.send_json(sock, payload)

    def broadcast_to_all(self, payload: dict):
        """Sends a JSON payload to every connected client."""
        with self.lock:
            target_sockets = list(self.clients.keys())

        for sock in target_sockets:
            self.send_json(sock, payload)

    def handle_client(self, client_socket: socket.socket, client_address):
        """
        Client communication loop: reads newline-delimited JSON messages,
        dispatches to specific action handlers, and handles disconnection.
        """
        buffer = ""

        try:
            while self.is_running:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    # Client disconnected (EOF)
                    break

                buffer += data.decode("utf-8", errors="replace")

                # Handle newline-delimited messages
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        packet = json.loads(line)
                        self.process_packet(client_socket, packet)
                    except json.JSONDecodeError:
                        self.send_json(client_socket, {
                            "action": "error",
                            "message": "Malformed JSON packet received."
                        })
        except (ConnectionResetError, ConnectionAbortedError, OSError):
            pass
        except Exception as e:
            self.log("ERROR", f"Exception handling client {client_address}: {e}")
        finally:
            self.cleanup_client(client_socket)

    def process_packet(self, sock: socket.socket, packet: dict):
        """Routes parsed JSON packets based on the 'action' field."""
        action = packet.get("action")

        if action == "register":
            self.handle_register(sock, packet)
        elif action == "login":
            self.handle_login(sock, packet)
        elif action == "get_rooms":
            self.handle_get_rooms(sock)
        elif action == "create_room":
            self.handle_create_room(sock, packet)
        elif action == "join_room":
            self.handle_join_room(sock, packet)
        elif action == "send_message":
            self.handle_send_message(sock, packet)
        elif action == "leave_room":
            self.handle_leave_room(sock)
        elif action == "disconnect":
            self.cleanup_client(sock)
        else:
            self.send_json(sock, {
                "action": "error",
                "message": f"Unknown action: '{action}'."
            })

    # =========================================================================
    # ACTION HANDLERS
    # =========================================================================

    def handle_register(self, sock: socket.socket, packet: dict):
        username = packet.get("username", "")
        password = packet.get("password", "")

        success, msg = database.register_user(username, password, db_path=self.db_path)
        if success:
            self.log("AUTH", f"User registered successfully: '{username}'")
            self.send_json(sock, {
                "action": "register_response",
                "status": "ok",
                "message": msg
            })
        else:
            self.log("AUTH", f"Registration failed for '{username}': {msg}")
            self.send_json(sock, {
                "action": "register_response",
                "status": "error",
                "message": msg
            })

    def handle_login(self, sock: socket.socket, packet: dict):
        username = packet.get("username", "")
        password = packet.get("password", "")

        # Check if this user is already active in another session
        with self.lock:
            for s, info in self.clients.items():
                if s != sock and info["username"] and info["username"].lower() == username.lower():
                    self.send_json(sock, {
                        "action": "login_response",
                        "status": "error",
                        "message": f"User '{username}' is already logged in on another client."
                    })
                    return

        success, msg = database.verify_user(username, password, db_path=self.db_path)
        if success:
            with self.lock:
                if sock in self.clients:
                    self.clients[sock]["username"] = username

            rooms = database.get_all_rooms(db_path=self.db_path)
            self.log("AUTH", f"User logged in: '{username}'")
            self.send_json(sock, {
                "action": "login_response",
                "status": "ok",
                "username": username,
                "message": f"Welcome back, {username}!",
                "rooms": rooms
            })
        else:
            self.log("AUTH", f"Failed login attempt for '{username}'")
            self.send_json(sock, {
                "action": "login_response",
                "status": "error",
                "message": msg
            })

    def handle_get_rooms(self, sock: socket.socket):
        rooms = database.get_all_rooms(db_path=self.db_path)
        self.send_json(sock, {
            "action": "rooms_list",
            "rooms": rooms
        })

    def handle_create_room(self, sock: socket.socket, packet: dict):
        with self.lock:
            client_info = self.clients.get(sock, {})
            username = client_info.get("username")

        if not username:
            self.send_json(sock, {"action": "error", "message": "Must be logged in to create a room."})
            return

        room_name = packet.get("room_name", "").strip()
        success, msg = database.create_room(room_name, created_by=username, db_path=self.db_path)

        if success:
            self.log("ROOM", f"Room '{room_name}' created by '{username}'")
            # Broadcast updated room list to all clients so everyone's UI refreshes live
            all_rooms = database.get_all_rooms(db_path=self.db_path)
            self.broadcast_to_all({
                "action": "rooms_list",
                "rooms": all_rooms,
                "notice": f"New room '{room_name}' was created by {username}!"
            })
        else:
            self.send_json(sock, {
                "action": "create_room_response",
                "status": "error",
                "message": msg
            })

    def handle_join_room(self, sock: socket.socket, packet: dict):
        with self.lock:
            client_info = self.clients.get(sock, {})
            username = client_info.get("username")
            prev_room = client_info.get("current_room")

        if not username:
            self.send_json(sock, {"action": "error", "message": "Must be logged in to join a room."})
            return

        new_room = packet.get("room_name", "").strip()
        if not new_room:
            self.send_json(sock, {"action": "error", "message": "Invalid room name."})
            return

        # If already in the requested room, do nothing
        if prev_room == new_room:
            return

        # Step 1: Leave previous room if any
        if prev_room:
            self._remove_from_room(sock, prev_room, notify=True)

        # Step 2: Add to new room
        with self.lock:
            if sock in self.clients:
                self.clients[sock]["current_room"] = new_room

            if new_room not in self.rooms:
                self.rooms[new_room] = set()
            self.rooms[new_room].add(sock)

            # Gather active usernames in new room
            active_users = [
                self.clients[s]["username"]
                for s in self.rooms[new_room]
                if s in self.clients and self.clients[s]["username"]
            ]

        # Step 3: Fetch message history from database
        history = database.get_room_history(new_room, limit=50, db_path=self.db_path)

        timestamp = datetime.now().strftime("[%H:%M]")
        self.log("ROOM", f"'{username}' joined room '{new_room}'")

        # Step 4: Send success response with history and active users to the joining client
        self.send_json(sock, {
            "action": "join_room_response",
            "status": "ok",
            "room_name": new_room,
            "history": history,
            "users": active_users
        })

        # Step 5: Broadcast arrival notification and updated user list to everyone else in new_room
        self.broadcast_to_room(new_room, {
            "action": "user_joined",
            "room_name": new_room,
            "username": username,
            "timestamp": timestamp,
            "users": active_users
        }, exclude_sock=sock)

    def handle_leave_room(self, sock: socket.socket):
        with self.lock:
            client_info = self.clients.get(sock, {})
            room = client_info.get("current_room")

        if room:
            self._remove_from_room(sock, room, notify=True)

    def _remove_from_room(self, sock: socket.socket, room_name: str, notify: bool = True):
        """Removes a socket from a room and notifies room participants."""
        username = None
        remaining_users = []

        with self.lock:
            if sock in self.clients:
                username = self.clients[sock]["username"]
                self.clients[sock]["current_room"] = None

            if room_name in self.rooms:
                self.rooms[room_name].discard(sock)
                remaining_users = [
                    self.clients[s]["username"]
                    for s in self.rooms[room_name]
                    if s in self.clients and self.clients[s]["username"]
                ]
                if not self.rooms[room_name]:
                    del self.rooms[room_name]

        if notify and username:
            timestamp = datetime.now().strftime("[%H:%M]")
            self.log("ROOM", f"'{username}' left room '{room_name}'")
            self.broadcast_to_room(room_name, {
                "action": "user_left",
                "room_name": room_name,
                "username": username,
                "timestamp": timestamp,
                "users": remaining_users
            })

    def handle_send_message(self, sock: socket.socket, packet: dict):
        with self.lock:
            client_info = self.clients.get(sock, {})
            username = client_info.get("username")
            current_room = client_info.get("current_room")

        if not username:
            self.send_json(sock, {"action": "error", "message": "Must be logged in to send messages."})
            return

        room_name = packet.get("room_name", "").strip()
        message_text = packet.get("message", "").strip()

        if not message_text:
            return

        if not room_name or room_name != current_room:
            self.send_json(sock, {
                "action": "error",
                "message": "You must join this room before sending messages."
            })
            return

        timestamp = datetime.now().strftime("[%H:%M]")

        # Persist message to SQLite database
        database.save_message(room_name, username, message_text, timestamp, db_path=self.db_path)
        self.log("CHAT", f"[{room_name}] {username}: {message_text}")

        # Broadcast real-time message to ALL participants in this room
        out_packet = {
            "action": "new_message",
            "room_name": room_name,
            "username": username,
            "message": message_text,
            "timestamp": timestamp
        }
        self.broadcast_to_room(room_name, out_packet)

    def cleanup_client(self, sock: socket.socket):
        """Cleans up client state when connection is closed."""
        username = None
        current_room = None
        remaining_users = []

        with self.lock:
            if sock in self.clients:
                username = self.clients[sock]["username"]
                current_room = self.clients[sock]["current_room"]
                del self.clients[sock]

            if current_room and current_room in self.rooms:
                self.rooms[current_room].discard(sock)
                remaining_users = [
                    self.clients[s]["username"]
                    for s in self.rooms[current_room]
                    if s in self.clients and self.clients[s]["username"]
                ]
                if not self.rooms[current_room]:
                    del self.rooms[current_room]

        if current_room and username:
            timestamp = datetime.now().strftime("[%H:%M]")
            self.log("ROOM", f"'{username}' left room '{current_room}'")
            self.broadcast_to_room(current_room, {
                "action": "user_left",
                "room_name": current_room,
                "username": username,
                "timestamp": timestamp,
                "users": remaining_users
            })

        if username:
            self.log("CONN", f"User '{username}' disconnected.")

        try:
            sock.close()
        except Exception:
            pass


def main():
    host = DEFAULT_HOST
    port = DEFAULT_PORT

    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"Invalid port: {sys.argv[2]}, using default {DEFAULT_PORT}")

    server = ChatServer(host=host, port=port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[INFO] KeyboardInterrupt received. Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
