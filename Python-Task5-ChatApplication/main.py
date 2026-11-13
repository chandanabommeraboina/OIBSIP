"""
main.py - Unified Launcher for Oasis Infobyte Chat Application
Oasis Infobyte Python Internship - Task 5

Allows beginners to effortlessly:
1. Start the Chat Server
2. Launch the Tkinter GUI Client
3. Launch Server + 2 Clients concurrently for immediate live testing
4. Run the comprehensive Automated Test Suite
"""

import sys
import os
import subprocess
import time


def print_banner():
    print("""
======================================================================
  ⚡ OASIS INFOBYTE PYTHON INTERNSHIP — TASK 5: CHAT APPLICATION ⚡
======================================================================
  Multi-User Real-Time Chat System with Rooms, Authentication,
  SQLite History, Unicode Emojis, and Modern Tkinter GUI.
======================================================================
""")


def start_server():
    """Starts the Chat Server in the current process."""
    print("\n[+] Starting Chat Server on 127.0.0.1:5555 ...")
    import server
    server.main()


def start_client():
    """Launches the Tkinter GUI Chat Client in the current process."""
    print("\n[+] Launching GUI Chat Client ...")
    import client
    client.main()


def launch_demo():
    """
    Spawns the server and two client instances as separate processes.
    Perfect for demonstrating real-time bidirectional communication between users!
    """
    python_bin = sys.executable
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(script_dir, "server.py")
    client_script = os.path.join(script_dir, "client.py")

    print("\n[+] Launching Demo Environment (1 Server + 2 Clients)...")

    # Start Server process
    server_proc = subprocess.Popen([python_bin, server_script])
    print(f"  [✓] Server process started (PID: {server_proc.pid})")
    time.sleep(1.2)  # Give server time to bind socket

    # Start Client 1
    client1_proc = subprocess.Popen([python_bin, client_script])
    print(f"  [✓] Client 1 window launched (PID: {client1_proc.pid})")
    time.sleep(0.5)

    # Start Client 2
    client2_proc = subprocess.Popen([python_bin, client_script])
    print(f"  [✓] Client 2 window launched (PID: {client2_proc.pid})")

    print("\n[INFO] Both client windows are now open! You can log in with two different accounts to chat.")
    print("[INFO] Press Ctrl+C in this console when finished to shut down the demo server.")

    try:
        server_proc.wait()
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down demo processes...")
        server_proc.terminate()
        client1_proc.terminate()
        client2_proc.terminate()
        print("[✓] All demo processes stopped cleanly.")


def run_tests():
    """Executes the automated test script."""
    import test_chat
    test_chat.run_all_tests()


def interactive_menu():
    """Interactive CLI menu for beginners."""
    while True:
        print_banner()
        print("Please choose an option to run:")
        print("  [1] Start Chat Server")
        print("  [2] Launch Chat Client (GUI)")
        print("  [3] Launch Server + 2 Clients (Live Demo)")
        print("  [4] Run Automated Verification Tests")
        print("  [5] Exit")
        print("----------------------------------------------------------------------")

        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            start_server()
            break
        elif choice == "2":
            start_client()
            break
        elif choice == "3":
            launch_demo()
            break
        elif choice == "4":
            run_tests()
            input("\nPress Enter to return to menu...")
        elif choice == "5":
            print("\nExiting. Happy Coding! 👋")
            sys.exit(0)
        else:
            print("\n[!] Invalid option. Please choose between 1 and 5.\n")
            time.sleep(1)


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ("--server", "-s"):
            start_server()
        elif arg in ("--client", "-c"):
            start_client()
        elif arg in ("--demo", "-d"):
            launch_demo()
        elif arg in ("--test", "-t"):
            run_tests()
        else:
            print(f"Unknown argument: {arg}")
            print("Usage: python main.py [--server | --client | --demo | --test]")
            sys.exit(1)
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
