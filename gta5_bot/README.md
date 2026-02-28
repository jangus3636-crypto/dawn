# GTA 5 AFK & Automation Bot

This program automates actions in GTA 5 (Grand Theft Auto V) on Windows. It includes an AFK mode to prevent being kicked for inactivity and can execute custom commands from a text file.

## Features

- **Mining Mode**: Automatically holds the 'E' key for 10 seconds to mine resources continuously. Toggle with `F8`.
- **AFK Mode**: Randomly presses keys (W, A, S, D, Space) to simulate activity. Toggle with `F9`.
- **Command Listener**: Reads commands from `commands.txt` to execute specific actions.
- **Exit**: Press `F10` to close the bot.

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

**IMPORTANT**: You must run this script or the executable as **Administrator** for the inputs to register in GTA 5.

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
    pyinstaller --onefile main.py
    ```
3.  The `main.exe` file will be created in the `dist` folder. You can move this file anywhere and run it (Right-click -> Run as Administrator).

## How to Control

- **F8**: Toggle Mining Mode ON/OFF.
- **F9**: Toggle AFK Mode ON/OFF.
- **F10**: Stop the bot.
- **commands.txt**: Create a file named `commands.txt` in the same folder as the script/exe. Write commands in it to control the bot remotely or via another script.
    - Supported commands:
        - `walk_forward [duration]`
        - `walk_back [duration]`
        - `left [duration]`
        - `right [duration]`
        - `jump`
        - `shoot`
        - `afk_on`
        - `afk_off`
        - `mine_on`
        - `mine_off`

**Note**: The game (GTA 5) must be the active window for the keystrokes to register.
