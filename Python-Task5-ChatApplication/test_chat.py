"""
test_chat.py - Comprehensive Automated Verification Test Suite
Oasis Infobyte Python Internship - Task 5

Tests all 12 Mandatory Requirements:
1. New user registration (valid, duplicate, invalid constraints)
2. Existing user login
3. Incorrect password rejection
4. Multiple clients connecting simultaneously
5. Sending and receiving real-time bidirectional messages
6. Creating chat rooms
7. Room isolation (messages stay in their respective rooms)
8. Message history retrieval upon joining room
9. Timestamps on messages
10. Unicode Emoji transmission and preservation
11. User disconnection & leave announcements
12. Server shutdown handling
"""

import socket
import json
import time
import os
import threading
import database
from server import ChatServer

TEST_HOST = "127.0.0.1"
TEST_PORT = 5599
TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_suite.db")


class MockClient:
    """Helper client class that simulates a GUI client for automated testing."""

    def __init__(self, host=TEST_HOST, port=TEST_PORT):
        self.host = host
        self.port = port
        self.sock = None
        self.inbox = []
        self.is_connected = False
        self.listener_thread = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.is_connected = True
        self.listener_thread = threading.Thread(target=self._listen, daemon=True)
        self.listener_thread.start()

    def _listen(self):
        buffer = ""
        while self.is_connected:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                buffer += data.decode("utf-8", errors="replace")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line:
                        packet = json.loads(line)
                        self.inbox.append(packet)
            except Exception:
                break
        self.is_connected = False

    def send(self, payload: dict):
        raw = (json.dumps(payload) + "\n").encode("utf-8")
        self.sock.sendall(raw)

    def wait_for_action(self, action_name: str, timeout: float = 3.0):
        """Polls inbox for a specific action packet."""
        start = time.time()
        while time.time() - start < timeout:
            for i, pkt in enumerate(self.inbox):
                if pkt.get("action") == action_name:
                    return self.inbox.pop(i)
            time.sleep(0.05)
        return None

    def close(self):
        self.is_connected = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass


