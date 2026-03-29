import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import winreg
from PIL import Image, ImageTk
from zonal_fog_formats import ZonalFogFileManager, ZGFile, ZPFile, PGFile, ZDFile, JFFile
from zpj_log_format import ZPJManager, ZPJFile
from datetime import datetime
import json
import io
import struct
import re

class LegoGameLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧱 LEGO Game Launcher")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        self.file_manager = ZonalFogFileManager()
        self.zpj_manager = ZPJManager()
        self.games = []
        self.categories = []
        self.settings = None
        self.steam_profile = None
        self.steam_path = None
        self.steam_connected = False
        
        # Erstelle Session-Log
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_log = self.zpj_manager.create_log(session_id)
        
        self.load_data()
        self.setup_gui()
        
        # Log Launcher-Start
        self.current_log.add_entry("startup", "Launcher gestartet", {
            "version": "1.0",
            "session_id": session_id,
            "python_version": "3.x"
        })
        self.save_log()
        
    def save_log(self):
        """Speichert das aktuelle Log"""
        try:
            self.zpj_manager.save_log(self.current_log)
        except Exception as e:
            print(f"Fehler beim Speichern des Logs: {e}")
    
    def log_event(self, event_type: str, message: str, details: dict = None):
        """Loggt ein Ereignis"""
        try:
            self.current_log.add_entry(event_type, message, details)
            self.save_log()
        except Exception as e:
            print(f"Fehler beim Loggen: {e}")
    
    def load_data(self):
        """Lädt alle Daten aus den Dateiformaten"""
        try:
            # Lade Launcher-Einstellungen (.zd)
            self.settings = self.file_manager.load_zd("launcher_settings")
        except:
            # Erstelle Standard-Einstellungen
            self.settings = ZDFile(
                storage_id="launcher_settings",
                data_type="config",
                content={"close_on_launch": False, "theme": "dark"},
                backup_count=0,
                compression=False
            )
            self.file_manager.save_zd(self.settings, "launcher_settings")
        
        # Lade Steam Profil (.zp)
        try:
            self.steam_profile = self.file_manager.load_zp("steam_profile")
            self.steam_path = self.steam_profile.preferences.get("steam_path", "")
            self.steam_connected = bool(self.steam_path)
        except:
            # Erstelle Standard-Profil
            self.steam_profile = ZPFile(
                username="SteamUser",
                level=1,
                experience=0,
                preferences={"auto_launch_steam": True, "steam_path": ""},
                friends=[]
            )
            self.file_manager.save_zp(self.steam_profile, "steam_profile")
        
        # Lade Spiele (.zg)
        self.games = []
        game_files = self.file_manager.list_files("zg")
        for game_file in game_files:
            if game_file.startswith("lego_"):
                game_data = self.file_manager.load_zg(game_file)
                self.games.append(game_data)
        
        # Lade Kategorien (.pg)
        self.categories = []
        category_files = self.file_manager.list_files("pg")
        for cat_file in category_files:
            if cat_file.startswith("category_"):
                category_data = self.file_manager.load_pg(cat_file)
                self.categories.append(category_data)
    
    def setup_gui(self):
        """Erstellt die GUI"""
        # Header
        header_frame = tk.Frame(self.root, bg='#1a1a1a', height=80)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        header_frame.pack_propagate(False)
        
        # Titel und Steam-Status
        title_container = tk.Frame(header_frame, bg='#1a1a1a')
        title_container.pack(pady=20)
        
        title_label = tk.Label(
            title_container, 
            text="🧱 LEGO Game Launcher", 
            font=('Arial', 24, 'bold'),
            fg='#ff6b35',
            bg='#1a1a1a'
        )
        title_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Steam-Status
        self.steam_status_label = tk.Label(
            title_container,
            text="🔴 Steam nicht verbunden" if not self.steam_connected else "🟢 Steam verbunden",
            font=('Arial', 12),
            fg='#ff4444' if not self.steam_connected else '#44ff44',
            bg='#1a1a1a'
        )
        self.steam_status_label.pack(side=tk.LEFT, padx=10)
        
        self.steam_connect_button = tk.Button(
            title_container,
            text="🔗 Mit Steam verbinden",
            font=('Arial', 10),
            bg='#4a4a4a',
            fg='white',
            command=self.connect_steam
        )
        self.steam_connect_button.pack(side=tk.LEFT)
        
        # Haupt-Content
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Linke Seite - Spiel-Liste
        left_frame = tk.Frame(main_frame, bg='#2b2b2b', width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        tk.Label(
            left_frame, 
            text="LEGO Spiele", 
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#2b2b2b'
        ).pack(pady=10)
        
        # Kategorie-Filter
        self.category_var = tk.StringVar(value="Alle Spiele")
        category_combo = ttk.Combobox(
            left_frame, 
            textvariable=self.category_var,
            values=["Alle Spiele"] + [cat.group_name for cat in self.categories],
            state="readonly"
        )
        category_combo.pack(pady=5, padx=5, fill=tk.X)
        category_combo.bind('<<ComboboxSelected>>', self.on_category_changed)
        
        # Spiel-Liste
        self.game_listbox = tk.Listbox(
            left_frame,
            bg='#3a3a3a',
            fg='white',
            selectbackground='#ff6b35',
            font=('Arial', 10)
        )
        self.game_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.game_listbox.bind('<<ListboxSelect>>', self.game_selected)
        
        # Rechte Seite - Spiel-Details
        right_frame = tk.Frame(main_frame, bg='#2b2b2b')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Spiel-Info
        self.info_frame = tk.Frame(right_frame, bg='#3a3a3a')
        self.info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.game_title = tk.Label(
            self.info_frame,
            text="Wähle ein Spiel aus",
            font=('Arial', 18, 'bold'),
            fg='white',
            bg='#3a3a3a'
        )
        self.game_title.pack(pady=20)
        
        self.game_icon_label = tk.Label(self.info_frame, bg='#3a3a3a')
        self.game_icon_label.pack(pady=10)
        
        self.game_info = tk.Label(
            self.info_frame,
            text="",
            font=('Arial', 10),
            fg='#cccccc',
            bg='#3a3a3a',
            wraplength=400,
            justify=tk.LEFT
        )
        self.game_info.pack(pady=10, padx=20)
        
        # Buttons
        button_frame = tk.Frame(right_frame, bg='#2b2b2b')
        button_frame.pack(fill=tk.X)
        
        self.launch_button = tk.Button(
            button_frame,
            text="🎮 Spiel starten",
            font=('Arial', 12, 'bold'),
            bg='#ff6b35',
            fg='white',
            command=self.launch_game,
            state=tk.DISABLED
        )
        self.launch_button.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="➕ Spiel hinzufügen",
            font=('Arial', 10),
            bg='#4a4a4a',
            fg='white',
            command=self.add_game
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="📂 Kategorie",
            font=('Arial', 10),
            bg='#4a4a4a',
            fg='white',
            command=self.manage_categories
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="⚙️ Einstellungen",
            font=('Arial', 10),
            bg='#4a4a4a',
            fg='white',
            command=self.open_settings
        ).pack(side=tk.LEFT, padx=5)
        
        # Spiele in Liste laden
        self.refresh_game_list()
    
    def on_category_changed(self, event):
        """Wird aufgerufen wenn die Kategorie geändert wird"""
        self.refresh_game_list()
    
    def refresh_game_list(self):
        """Aktualisiert die Spiel-Liste"""
        self.game_listbox.delete(0, tk.END)
        
        selected_category = self.category_var.get()
        
        for game in self.games:
            if selected_category == "Alle Spiele" or selected_category in game.player_stats.get("categories", []):
                self.game_listbox.insert(tk.END, game.game_name)
    
    def game_selected(self, event):
        """Wird aufgerufen wenn ein Spiel ausgewählt wird"""
        selection = self.game_listbox.curselection()
        if selection:
            game_name = self.game_listbox.get(selection[0])
            
            # Finde das Spiel-Daten
            selected_game = None
            for game in self.games:
                if game.game_name == game_name:
                    selected_game = game
                    break
            
            if selected_game:
                self.show_game_info(selected_game)
                self.launch_button.config(state=tk.NORMAL)
    
    def launch_game(self, game):
        """Startet ein Spiel"""
        try:
            game_path = game.player_stats.get('path')
            if not game_path or not os.path.exists(game_path):
                messagebox.showerror("Fehler", f"Spiel-Pfad nicht gefunden: {game_path}")
                self.log_event("error", f"Spiel-Pfad nicht gefunden", {"game": game.game_name, "path": game_path})
                return
            
            # Log Spiel-Start
            self.log_event("launch", f"Spiel gestartet: {game.game_name}", {
                "game_name": game.game_name,
                "path": game_path,
                "playtime_before": game.playtime
            })
            
            # Spiel starten
            subprocess.Popen([game_path], shell=True)
            
            # Playtime aktualisieren (vereinfacht)
            game.playtime += 1
            game.last_played = datetime.now().isoformat()
            
            # Spiel-Daten speichern
            filename = f"lego_{game.game_name.lower().replace(' ', '_')}"
            self.file_manager.save_zg(game, filename)
            
            # Log erfolgreichen Start
            self.log_event("launch", f"Spiel erfolgreich gestartet", {
                "game_name": game.game_name,
                "new_playtime": game.playtime
            })
            
            # Launcher schließen wenn eingestellt
            if self.settings.content.get('close_on_launch', False):
                self.log_event("settings", "Launcher nach Spielstart geschlossen")
                self.root.quit()
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Starten des Spiels: {str(e)}")
            self.log_event("error", f"Fehler beim Spielstart", {
                "game": game.game_name,
                "error": str(e)
            })
    
    def show_game_info(self, game):
        """Zeigt Spiel-Informationen an"""
        self.game_title.config(text=game.game_name)
        
        # Lade Icon wenn vorhanden
        icon_loaded = False
        
        # Versuche .jf Icon zu laden
        try:
            icon_filename = f"icon_{game.game_name.lower().replace(' ', '_')}"
            print(f"Versuche .jf zu laden: {icon_filename}")
            
            icon_file = self.file_manager.load_jf(icon_filename)
            if icon_file.content:
                icon_image = Image.open(io.BytesIO(icon_file.content))
                icon_image = icon_image.resize((256, 256), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(icon_image)
                self.game_icon_label.config(image=photo)
                self.game_icon_label.image = photo
                icon_loaded = True
                print(f".jf Icon geladen: {game.game_name}")
            else:
                print(f".jf Datei leer: {game.game_name}")
        except Exception as e:
            print(f"Fehler beim .jf Icon: {e}")
        
        # Fallback: Versuche Steam-Icon
        if not icon_loaded:
            try:
                steam_icon_path = self.get_steam_icon_path(game.game_name)
                if steam_icon_path and os.path.exists(steam_icon_path):
                    icon_image = Image.open(steam_icon_path)
                    icon_image = icon_image.resize((256, 256), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(icon_image)
                    self.game_icon_label.config(image=photo)
                    self.game_icon_label.image = photo
                    icon_loaded = True
                    print(f"Steam Icon geladen: {game.game_name}")
            except Exception as e:
                print(f"Fehler beim Steam Icon: {e}")
        
        # Fallback: Versuche .exe Icon direkt
        if not icon_loaded:
            try:
                exe_path = game.player_stats.get('path')
                if exe_path and os.path.exists(exe_path):
                    icon_data = self.extract_icon_from_exe(exe_path)
                    if icon_data:
                        icon_image = Image.open(io.BytesIO(icon_data))
                        photo = ImageTk.PhotoImage(icon_image)
                        self.game_icon_label.config(image=photo)
                        self.game_icon_label.image = photo
                        icon_loaded = True
                        print(f"EXE Icon geladen: {game.game_name}")
            except Exception as e:
                print(f"Fehler beim EXE Icon: {e}")
        
        # Letzter Fallback: LEGO Icon
        if not icon_loaded:
            try:
                img = Image.new('RGB', (256, 256), color='#ff6b35')
                from PIL import ImageDraw
                draw = ImageDraw.Draw(img)
                
                # LEGO Block zeichnen (größer)
                block_size = 180
                offset = (256 - block_size) // 2
                nub_size = 15
                
                # Äußerer Rahmen
                draw.rectangle([offset-10, offset-10, offset+block_size+10, offset+block_size+10], 
                             fill='#e74c3c', outline='#c0392b', width=4)
                draw.rectangle([offset, offset, offset+block_size, offset+block_size], 
                             fill='#ff6b35')
                
                # Innerer Block
                inner_offset = offset + 20
                inner_size = block_size - 40
                draw.rectangle([inner_offset, inner_offset, inner_offset+inner_size, inner_offset+inner_size], 
                             fill='#ff8c42')
                
                # Nubs (größer und mehr)
                for x in range(inner_offset + 20, inner_offset + inner_size, 30):
                    draw.ellipse([x-nub_size, offset+5, x+nub_size, offset+5+nub_size*2], fill='#e74c3c')
                
                photo = ImageTk.PhotoImage(img)
                self.game_icon_label.config(image=photo)
                self.game_icon_label.image = photo
                print(f"LEGO Fallback Icon: {game.game_name}")
            except Exception as e:
                print(f"Fehler beim LEGO Icon: {e}")
                self.game_icon_label.config(image="", text="🎮", font=('Arial', 96))
        
        # Zeige Spiel-Info
        info_text = f"Pfad: {game.player_stats.get('path', 'Nicht festgelegt')}\n"
        info_text += f"Kategorien: {', '.join(game.player_stats.get('categories', ['Keine']))}\n"
        info_text += f"Zuletzt gespielt: {game.last_played[:10] if game.last_played else 'Nie'}\n"
        info_text += f"Spielzeit: {game.playtime} Stunden"
        
        self.game_info.config(text=info_text)
    
    def launch_game(self):
        """Startet das ausgewählte Spiel"""
        selection = self.game_listbox.curselection()
        if not selection:
            return
        
        game_name = self.game_listbox.get(selection[0])
        
        # Finde das Spiel
        selected_game = None
        for game in self.games:
            if game.game_name == game_name:
                selected_game = game
                break
        
        if selected_game:
            self.launch_game(selected_game)
    
    def add_game(self):
        """Fügt ein neues Spiel hinzu"""
        dialog = GameDialog(self.root, "Spiel hinzufügen")
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            game_name, game_path, categories = dialog.result
            
            # Erstelle neue Spiel-Datei
            new_game = ZGFile(
                game_name=game_name,
                player_stats={
                    "path": game_path,
                    "categories": categories,
                    "executable": os.path.basename(game_path)
                },
                achievements=[],
                playtime=0,
                last_played=""
            )
            
            filename = f"lego_{game_name.lower().replace(' ', '_')}"
            self.file_manager.save_zg(new_game, filename)
            
            self.games.append(new_game)
            self.refresh_game_list()
            messagebox.showinfo("Erfolg", f"Spiel {game_name} wurde hinzugefügt!")
    
    def manage_categories(self):
        """Kategorien verwalten"""
        dialog = CategoryDialog(self.root, self.categories, self.file_manager)
        self.root.wait_window(dialog.dialog)
        
        # Lade Kategorien neu
        self.categories = []
        category_files = self.file_manager.list_files("pg")
        for cat_file in category_files:
            if cat_file.startswith("category_"):
                category_data = self.file_manager.load_pg(cat_file)
                self.categories.append(category_data)
        
        # Update Kategorie-Combo
        category_values = ["Alle Spiele"] + [cat.group_name for cat in self.categories]
        self.category_var.set("Alle Spiele")
    
    def open_settings(self):
        """Öffnet Einstellungen"""
        dialog = SettingsDialog(self.root, self.settings, self.file_manager)
        self.root.wait_window(dialog.dialog)
        
        # Lade Einstellungen neu
        try:
            self.settings = self.file_manager.load_zd("launcher_settings")
        except:
            pass
    
    def run(self):
        """Startet den Launcher"""
        self.root.mainloop()
    
    def connect_steam(self):
        """Verbindet mit Steam und importiert LEGO Spiele"""
        try:
            # Finde Steam-Installation
            steam_path = self.find_steam_installation()
            if not steam_path:
                messagebox.showerror("Fehler", "Steam Installation nicht gefunden!")
                return
            
            # Speichere Steam-Pfad
            self.steam_path = steam_path
            self.steam_connected = True
            self.steam_profile.preferences["steam_path"] = steam_path
            self.file_manager.save_zp(self.steam_profile, "steam_profile")
            
            # Update UI
            self.steam_status_label.config(text="🟢 Steam verbunden", fg="#44ff44")
            self.steam_connect_button.config(state=tk.DISABLED)
            
            # Importiere LEGO Spiele
            self.import_lego_games()
            
            messagebox.showinfo("Erfolg", f"Steam verbunden! {len(self.get_lego_games_from_steam())} LEGO Spiele gefunden.")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Steam-Verbindung fehlgeschlagen: {str(e)}")
    
    def find_steam_installation(self):
        """Findet Steam-Installation über Registry"""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam") as key:
                install_path = winreg.QueryValueEx(key, "InstallPath")[0]
                return install_path
        except:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Valve\Steam") as key:
                    install_path = winreg.QueryValueEx(key, "InstallPath")[0]
                    return install_path
            except:
                return None
    
    def get_steam_library_paths(self):
        """Holt alle Steam Library Pfade"""
        library_paths = []
        
        # Haupt-Library
        main_library = os.path.join(self.steam_path, "steamapps")
        if os.path.exists(main_library):
            library_paths.append(main_library)
        
        # Additional Libraries aus libraryfolders.vdf
        libraryfolders_path = os.path.join(self.steam_path, "steamapps", "libraryfolders.vdf")
        if os.path.exists(libraryfolders_path):
            try:
                with open(libraryfolders_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Besserer VDF Parser
                    import re
                    paths = re.findall(r'"path"\s*"([^"]+)"', content)
                    for path in paths:
                        library_path = os.path.join(path, "steamapps")
                        if os.path.exists(library_path) and library_path not in library_paths:
                            library_paths.append(library_path)
            except:
                pass
        
        return library_paths
    
    def get_lego_games_from_steam(self):
        """Findet alle LEGO Spiele in Steam Libraries"""
        lego_games = []
        library_paths = self.get_steam_library_paths()
        
        for library_path in library_paths:
            manifest_dir = os.path.join(library_path, "common")
            if os.path.exists(manifest_dir):
                for folder in os.listdir(manifest_dir):
                    if "lego" in folder.lower():
                        game_path = os.path.join(manifest_dir, folder)
                        if os.path.isdir(game_path):
                            # Finde .exe Datei
                            exe_files = [f for f in os.listdir(game_path) if f.endswith('.exe')]
                            if exe_files:
                                # Finde AppID aus Manifest
                                app_id = self.find_game_app_id(folder)
                                steam_stats = self.get_steam_game_stats(app_id) if app_id else None
                                
                                lego_games.append({
                                    'name': folder.replace('_', ' ').title(),
                                    'path': os.path.join(game_path, exe_files[0]),
                                    'folder': folder,
                                    'app_id': app_id,
                                    'steam_stats': steam_stats
                                })
        
        return lego_games
    
    def import_lego_games(self):
        """Importiert LEGO Spiele aus Steam"""
        if not self.steam_connected:
            messagebox.showerror("Fehler", "Bitte zuerst mit Steam verbinden!")
            return
        
        try:
            lego_games = self.get_lego_games_from_steam()
            
            if not lego_games:
                messagebox.showinfo("Info", "Keine LEGO Spiele in Steam gefunden!")
                return
            
            imported_count = 0
            
            for game_info in lego_games:
                # Prüfe ob Spiel schon existiert
                if not any(g.game_name == game_info['name'] for g in self.games):
                    print(f"\n=== Importiere Spiel: {game_info['name']} ===")
                    
                    # Hole Steam Stats
                    steam_stats = self.get_steam_game_stats(game_info.get('app_id'))
                    playtime = steam_stats.get('playtime_forever', 0) // 60 if steam_stats else 0
                    last_played = datetime.fromtimestamp(steam_stats.get('rtime_last_played', 0)).isoformat() if steam_stats and steam_stats.get('rtime_last_played', 0) > 0 else ""
                    
                    # Erstelle neues Spiel
                    new_game = ZGFile(
                        game_name=game_info['name'],
                        player_stats={
                            "path": game_info['path'],
                            "executable": os.path.basename(game_info['path']),
                            "steam_folder": game_info['folder'],
                            "app_id": game_info.get('app_id', ""),
                            "steam_playtime": steam_stats.get('playtime_forever', 0),
                            "steam_last_played": steam_stats.get('rtime_last_played', 0)
                        },
                        achievements=[],
                        playtime=playtime,
                        last_played=last_played
                    )
                    
                    filename = f"lego_{game_info['name'].lower().replace(' ', '_')}"
                    self.file_manager.save_zg(new_game, filename)
                    self.games.append(new_game)
                    print(f"✅ Spiel gespeichert: {filename}.zg")
                    
                    # Versuche Icon zu importieren (von .exe)
                    print(f"🎮 Versuche Icon zu importieren...")
                    self.import_exe_icon(game_info)
                    imported_count += 1
                else:
                    print(f"⚠️ Spiel existiert schon: {game_info['name']}")
        
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Import: {str(e)}")
            print(f"Import Fehler: {e}")
        
        self.refresh_game_list()
        messagebox.showinfo("Erfolg", f"{imported_count} LEGO Spiele importiert!")
    
    def get_steam_icon_path(self, game_name):
        """Holt Icon-Pfad für ein Spiel"""
        for game in self.games:
            if game.game_name == game_name:
                steam_folder = game.player_stats.get('steam_folder')
                if steam_folder:
                    # Suche Icon im Steam-Ordner
                    library_paths = self.get_steam_library_paths()
                    for library_path in library_paths:
                        game_folder = os.path.join(library_path, "common", steam_folder)
                        if os.path.exists(game_folder):
                            icon_files = [f for f in os.listdir(game_folder) if f.endswith(('.png', '.jpg', '.ico'))]
                            if icon_files:
                                return os.path.join(game_folder, icon_files[0])
        return None
    
    def import_exe_icon(self, game_info):
        """Importiert Icon direkt von .exe Datei"""
        try:
            exe_path = game_info['path']
            if os.path.exists(exe_path):
                print(f"Versuche Icon zu extrahieren aus: {exe_path}")
                
                # Icon aus .exe extrahieren
                icon_data = self.extract_icon_from_exe(exe_path)
                if icon_data:
                    # JF Datei erstellen
                    icon_filename = f"icon_{game_info['name'].lower().replace(' ', '_')}"
                    
                    icon_file = JFFile(
                        file_id=icon_filename,
                        original_name=f"{game_info['name']}_icon.png",
                        file_type="icon",
                        content=icon_data,
                        metadata={"source": "exe", "game": game_info['name'], "exe_path": exe_path},
                        created_date=datetime.now().isoformat()
                    )
                    
                    # Speichern mit Debug
                    print(f"Versuche .jf zu speichern: {icon_filename}")
                    try:
                        saved_path = self.file_manager.save_jf(icon_file, icon_filename)
                        print(f"✅ Icon als .jf gespeichert: {saved_path}")
                        
                        # Überprüfen ob Datei existiert
                        if os.path.exists(saved_path):
                            print(f"✅ .jf Datei existiert: {saved_path}")
                            print(f"📁 Dateigröße: {os.path.getsize(saved_path)} Bytes")
                            
                            # Teste ob wir es laden können
                            try:
                                test_load = self.file_manager.load_jf(icon_filename)
                                print(f"✅ .jf Datei kann geladen werden: {len(test_load.content)} Bytes")
                            except Exception as e:
                                print(f"❌ .jf Datei kann nicht geladen werden: {e}")
                        else:
                            print(f"❌ .jf Datei nicht gefunden: {saved_path}")
                            
                    except Exception as save_error:
                        print(f"❌ Fehler beim Speichern der .jf Datei: {save_error}")
                        
                else:
                    print(f"❌ Kein Icon gefunden für: {game_info['name']}")
            else:
                print(f"❌ .exe Datei nicht gefunden: {exe_path}")
                
        except Exception as e:
            print(f"❌ Fehler beim Icon-Import für {game_info['name']}: {e}")
            # Fallback zu Steam Icon
            self.import_steam_icon(game_info)
    
    def import_steam_icon(self, game_info):
        """Importiert Icon aus Steam"""
        try:
            print(f"Versuche Steam Icon für: {game_info['name']}")
            
            # Suche nach Icon-Dateien
            game_folder = os.path.join(os.path.dirname(game_info['path']), '..')
            if os.path.exists(game_folder):
                icon_files = [f for f in os.listdir(game_folder) if f.endswith(('.png', '.jpg', '.ico'))]
                
                if icon_files:
                    icon_path = os.path.join(game_folder, icon_files[0])
                    print(f"Gefundenes Steam Icon: {icon_path}")
                    
                    with open(icon_path, 'rb') as f:
                        icon_data = f.read()
                    
                    # JF Datei erstellen
                    icon_filename = f"icon_{game_info['name'].lower().replace(' ', '_')}"
                    
                    icon_file = JFFile(
                        file_id=icon_filename,
                        original_name=icon_files[0],
                        file_type="icon",
                        content=icon_data,
                        metadata={"source": "steam", "game": game_info['name']},
                        created_date=datetime.now().isoformat()
                    )
                    
                    # Speichern
                    self.file_manager.save_jf(icon_file, icon_filename)
                    print(f"✅ Steam Icon als .jf gespeichert: {icon_filename}.jf")
                    
                    # Überprüfen ob Datei existiert
                    jf_path = os.path.join("jf", f"{icon_filename}.jf")
                    if os.path.exists(jf_path):
                        print(f"✅ Steam .jf Datei existiert: {jf_path}")
                        print(f"📁 Dateigröße: {os.path.getsize(jf_path)} Bytes")
                    else:
                        print(f"❌ Steam .jf Datei nicht gefunden: {jf_path}")
                else:
                    print(f"❌ Keine Steam Icons gefunden in: {game_folder}")
            else:
                print(f"❌ Steam Spiel-Ordner nicht gefunden: {game_folder}")
                
        except Exception as e:
            print(f"❌ Fehler beim Steam Icon Import: {e}")
    
    def find_game_app_id(self, folder_name):
        """Findet AppID für ein Spiel anhand des Ordnernamens"""
        try:
            library_paths = self.get_steam_library_paths()
            for library_path in library_paths:
                manifest_dir = os.path.join(library_path, "common", folder_name)
                if os.path.exists(manifest_dir):
                    # Suche nach .acf Datei
                    acf_files = [f for f in os.listdir(os.path.join(library_path, "appmanifest")) 
                                if f.startswith("appmanifest_") and f.endswith(".acf")]
                    
                    for acf_file in acf_files:
                        acf_path = os.path.join(library_path, "appmanifest", acf_file)
                        try:
                            with open(acf_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Parse ACF Datei
                                lines = content.split('\n')
                                for line in lines:
                                    if '"installdir"' in line and folder_name.lower() in line.lower():
                                        # Finde AppID in derselben Datei
                                        for other_line in lines:
                                            if '"appid"' in other_line:
                                                app_id = other_line.split('"')[3]
                                                print(f"AppID gefunden für {folder_name}: {app_id}")
                                                return int(app_id)
                        except:
                            continue
        except Exception as e:
            print(f"Fehler bei AppID Suche: {e}")
        return None
    
    def get_steam_game_stats(self, app_id):
        """Holt Spiel-Statistiken von Steam"""
        if not app_id:
            return None
            
        try:
            # Versuche Steam Userdaten zu finden
            steam_userdata_path = os.path.join(self.steam_path, "userdata")
            if not os.path.exists(steam_userdata_path):
                return None
            
            # Finde den ersten User-Ordner
            user_folders = [f for f in os.listdir(steam_userdata_path) if f.isdigit()]
            if not user_folders:
                return None
            
            user_folder = user_folders[0]
            config_path = os.path.join(steam_userdata_path, user_folder, "config", "localconfig.vdf")
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Suche nach Spiel-Stats
                import re
                pattern = rf'"{app_id}".*?\{{([^}}]+)\}}'
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    stats_str = match.group(1)
                    stats = {}
                    
                    # Parse Stats
                    for line in stats_str.split('\n'):
                        if '"' in line and ':' in line:
                            key_match = re.search(r'"([^"]+)"', line)
                            value_match = re.search(r'"([^"]+)"', line[line.find(':'):])
                            
                            if key_match and value_match:
                                key = key_match.group(1)
                                value = value_match.group(1)
                                
                                # Konvertiere zu Zahlen wenn möglich
                                try:
                                    if key in ['playtime_forever', 'rtime_last_played']:
                                        value = int(value)
                                except:
                                    pass
                                
                                stats[key] = value
                    
                    return stats
                    
        except Exception as e:
            print(f"Fehler beim Lesen Steam Stats: {e}")
            
        return None
    
    def extract_icon_from_exe(self, exe_path):
        """Extrahiert echtes Icon aus .exe Datei"""
        try:
            # Methode 1: PowerShell .NET Icon Extraktion
            from real_exe_icon import extract_real_exe_icon
            
            icon_data = extract_real_exe_icon(exe_path)
            if icon_data:
                print(f"Echtes .exe Icon extrahiert: {os.path.basename(exe_path)}")
                return icon_data
                
        except Exception as e:
            print(f"PowerShell Icon Fehler: {e}")
        
        # Methode 2: PIL direkt mit .exe (manchmal klappt es)
        try:
            img = Image.open(exe_path)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img = img.resize((128, 128), Image.Resampling.LANCZOS)
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            print(f"PIL .exe Icon geladen: {os.path.basename(exe_path)}")
            return img_bytes.getvalue()
        except:
            pass
        
        # Methode 3: Fallback Icon mit Spielnamen
        try:
            from real_exe_icon import create_fallback_icon
            
            icon_data = create_fallback_icon(exe_path)
            if icon_data:
                print(f"Fallback Icon erstellt: {os.path.basename(exe_path)}")
                return icon_data
                
        except Exception as e:
            print(f"Fallback Icon Fehler: {e}")
        
        # Methode 4: Letztes LEGO Icon
        try:
            img = Image.new('RGB', (128, 128), color='#ff6b35')
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            
            # LEGO Block zeichnen
            draw.rectangle([20, 20, 108, 108], fill='#e74c3c', outline='#c0392b', width=2)
            draw.rectangle([30, 30, 98, 98], fill='#ff6b35')
            
            # Nubs zeichnen
            for x in range(40, 90, 20):
                draw.ellipse([x-5, 25, x+5, 35], fill='#e74c3c')
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            print("Letztes LEGO Fallback Icon")
            return img_bytes.getvalue()
            
        except:
            pass
            
        return None

class GameDialog:
    def __init__(self, parent, title):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Spiel-Name
        tk.Label(self.dialog, text="Spiel-Name:", fg='white', bg='#2b2b2b').pack(pady=5)
        self.name_entry = tk.Entry(self.dialog, width=40)
        self.name_entry.pack(pady=5)
        
        # Spiel-Pfad
        tk.Label(self.dialog, text="Spiel-Pfad:", fg='white', bg='#2b2b2b').pack(pady=5)
        path_frame = tk.Frame(self.dialog, bg='#2b2b2b')
        path_frame.pack(pady=5)
        
        self.path_entry = tk.Entry(path_frame, width=35)
        self.path_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            path_frame,
            text="Durchsuchen",
            command=self.browse_file
        ).pack(side=tk.LEFT)
        
        # Kategorien
        tk.Label(self.dialog, text="Kategorien (komma-getrennt):", fg='white', bg='#2b2b2b').pack(pady=5)
        self.categories_entry = tk.Entry(self.dialog, width=40)
        self.categories_entry.pack(pady=5)
        self.categories_entry.insert(0, "LEGO, Action")
        
        # Buttons
        button_frame = tk.Frame(self.dialog, bg='#2b2b2b')
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="OK",
            command=self.ok_clicked,
            bg='#ff6b35',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Abbrechen",
            command=self.cancel_clicked,
            bg='#4a4a4a',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
    
    def browse_file(self):
        """Öffnet Datei-Dialog"""
        filename = filedialog.askopenfilename(
            title="Wähle Spiel-Datei",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )
        if filename:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, filename)
    
    def ok_clicked(self):
        """Speichert die Eingabe"""
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip()
        categories = [cat.strip() for cat in self.categories_entry.get().split(",") if cat.strip()]
        
        if name and path:
            self.result = (name, path, categories)
            self.dialog.destroy()
    
    def cancel_clicked(self):
        """Bricht ab"""
        self.dialog.destroy()

class CategoryDialog:
    def __init__(self, parent, categories, file_manager):
        self.categories = categories
        self.file_manager = file_manager
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Kategorien verwalten")
        self.dialog.geometry("400x400")
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        tk.Label(self.dialog, text="Kategorien:", font=('Arial', 14, 'bold'), fg='white', bg='#2b2b2b').pack(pady=10)
        
        # Kategorien-Liste
        self.listbox = tk.Listbox(self.dialog, bg='#3a3a3a', fg='white')
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for category in self.categories:
            self.listbox.insert(tk.END, category.group_name)
        
        # Eingabe für neue Kategorie
        input_frame = tk.Frame(self.dialog, bg='#2b2b2b')
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(input_frame, text="Neue Kategorie:", fg='white', bg='#2b2b2b').pack(side=tk.LEFT)
        self.entry = tk.Entry(input_frame, width=20)
        self.entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = tk.Frame(self.dialog, bg='#2b2b2b')
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Hinzufügen", command=self.add_category, bg='#ff6b35', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Löschen", command=self.delete_category, bg='#ff4444', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Schließen", command=self.dialog.destroy, bg='#4a4a4a', fg='white').pack(side=tk.LEFT, padx=2)
    
    def add_category(self):
        """Fügt neue Kategorie hinzu"""
        name = self.entry.get().strip()
        if name:
            new_category = PGFile(
                group_name=name,
                members=[],
                group_type="category",
                created_date=datetime.now().isoformat(),
                permissions={"admin": [], "member": []}
            )
            
            filename = f"category_{name.lower().replace(' ', '_')}"
            self.file_manager.save_pg(new_category, filename)
            
            self.listbox.insert(tk.END, name)
            self.entry.delete(0, tk.END)
    
    def delete_category(self):
        """Löscht ausgewählte Kategorie"""
        selection = self.listbox.curselection()
        if selection:
            category_name = self.listbox.get(selection[0])
            
            # Lösche Datei
            filename = f"category_{category_name.lower().replace(' ', '_')}"
            self.file_manager.delete_file("pg", filename)
            
            # Entferne aus Liste
            self.listbox.delete(selection[0])

class SettingsDialog:
    def __init__(self, parent, settings, file_manager):
        self.settings = settings
        self.file_manager = file_manager
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Einstellungen")
        self.dialog.geometry("400x350")
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        tk.Label(self.dialog, text="Launcher-Einstellungen", font=('Arial', 14, 'bold'), fg='white', bg='#2b2b2b').pack(pady=10)
        
        # Close on Launch
        self.close_var = tk.BooleanVar(value=self.settings.content.get("close_on_launch", False))
        tk.Checkbutton(
            self.dialog,
            text="Launcher nach Spiel-Start schließen",
            variable=self.close_var,
            fg='white',
            bg='#2b2b2b',
            selectcolor='#3a3a3a'
        ).pack(pady=10)
        
        # Steam Auto-Launch
        self.steam_var = tk.BooleanVar(value=self.settings.content.get("steam_auto_launch", True))
        tk.Checkbutton(
            self.dialog,
            text="Steam automatisch starten",
            variable=self.steam_var,
            fg='white',
            bg='#2b2b2b',
            selectcolor='#3a3a3a'
        ).pack(pady=10)
        
        # Theme
        tk.Label(self.dialog, text="Theme:", fg='white', bg='#2b2b2b').pack(pady=5)
        self.theme_var = tk.StringVar(value=self.settings.content.get("theme", "dark"))
        theme_combo = ttk.Combobox(
            self.dialog,
            textvariable=self.theme_var,
            values=["dark", "light"],
            state="readonly"
        )
        theme_combo.pack(pady=5)
        
        # Auto-Import LEGO Spiele
        self.auto_import_var = tk.BooleanVar(value=self.settings.content.get("auto_import_lego", True))
        tk.Checkbutton(
            self.dialog,
            text="LEGO Spiele automatisch importieren",
            variable=self.auto_import_var,
            fg='white',
            bg='#2b2b2b',
            selectcolor='#3a3a3a'
        ).pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(self.dialog, bg='#2b2b2b')
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="💾 Speichern",
            command=self.save_settings,
            bg='#ff6b35',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Abbrechen",
            command=self.cancel_clicked,
            bg='#4a4a4a',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="🔄 Zurücksetzen",
            command=self.reset_settings,
            bg='#ff4444',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
    
    def save_settings(self):
        """Speichert die Einstellungen"""
        self.settings.content["close_on_launch"] = self.close_var.get()
        self.settings.content["steam_auto_launch"] = self.steam_var.get()
        self.settings.content["theme"] = self.theme_var.get()
        self.settings.content["auto_import_lego"] = self.auto_import_var.get()
        
        self.file_manager.save_zd(self.settings, "launcher_settings")
        
        messagebox.showinfo("Erfolg", "Einstellungen wurden gespeichert!")
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Bricht ab"""
        self.dialog.destroy()
    
    def reset_settings(self):
        """Setzt Einstellungen zurück"""
        result = messagebox.askyesno("Zurücksetzen", "Alle Einstellungen zurücksetzen?")
        if result:
            self.close_var.set(False)
            self.steam_var.set(True)
            self.theme_var.set("dark")
            self.auto_import_var.set(True)

if __name__ == "__main__":
    import io  # Für Bild-Handling
    
    launcher = LegoGameLauncher()
    launcher.run()
