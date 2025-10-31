# AFK Mouse

AFK Mouse keeps your machine awake by nudging the cursor at a configurable interval. A minimal Tkinter GUI lets you toggle movement, tweak how often the cursor moves, and quit cleanly. A global `F6` hotkey is also provided so you can pause/resume without switching back to the window.

## Features
- Randomized cursor hops that stay away from screen edges to avoid triggering fail-safe aborts.
- Adjustable move interval (1–30 seconds) from the GUI slider.
- Global `F6` hotkey to toggle without focusing the window.
- Graceful shutdown that stops the worker thread and hotkey listener.

## Requirements
- Python 3.9 or newer.
- GUI support (Tkinter is included with most Python distributions).
- [PyAutoGUI](https://pyautogui.readthedocs.io/) and [pynput](https://pypi.org/project/pynput/).

Install dependencies into a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Platform notes
- **macOS:** Grant accessibility permissions for both the terminal and the bundled app so PyAutoGUI can control the cursor. The required Quartz bridge (`pyobjc-framework-Quartz`) is listed in `requirements.txt`.
- **macOS bundle:** The first time you open `AFK Mouse.app`, macOS will ask for *Input Monitoring* access so the F6 global hotkey can work. Approve the prompt or enable it under *System Settings → Privacy & Security → Input Monitoring*.
- **Windows:** No extra system packages are required. If you bundle with PyInstaller, replace the icon path or use `--icon` with an `.ico` file.
- **Linux (X11):** Ensure `python3-xlib` and an X11 session are available. On Wayland, global hotkeys may be blocked; the app falls back to GUI controls if the listener cannot start.

## Usage

```bash
python main.py
```

Controls:
- **Start / Stop buttons:** begin or pause cursor movement.
- **F6:** toggle start/stop from anywhere.
- **Interval slider:** choose how often the cursor should move.
- **Quit:** stop the background worker and close the app.

### Running from source
Run `python main.py` as shown above. The window title displays the current state; the status label also updates when the global hotkey is pressed.

### Building a standalone app (optional)
Install PyInstaller alongside the requirements, then build a distributable bundle:

```bash
pip install pyinstaller
pyinstaller --windowed --name "AFK Mouse" --icon afk-mouse.icns main.py
```
