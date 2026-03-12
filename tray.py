"""
System tray icon and menu for Scan to Print.

The tray icon is shown whenever the app is running.  When the main window is
minimised, it is withdrawn from the taskbar; the user interacts with the app
exclusively through the tray icon until they choose Restore.

The pystray event loop runs in its own daemon thread.  Every callback that
touches Tkinter widgets must be dispatched via ``root.after(0, fn)`` to stay on
the main thread.
"""
import os
import sys
import threading

import pystray
from PIL import Image

import i18n


def _icon_image() -> Image.Image:
    """Load the application icon as a PIL Image."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    path = os.path.join(base, "images", "scan-to-print.png")
    try:
        return Image.open(path).convert("RGBA")
    except Exception:
        # Fallback: plain coloured square
        img = Image.new("RGBA", (64, 64), (30, 144, 255, 255))
        return img


class TrayManager:
    """Manages the pystray tray icon lifecycle."""

    def __init__(
        self,
        root,
        *,
        on_restore,
        on_exit,
        on_toggle_scan,
        get_scan_paused,
    ):
        self._root = root
        self._on_restore = on_restore
        self._on_exit = on_exit
        self._on_toggle_scan = on_toggle_scan
        self._get_scan_paused = get_scan_paused

        self._icon = None  # pystray.Icon
        self._thread = None  # threading.Thread

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the tray icon in its own daemon thread."""
        if self._icon is not None:
            return
        self._icon = pystray.Icon(
            "ScanToPrint",
            _icon_image(),
            "Scan to Print",
            menu=self._build_menu(),
        )
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the tray icon (call on app exit)."""
        if self._icon is not None:
            self._icon.stop()
            self._icon = None

    def update_menu(self) -> None:
        """Rebuild the tray menu (call after scanner state changes)."""
        if self._icon is not None:
            self._icon.menu = self._build_menu()
            self._icon.update_menu()

    def notify(self, title: str, message: str) -> None:
        """Show a tray balloon notification."""
        if self._icon is not None:
            try:
                self._icon.notify(message, title)
            except Exception:
                pass  # notifications not supported on all platforms

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem(
                i18n.t("tray_restore"),
                self._cb_restore,
                default=True,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                self._scan_toggle_label,
                self._cb_toggle_scan,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(i18n.t("tray_exit"), self._cb_exit),
        )

    def _scan_toggle_label(self, _item) -> str:
        if self._get_scan_paused():
            return i18n.t("tray_resume_scan")
        return i18n.t("tray_pause_scan")

    def _cb_restore(self, _icon, _item) -> None:
        self._root.after(0, self._on_restore)

    def _cb_exit(self, _icon, _item) -> None:
        self._root.after(0, self._on_exit)

    def _cb_toggle_scan(self, _icon, _item) -> None:
        self._root.after(0, self._on_toggle_scan)
