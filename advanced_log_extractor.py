import json
import os
from datetime import datetime
from typing import List, Dict, Any

class ZPJLogExtractor:
    """Erweiterte Log-Extraktion für .zpj Dateien"""
    
    def __init__(self, zpj_dir: str = "zpj"):
        self.zpj_dir = zpj_dir
    
    def extract_all_logs(self, output_dir: str = "extracted_logs"):
        """Extrahiert alle .zpj Logs in lesbare Formate"""
        os.makedirs(output_dir, exist_ok=True)
        
        if not os.path.exists(self.zpj_dir):
            print(f"zpj Ordner nicht gefunden: {self.zpj_dir}")
            return
        
        zpj_files = [f for f in os.listdir(self.zpj_dir) if f.endswith('.zpj')]
        
        if not zpj_files:
            print("Keine .zpj Dateien gefunden!")
            return
        
        print(f"Gefunden: {len(zpj_files)} .zpj Dateien")
        
        for zpj_file in zpj_files:
            self.extract_single_log(zpj_file, output_dir)
    
    def extract_single_log(self, zpj_file: str, output_dir: str):
        """Extrahiert eine einzelne .zpj Datei"""
        filepath = os.path.join(self.zpj_dir, zpj_file)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            base_name = os.path.splitext(zpj_file)[0]
            
            # 1. Text-Format
            self._save_as_text(log_data, base_name, output_dir)
            
            # 2. CSV-Format
            self._save_as_csv(log_data, base_name, output_dir)
            
            # 3. HTML-Format
            self._save_as_html(log_data, base_name, output_dir)
            
            print(f"Extrahiert: {base_name}")
            
        except Exception as e:
            print(f"Fehler bei {zpj_file}: {e}")
    
    def _save_as_text(self, log_data: Dict, base_name: str, output_dir: str):
        """Speichert als lesbare Text-Datei"""
        output_file = os.path.join(output_dir, f"{base_name}_log.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 50 + "\n")
            f.write(f"LEGO Launcher Log: {base_name}\n")
            f.write("=" * 50 + "\n")
            f.write(f"Erstellt: {log_data['created_date']}\n")
            f.write(f"Anzahl Einträge: {len(log_data['entries'])}\n")
            f.write("\n")
            
            for entry in log_data['entries']:
                timestamp = entry['timestamp'][:19].replace('T', ' ')
                f.write(f"[{timestamp}] {entry['type'].upper()}: {entry['message']}\n")
                
                if entry['details']:
                    for key, value in entry['details'].items():
                        f.write(f"  - {key}: {value}\n")
                f.write("\n")
    
    def _save_as_csv(self, log_data: Dict, base_name: str, output_dir: str):
        """Speichert als CSV-Datei"""
        output_file = os.path.join(output_dir, f"{base_name}_log.csv")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Timestamp,Type,Message,Details\n")
            
            for entry in log_data['entries']:
                timestamp = entry['timestamp'][:19].replace('T', ' ')
                log_type = entry['type']
                message = entry['message'].replace('"', '""')
                details = str(entry['details']).replace('"', '""')
                
                f.write(f'"{timestamp}","{log_type}","{message}","{details}"\n')
    
    def _save_as_html(self, log_data: Dict, base_name: str, output_dir: str):
        """Speichert als HTML-Datei"""
        output_file = os.path.join(output_dir, f"{base_name}_log.html")
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>LEGO Launcher Log: {base_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #ff6b35; color: white; padding: 20px; border-radius: 5px; }}
        .entry {{ background: white; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #ff6b35; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
        .type {{ font-weight: bold; text-transform: uppercase; }}
        .error {{ border-left-color: #e74c3c; }}
        .startup {{ border-left-color: #27ae60; }}
        .launch {{ border-left-color: #3498db; }}
        .details {{ margin-top: 10px; background: #f8f9fa; padding: 10px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧱 LEGO Launcher Log: {base_name}</h1>
        <p>Erstellt: {log_data['created_date']}</p>
        <p>Anzahl Einträge: {len(log_data['entries'])}</p>
    </div>
"""
        
        for entry in log_data['entries']:
            timestamp = entry['timestamp'][:19].replace('T', ' ')
            log_type = entry['type']
            css_class = log_type
            
            html_content += f"""
    <div class="entry {css_class}">
        <div class="timestamp">{timestamp}</div>
        <div class="type">{log_type}</div>
        <div class="message">{entry['message']}</div>
"""
            
            if entry['details']:
                html_content += '<div class="details"><strong>Details:</strong><ul>'
                for key, value in entry['details'].items():
                    html_content += f'<li><strong>{key}:</strong> {value}</li>'
                html_content += '</ul></div>'
            
            html_content += '</div>'
        
        html_content += """
</body>
</html>"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

if __name__ == "__main__":
    extractor = ZPJLogExtractor()
    extractor.extract_all_logs()
    print("Logs extrahiert nach: extracted_logs/")
