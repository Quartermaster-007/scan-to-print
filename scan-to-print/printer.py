
import os
import win32print
import win32ui
from PIL import Image, ImageWin

SUPPORTED_PRINTER_KEYWORDS = ["dymo", "zebra", "zdesigner"]

def find_compatible_printers():
    all_printers = [p[2] for p in win32print.EnumPrinters(
        win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
    return [p for p in all_printers if any(k in p.lower() for k in SUPPORTED_PRINTER_KEYWORDS)]

def print_image(printer_name, image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")
    image = Image.open(image_path)
    pdc = win32ui.CreateDC()
    pdc.CreatePrinterDC(printer_name)
    pdc.StartDoc(image_path)
    pdc.StartPage()

    printable_area = pdc.GetDeviceCaps(8), pdc.GetDeviceCaps(10)
    image_width, image_height = image.size
    ratio = min(printable_area[0] / image_width, printable_area[1] / image_height)
    scaled_width = int(image_width * ratio)
    scaled_height = int(image_height * ratio)
    x = (printable_area[0] - scaled_width) // 2
    y = (printable_area[1] - scaled_height) // 2

    dib = ImageWin.Dib(image)
    dib.draw(pdc.GetHandleOutput(), (x, y, x + scaled_width, y + scaled_height))

    pdc.EndPage()
    pdc.EndDoc()
    pdc.DeleteDC()
