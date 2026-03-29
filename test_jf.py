import os
import json
from datetime import datetime

def test_jf_saving():
    """Testet .jf Datei Speichern"""
    print("Teste .jf Speichern...")
    
    # Erstelle Test-Icon-Daten
    test_icon_data = b"fake_icon_data_for_testing"
    
    # Test JFFile
    from zonal_fog_formats import JFFile, ZonalFogFileManager
    
    manager = ZonalFogFileManager()
    
    # Erstelle Test-Icon
    test_icon = JFFile(
        file_id="test_icon",
        original_name="test.png",
        file_type="icon",
        content=test_icon_data,
        metadata={"source": "test", "game": "Test Game"},
        created_date=datetime.now().isoformat()
    )
    
    try:
        # Speichern
        saved_path = manager.save_jf(test_icon, "test_icon")
        print(f"Test .jf gespeichert: {saved_path}")
        
        # Überprüfen
        if os.path.exists(saved_path):
            print(f"Datei existiert: {saved_path}")
            print(f"Groesse: {os.path.getsize(saved_path)} Bytes")
            
            # Laden
            loaded = manager.load_jf("test_icon")
            print(f"Geladen: {len(loaded.content)} Bytes")
            
            # Inhalt vergleichen
            if loaded.content == test_icon_data:
                print("Inhalt identisch!")
            else:
                print("Inhalt unterschiedlich!")
                
        else:
            print(f"Datei nicht gefunden: {saved_path}")
            
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_jf_saving()
