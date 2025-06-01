# scan-to-print

A simple Windows-based Python application with a Tkinter GUI to print images from barcode inputs, using CSV mappings and compatible label printers (DYMO, Zebra).

## Features

* Load barcode-to-image mappings from a CSV file.
* Select and save preferred label printer.
* Print images by entering barcodes.
* Simple UI with log output and sound feedback.
* Supports DYMO, Zebra, and ZDesigner printers.

## Requirements

* Windows OS (due to Windows printing APIs)
* Python 3.8+
* Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Quartermaster-007/scan-to-print.git
    cd scan-to-print
    ```

2. Create and activate a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    .\venv\Scripts\activate   # Windows PowerShell
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the app:

```bash
python app.py
```

* Click **Select CSV** to load your barcode-to-image CSV file.
* Click **Select Printer** to choose a supported printer.
* Enter a barcode and press **Enter** or click **Print**.
* Use **Reload CSV** to reload the CSV if it changes.
* Logs and status messages appear in the app window.
* Config (last CSV and printer) is saved automatically.

## CSV Format

The CSV must have two columns with headers:

* barcode — the barcode string
* file_path — path to the image file to print

Example:

```csv
barcode,file_path
12345,C:\images\label1.png
67890,C:\images\label2.png
```

## Project Structure

```
label_printer/
├── app.py            # Main app launcher
├── gui.py            # Tkinter UI and event handling
├── config.py         # Config load/save logic
├── csv_handler.py    # CSV parsing logic
├── printer.py        # Printer discovery and printing logic
├── sounds.py         # Success and error sounds
├── requirements.txt  # Python dependencies
└── resources/        # (Optional) sounds or other assets
```

## Troubleshooting

* **No supported printers found**: Ensure DYMO, Zebra, or ZDesigner printers are installed and connected.
* **Sound doesn’t play**: Verify sound file paths or Windows sound settings.
* **Image not printing**: Confirm image paths are correct in CSV and printer is selected.

## License

MIT License — feel free to modify and use!