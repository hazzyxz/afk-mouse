"""AFK Mouse: Keep your machine awake with randomized cursor movement and a tiny GUI."""

import pyautogui
import time
import random
import math
import threading
import sys
import tkinter as tk
from tkinter import ttk
from pynput import keyboard as kb

# ---------------- Settings ----------------
pyautogui.PAUSE = 0               # no extra delay between pyautogui actions
# pyautogui.FAILSAFE = True       # keep default True for emergency abort (slam cursor to top-left)

SAFE_MARGIN = 5          # keep cursor away from exact edges to avoid fail-safe trips
MOVE_MIN = 60            # min pixels per hop
MOVE_MAX = 140           # max pixels per hop
MOVE_DURATION = 0.18     # seconds to animate each move
INTERVAL_SEC_DEFAULT = 5.0  # default seconds between moves
DEBOUNCE_SEC = 0.4
interval_sec = INTERVAL_SEC_DEFAULT  # current interval; updated by GUI slider

# ---------------- State ----------------
running = threading.Event()   # toggled by GUI or F6
alive = threading.Event()     # cleared on quit to stop threads
alive.set()
_last_toggle = 0.0

# ---------------- Helpers ----------------

def now():
    return time.monotonic()


def get_interval() -> float:
    return float(interval_sec)

def set_interval(sec: float) -> None:
    global interval_sec
    # clamp to sane bounds in case of programmatic calls
    if sec < 0.5:
        sec = 0.5
    elif sec > 60.0:
        sec = 60.0
    interval_sec = round(sec, 2)


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def random_target(x, y, screen_w, screen_h):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(MOVE_MIN, MAX_DIST := MOVE_MAX)
    nx = x + math.cos(angle) * dist
    ny = y + math.sin(angle) * dist
    nx = clamp(nx, SAFE_MARGIN, screen_w - 1 - SAFE_MARGIN)
    ny = clamp(ny, SAFE_MARGIN, screen_h - 1 - SAFE_MARGIN)
    return nx, ny


def move_once():
    try:
        screen_w, screen_h = pyautogui.size()  # re-read for display changes
        x, y = pyautogui.position()
        tx, ty = random_target(x, y, screen_w, screen_h)
        pyautogui.moveTo(tx, ty, duration=MOVE_DURATION)
    except pyautogui.FailSafeException:
        # If user slammed to (0,0), skip this move and keep running
        print("Fail-safe triggered. Move skipped.")
        time.sleep(0.2)
    except Exception as exc:  # pragma: no cover - defensive catch for platform quirks
        print(f"Cursor move failed: {exc}")
        time.sleep(0.5)


# ---------------- Worker Thread ----------------

def worker(status_cb=None):
    print("Mouse mover ready. F6 toggles start/stop. Close the window or press Quit to exit.")
    while alive.is_set():
        if running.is_set():
            move_once()
            # wait until next tick but remain responsive
            end = now() + get_interval()
            while running.is_set() and now() < end and alive.is_set():
                time.sleep(0.05)
        else:
            time.sleep(0.05)
    if status_cb:
        status_cb(False)


# ---------------- Global Hotkey ----------------

def on_press(key, status_cb=None):
    global _last_toggle
    if key == kb.Key.f6:
        t = now()
        if t - _last_toggle >= DEBOUNCE_SEC:
            _last_toggle = t
            if running.is_set():
                running.clear()
                print("[Paused]")
                if status_cb: status_cb(False)
            else:
                running.set()
                print("[Running]")
                if status_cb: status_cb(True)


# ---------------- GUI ----------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AFK Mouse")
        self.resizable(False, False)

        # Style
        try:
            self.call("tk", "scaling", 1.2)
        except Exception:
            pass

        frame = ttk.Frame(self, padding=16)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(2, weight=1)

        self.status_var = tk.StringVar(value="Status: Paused")
        self.indicator = ttk.Label(frame, textvariable=self.status_var)
        self.indicator.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        self.start_btn = ttk.Button(frame, text="Start", command=self.start)
        self.stop_btn = ttk.Button(frame, text="Stop", command=self.stop, state=tk.DISABLED)
        self.quit_btn = ttk.Button(frame, text="Quit", command=self.on_quit)

        self.start_btn.grid(row=1, column=0, padx=(0, 6))
        self.stop_btn.grid(row=1, column=1, padx=(0, 6))
        self.quit_btn.grid(row=1, column=2)

        self.hint = ttk.Label(frame, text="Hotkey: F6 to toggle", foreground="#666")
        self.hint.grid(row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))

        # Interval controls
        self.interval_label = ttk.Label(frame, text=f"Interval: {int(get_interval())}s")
        self.interval_label.grid(row=3, column=0, sticky="w", pady=(8, 0))

        self.interval_scale = ttk.Scale(
            frame,
            from_=1,
            to=30,
            orient="horizontal",
            command=self.on_interval_change
        )
        # set initial position
        self.interval_scale.set(get_interval())
        self.interval_scale.grid(row=3, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=(8, 0))

        # Start background worker
        self.worker_thread = threading.Thread(target=worker, args=(self._set_status_from_worker,), daemon=True)
        self.worker_thread.start()

        # Global hotkey listener
        self.listener = None
        try:
            self.listener = kb.Listener(on_press=lambda k: on_press(k, self._set_status_from_worker))
            self.listener.start()
        except Exception as exc:
            # Some environments (e.g., Wayland without permissions) do not allow global hooks
            print(f"Global hotkey disabled: {exc}")
            self.hint.configure(text=f"Hotkey unavailable on {sys.platform}")

        # Clean shutdown on window close
        self.protocol("WM_DELETE_WINDOW", self.on_quit)

    # GUI actions
    def start(self):
        if not running.is_set():
            running.set()
            self._set_status(True)

    def stop(self):
        if running.is_set():
            running.clear()
            self._set_status(False)

    def _set_status(self, is_running: bool):
        self.status_var.set("Status: Running" if is_running else "Status: Paused")
        self.start_btn.configure(state=(tk.DISABLED if is_running else tk.NORMAL))
        self.stop_btn.configure(state=(tk.NORMAL if is_running else tk.DISABLED))

    def _set_status_from_worker(self, is_running: bool):
        # ensure thread-safe UI updates
        self.after(0, lambda: self._set_status(is_running))

    def on_interval_change(self, val):
        try:
            sec = float(val)
        except Exception:
            sec = INTERVAL_SEC_DEFAULT
        set_interval(sec)
        self.interval_label.configure(text=f"Interval: {int(get_interval())}s")

    def on_quit(self):
        alive.clear()
        running.clear()
        try:
            if hasattr(self, 'listener') and self.listener:
                self.listener.stop()
        except Exception:
            pass
        # Give worker a moment to exit cleanly
        self.after(100, self.destroy)


def main():
    """Run the AFK Mouse Tkinter application."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
