import os

CONFIG_FILE = 'config.txt'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, 'r') as f:
        lines = f.readlines()
    config = dict(line.strip().split('=', 1) for line in lines if '=' in line)
    return config

def save_config(csv_path, printer_name):
    with open(CONFIG_FILE, 'w') as f:
        f.write(f"CSV_FILE = {csv_path}\n")
        f.write(f"PRINTER = {printer_name}\n")
