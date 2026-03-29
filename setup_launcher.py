import os
import sys
import ctypes
import subprocess
from pathlib import Path

def create_launcher():
    """Erstellt Launcher-Dateien für Taskbar und Desktop"""
    
    # Projekt-Pfad ermitteln
    project_path = os.path.dirname(os.path.abspath(__file__))
    
    # PowerShell Script erstellen
    ps_script = f'''@echo off
cd "{project_path}"
python lego_game_launcher.py
pause
'''
    
    # Batch-Datei für PowerShell
    batch_file = os.path.join(project_path, "start_lego_launcher.bat")
    with open(batch_file, 'w', encoding='utf-8') as f:
        f.write(ps_script)
    
    # PowerShell Script für Desktop Shortcut
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{desktop_path}\\LEGO Game Launcher.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-NoExit -Command \\"cd \\"{project_path}\\"; python lego_game_launcher.py\\""
$Shortcut.WorkingDirectory = "{project_path}"
$Shortcut.IconLocation = "shell32.dll,44"
$Shortcut.Description = "LEGO Game Launcher"
$Shortcut.Save()
'''
    
    # PowerShell Script ausführen
    ps_file = os.path.join(project_path, "create_shortcut.ps1")
    with open(ps_file, 'w', encoding='utf-8') as f:
        f.write(shortcut_script)
    
    try:
        # PowerShell Script ausführen (um Shortcut zu erstellen)
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_file], 
                      check=True, capture_output=True)
        
        # Temporäre Dateien löschen
        os.remove(ps_file)
        
        print("✅ Desktop-Shortcut erstellt!")
        print(f"📁 Pfad: {desktop_path}\\LEGO Game Launcher.lnk")
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen des Shortcuts: {e}")
        print(f"💡 Manuelles Starten: Doppelklick auf {batch_file}")
    
    # Taskbar Launcher (Windows Terminal/PowerShell Profil)
    try:
        # Für Windows Terminal
        terminal_config_path = os.path.join(os.path.expanduser("~"), 
                                           "AppData\\Local\\Packages\\Microsoft.WindowsTerminal_8wekyb3d8bbwe\\LocalState\\settings.json")
        
        if os.path.exists(terminal_config_path):
            print("💡 Windows Terminal gefunden - Manuelles Hinzufügen empfohlen")
            print(f"📋 Befehl: cd \"{project_path}\" && python lego_game_launcher.py")
        
        return batch_file
        
    except:
        pass
    
    return batch_file

def setup_autostart():
    """Richtet Autostart ein (optional)"""
    project_path = os.path.dirname(os.path.abspath(__file__))
    
    # Registry Eintrag für Autostart
    try:
        import winreg
        
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 
                           0, winreg.KEY_SET_VALUE)
        
        launcher_path = os.path.join(project_path, "start_lego_launcher.bat")
        winreg.SetValueEx(key, "LEGOGameLauncher", 0, winreg.REG_SZ, launcher_path)
        winreg.CloseKey(key)
        
        print("✅ Autostart eingerichtet!")
        
    except Exception as e:
        print(f"❌ Autostart fehlgeschlagen: {e}")

if __name__ == "__main__":
    print("🧱 LEGO Game Launcher Setup")
    print("=" * 40)
    
    # Launcher erstellen
    launcher_file = create_launcher()
    
    # Frage nach Autostart
    response = input("\n🚀 Möchtest du den Launcher beim Windows-Start automatisch öffnen? (j/n): ")
    if response.lower() in ['j', 'ja', 'y', 'yes']:
        setup_autostart()
    
    print("\n✅ Setup abgeschlossen!")
    print(f"📂 Projekt-Pfad: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"🎮 Start-Datei: {launcher_file}")
    print("🖥️  Desktop-Shortcut: LEGO Game Launcher.lnk")
    
    input("\nDrücke Enter zum Beenden...")
