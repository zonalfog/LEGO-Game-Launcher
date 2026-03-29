import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class ZPJFile:
    """ZonalFogProject-Journal - Launcher Logs"""
    file_id: str
    created_date: str
    entries: List[Dict[str, Any]]
    
    def add_entry(self, log_type: str, message: str, details: Dict[str, Any] = None):
        """Fügt einen neuen Log-Eintrag hinzu"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": log_type,  # "startup", "launch", "error", "import", "settings"
            "message": message,
            "details": details or {}
        }
        self.entries.append(entry)
    
    def get_entries_by_type(self, log_type: str) -> List[Dict[str, Any]]:
        """Holt alle Einträge eines bestimmten Typs"""
        return [entry for entry in self.entries if entry["type"] == log_type]
    
    def get_entries_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Holt alle Einträge eines bestimmten Datums"""
        return [entry for entry in self.entries if entry["timestamp"].startswith(date)]

class ZPJManager:
    """Manager für .zpj Log-Dateien"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.zpj_dir = os.path.join(base_path, "zpj")
        os.makedirs(self.zpj_dir, exist_ok=True)
    
    def create_log(self, file_id: str) -> ZPJFile:
        """Erstellt eine neue Log-Datei"""
        log_file = ZPJFile(
            file_id=file_id,
            created_date=datetime.now().isoformat(),
            entries=[]
        )
        log_file.add_entry("startup", f"Log-Datei erstellt: {file_id}")
        return log_file
    
    def save_log(self, log_file: ZPJFile) -> str:
        """Speichert eine .zpj Datei"""
        filepath = os.path.join(self.zpj_dir, f"{log_file.file_id}.zpj")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(log_file), f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def load_log(self, file_id: str) -> ZPJFile:
        """Lädt eine .zpj Datei"""
        filepath = os.path.join(self.zpj_dir, f"{file_id}.zpj")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return ZPJFile(**data)
    
    def list_logs(self) -> List[str]:
        """Listet alle verfügbaren Logs auf"""
        if not os.path.exists(self.zpj_dir):
            return []
        
        files = [f for f in os.listdir(self.zpj_dir) if f.endswith('.zpj')]
        return [os.path.splitext(f)[0] for f in files]
    
    def get_latest_log(self) -> ZPJFile:
        """Holt das neueste Log"""
        logs = self.list_logs()
        if not logs:
            return self.create_log("current")
        
        # Sortiere nach Erstellungsdatum
        latest_log = max(logs, key=lambda x: self.load_log(x).created_date)
        return self.load_log(latest_log)

# Beispiel-Nutzung
if __name__ == "__main__":
    manager = ZPJManager()
    
    # Erstelle Log
    log = manager.create_log("launcher_session_001")
    log.add_entry("startup", "Launcher gestartet", {"version": "1.0", "user": "Jayden"})
    log.add_entry("launch", "Lego City Undercover gestartet", {"game_id": "12345", "duration": "2h 30m"})
    log.add_entry("error", "Steam Verbindung fehlgeschlagen", {"error_code": "500"})
    
    # Speichern
    manager.save_log(log)
    print("Log gespeichert!")
