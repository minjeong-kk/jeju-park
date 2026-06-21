@echo off
setlocal
cd /d "%~dp0"

echo [STEP 1] Checking Virtual Environment...
if exist env\Scripts\activate.bat (
    echo Found 'env' folder. Activating...
    call env\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    echo Found 'venv' folder. Activating...
    call venv\Scripts\activate.bat
) else (
    echo [NOTICE] Cannot find virtual environment. Creating 'env' folder now...
    python -m venv env
    if errorlevel 1 (
        echo [ERROR] Python is not installed or not in PATH!
        goto error_pause
    )
    call env\Scripts\activate.bat
)

echo [STEP 2] Updating Packages...
pip install --upgrade pyinstaller psutil PySide6
if errorlevel 1 (
    echo [ERROR] Failed to install packages!
    goto error_pause
)

echo [STEP 3] Starting PyInstaller Build...
pyinstaller --onedir --windowed --noconfirm --name DesktopPet --add-data "assets;assets" --exclude-module PySide6.QtWebEngineWidgets --exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.QtMultimedia --exclude-module PySide6.QtNetwork --exclude-module PySide6.QtSql --exclude-module PySide6.QtQml --exclude-module PySide6.QtQuick --exclude-module PySide6.QtPdf --exclude-module PySide6.QtBluetooth --exclude-module PySide6.QtSerialPort --exclude-module PySide6.QtPositioning --exclude-module PySide6.QtSensors --exclude-module PySide6.QtTest --exclude-module PySide6.QtDesigner --exclude-module PySide6.QtHelp main.py

echo ============================================================
echo BUILD SUCCESS! Check 'dist\DesktopPet' folder.
echo ============================================================
pause
exit /b

:error_pause
echo ------------------------------------------------------------
echo BUILD FAILED! Check the error message above.
echo ------------------------------------------------------------
pause