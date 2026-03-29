@echo off
echo ========================================
echo    LEGO Launcher Log Extractor v1.0
echo ========================================
echo.

set ZPJ_DIR=zpj
set OUTPUT_DIR=extracted_logs

echo Erstelle Output-Verzeichnis...
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo.
echo Suche nach .zpj Log-Dateien...
if not exist "%ZPJ_DIR%" (
    echo FEHLER: zpj Ordner nicht gefunden!
    pause
    exit /b 1
)

set found_logs=0
for %%f in ("%ZPJ_DIR%\*.zpj") do (
    set found_logs=1
    echo.
    echo Extrahiere: %%~nf.zpj
    
    powershell -Command ^
        "$content = Get-Content '%%f' | ConvertFrom-Json; ^
         $logName = '%%~nf'; ^
         $outputFile = '%OUTPUT_DIR%\%%~nf_log.txt'; ^
         Add-Content $outputFile '========================================'; ^
         Add-Content $outputFile 'LEGO Launcher Log: %%~nf'; ^
         Add-Content $outputFile '========================================'; ^
         Add-Content $outputFile 'Erstellt: ' + $content.created_date; ^
         Add-Content $outputFile 'Anzahl Eintraege: ' + $content.entries.Count; ^
         Add-Content $outputFile ''; ^
         foreach ($entry in $content.entries) { ^
             Add-Content $outputFile ('[' + $entry.timestamp + '] ' + $entry.type.ToUpper() + ': ' + $entry.message); ^
             if ($entry.details) { ^
                 foreach ($key in $entry.details.Keys) { ^
                     Add-Content $outputFile ('  - ' + $key + ': ' + $entry.details[$key]); ^
                 } ^
             } ^
             Add-Content $outputFile ''; ^
         }; ^
         Write-Host 'Gespeichert als: %%~nf_log.txt'"
    
    echo   -> %%~nf_log.txt
)

if %found_logs%==0 (
    echo Keine .zpj Dateien gefunden!
) else (
    echo.
    echo ========================================
    echo Extraktion abgeschlossen!
    echo Logs gespeichert in: %OUTPUT_DIR%\
    echo ========================================
)

echo.
pause
