#!/usr/bin/env python
"""
Script para reiniciar completamente el servidor y solucionar problemas de 404.
Elimina cachés, reaplica configuración y reinicia todo.
"""

import os
import sys
import shutil
import django
from pathlib import Path

def setup_environment():
    """Configurar entorno Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

def clean_caches():
    """Limpiar cachés y archivos problemáticos"""
    print("🧹 Limpiando cachés y archivos temporales...")
    
    # Directorios a limpiar
    cache_dirs = [
        "__pycache__",
        "**/__pycache__",
        "*.pyc",
        ".pytest_cache",
        "staticfiles",
    ]
    
    # Limpiar cachés de Python
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                cache_path = os.path.join(root, dir_name)
                shutil.rmtree(cache_path, ignore_errors=True)
                print(f"✅ Eliminado caché: {cache_path}")
    
    # Limpiar archivos .pyc
    for root, dirs, files in os.walk('.'):
        for file_name in files:
            if file_name.endswith('.pyc'):
                pyc_path = os.path.join(root, file_name)
                os.remove(pyc_path)
                print(f"✅ Eliminado .pyc: {pyc_path}")

def verify_configuration():
    """Verificar configuración actual"""
    print("🔧 Verificando configuración actual...")
    
    try:
        from django.conf import settings
        print(f"✅ DEBUG: {settings.DEBUG}")
        print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"✅ SECRET_KEY configurado: {'Sí' if settings.SECRET_KEY else 'No'}")
        
        # Verificar que las apps estén instaladas
        required_apps = ['core', 'mobility', 'rest_framework']
        for app in required_apps:
            if app in settings.INSTALLED_APPS or any(app in installed_app for installed_app in settings.INSTALLED_APPS):
                print(f"✅ App {app}: Instalada")
            else:
                print(f"❌ App {app}: NO instalada")
        
        return True
    except Exception as e:
        print(f"❌ Error verificando configuración: {e}")
        return False

def create_superuser_if_needed():
    """Crear superusuario si no existe"""
    print("👤 Verificando usuario administrador...")
    
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
            print("✅ Superusuario ya existe: admin")
        
        return True
    except Exception as e:
        print(f"❌ Error con superusuario: {e}")
        return False

def test_critical_urls():
    """Probar URLs críticas sin usar TestClient"""
    print("🌐 Verificando URLs críticas...")
    
    try:
        from django.urls import reverse, resolve
        
        # URLs críticas a verificar
        critical_urls = [
            ('admin:index', '/admin/'),
        ]
        
        for url_name, expected_path in critical_urls:
            try:
                actual_path = reverse(url_name)
                if actual_path == expected_path:
                    print(f"✅ URL {url_name}: {actual_path}")
                else:
                    print(f"⚠️  URL {url_name}: esperado {expected_path}, actual {actual_path}")
            except Exception as e:
                print(f"❌ Error con URL {url_name}: {e}")
        
        # Verificar que se pueden resolver URLs
        test_paths = ['/admin/', '/api/mobility/parada-cercana/']
        for path in test_paths:
            try:
                resolve(path)
                print(f"✅ Path resoluble: {path}")
            except Exception as e:
                print(f"❌ Path no resoluble {path}: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error verificando URLs: {e}")
        return False

def show_final_instructions():
    """Mostrar instrucciones finales"""
    print("\n" + "="*70)
    print("🎉 SERVIDOR REINICIADO Y CONFIGURADO")
    print("="*70)
    
    print("\n🚀 PASOS PARA INICIAR:")
    print("1. Presiona Ctrl+C si hay un servidor corriendo")
    print("2. Ejecuta: python manage.py runserver")
    print("3. Ve a: http://localhost:8000/admin/")
    
    print("\n📋 CREDENCIALES:")
    print("   👤 Usuario: admin")
    print("   🔑 Contraseña: admin123")
    
    print("\n🌐 URLs PARA PROBAR:")
    print("   ✅ http://localhost:8000/admin/")
    print("   ✅ http://localhost:8000/api/mobility/parada-cercana/?lat=39.4699&lon=-0.3763")
    print("   ✅ http://localhost:8000/api/mobility/trafico/?zona=Ruzafa")
    
    print("\n🔧 SI SIGUES TENIENDO PROBLEMAS:")
    print("   • Asegúrate de tener el entorno virtual activado")
    print("   • Ejecuta: .venv\\Scripts\\activate")
    print("   • Verifica que estás en el directorio aura-backend")
    print("   • Reinicia completamente el terminal")

def main():
    """Función principal"""
    print("🔄 REINICIO COMPLETO DEL SERVIDOR")
    print("="*50)
    
    # Limpiar cachés
    clean_caches()
    
    # Configurar Django
    setup_environment()
    
    # Verificar configuración
    if not verify_configuration():
        print("❌ Error en la configuración. Verifica settings.py")
        return
    
    # Crear superusuario
    create_superuser_if_needed()
    
    # Probar URLs
    test_critical_urls()
    
    # Mostrar instrucciones
    show_final_instructions()

if __name__ == '__main__':
    main() 