#!/usr/bin/env python
"""
Script de configuración completa para el Asistente de Voz de Movilidad Urbana - Valencia
Implementa todas las funcionalidades descritas en la guía técnica.

Uso: python setup_voice_assistant.py [--install-deps] [--create-superuser]
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(message):
    print(f"{Colors.OKCYAN}🔧 {message}{Colors.ENDC}")

def print_success(message):
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def run_command(command, description=""):
    """Ejecuta un comando y maneja errores."""
    try:
        print_step(f"Ejecutando: {description or command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Error en comando: {command}")
        if e.stderr:
            print(e.stderr)
        return False

def check_python_version():
    """Verifica la versión de Python."""
    print_step("Verificando versión de Python...")
    if sys.version_info < (3, 8):
        print_error("Se requiere Python 3.8 o superior")
        return False
    print_success(f"Python {sys.version.split()[0]} ✓")
    return True

def create_directories():
    """Crea directorios necesarios para el asistente de voz."""
    print_step("Creando directorios necesarios...")
    directories = [
        "media/audio",
        "media/temp_audio", 
        "models",
        "logs",
        "staticfiles"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print_success(f"Directorio creado: {directory}")

def install_dependencies():
    """Instala las dependencias del proyecto."""
    print_step("Instalando dependencias...")
    
    # Verificar si estamos en un entorno virtual
    if sys.prefix == sys.base_prefix:
        print_warning("No estás en un entorno virtual. Se recomienda usar uno.")
        response = input("¿Continuar de todos modos? (y/N): ")
        if response.lower() not in ['y', 'yes', 'sí', 'si']:
            return False
    
    # Instalar python-decouple primero
    if not run_command("pip install python-decouple", "Instalando python-decouple"):
        return False
    
    # Instalar todas las dependencias
    if not run_command("pip install -r requirements.txt", "Instalando dependencias desde requirements.txt"):
        return False
    
    print_success("Dependencias instaladas correctamente")
    return True

def setup_database():
    """Configura la base de datos."""
    print_step("Configurando base de datos...")
    
    # Crear migraciones
    if not run_command("python manage.py makemigrations", "Creando migraciones"):
        return False
    
    if not run_command("python manage.py makemigrations core", "Creando migraciones para core"):
        return False
        
    if not run_command("python manage.py makemigrations mobility", "Creando migraciones para mobility"):
        return False
    
    # Aplicar migraciones
    if not run_command("python manage.py migrate", "Aplicando migraciones"):
        return False
    
    print_success("Base de datos configurada")
    return True

def create_env_file():
    """Crea archivo .env con configuración básica."""
    print_step("Creando archivo de configuración .env...")
    
    env_content = """# Configuración del Asistente de Voz de Movilidad Urbana - Valencia
# Copia este archivo a .env y ajusta los valores según tu entorno

# Configuración Django
SECRET_KEY=django-insecure-voice-assistant-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (SQLite por defecto)
# Para producción, configurar PostgreSQL si se desea

# APIs externas
VALENCIA_OPENDATA_API_KEY=
OSRM_API_KEY=

# Configuración de voz
VOSK_MODEL_LANGUAGE=es
TTS_LANGUAGE=es
TTS_SPEED=normal

