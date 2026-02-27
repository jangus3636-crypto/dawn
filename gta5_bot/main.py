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
        self.attributes('-alpha', 0.85) # 85% opacity

        # Dark purple and black theme
        self.bg_color = '#0a0a0a' # Very dark grey/black
        self.fg_color = '#b366ff' # Neon purple
        self.config(bg=self.bg_color)

        # Position in top left
        self.geometry("+20+20")

        self.status_label = tk.Label(
            self,
            text="Loading...",
            font=("Consolas", 12, "bold"),
            fg=self.fg_color,
            bg=self.bg_color,
            justify=tk.LEFT,
            padx=15,
            pady=15
        )
        self.status_label.pack()

        self.update_status_text()

        # Start hidden
        self.withdraw()

        # Schedule periodic checks for state updates and exit condition
        self.check_state()

    def update_status_text(self):
        text = "GTA 5 Bot Menu\n"
        text += "="*20 + "\n"
        text += f"AFK Movement: {'[ON]' if is_afk_mode else '[OFF]'} (F8)\n"
        text += f"AFK Fishing:  {'[ON]' if is_fishing_mode else '[OFF]'} (F7)\n"
        text += "="*20 + "\n"
        text += "Hide/Show Menu: (F9)\n"
        text += "Exit Bot:       (F10)"
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
    Automates fishing minigame:
    1. Casts line with '1'
    2. Detects the white hook and the cyan/blue wave zone.
    3. Holds left click if hook is to the right of the wave center.
    4. Releases left click if hook is to the left of the wave center.
    """
    global is_fishing_mode, is_running

    print("Fishing Mode Thread Started.")

    # We need to maintain state of mouse button to avoid spamming click commands
    mouse_held = False

    with mss.mss() as sct:
        # Define screen region to capture (approximate lower center where the bar is)
        # You may need to tune this to your specific resolution (e.g., 1920x1080)
        monitor = {"top": 600, "left": 400, "width": 1120, "height": 300}

        # Color definitions for detection (HSV space)
        # Cyan/Blue wave
        lower_cyan = np.array([80, 100, 100])
        upper_cyan = np.array([100, 255, 255])

        # White Hook
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])

        while is_running:
            if not is_fishing_mode:
                if mouse_held:
                    with command_lock:
                        try: pydirectinput.mouseUp()
                        except: pass
                    mouse_held = False
                time.sleep(1)
                continue

            try:
                # 1. Cast line
                with command_lock:
                    pydirectinput.press('1')

                time.sleep(2) # Wait for cast animation
                print("Fishing: Line cast. Entering tracking loop...")

                # Assume a single minigame session doesn't last longer than 60 seconds
                timeout = time.time() + 60

                while time.time() < timeout and is_fishing_mode and is_running:
                    img = np.array(sct.grab(monitor))
                    hsv = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    hsv = cv2.cvtColor(hsv, cv2.COLOR_BGR2HSV)

                    # Create masks
                    mask_cyan = cv2.inRange(hsv, lower_cyan, upper_cyan)
                    mask_white = cv2.inRange(hsv, lower_white, upper_white)

                    # Find contours to locate the objects
                    contours_cyan, _ = cv2.findContours(mask_cyan, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    contours_white, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    cyan_x_center = None
                    hook_x = None

                    # Find largest cyan contour (the wave)
                    if contours_cyan:
                        c_max = max(contours_cyan, key=cv2.contourArea)
                        if cv2.contourArea(c_max) > 100: # noise filter
                            x, y, w, h = cv2.boundingRect(c_max)
                            cyan_x_center = x + (w // 2)

                    # Find white hook
                    # The hook is small, so we look for a smaller area contour
                    if contours_white:
                        for c in contours_white:
                            if 50 < cv2.contourArea(c) < 1000:
                                x, y, w, h = cv2.boundingRect(c)
                                hook_x = x + (w // 2)
                                break # Found a plausible hook

                    # Logic: Keep hook in the cyan area
                    if cyan_x_center is not None and hook_x is not None:
                        # If hook is to the right of the wave's center, we need to move wave right (hold click)
                        if hook_x > cyan_x_center + 10:
                            if not mouse_held:
                                with command_lock:
                                    pydirectinput.mouseDown()
                                mouse_held = True

                        # If hook is to the left, let wave move left (release click)
                        elif hook_x < cyan_x_center - 10:
                            if mouse_held:
                                with command_lock:
                                    pydirectinput.mouseUp()
                                mouse_held = False
                    else:
                        # If we lose track of objects, release mouse to be safe
                        if mouse_held:
                            with command_lock:
                                pydirectinput.mouseUp()
                            mouse_held = False

                    time.sleep(0.02) # High frequency polling for smooth tracking

                # End of fishing session attempt
                if mouse_held:
                    with command_lock:
                        pydirectinput.mouseUp()
                    mouse_held = False

                time.sleep(3) # Wait before next cast

            except Exception as e:
                 print(f"Fishing simulation/error: {e}")
                 if mouse_held:
                    try: pydirectinput.mouseUp()
                    except: pass
                    mouse_held = False
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
