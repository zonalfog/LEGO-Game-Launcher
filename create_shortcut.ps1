
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("C:\Users\jayde\Desktop\LEGO Game Launcher.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-NoExit -Command \"cd \"C:\Users\jayde\Desktop\Project\"; python lego_game_launcher.py\""
$Shortcut.WorkingDirectory = "C:\Users\jayde\Desktop\Project"
$Shortcut.IconLocation = "shell32.dll,44"
$Shortcut.Description = "LEGO Game Launcher"
$Shortcut.Save()