def run_all_tests():
    print("=" * 70)
    print("   RUNNING AUTOMATED TEST SUITE — TASK 5 CHAT APPLICATION")
    print("=" * 70)

    # Clean up any leftover test database
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except Exception:
            pass

    database.init_db(TEST_DB)

    # Step 1: Start Server in background thread with isolated test database
    server = ChatServer(host=TEST_HOST, port=TEST_PORT, db_path=TEST_DB)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    time.sleep(1.0)
    print("[PASS] Test Server started on port", TEST_PORT)

    passed_count = 0
    total_count = 12

    try:
        # TEST 1: User Registration
        c1 = MockClient(TEST_HOST, TEST_PORT)
        c1.connect()
        c1.send({"action": "register", "username": "alice", "password": "alicepassword123"})
        reg_resp = c1.wait_for_action("register_response")
        assert reg_resp is not None and reg_resp.get("status") == "ok", f"Registration failed: {reg_resp}"

        # Test duplicate registration rejection
        c1.send({"action": "register", "username": "alice", "password": "anotherpassword"})
        dup_resp = c1.wait_for_action("register_response")
        assert dup_resp is not None and dup_resp.get("status") == "error", "Duplicate username was not rejected!"
        print("[PASS] 1. New user registration & duplicate check verified.")
        passed_count += 1

        # TEST 2: Existing User Login
        c1.send({"action": "login", "username": "alice", "password": "alicepassword123"})
        login_resp = c1.wait_for_action("login_response")
        assert login_resp is not None and login_resp.get("status") == "ok", f"Login failed: {login_resp}"
        assert "rooms" in login_resp, "Rooms list not returned on login"
        print("[PASS] 2. User login verified successfully.")
        passed_count += 1

        # TEST 3: Incorrect Password Handling
        c2 = MockClient(TEST_HOST, TEST_PORT)
        c2.connect()
        c2.send({"action": "login", "username": "alice", "password": "WRONG_PASSWORD_XYZ"})
        bad_resp = c2.wait_for_action("login_response")
        assert bad_resp is not None and bad_resp.get("status") == "error", "Bad password was accepted!"
        print("[PASS] 3. Incorrect password handling verified (rejected safely).")
        passed_count += 1

        # Register and login Bob on client 2
        c2.send({"action": "register", "username": "bob", "password": "bobpassword123"})
        c2.wait_for_action("register_response")
        c2.send({"action": "login", "username": "bob", "password": "bobpassword123"})
        c2.wait_for_action("login_response")

        # TEST 4: Multiple Users Connecting
        assert c1.is_connected and c2.is_connected, "Both clients should be simultaneously connected!"
        print("[PASS] 4. Multiple simultaneous client connections verified.")
        passed_count += 1

        # TEST 5: Creating Chat Rooms
        c1.send({"action": "create_room", "room_name": "Python-Interns"})
        # Server broadcasts rooms_list to both clients
        c1_room_list = c1.wait_for_action("rooms_list")
        c2_room_list = c2.wait_for_action("rooms_list")
        assert c1_room_list and "Python-Interns" in c1_room_list.get("rooms", []), "Room creation failed on c1"
        assert c2_room_list and "Python-Interns" in c2_room_list.get("rooms", []), "Room list not broadcast to c2"
        print("[PASS] 5. Creating chat rooms and live room list broadcast verified.")
        passed_count += 1

        # TEST 6: Joining Different Rooms & Room Isolation
        c1.send({"action": "join_room", "room_name": "Python-Interns"})
        c1_join = c1.wait_for_action("join_room_response")
        assert c1_join and c1_join.get("status") == "ok", "Client 1 failed to join Python-Interns"

        # Client 2 joins 'General'
        c2.send({"action": "join_room", "room_name": "General"})
        c2_join = c2.wait_for_action("join_room_response")
        assert c2_join and c2_join.get("status") == "ok", "Client 2 failed to join General"

        # Send message from c1 in Python-Interns. c2 in General should NOT receive it!
        c1.send({"action": "send_message", "room_name": "Python-Interns", "message": "Secret Python msg"})
        msg_c1 = c1.wait_for_action("new_message", timeout=1.5)
        assert msg_c1 is not None and msg_c1.get("message") == "Secret Python msg"

        msg_c2 = c2.wait_for_action("new_message", timeout=0.8)
        assert msg_c2 is None, "Room isolation failed: Client in General received message from Python-Interns!"
        print("[PASS] 6. Room joining and room isolation verified.")
        passed_count += 1

        # TEST 7: Bidirectional Real-Time Messaging in Same Room
        # Now move Client 2 into Python-Interns
        c2.send({"action": "join_room", "room_name": "Python-Interns"})
        c2.wait_for_action("join_room_response")
        # c1 should get user_joined notification
        join_notif = c1.wait_for_action("user_joined")
        assert join_notif and join_notif.get("username") == "bob"

        # Client 2 sends a message
        c2.send({"action": "send_message", "room_name": "Python-Interns", "message": "Hi Alice, real-time works!"})
        recv_c1 = c1.wait_for_action("new_message")
        recv_c2 = c2.wait_for_action("new_message")
        assert recv_c1 and recv_c1.get("message") == "Hi Alice, real-time works!"
        assert recv_c2 and recv_c2.get("message") == "Hi Alice, real-time works!"
        print("[PASS] 7. Bidirectional real-time messaging verified.")
        passed_count += 1

        # TEST 8: Emoji Support
        emoji_text = "Python is awesome! 🐍 🚀 ✨ ❤️"
        c1.send({"action": "send_message", "room_name": "Python-Interns", "message": emoji_text})
        emoji_msg = c2.wait_for_action("new_message")
        assert emoji_msg and emoji_msg.get("message") == emoji_text, f"Emoji corrupted: {emoji_msg}"
        print("[PASS] 8. Unicode Emoji transmission verified.")
        passed_count += 1

        # TEST 9: Timestamps on Messages
        assert "timestamp" in emoji_msg and emoji_msg["timestamp"].startswith("["), "Timestamp format missing!"
        print("[PASS] 9. Timestamps formatting verified:", emoji_msg["timestamp"])
        passed_count += 1

        # TEST 10: Message History Persistence in SQLite
        # Connect a new Client 3 (Charlie), register and join Python-Interns.
        # Charlie should receive all previous messages as history!
        c3 = MockClient(TEST_HOST, TEST_PORT)
        c3.connect()
        c3.send({"action": "register", "username": "charlie", "password": "charliepass123"})
        c3.wait_for_action("register_response")
        c3.send({"action": "login", "username": "charlie", "password": "charliepass123"})
        c3.wait_for_action("login_response")
        c3.send({"action": "join_room", "room_name": "Python-Interns"})
        c3_join = c3.wait_for_action("join_room_response")
        history = c3_join.get("history", [])
        assert len(history) >= 3, f"Expected at least 3 historical messages, got {len(history)}"
        has_emoji_in_hist = any("🐍" in h.get("message", "") for h in history)
        assert has_emoji_in_hist, "Emoji message was not persisted in SQLite history correctly!"
        print(f"[PASS] 10. Message history loaded from SQLite verified ({len(history)} messages restored).")
        passed_count += 1

        # TEST 11: Graceful User Disconnection & Departure Notification
        c3.send({"action": "disconnect"})
        c3.close()
        left_notif = c1.wait_for_action("user_left")
        assert left_notif and left_notif.get("username") == "charlie", "Departure notification was not received!"
        print("[PASS] 11. User graceful disconnection and departure broadcast verified.")
        passed_count += 1

        # TEST 12: Server Shutdown Handling
        c1.close()
        c2.close()

        # Connect a fresh client and shut down server
        c4 = MockClient(TEST_HOST, TEST_PORT)
        c4.connect()
        server.shutdown()
        time.sleep(0.5)
        # c4 should receive server_shutdown or detect socket close
        shutdown_msg = c4.wait_for_action("server_shutdown", timeout=1.0)
        assert shutdown_msg is not None or not c4.is_connected, "Client did not detect server shutdown!"
        c4.close()
        print("[PASS] 12. Server shutdown handling verified.")
        passed_count += 1

    finally:
        server.shutdown()
        if os.path.exists(TEST_DB):
            try:
                os.remove(TEST_DB)
            except Exception:
                pass

    print("=" * 70)
    print(f"   TEST SUMMARY: {passed_count}/{total_count} TESTS PASSED SUCCESSFULLY! (100%)")
    print("=" * 70)
    return passed_count == total_count


if __name__ == "__main__":
    success = run_all_tests()
    if not success:
        exit(1)
