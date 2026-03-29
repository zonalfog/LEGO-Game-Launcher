import os
import subprocess
import tempfile
from PIL import Image, ImageDraw
import io

def extract_real_exe_icon(exe_path):
    """Extrahiert das echte Icon aus der .exe Datei mit PowerShell"""
    try:
        # PowerShell Script zum Icon extrahieren
        ps_script = f'''
Add-Type -AssemblyName System.Drawing
$icon = [System.Drawing.Icon]::ExtractAssociatedIcon("{exe_path}")
if ($icon -ne $null) {{
    $bitmap = $icon.ToBitmap()
    $bitmap.Save("$env:TEMP\\temp_icon.png", [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Output "SUCCESS"
}} else {{
    Write-Output "FAILED"
}}
'''
        
        # PowerShell ausführen
        with tempfile.NamedTemporaryFile(suffix='.ps1', delete=False, mode='w') as ps_file:
            ps_file.write(ps_script)
            ps_file_path = ps_file.name
        
        try:
            # PowerShell Script ausführen
            result = subprocess.run(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "SUCCESS" in result.stdout:
                # Lese das extrahierte Icon
                temp_icon_path = os.path.join(tempfile.gettempdir(), "temp_icon.png")
                if os.path.exists(temp_icon_path):
                    with open(temp_icon_path, 'rb') as f:
                        icon_data = f.read()
                    
                    # Icon auf 128x128 skalieren
                    img = Image.open(io.BytesIO(icon_data))
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                    img = img.resize((128, 128), Image.Resampling.LANCZOS)
                    
                    # In Bytes konvertieren
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format='PNG')
                    
                    # Temporäre Datei löschen
                    os.unlink(temp_icon_path)
                    
                    return img_bytes.getvalue()
            
        except subprocess.TimeoutExpired:
            print("PowerShell Script timeout")
        except Exception as e:
            print(f"PowerShell Fehler: {e}")
        finally:
            # PowerShell Script löschen
            try:
                os.unlink(ps_file_path)
            except:
                pass
            
    except Exception as e:
        print(f"Icon Extraktion Fehler: {e}")
    
    return None

def create_fallback_icon(exe_path):
    """Erstellt Fallback Icon mit Spielnamen"""
    try:
        # Spielname extrahieren
        exe_name = os.path.basename(exe_path).replace('.exe', '')
        
        # Kürze Namen zu max 8 Zeichen
        if len(exe_name) > 8:
            display_name = exe_name[:8] + ".."
        else:
            display_name = exe_name
        
        # Erstelle Icon
        img = Image.new('RGB', (128, 128), color='#2b2b2b')
        draw = ImageDraw.Draw(img)
        
        # Hintergrund
        draw.rectangle([5, 5, 123, 123], fill='#ff6b35', outline='#e74c3c', width=3)
        draw.rectangle([15, 15, 113, 113], fill='#e74c3c')
        
        # LEGO Block
        draw.rectangle([25, 25, 103, 103], fill='#ff6b35', outline='#c0392b', width=2)
        draw.rectangle([35, 35, 93, 93], fill='#ff8c42')
        
        # Nubs
        for x in range(45, 85, 15):
            draw.ellipse([x-4, 30, x+4, 38], fill='#e74c3c')
        
        # Text (ohne Font dependency)
        try:
            # Versuche Arial
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            # Fallback: Default Font
            font = ImageFont.load_default()
        
        # Text in die Mitte
        try:
            bbox = draw.textbbox((0, 0), display_name, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (128 - text_width) // 2
            y = (128 - text_height) // 2
            
            draw.text((x, y), display_name, fill='white', font=font)
        except:
            # Wenn Text fehlschlägt, lasse es leer
            pass
        
        # In Bytes konvertieren
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
        
    except Exception as e:
        print(f"Fallback Icon Fehler: {e}")
        return None

# Test
if __name__ == "__main__":
    # Test mit Beispiel-EXE
    test_exe = "C:\\Windows\\System32\\notepad.exe"
    
    print("Versuche echtes .exe Icon zu extrahieren...")
    icon_data = extract_real_exe_icon(test_exe)
    
    if icon_data:
        with open("real_exe_icon.png", "wb") as f:
            f.write(icon_data)
        print("Echtes .exe Icon erstellt: real_exe_icon.png")
    else:
        print("Echtes Icon fehlgeschlagen, versuche Fallback...")
        fallback_data = create_fallback_icon(test_exe)
        
        if fallback_data:
            with open("fallback_icon.png", "wb") as f:
                f.write(fallback_data)
            print("Fallback Icon erstellt: fallback_icon.png")
        else:
            print("Alles fehlgeschlagen")
