# GTA 5 AFK & Automation Bot

This program automates actions in GTA 5 (Grand Theft Auto V) on Windows. It includes an AFK movement mode, an automated Fishing mode, and an on-screen overlay menu.

## Features

- **In-Game Overlay Menu**: Press `F9` to toggle a transparent status menu on top of the game.
- **AFK Movement Mode**: Randomly presses keys (W, A, S, D, Space) to simulate activity and prevent inactivity kicks. Toggle with `F8`.
- **AFK Fishing Mode**: Automatically casts the fishing rod (pressing '1') and uses screen detection to click when the blue progress bar indicates a catch. Toggle with `F7`.
- **Command Listener**: Reads commands from `commands.txt` to execute specific actions programmatically.
- **Exit**: Press `F10` to close the bot safely.

## Requirements

- Windows OS
- Python 3.x

## Installation & Setup

1.  **Install Python**: Download and install Python from [python.org](https://www.python.org/downloads/). Ensure you check "Add Python to PATH" during installation.
2.  **Open Command Prompt**: Press `Win + R`, type `cmd`, and press Enter.
3.  **Navigate to this folder**: Use `cd` to go to the folder where you extracted these files.
    ```bash
    cd path\to\gta5_bot
    ```
4.  **Install Dependencies**: Run the following command:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

**IMPORTANT:**
1. You must run this script or the executable as **Administrator** for the inputs to register in GTA 5.
2. For the overlay menu to be visible, GTA 5 must be set to **"Windowed Borderless"** or **"Windowed"** mode in the game's Graphics settings. Exclusive Fullscreen mode will block the overlay.

### Running as a Script

To run the bot directly:

1. Open Command Prompt as Administrator.
2. Run the script:
   ```bash
   python main.py
   ```

### Creating an Executable (.exe)

To compile the script into a standalone `.exe` file that you can run without opening a terminal:

1.  Ensure you have installed the requirements (specifically `pyinstaller`).
2.  Run the following command:
    ```bash
    pyinstaller --onefile --noconsole main.py
    ```
    *(Note: Using `--noconsole` is now recommended since the GUI overlay handles state display.)*
3.  The `main.exe` file will be created in the `dist` folder. You can move this file anywhere and run it (Right-click -> Run as Administrator).

## How to Control (Hotkeys)

- **F7**: Toggle AFK Fishing Mode ON/OFF.
- **F8**: Toggle AFK Movement Mode ON/OFF.
- **F9**: Toggle Overlay Menu visibility ON/OFF.
- **F10**: Stop and Exit the bot.

## Note on Fishing Mode
The fishing bot captures a specific region of the screen and looks for a specific blue color. Depending on your monitor resolution and the specific server's fishing UI, you may need to open `main.py` and adjust the `monitor` coordinates or the HSV color range (`lower_blue`, `upper_blue`) inside the `fish_loop` function.
