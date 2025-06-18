"""
Comando de gestión para configurar y verificar el servidor del asistente de voz.
Uso: python manage.py setup_server
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Configura y verifica el servidor del asistente de voz'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-admin',
            action='store_true',
            help='Crear usuario administrador'
        )
        parser.add_argument(
            '--test-urls',
            action='store_true', 
            help='Probar que las URLs funcionan'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🎙️ Configurando servidor del asistente de voz...\n')
        )
        
        # Crear administrador si se solicita
        if options['create_admin']:
            self.create_admin_user()
        
        # Probar URLs si se solicita
        if options['test_urls']:
            self.test_urls()
        
        # Si no se especifica nada, hacer todo
        if not options['create_admin'] and not options['test_urls']:
            self.create_admin_user()
            self.test_urls()
        
        self.show_final_info()
    
    def create_admin_user(self):
        """Crear usuario administrador"""
        self.stdout.write('🔧 Configurando usuario administrador...')
        
        try:
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@aura-voice.com',
                    password='admin123'
                )
                self.stdout.write(
                    self.style.SUCCESS('✅ Usuario administrador creado: admin/admin123')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️  Usuario administrador ya existe')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creando administrador: {e}')
            )
    
    def test_urls(self):
        """Probar que las URLs funcionan correctamente"""
        self.stdout.write('\n🔧 Verificando endpoints del asistente de voz...')
        
        client = Client()
        
        # URLs a probar
        test_cases = [
            {
                'url': '/admin/',
                'method': 'GET',
                'description': 'Panel de administración',
                'expected_codes': [200, 302]
            },
            {
                'url': '/api/mobility/parada-cercana/',
                'method': 'GET',
                'description': 'API paradas cercanas',
                'expected_codes': [400, 401]  # 400 porque faltan parámetros
            },
            {
                'url': '/api/mobility/trafico/',
                'method': 'GET', 
                'description': 'API estado tráfico',
                'expected_codes': [400, 401]  # 400 porque faltan parámetros
            },
            {
                'url': '/api/mobility/accesibilidad/',
                'method': 'GET',
                'description': 'API información accesibilidad', 
                'expected_codes': [400, 401]  # 400 porque faltan parámetros
            },
            {
                'url': '/api/mobility/consulta-voz/',
                'method': 'POST',
                'description': 'API consulta de voz completa',
                'expected_codes': [400, 401, 405]  # Métodos/auth requeridos
            }
        ]
        
        for test in test_cases:
            try:
                if test['method'] == 'GET':
                    response = client.get(test['url'])
                else:
                    response = client.post(test['url'])
                
                status_code = response.status_code
                
                if status_code in test['expected_codes']:
                    status_icon = '✅'
                    status_text = 'OK'
                else:
                    status_icon = '⚠️'
                    status_text = f'Código inesperado: {status_code}'
                
                self.stdout.write(
                    f'   {status_icon} {test["description"]}: {test["url"]} - {status_text}'
                )
                
            except Exception as e:
                self.stdout.write(
                    f'   ❌ {test["description"]}: {test["url"]} - Error: {e}'
                )
    
    def show_final_info(self):
        """Mostrar información final de configuración"""
        self.stdout.write(
            self.style.SUCCESS('\n🚀 ¡Configuración del servidor completada!')
        )
        
        self.stdout.write('\n📋 Información de acceso:')
        self.stdout.write('   👤 Usuario: admin')
        self.stdout.write('   🔑 Contraseña: admin123')
        
        self.stdout.write('\n🌐 URLs principales:')
        self.stdout.write('   🏠 Panel Admin: http://localhost:8000/admin/')
        self.stdout.write('   🚌 API Paradas: http://localhost:8000/api/mobility/parada-cercana/?lat=39.4699&lon=-0.3763')
        self.stdout.write('   🚦 API Tráfico: http://localhost:8000/api/mobility/trafico/?zona=Ruzafa')
        self.stdout.write('   ♿ API Accesibilidad: http://localhost:8000/api/mobility/accesibilidad/?lugar=Museo IVAM')
        self.stdout.write('   🎤 API Voz: http://localhost:8000/api/mobility/consulta-voz/ (POST)')
        
        self.stdout.write('\n🔧 Comandos útiles:')
        self.stdout.write('   📊 Shell Django: python manage.py shell')
        self.stdout.write('   🧹 Limpiar archivos: python manage.py cleanup_voice_files --force')
        self.stdout.write('   ✅ Verificar config: python manage.py check')
        
        self.stdout.write(
            self.style.WARNING('\n⚠️  IMPORTANTE: Cambiar contraseña de admin en producción')
        ) 