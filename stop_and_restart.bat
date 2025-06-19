@echo off
echo 🚨 DETENIENDO Y REINICIANDO SERVIDOR COMPLETO
echo ============================================

:: Matar cualquier proceso Django que esté corriendo
echo 🔫 Deteniendo procesos Django existentes...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

:: Activar entorno virtual
echo 🔧 Activando entorno virtual...
call .venv\Scripts\activate.bat

:: Ejecutar script de reinicio
echo 🔄 Ejecutando reinicio completo...
python restart_server.py

echo.
echo 🚀 INICIAR SERVIDOR AHORA:
echo    python manage.py runserver
echo.
echo 🌐 LUEGO IR A:
echo    http://localhost:8000/admin/
echo    Usuario: admin | Contraseña: admin123
echo.

pause 