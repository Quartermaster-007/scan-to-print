"""
Simulates a USB barcode scanner by injecting keystrokes at scanner speed.

Usage:
    python test_scan.py [barcode]

Default barcode: 123
The app must already be running. Switch focus away from the app after
starting this script — the global listener should still pick it up.
"""
import sys
import time

try:
    from pynput.keyboard import Controller, Key
except ImportError:
    print("pynput not installed. Run: pip install pynput")
    sys.exit(1)

BARCODE = sys.argv[1] if len(sys.argv) > 1 else "123"
DELAY = 3       # seconds before typing starts (time to switch focus)
INTERVAL = 0.02 # 20ms between keystrokes — well within the 50ms threshold

print(f"Sending barcode '{BARCODE}' in {DELAY} seconds...")
print("You can switch focus away from this terminal now.")
time.sleep(DELAY)

kb = Controller()
for char in BARCODE:
    kb.press(char)
    kb.release(char)
    time.sleep(INTERVAL)

kb.press(Key.enter)
kb.release(Key.enter)

print("Done.")
