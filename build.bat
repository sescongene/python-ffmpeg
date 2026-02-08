@echo off
echo Checking for PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

echo Building standalone executable...
python -m PyInstaller --noconfirm --onefile --windowed --name "VideoConverter" gui.py

if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b %errorlevel%
)

echo.
echo Build complete!
echo Your executable is located in: dist\VideoConverter.exe
echo.
pause
