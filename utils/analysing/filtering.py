import re
def filter_row(row):
    cleaned_row = re.sub(r'^\d+\.\s*', '', row)
    cleaned_row = re.sub(r'^-\s*', '', cleaned_row)
    cleaned_row = re.sub(r'[^a-zA-Zа-яА-Я\s;]', '', cleaned_row)
    cleaned_row = cleaned_row.strip()
    if ';' not in cleaned_row:
        return False
    parts = cleaned_row.split(';')
    if len(parts) != 2:
        return False
    for part in parts:
        part = part.strip()
        if not part or len(part.split()) > 3:
            return False
    return True

