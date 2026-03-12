"""
Printer listing and print job logic (Windows only).
"""
import os


def get_printers():
    """Return list of installed printer names."""
    try:
        import win32print
        printers = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        )
        return [p[2] for p in printers]
    except ImportError:
        return ["(pywin32 not installed — Windows only)"]


def get_default_printer() -> str:
    """Return the Windows default printer name, or empty string if unavailable."""
    try:
        import win32print
        return win32print.GetDefaultPrinter()
    except Exception:
        return ""


def print_file(file_path: str, printer_name: str, copies: int = 1) -> None:
    """Send a file directly to the named printer without changing the system default."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    copies = max(1, int(copies))
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        _print_pdf(file_path, printer_name, copies)
    elif ext in (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".tif"):
        _print_image(file_path, printer_name, copies)
    else:
        raise ValueError(f"Unsupported file type: {ext!r}. Supported: PDF, PNG, JPG, BMP, GIF, TIFF")


def _make_printer_dc(printer_name: str):
    """Return an MFC printer device context for the named printer."""
    import win32ui
    pdc = win32ui.CreateDC()
    pdc.CreatePrinterDC(printer_name)
    return pdc


def _fit_rect(src_w: int, src_h: int, dst_w: int, dst_h: int) -> tuple[int, int]:
    """Return (w, h) that fits src inside dst while preserving aspect ratio."""
    ratio = min(dst_w / src_w, dst_h / src_h)
    return int(src_w * ratio), int(src_h * ratio)


def _print_pdf(file_path: str, printer_name: str, copies: int = 1) -> None:
    import win32con
    import pypdfium2 as pdfium
    from PIL import ImageWin

    pdf = pdfium.PdfDocument(file_path)
    pdc = _make_printer_dc(printer_name)

    printable_w = pdc.GetDeviceCaps(win32con.HORZRES)
    printable_h = pdc.GetDeviceCaps(win32con.VERTRES)
    dpi = pdc.GetDeviceCaps(win32con.LOGPIXELSX)
    scale = max(dpi / 72.0, 1.0)  # PDF points are 1/72 inch

    # Pre-render all pages once; repeat per copy
    pages = []
    for i in range(len(pdf)):
        bitmap = pdf[i].render(scale=scale)
        pages.append(bitmap.to_pil().convert("RGB"))

    pdc.StartDoc(os.path.basename(file_path))
    try:
        for _ in range(copies):
            for img in pages:
                draw_w, draw_h = _fit_rect(img.width, img.height, printable_w, printable_h)
                pdc.StartPage()
                ImageWin.Dib(img).draw(pdc.GetHandleOutput(), (0, 0, draw_w, draw_h))
                pdc.EndPage()

        pdc.EndDoc()
    except Exception:
        pdc.AbortDoc()
        raise
    finally:
        pdc.DeleteDC()
        pdf.close()


def _print_image(file_path: str, printer_name: str, copies: int = 1) -> None:
    import win32con
    from PIL import Image, ImageWin

    img = Image.open(file_path).convert("RGB")
    pdc = _make_printer_dc(printer_name)

    printable_w = pdc.GetDeviceCaps(win32con.HORZRES)
    printable_h = pdc.GetDeviceCaps(win32con.VERTRES)
    draw_w, draw_h = _fit_rect(img.width, img.height, printable_w, printable_h)
    dib = ImageWin.Dib(img)

    pdc.StartDoc(os.path.basename(file_path))
    try:
        for _ in range(copies):
            pdc.StartPage()
            dib.draw(pdc.GetHandleOutput(), (0, 0, draw_w, draw_h))
            pdc.EndPage()
        pdc.EndDoc()
    except Exception:
        pdc.AbortDoc()
        raise
    finally:
        pdc.DeleteDC()
