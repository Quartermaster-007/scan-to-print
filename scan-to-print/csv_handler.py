import csv

def load_csv(csv_path):
    records = {}
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        records = {row['barcode']: row['file_path'] for row in reader}
    return records