# Logging
LOG_LEVEL=INFO
"""
    
    env_file = Path(".env.example")
    env_file.write_text(env_content, encoding='utf-8')
    
    if not Path(".env").exists():
        Path(".env").write_text(env_content, encoding='utf-8')
        print_success("Archivo .env creado")
    else:
        print_warning("Archivo .env ya existe, no se sobrescribió")
    
    print_success("Archivo .env.example creado como plantilla")

def download_vosk_model():
    """Descarga el modelo de Vosk en español."""
    print_step("Verificando modelo de voz Vosk...")
    
    model_path = Path("models/vosk-model-es")
    if model_path.exists():
        print_success("Modelo Vosk ya existe")
        return True
    
    print_step("El modelo de Vosk se descargará automáticamente en el primer uso")
    print_warning("El modelo español de Vosk (~50MB) se descargará cuando sea necesario")
    return True

def create_superuser():
    """Crea un superusuario para Django admin."""
    print_step("¿Deseas crear un superusuario para acceder al panel de administración?")
    response = input("(y/N): ")
    
    if response.lower() in ['y', 'yes', 'sí', 'si']:
        return run_command("python manage.py createsuperuser", "Creando superusuario")
    
    return True

def run_checks():
    """Ejecuta verificaciones del proyecto."""
    print_step("Ejecutando verificaciones del proyecto...")
    
    if not run_command("python manage.py check", "Verificando configuración Django"):
        return False
    
    # Verificar que los servicios se puedan importar
    print_step("Verificando servicios del asistente de voz...")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        import django
        django.setup()
        
        from mobility.services import ValenciaOpenDataService
        from mobility.voice_services import VoiceServiceManager
        from mobility.nlp_service import SpanishNLPService
        
        print_success("Servicios importados correctamente")
        return True
    except Exception as e:
        print_error(f"Error importando servicios: {e}")
        return False

def print_final_instructions():
    """Imprime instrucciones finales."""
    print(f"\n{Colors.HEADER}🎉 ¡Configuración del Asistente de Voz completada!{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}📋 Próximos pasos:{Colors.ENDC}")
    print("1. Activar el entorno virtual si no lo has hecho:")
    print(f"   {Colors.OKCYAN}.venv/Scripts/Activate.ps1{Colors.ENDC} (Windows)")
    print(f"   {Colors.OKCYAN}source .venv/bin/activate{Colors.ENDC} (Linux/Mac)")
    
    print("\n2. Iniciar el servidor de desarrollo:")
    print(f"   {Colors.OKCYAN}python manage.py runserver{Colors.ENDC}")
    
    print("\n3. Probar los endpoints principales:")
    print(f"   🌐 Admin: {Colors.OKBLUE}http://localhost:8000/admin/{Colors.ENDC}")
    print(f"   🚌 Parada cercana: {Colors.OKBLUE}http://localhost:8000/api/mobility/parada-cercana/?lat=39.4699&lon=-0.3763{Colors.ENDC}")
    print(f"   🎤 Consulta de voz: {Colors.OKBLUE}POST http://localhost:8000/api/mobility/consulta-voz/{Colors.ENDC}")
    
    print(f"\n📚 {Colors.BOLD}Funcionalidades implementadas:{Colors.ENDC}")
    print("   ✅ Reconocimiento de voz offline (Vosk)")
    print("   ✅ Síntesis de voz (gTTS)")
    print("   ✅ Procesamiento NLP en español")
    print("   ✅ Integración con APIs de datos abiertos de Valencia")
    print("   ✅ Endpoints REST para paradas, rutas, tráfico y accesibilidad")
    print("   ✅ Panel de administración Django")
    print("   ✅ Sistema de caché y logging")
    
    print(f"\n🔧 {Colors.BOLD}Comandos útiles:{Colors.ENDC}")
    print(f"   🧹 Limpiar archivos: {Colors.OKCYAN}python manage.py cleanup_voice_files --force{Colors.ENDC}")
    print(f"   📊 Shell Django: {Colors.OKCYAN}python manage.py shell{Colors.ENDC}")
    print(f"   🗃️  Migraciones: {Colors.OKCYAN}python manage.py makemigrations && python manage.py migrate{Colors.ENDC}")

def main():
    """Función principal del script de configuración."""
    print(f"{Colors.HEADER}")
    print("🎙️ " + "="*60)
    print("   CONFIGURACIÓN ASISTENTE DE VOZ - MOVILIDAD URBANA VALENCIA")
    print("   Implementación completa según guía técnica")
    print("="*60)
    print(f"{Colors.ENDC}")
    
    # Argumentos de línea de comandos
    install_deps = "--install-deps" in sys.argv
    create_super = "--create-superuser" in sys.argv
    
    # Verificaciones iniciales
    if not check_python_version():
        sys.exit(1)
    
    # Crear directorios
    create_directories()
    
    # Instalar dependencias si se solicita
    if install_deps:
        if not install_dependencies():
            print_error("Error instalando dependencias")
            sys.exit(1)
    else:
        print_warning("Saltando instalación de dependencias (usar --install-deps)")
    
    # Crear archivo de configuración
    create_env_file()
    
    # Configurar base de datos
    if not setup_database():
        print_error("Error configurando base de datos")
        sys.exit(1)
    
    # Descargar modelo de voz
    download_vosk_model()
    
    # Ejecutar verificaciones
    if not run_checks():
        print_error("Error en verificaciones del proyecto")
        sys.exit(1)
    
    # Crear superusuario si se solicita
    if create_super:
        create_superuser()
    
    # Instrucciones finales
    print_final_instructions()

if __name__ == "__main__":
    main() 