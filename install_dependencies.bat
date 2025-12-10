@echo off
chcp 65001 >nul
echo ========================================
echo Instalando dependencias del Analizador BBPP
echo ========================================
echo.

:: Verificar que Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en PATH
    echo.
    echo Por favor, instala Python desde: https://www.python.org/downloads/
    echo Asegúrate de marcar "Add Python to PATH" durante la instalación.
    pause
    exit /b 1
)

echo [1/4] Verificando Python...
python --version
echo.

echo [2/4] Actualizando pip...
python -m pip install --upgrade pip
echo.

echo [3/4] Instalando dependencias desde requirements.txt...
python -m pip install -r requirements.txt
echo.

echo [4/4] Instalando dependencias adicionales...
python -m pip install packaging openpyxl Pillow
echo.

echo ========================================
echo ✓ Dependencias instaladas correctamente
echo ========================================
echo.
echo Puedes cerrar esta ventana y ejecutar el Analizador BBPP.
pause
