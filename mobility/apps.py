"""
Configuración de la aplicación Mobility para el asistente de voz de movilidad urbana.
Esta aplicación gestiona todas las funcionalidades relacionadas con:
- Consultas de paradas de transporte público
- Cálculo de rutas
- Estado del tráfico
- Información de accesibilidad
- Integración con APIs de datos abiertos de Valencia
"""

from django.apps import AppConfig


class MobilityConfig(AppConfig):
    """
    Configuración de la aplicación Mobility.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mobility'
    verbose_name = 'Movilidad Urbana - Valencia'
    
    def ready(self):
        """
        Método ejecutado cuando la aplicación está lista.
        Aquí se pueden realizar configuraciones adicionales como:
        - Inicialización de modelos de Vosk
        - Configuración de directorios de audio
        - Validación de APIs externas
        """
        from . import signals  # Importar señales si las hay
        
        # Crear directorios necesarios para archivos de audio
        from django.conf import settings
        import os
        
        os.makedirs(settings.AUDIO_OUTPUT_DIR, exist_ok=True)
        os.makedirs(settings.MEDIA_ROOT / "temp_audio", exist_ok=True) 