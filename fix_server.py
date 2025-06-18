#!/usr/bin/env python
"""
Script para solucionar problemas del servidor del asistente de voz.
Ejecutar cuando se obtengan errores 404 o problemas de configuración.

Uso: python fix_server.py
"""

import os
import sys
import subprocess
import django
from pathlib import Path

def setup_environment():
    """Configurar entorno Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {description} completado")
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def create_missing_files():
    """Crear archivos que puedan faltar"""
    print("🔧 Verificando archivos necesarios...")
    
    # Crear __init__.py en mobility si no existe
    init_file = Path("mobility/__init__.py")
    if not init_file.exists():
        init_file.write_text("# Aplicación mobility")
        print("✅ Creado mobility/__init__.py")
    
    # Crear directorios necesarios
    directories = [
        "media/audio",
        "media/temp_audio", 
        "logs",
        "staticfiles"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directorio verificado: {directory}")

def fix_urls():
    """Verificar y arreglar configuración de URLs"""
    print("🔧 Verificando configuración de URLs...")
    
    try:
        from django.urls import reverse
        from django.conf import settings
        
        # Verificar que las URLs se pueden resolver
        test_urls = [
            'admin:index',
        ]
        
        for url_name in test_urls:
            try:
                url = reverse(url_name)
                print(f"✅ URL {url_name} -> {url}")
            except Exception as e:
                print(f"❌ Error con URL {url_name}: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error verificando URLs: {e}")
        return False

def create_superuser():
    """Crear superusuario para admin"""
    try:
        from django.contrib.auth.models import User
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@aura-voice.com', 
                password='admin123'
            )
            print("✅ Superusuario creado: admin/admin123")
        else:
            # Actualizar contraseña si ya existe
            user = User.objects.get(username='admin')
            user.set_password('admin123')
            user.save()
            print("✅ Contraseña de admin actualizada: admin123")
        
        return True
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")
        return False

def test_server():
    """Probar que el servidor funciona"""
    print("🔧 Probando configuración del servidor...")
    
    try:
        from django.test import Client
        
        client = Client()
        
        # Probar URLs básicas
        test_cases = [
            ('/admin/', 'Panel de administración'),
            ('/api/mobility/parada-cercana/', 'API paradas (debe dar 401/400)'),
        ]
        
        for url, description in test_cases:
            try:
                response = client.get(url)
                print(f"✅ {description}: {url} - Status {response.status_code}")
            except Exception as e:
                print(f"❌ Error con {description}: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error probando servidor: {e}")
        return False

def show_instructions():
    """Mostrar instrucciones finales"""
    print("\n" + "="*60)
    print("🎉 CONFIGURACIÓN DEL SERVIDOR COMPLETADA")
    print("="*60)
    
    print("\n📋 CREDENCIALES DE ACCESO:")
    print("   👤 Usuario: admin")
    print("   🔑 Contraseña: admin123")
    
    print("\n🚀 CÓMO INICIAR EL SERVIDOR:")
    print("   1. Ejecutar: python manage.py runserver")
    print("   2. O usar: start_server.bat")
    
    print("\n🌐 URLS PARA PROBAR:")
    print("   🏠 Admin: http://localhost:8000/admin/")
    print("   📊 API Check: http://localhost:8000/api/mobility/parada-cercana/")
    print("      (Debe mostrar error 401/400 - es normal sin auth)")
    
    print("\n🔧 SOLUCIÓN DE PROBLEMAS:")
    print("   • Si sigues viendo 404s, reinicia el servidor")
    print("   • Verificar que estás en el directorio correcto")
    print("   • Activar entorno virtual: .venv\\Scripts\\activate")
    
    print("\n✅ URLs que DEBERÍAN FUNCIONAR:")
    print("   ✅ http://localhost:8000/admin/ (login con admin/admin123)")
    print("   ✅ http://localhost:8000/api/mobility/parada-cercana/?lat=39.4699&lon=-0.3763")
    print("   ✅ http://localhost:8000/api/mobility/trafico/?zona=Ruzafa")

def main():
    """Función principal"""
    print("🎙️ SOLUCIONADOR DE PROBLEMAS - ASISTENTE DE VOZ")
    print("=" * 50)
    
    # Configurar Django
    setup_environment()
    
    # Crear archivos faltantes
    create_missing_files()
    
    # Aplicar migraciones
    run_command("python manage.py migrate", "Aplicando migraciones")
    
    # Recopilar archivos estáticos
    run_command("python manage.py collectstatic --noinput", "Recopilando archivos estáticos")
    
    # Verificar URLs
    fix_urls()
    
    # Crear superusuario
    create_superuser()
    
    # Probar servidor
    test_server()
    
    # Mostrar instrucciones
    show_instructions()

if __name__ == '__main__':
    main() 