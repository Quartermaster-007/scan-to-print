import tkinter as tk
from gui import scanToPrint

if __name__ == "__main__":
    root = tk.Tk()
    app = scanToPrint(root)
    root.mainloop()
