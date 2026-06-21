@echo off
setlocal

REM ============================================================
REM  DesktopPet exe 빌드 스크립트
REM  - onedir 모드
REM  - 안 쓰는 Qt 모듈 제외
REM ============================================================

REM 1) 필요한 패키지 설치
pip install --upgrade pyinstaller psutil PySide6

REM 2) 이전 빌드 결과물 정리 (선택)
rmdir /s /q build  2>nul
rmdir /s /q dist   2>nul

REM 3) 빌드
pyinstaller --onedir --windowed --noconfirm ^
  --name DesktopPet ^
  --add-data "assets;assets" ^
  --exclude-module PySide6.QtWebEngineWidgets ^
  --exclude-module PySide6.QtWebEngineCore ^
  --exclude-module PySide6.QtMultimedia ^
  --exclude-module PySide6.QtNetwork ^
  --exclude-module PySide6.QtSql ^
  --exclude-module PySide6.QtQml ^
  --exclude-module PySide6.QtQuick ^
  --exclude-module PySide6.QtPdf ^
  --exclude-module PySide6.QtBluetooth ^
  --exclude-module PySide6.QtSerialPort ^
  --exclude-module PySide6.QtPositioning ^
  --exclude-module PySide6.QtSensors ^
  --exclude-module PySide6.QtTest ^
  --exclude-module PySide6.QtDesigner ^
  --exclude-module PySide6.QtHelp ^
  main.py

echo.
echo ============================================================
echo 빌드 완료. dist\DesktopPet\DesktopPet.exe 를 실행해 확인하세요.
echo 배포할 때는 DesktopPet.exe만 옮기면 안 되고,
echo dist\DesktopPet 폴더 전체를 같이 옮겨야 합니다 (DLL/리소스 포함).
echo ============================================================
pause