"""
Global barcode scanner input via pynput keyboard listener.

USB barcode scanners type all characters within ~50 ms then press Enter.
Human typing is much slower — any gap > THRESHOLD_MS resets the buffer.
The listener runs in a background thread and is active regardless of which
window has focus, so scanning works even when the app is minimised.
"""
import threading
import time

try:
    from pynput import keyboard
    _PYNPUT_AVAILABLE = True
except ImportError:
    _PYNPUT_AVAILABLE = False

THRESHOLD_MS = 100  # max ms between keystrokes to be treated as scanner input
MIN_LENGTH = 3      # ignore sequences shorter than this (avoids stray Enter presses)


class BarcodeScanner:
    def __init__(self, root, on_scan_callback, threshold_ms: int = THRESHOLD_MS):
        """
        Installs a global keyboard listener.
        on_scan_callback(barcode: str) is called on the Tkinter main thread.
        threshold_ms controls how fast consecutive keys must arrive to be
        treated as scanner input rather than human typing.
        """
        self._root = root
        self._callback = on_scan_callback
        self._threshold_ms = threshold_ms
        self._buffer = []
        self._last_time = None
        self._lock = threading.Lock()
        self._listener = None

        self._paused = False

        if _PYNPUT_AVAILABLE:
            self._listener = keyboard.Listener(on_press=self._on_press)
            self._listener.daemon = True
            self._listener.start()

    @property
    def paused(self):
        return self._paused

    @property
    def threshold_ms(self):
        return self._threshold_ms

    @threshold_ms.setter
    def threshold_ms(self, value: int):
        self._threshold_ms = value

    def toggle(self):
        self._paused = not self._paused
        with self._lock:
            self._buffer.clear()
            self._last_time = None

    def _on_press(self, key):
        if self._paused:
            return

        now = time.monotonic()

        with self._lock:
            if self._last_time is not None:
                elapsed_ms = (now - self._last_time) * 1000
                if elapsed_ms > self._threshold_ms:
                    self._buffer.clear()

            self._last_time = now

            if key == keyboard.Key.enter:
                barcode = "".join(self._buffer)
                self._buffer.clear()
                self._last_time = None
                if len(barcode) >= MIN_LENGTH:
                    self._root.after(0, self._callback, barcode)

            elif key == keyboard.Key.backspace:
                if self._buffer:
                    self._buffer.pop()

            else:
                try:
                    char = key.char
                    if char:
                        self._buffer.append(char)
                except AttributeError:
                    # Special key (shift, ctrl, etc.) — reset buffer
                    self._buffer.clear()
                    self._last_time = None

    def stop(self):
        if self._listener:
            self._listener.stop()
