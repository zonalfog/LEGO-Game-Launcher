import vdf

def load_vdf(file_path):
    """Lädt VDF Dateien (Valve Data Format)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return vdf.load(f)
    except:
        return None
