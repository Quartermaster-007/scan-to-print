"""
Barcode scanner input handling.

USB barcode scanners act as a keyboard: they type the barcode value and press Enter.
We capture the Enter key on the barcode entry field and fire a callback.
"""


class BarcodeScanner:
    def __init__(self, root, on_scan_callback):
        """
        Binds Enter key on the barcode entry widget in app.py.
        on_scan_callback(barcode: str) is called with the scanned value.
        """
        self.callback = on_scan_callback
        # Find the barcode entry widget and bind to it
        # The entry widget is set up in app.py; we bind via the root window
        root.bind_all("<Return>", self._on_enter)

    def _on_enter(self, event):
        widget = event.widget
        # Only fire if the event came from an Entry widget
        if hasattr(widget, "get"):
            value = widget.get().strip()
            if value:
                self.callback(value)
                widget.delete(0, "end")
