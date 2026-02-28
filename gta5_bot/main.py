import time
import random
import os
import threading

# These imports are wrapped in try-except because pydirectinput and keyboard might
# not be installed or work correctly in non-Windows/CI environments during initial setup.
# However, for the final Windows exe, they are required.
try:
    import pydirectinput
    import keyboard
except ImportError:
    print("Warning: One or more libraries (pydirectinput, keyboard) not found.")
    print("This script is intended to run on Windows with these libraries installed.")

# Global flag to control the bot
is_running = False
is_afk_mode = False
is_mining_mode = False

COMMAND_FILE = "commands.txt"
command_lock = threading.Lock()

def mining_loop():
    """
    Holds the 'e' key for 10.1 seconds to mine, then repeats.
    """
    global is_mining_mode
    print("Mining Mode Started. Press F8 to stop.")

    while is_running:
        if not is_mining_mode:
            time.sleep(1)
            continue

        print("Mining Action: Holding 'e' for 10.1s")

        with command_lock:
            try:
                pydirectinput.keyDown('e')
                time.sleep(10.1)
                pydirectinput.keyUp('e')
            except NameError:
                print("[Simulation] Holding 'e' for 10.1s")
                time.sleep(10.1)

        # Small pause between mining actions
        time.sleep(0.5)

def afk_loop():
    """
    Performs random movements to prevent being kicked for inactivity.
    """
    global is_afk_mode
    print("AFK Mode Started. Press F9 to stop.")

    keys = ['w', 'a', 's', 'd', 'space']

    while is_running:
        if not is_afk_mode:
            time.sleep(1)
            continue

        key = random.choice(keys)
        duration = random.uniform(0.1, 1.0)

        print(f"AFK Action: Pressing {key} for {duration:.2f}s")

        # Acquire lock to prevent conflict with manual commands
        with command_lock:
            try:
                pydirectinput.keyDown(key)
                time.sleep(duration)
                pydirectinput.keyUp(key)
            except NameError:
                 print(f"[Simulation] Pressing {key} for {duration:.2f}s")

        # Random interval between actions
        time.sleep(random.uniform(1, 5))

def process_commands_loop():
    """
    Continuously reads commands from a text file and executes them in a separate thread.
    """
    global is_afk_mode, is_running, is_mining_mode

    print(f"Command Processor Started. Monitoring {COMMAND_FILE}...")

    # Create the command file if it doesn't exist
    if not os.path.exists(COMMAND_FILE):
        with open(COMMAND_FILE, 'w') as f:
            pass

    while is_running:
        if os.path.exists(COMMAND_FILE):
            try:
                with open(COMMAND_FILE, 'r') as f:
                    lines = f.readlines()

                # Only clear if there were lines
                if lines:
                    with open(COMMAND_FILE, 'w') as f:
                        pass

                for line in lines:
                    command = line.strip().lower()
                    if not command:
                        continue

                    print(f"Executing command: {command}")

                    try:
                        parts = command.split()
                        cmd = parts[0]

                        # Use lock for game inputs
                        with command_lock:
                            if cmd == "walk_forward":
                                duration = float(parts[1]) if len(parts) > 1 else 1.0
                                pydirectinput.keyDown('w')
                                time.sleep(duration)
                                pydirectinput.keyUp('w')

                            elif cmd == "walk_back":
                                duration = float(parts[1]) if len(parts) > 1 else 1.0
                                pydirectinput.keyDown('s')
                                time.sleep(duration)
                                pydirectinput.keyUp('s')

                            elif cmd == "left":
                                duration = float(parts[1]) if len(parts) > 1 else 0.5
                                pydirectinput.keyDown('a')
                                time.sleep(duration)
                                pydirectinput.keyUp('a')

                            elif cmd == "right":
                                duration = float(parts[1]) if len(parts) > 1 else 0.5
                                pydirectinput.keyDown('d')
                                time.sleep(duration)
                                pydirectinput.keyUp('d')

                            elif cmd == "jump":
                                pydirectinput.press('space')

                            elif cmd == "shoot":
                                pydirectinput.mouseDown()
                                time.sleep(0.5)
                                pydirectinput.mouseUp()

                            elif cmd == "afk_on":
                                if not is_afk_mode:
                                    is_afk_mode = True
                                    print("AFK Mode Toggled ON via command")

                            elif cmd == "afk_off":
                                if is_afk_mode:
                                    is_afk_mode = False
                                    print("AFK Mode Toggled OFF via command")

                            elif cmd == "mine_on":
                                if not is_mining_mode:
                                    is_mining_mode = True
                                    print("Mining Mode Toggled ON via command")

                            elif cmd == "mine_off":
                                if is_mining_mode:
                                    is_mining_mode = False
                                    print("Mining Mode Toggled OFF via command")

                            else:
                                print(f"Unknown command: {cmd}")

                    except Exception as e:
                        print(f"Error executing command '{command}': {e}")
            except Exception as e:
                print(f"Error reading command file: {e}")

        time.sleep(1)

def main():
    global is_running, is_afk_mode, is_mining_mode
    is_running = True

    print("GTA 5 Bot Started.")
    print("Press F8 to toggle Mining Mode manually.")
    print("Press F9 to toggle AFK Mode manually.")
    print("Press F10 to Exit.")

    # Start Command Processor Thread
    cmd_thread = threading.Thread(target=process_commands_loop)
    cmd_thread.daemon = True
    cmd_thread.start()

    # Start AFK Thread (it will sleep when is_afk_mode is False)
    afk_thread = threading.Thread(target=afk_loop)
    afk_thread.daemon = True
    afk_thread.start()

    # Start Mining Thread
    mining_thread = threading.Thread(target=mining_loop)
    mining_thread.daemon = True
    mining_thread.start()

    try:
        while is_running:
            # Check for hotkeys
            try:
                if keyboard.is_pressed('F10'):
                    print("Exiting...")
                    is_running = False
                    is_afk_mode = False
                    is_mining_mode = False
                    break

                if keyboard.is_pressed('F8'):
                    if is_mining_mode:
                        is_mining_mode = False
                        print("Mining Mode Toggled OFF")
                    else:
                        is_mining_mode = True
                        print("Mining Mode Toggled ON")
                    time.sleep(0.5) # Debounce

                if keyboard.is_pressed('F9'):
                    if is_afk_mode:
                        is_afk_mode = False
                        print("AFK Mode Toggled OFF")
                    else:
                        is_afk_mode = True
                        print("AFK Mode Toggled ON")
                    time.sleep(0.5) # Debounce
            except NameError:
                pass # Keyboard library not loaded
            except Exception as e:
                print(f"Keyboard error: {e}")

            time.sleep(0.1) # Short sleep to prevent high CPU usage

    except KeyboardInterrupt:
        print("Bot stopped by user.")
        is_running = False

if __name__ == "__main__":
    main()
