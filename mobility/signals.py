"""
Señales para la aplicación Mobility.
Gestiona eventos automáticos del sistema como creación de usuarios, limpieza de archivos, etc.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
import os
import logging

from .models import UserPreferences, VoiceQuery

logger = logging.getLogger('mobility')


@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    """
    Crea automáticamente preferencias por defecto cuando se registra un nuevo usuario.
    """
    if created:
        try:
            UserPreferences.objects.create(
                user=instance,
                preferred_transport='walking',
                max_walking_distance=500,
                voice_speed='normal',
                include_accessibility_info=True
            )
            logger.info(f"Preferencias creadas para usuario: {instance.username}")
        except Exception as e:
            logger.error(f"Error creando preferencias para {instance.username}: {e}")


@receiver(post_delete, sender=VoiceQuery)
def cleanup_voice_query_files(sender, instance, **kwargs):
    """
    Limpia archivos asociados cuando se elimina una consulta de voz.
    Mantiene el sistema limpio de archivos huérfanos.
    """
    # Esta señal se puede usar para limpiar archivos de audio temporales
    # asociados a consultas específicas si los hubiera
    logger.info(f"Consulta de voz eliminada: {instance.id}")


# Función auxiliar para limpieza programada
def cleanup_old_audio_files():
    """
    Función para limpiar archivos de audio antiguos.
    Puede ser llamada desde un comando de gestión o tarea programada.
    """
    try:
        audio_dir = settings.AUDIO_OUTPUT_DIR
        temp_audio_dir = settings.MEDIA_ROOT / "temp_audio"
        
        import time
        current_time = time.time()
        max_age_seconds = 24 * 3600  # 24 horas
        
        deleted_count = 0
        
        # Limpiar archivos de audio generados por TTS
        if audio_dir.exists():
            for file_path in audio_dir.glob("tts_*.mp3"):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    file_path.unlink()
                    deleted_count += 1
        
        # Limpiar archivos temporales de audio
        if temp_audio_dir.exists():
            for file_path in temp_audio_dir.glob("*"):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > 3600:  # 1 hora para archivos temporales
                    file_path.unlink()
                    deleted_count += 1
        
        logger.info(f"Limpieza automática: {deleted_count} archivos eliminados")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error en limpieza automática de archivos: {e}")
        return 0 