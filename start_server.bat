@echo off
echo 🎙️ Iniciando Asistente de Voz de Movilidad Urbana - Valencia
echo ============================================================

:: Activar entorno virtual
echo 🔧 Activando entorno virtual...
call .venv\Scripts\activate.bat

:: Verificar configuración
echo 🔧 Verificando configuración...
python test_server.py

:: Iniciar servidor
echo 🚀 Iniciando servidor Django...
echo.
echo 📋 URLs disponibles:
echo    🌐 Admin: http://localhost:8000/admin/
echo    🚌 API Paradas: http://localhost:8000/api/mobility/parada-cercana/?lat=39.4699^&lon=-0.3763
echo    🎤 API Voz: http://localhost:8000/api/mobility/consulta-voz/
echo.
echo ⚠️  Para detener el servidor: Ctrl+C
echo.

python manage.py runserver

pause 