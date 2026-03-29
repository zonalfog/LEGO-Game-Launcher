import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ZGFile:
    """ZonalFogGames - Spieldaten"""
    game_name: str
    player_stats: Dict[str, Any]
    achievements: List[str]
    playtime: int
    last_played: str
    
@dataclass
class ZPFile:
    """ZonalFogProf-ile - Profile"""
    username: str
    level: int
    experience: int
    preferences: Dict[str, Any]
    friends: List[str]
    
@dataclass
class PGFile:
    """#pachaggang - Gruppierungs-System"""
    group_name: str
    members: List[str]
    group_type: str
    created_date: str
    permissions: Dict[str, List[str]]
    
@dataclass
class ZDFile:
    """ZonalFogsData-Stor-age - Datenspeicher"""
    storage_id: str
    data_type: str
    content: Dict[str, Any]
    backup_count: int
    compression: bool
    
@dataclass
class JFFile:
    """JaydensFR-Files - Speicher-Dateien"""
    file_id: str
    original_name: str
    file_type: str
    content: bytes
    metadata: Dict[str, Any]
    created_date: str

class ZonalFogFileManager:
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.ensure_directories()
    
    def ensure_directories(self):
        """Stellt sicher dass alle Verzeichnisse existieren"""
        dirs = ["zg", "zp", "pg", "zd", "jf"]
        for dir_name in dirs:
            os.makedirs(os.path.join(self.base_path, dir_name), exist_ok=True)
    
    def save_zg(self, data: ZGFile, filename: str) -> str:
        """Speichert .zg Datei"""
        filepath = os.path.join(self.base_path, "zg", f"{filename}.zg")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(data), f, indent=2, ensure_ascii=False)
        return filepath
    
    def load_zg(self, filename: str) -> ZGFile:
        """Lädt .zg Datei"""
        filepath = os.path.join(self.base_path, "zg", f"{filename}.zg")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return ZGFile(**data)
    
    def save_zp(self, data: ZPFile, filename: str) -> str:
        """Speichert .zp Datei"""
        filepath = os.path.join(self.base_path, "zp", f"{filename}.zp")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(data), f, indent=2, ensure_ascii=False)
        return filepath
    
    def load_zp(self, filename: str) -> ZPFile:
        """Lädt .zp Datei"""
        filepath = os.path.join(self.base_path, "zp", f"{filename}.zp")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return ZPFile(**data)
    
    def save_pg(self, data: PGFile, filename: str) -> str:
        """Speichert .pg Datei"""
        filepath = os.path.join(self.base_path, "pg", f"{filename}.pg")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(data), f, indent=2, ensure_ascii=False)
        return filepath
    
    def load_pg(self, filename: str) -> PGFile:
        """Lädt .pg Datei"""
        filepath = os.path.join(self.base_path, "pg", f"{filename}.pg")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return PGFile(**data)
    
    def save_zd(self, data: ZDFile, filename: str) -> str:
        """Speichert .zd Datei"""
        filepath = os.path.join(self.base_path, "zd", f"{filename}.zd")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(data), f, indent=2, ensure_ascii=False)
        return filepath
    
    def load_zd(self, filename: str) -> ZDFile:
        """Lädt .zd Datei"""
        filepath = os.path.join(self.base_path, "zd", f"{filename}.zd")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return ZDFile(**data)
    
    def save_jf(self, data: JFFile, filename: str) -> str:
        """Speichert .jf Datei"""
        filepath = os.path.join(self.base_path, "jf", f"{filename}.jf")
        
        # Speichere Metadaten als JSON
        metadata = {
            "file_id": data.file_id,
            "original_name": data.original_name,
            "file_type": data.file_type,
            "metadata": data.metadata,
            "created_date": data.created_date,
            "content_base64": data.content.hex()  # Bytes als hex speichern
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        return filepath
    
    def load_jf(self, filename: str) -> JFFile:
        """Lädt .jf Datei"""
        filepath = os.path.join(self.base_path, "jf", f"{filename}.jf")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Konvertiere hex zurück zu bytes
        content = bytes.fromhex(data.pop("content_base64"))
        
        return JFFile(
            file_id=data["file_id"],
            original_name=data["original_name"],
            file_type=data["file_type"],
            content=content,
            metadata=data["metadata"],
            created_date=data["created_date"]
        )
    
    def list_files(self, format_type: str) -> List[str]:
        """Listet alle Dateien eines Formats auf"""
        if format_type not in ["zg", "zp", "pg", "zd", "jf"]:
            raise ValueError(f"Unbekanntes Format: {format_type}")
        
        dir_path = os.path.join(self.base_path, format_type)
        if not os.path.exists(dir_path):
            return []
        
        files = [f for f in os.listdir(dir_path) if f.endswith(f".{format_type}")]
        return [os.path.splitext(f)[0] for f in files]
    
    def delete_file(self, format_type: str, filename: str) -> bool:
        """Löscht eine Datei"""
        if format_type not in ["zg", "zp", "pg", "zd", "jf"]:
            raise ValueError(f"Unbekanntes Format: {format_type}")
        
        filepath = os.path.join(self.base_path, format_type, f"{filename}.{format_type}")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

# Beispiel-Nutzung
if __name__ == "__main__":
    manager = ZonalFogFileManager()
    
    # Beispiel .zg Datei erstellen
    game_data = ZGFile(
        game_name="ZonalFog Adventure",
        player_stats={"level": 42, "health": 100, "mana": 50},
        achievements=["first_blood", "explorer"],
        playtime=3600,
        last_played=datetime.now().isoformat()
    )
    manager.save_zg(game_data, "save1")
    
    # Beispiel .zp Datei erstellen
    profile_data = ZPFile(
        username="JaydenFR",
        level=15,
        experience=2500,
        preferences={"theme": "dark", "language": "de"},
        friends=["Alice", "Bob"]
    )
    manager.save_zp(profile_data, "player1")
    
    # Beispiel .pg Datei erstellen
    group_data = PGFile(
        group_name="#pachaggang",
        members=["JaydenFR", "Alice", "Bob"],
        group_type="gaming",
        created_date=datetime.now().isoformat(),
        permissions={"admin": ["JaydenFR"], "member": ["Alice", "Bob"]}
    )
    manager.save_pg(group_data, "main_group")
    
    print("Alle Dateiformate wurden erfolgreich erstellt!")
    print("Verfügbare .zg Dateien:", manager.list_files("zg"))
    print("Verfügbare .zp Dateien:", manager.list_files("zp"))
    print("Verfügbare .pg Dateien:", manager.list_files("pg"))
