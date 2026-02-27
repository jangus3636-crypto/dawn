import time
import random
import os
import threading
import tkinter as tk
import numpy as np
import cv2
import mss

try:
    import pydirectinput
    import keyboard
except ImportError:
    print("Warning: One or more libraries (pydirectinput, keyboard) not found.")
    print("This script is intended to run on Windows with these libraries installed.")

# Global state
is_running = True
is_afk_mode = False
is_fishing_mode = False
overlay_visible = False

COMMAND_FILE = "commands.txt"
command_lock = threading.Lock()

# --- GUI Application ---
class BotOverlay(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GTA 5 Bot Overlay")

        # Make window stay on top, transparent, and borderless
        self.attributes('-topmost', True)
        self.overrideredirect(True)
        self.attributes('-alpha', 0.8) # 80% opacity
        self.config(bg='black')

        # Position in top left
        self.geometry("+20+20")

        self.status_label = tk.Label(
            self,
            text="Loading...",
            font=("Consolas", 12, "bold"),
            fg="#00FF00", # Matrix green
            bg="black",
            justify=tk.LEFT,
            padx=10,
            pady=10
        )
        self.status_label.pack()

        self.update_status_text()

        # Start hidden
        self.withdraw()

        # Schedule periodic checks for state updates and exit condition
        self.check_state()

    def update_status_text(self):
        text = "GTA 5 Bot Menu\n"
        text += "-"*20 + "\n"
        text += f"AFK Movement: {'ON' if is_afk_mode else 'OFF'} [F8]\n"
        text += f"AFK Fishing: {'ON' if is_fishing_mode else 'OFF'} [F7]\n"
        text += "-"*20 + "\n"
        text += "Hide/Show Menu: [F9]\n"
        text += "Exit Bot: [F10]"
        self.status_label.config(text=text)

    def check_state(self):
        global is_running, overlay_visible

        if not is_running:
            self.destroy()
            return

        # Update text dynamically if states changed
        self.update_status_text()

        # Handle visibility
        if overlay_visible and self.state() == 'withdrawn':
            self.deiconify()
        elif not overlay_visible and self.state() == 'normal':
            self.withdraw()

        # Check again in 100ms
        self.after(100, self.check_state)


# --- Bot Logic Threads ---

def fish_loop():
    """
    Automates fishing:
    1. Presses '1' to equip/cast rod.
    2. Uses mss and OpenCV to detect a specific blue color on the screen.
    3. Clicks when the color (fish/bobber moving to the blue bar) is detected.
    """
    global is_fishing_mode, is_running

    print("Fishing Mode Thread Started.")

    with mss.mss() as sct:
        # Define screen region to capture
        monitor = {"top": 400, "left": 700, "width": 500, "height": 300}

        # Define HSV color range for the "blue bar"
        lower_blue = np.array([100, 150, 0])
        upper_blue = np.array([140, 255, 255])

        while is_running:
            if not is_fishing_mode:
                time.sleep(1)
                continue

            try:
                # 1. Cast line (Requires lock only for the input)
                with command_lock:
                    pydirectinput.press('1')

                time.sleep(2) # Wait for animation outside of lock
                print("Fishing: Line cast. Waiting for bite...")

                # 2. Watch for the blue color for up to 30 seconds
                timeout = time.time() + 30
                caught = False

                while time.time() < timeout and is_fishing_mode and is_running:
                    # Capture screen
                    img = np.array(sct.grab(monitor))

                    # Convert BGR to HSV
                    hsv = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    hsv = cv2.cvtColor(hsv, cv2.COLOR_BGR2HSV)

                    # Threshold the HSV image to get only blue colors
                    mask = cv2.inRange(hsv, lower_blue, upper_blue)

                    # Count blue pixels
                    blue_pixels = cv2.countNonZero(mask)

                    # If significant blue is detected, trigger the click
                    if blue_pixels > 50:
                        print("Fishing: Blue detected! Clicking...")
                        # 3. Reel in (Requires lock only for the input)
                        with command_lock:
                            pydirectinput.click()
                        time.sleep(1) # Prevent spam clicking
                        caught = True
                        break

                    time.sleep(0.05) # Loop delay

                if not caught and is_fishing_mode:
                    print("Fishing: Timeout, recasting...")

                time.sleep(3) # Wait before next cast

            except Exception as e:
                 print(f"Fishing simulation/error: {e}")
                 time.sleep(2)

def afk_loop():
    """
    Performs random movements to prevent being kicked for inactivity.
    """
    global is_afk_mode, is_running

    keys = ['w', 'a', 's', 'd', 'space']

    while is_running:
        if not is_afk_mode:
            time.sleep(1)
            continue

        key = random.choice(keys)
        duration = random.uniform(0.1, 1.0)

        with command_lock:
            try:
                pydirectinput.keyDown(key)
                time.sleep(duration)
                pydirectinput.keyUp(key)
            except NameError:
                 pass

        time.sleep(random.uniform(1, 5))

def process_commands_loop():
    global is_running

    while is_running:
        if os.path.exists(COMMAND_FILE):
            try:
                # Read contents safely
                with open(COMMAND_FILE, 'r') as f:
                    lines = f.readlines()

                if lines:
                    # Clear the file after reading
                    with open(COMMAND_FILE, 'w') as f:
                        pass

                for line in lines:
                    command = line.strip().lower()
                    if not command: continue

                    try:
                        parts = command.split()
                        cmd = parts[0]

                        with command_lock:
                            if cmd == "walk_forward":
                                pydirectinput.keyDown('w')
                                time.sleep(float(parts[1]) if len(parts)>1 else 1.0)
                                pydirectinput.keyUp('w')
                            elif cmd == "left":
                                pydirectinput.keyDown('a')
                                time.sleep(0.5)
                                pydirectinput.keyUp('a')
                            elif cmd == "shoot":
                                pydirectinput.click()

                    except Exception as e:
                        print(f"Error executing command: {e}")
            except Exception:
                pass

        time.sleep(1)

def keyboard_listener_loop():
    """
    Listens for hotkeys in a background thread and updates global state variables.
    The Tkinter main thread will pick up these changes safely via root.after().
    """
    global is_running, is_afk_mode, is_fishing_mode, overlay_visible

    while is_running:
        try:
            if keyboard.is_pressed('F10'):
                print("Exiting...")
                is_running = False
                break

            if keyboard.is_pressed('F9'):
                overlay_visible = not overlay_visible
                time.sleep(0.3) # Debounce

            if keyboard.is_pressed('F8'):
                is_afk_mode = not is_afk_mode
                print(f"AFK Movement Mode: {is_afk_mode}")
                time.sleep(0.3)

            if keyboard.is_pressed('F7'):
                is_fishing_mode = not is_fishing_mode
                print(f"AFK Fishing Mode: {is_fishing_mode}")
                time.sleep(0.3)

        except NameError:
            pass # Keyboard library not loaded (e.g. testing on Linux)
        except Exception as e:
            pass

        time.sleep(0.05)

def main():
    print("GTA 5 Bot Started.")

    # Start Background Threads
    t_cmd = threading.Thread(target=process_commands_loop)
    t_cmd.daemon = True
    t_cmd.start()

    t_afk = threading.Thread(target=afk_loop)
    t_afk.daemon = True
    t_afk.start()

    t_fish = threading.Thread(target=fish_loop)
    t_fish.daemon = True
    t_fish.start()

    t_keys = threading.Thread(target=keyboard_listener_loop)
    t_keys.daemon = True
    t_keys.start()

    # Start Tkinter Main Loop (Must run in the main thread)
    try:
        app = BotOverlay()
        app.mainloop()
    except Exception as e:
        print(f"GUI Error: {e}")
        global is_running
        is_running = False

if __name__ == "__main__":
    main()
