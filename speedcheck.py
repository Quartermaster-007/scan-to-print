"""
Scanner Speed Check window.

Installs a temporary keyboard listener to measure the inter-key gap of
the connected barcode scanner, then suggests a threshold with margin.
"""
import threading
import time
import tkinter as tk
from tkinter import ttk

try:
    from pynput import keyboard
    _PYNPUT_AVAILABLE = True
except ImportError:
    _PYNPUT_AVAILABLE = False

DEFAULT_THRESHOLD = 100  # ms — used when resetting


def _suggest(max_gap_ms: float) -> int:
    """Return a threshold with 50% margin (min +20 ms), rounded up to 10 ms."""
    margin = max(max_gap_ms * 0.5, 20)
    raw = max_gap_ms + margin
    return int((raw // 10 + 1) * 10)


class SpeedcheckWindow:
    def __init__(self, parent, current_threshold: int, on_apply):
        """
        parent           — Tkinter root/toplevel
        current_threshold — scanner's current threshold_ms
        on_apply(ms: int) — called when user clicks Apply or Reset
        """
        self._on_apply = on_apply
        self._current_threshold = current_threshold
        self._lock = threading.Lock()
        self._timestamps: list[float] = []
        self._listener = None

        self._win = tk.Toplevel(parent)
        self._win.title("Scanner Speed Check")
        self._win.resizable(False, False)
        self._win.grab_set()

        self._build_ui(current_threshold)
        self._win.protocol("WM_DELETE_WINDOW", self._close)
        self._start_listener()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self, current_threshold: int):
        pad = {"padx": 12, "pady": 6}

        ttk.Label(
            self._win,
            text="Scan any barcode to measure your scanner's speed.\n"
                 "The app will suggest a safe threshold with margin.",
            justify="left",
        ).grid(row=0, column=0, columnspan=2, sticky="w", **pad)

        ttk.Separator(self._win, orient="horizontal").grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=4
        )

        # Results grid
        labels = [
            ("Max gap between keys:", "_gap_var", "-- ms"),
            ("Suggested threshold:",  "_sugg_var", "-- ms"),
            ("Current threshold:",    "_curr_var", f"{current_threshold} ms"),
        ]
        for i, (text, attr, default) in enumerate(labels):
            ttk.Label(self._win, text=text, anchor="w").grid(
                row=2 + i, column=0, sticky="w", padx=(12, 4), pady=2
            )
            var = tk.StringVar(value=default)
            setattr(self, attr, var)
            ttk.Label(self._win, textvariable=var, anchor="w", width=12).grid(
                row=2 + i, column=1, sticky="w", padx=(0, 12), pady=2
            )

        ttk.Separator(self._win, orient="horizontal").grid(
            row=5, column=0, columnspan=2, sticky="ew", padx=12, pady=4
        )

        # Buttons
        btn_frame = ttk.Frame(self._win)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(0, 12))

        self._apply_btn = ttk.Button(
            btn_frame, text="Apply & Save", command=self._apply, state="disabled"
        )
        self._apply_btn.pack(side="left", padx=6)

        ttk.Button(btn_frame, text="Reset to Default", command=self._reset).pack(
            side="left", padx=6
        )
        ttk.Button(btn_frame, text="Close", command=self._close).pack(
            side="left", padx=6
        )

    # ------------------------------------------------------------------
    # Listener
    # ------------------------------------------------------------------

    def _start_listener(self):
        if not _PYNPUT_AVAILABLE:
            return
        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.daemon = True
        self._listener.start()

    def _on_press(self, key):
        now = time.monotonic()
        with self._lock:
            if key == keyboard.Key.enter:
                timestamps = list(self._timestamps)
                self._timestamps.clear()
                if len(timestamps) >= 2:
                    gaps = [
                        (timestamps[i + 1] - timestamps[i]) * 1000
                        for i in range(len(timestamps) - 1)
                    ]
                    max_gap = max(gaps)
                    suggested = _suggest(max_gap)
                    self._win.after(0, self._update_results, max_gap, suggested)
            else:
                try:
                    if key.char:
                        self._timestamps.append(now)
                except AttributeError:
                    self._timestamps.clear()

    def _update_results(self, max_gap: float, suggested: int):
        self._gap_var.set(f"{max_gap:.1f} ms")
        self._sugg_var.set(f"{suggested} ms")
        self._curr_var.set(f"{self._current_threshold} ms")
        self._suggested = suggested
        self._apply_btn.config(state="normal")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _apply(self):
        self._on_apply(self._suggested)
        self._close()

    def _reset(self):
        self._on_apply(DEFAULT_THRESHOLD)
        self._close()

    def _close(self):
        if self._listener:
            self._listener.stop()
        self._win.destroy()
