"""
Comando de gestión para limpiar archivos de audio y caché del asistente de voz.
Uso: python manage.py cleanup_voice_files [--force] [--max-age-hours=24]
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from mobility.models import ApiCache
from mobility.signals import cleanup_old_audio_files
import os
import time


class Command(BaseCommand):
    help = 'Limpia archivos de audio antiguos y caché expirado del asistente de voz'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la limpieza sin preguntar confirmación'
        )
        parser.add_argument(
            '--max-age-hours',
            type=int,
            default=24,
            help='Edad máxima de archivos en horas (default: 24)'
        )
        parser.add_argument(
            '--cleanup-cache',
            action='store_true',
            help='También limpia el caché expirado de APIs'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🗑️  Iniciando limpieza del asistente de voz...')
        )
        
        # Verificar configuración
        if not hasattr(settings, 'AUDIO_OUTPUT_DIR'):
            raise CommandError('AUDIO_OUTPUT_DIR no está configurado en settings')
        
        force = options['force']
        max_age_hours = options['max_age_hours']
        cleanup_cache = options['cleanup_cache']
        
        # Mostrar información de lo que se va a limpiar
        self._show_cleanup_info(max_age_hours, cleanup_cache)
        
        # Pedir confirmación si no se usa --force
        if not force:
            confirm = input('\n¿Continuar con la limpieza? [y/N]: ')
            if confirm.lower() not in ['y', 'yes', 'sí', 'si']:
                self.stdout.write(self.style.WARNING('Limpieza cancelada'))
                return
        
        # Realizar limpieza
        total_deleted = 0
        
        # 1. Limpiar archivos de audio
        self.stdout.write('\n📁 Limpiando archivos de audio...')
        audio_deleted = self._cleanup_audio_files(max_age_hours)
        total_deleted += audio_deleted
        
        # 2. Limpiar caché si se solicita
        if cleanup_cache:
            self.stdout.write('\n💾 Limpiando caché expirado...')
            cache_deleted = self._cleanup_expired_cache()
            self.stdout.write(
                f'   ✓ {cache_deleted} entradas de caché eliminadas'
            )
        
        # Resumen final
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Limpieza completada: {total_deleted} archivos eliminados'
            )
        )
    
    def _show_cleanup_info(self, max_age_hours, cleanup_cache):
        """
        Muestra información sobre lo que se va a limpiar.
        """
        self.stdout.write('\n📋 Información de limpieza:')
        self.stdout.write(f'   • Archivos de audio más antiguos que {max_age_hours} horas')
        self.stdout.write(f'   • Directorio TTS: {settings.AUDIO_OUTPUT_DIR}')
        self.stdout.write(f'   • Directorio temporal: {settings.MEDIA_ROOT}/temp_audio')
        
        if cleanup_cache:
            self.stdout.write('   • Caché expirado de APIs externas')
        
        # Mostrar estadísticas actuales
        self._show_current_stats()
    
    def _show_current_stats(self):
        """
        Muestra estadísticas actuales de archivos y caché.
        """
        try:
            # Contar archivos de audio
            audio_dir = settings.AUDIO_OUTPUT_DIR
            temp_dir = settings.MEDIA_ROOT / "temp_audio"
            
            audio_count = len(list(audio_dir.glob("tts_*.mp3"))) if audio_dir.exists() else 0
            temp_count = len(list(temp_dir.glob("*"))) if temp_dir.exists() else 0
            
            # Contar caché
            cache_count = ApiCache.objects.count()
            expired_cache = sum(1 for cache in ApiCache.objects.all() if cache.is_expired())
            
            self.stdout.write('\n📊 Estado actual:')
            self.stdout.write(f'   • Archivos TTS: {audio_count}')
            self.stdout.write(f'   • Archivos temporales: {temp_count}')
            self.stdout.write(f'   • Entradas de caché: {cache_count} (expiradas: {expired_cache})')
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'   ⚠️  Error obteniendo estadísticas: {e}')
            )
    
    def _cleanup_audio_files(self, max_age_hours):
        """
        Limpia archivos de audio antiguos.
        """
        try:
            audio_dir = settings.AUDIO_OUTPUT_DIR
            temp_dir = settings.MEDIA_ROOT / "temp_audio"
            
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            deleted_count = 0
            
            # Limpiar archivos TTS
            if audio_dir.exists():
                for file_path in audio_dir.glob("tts_*.mp3"):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        try:
                            file_path.unlink()
                            deleted_count += 1
                            self.stdout.write(f'   ✓ Eliminado: {file_path.name}')
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(f'   ⚠️  Error eliminando {file_path.name}: {e}')
                            )
            
            # Limpiar archivos temporales (más agresivo - 1 hora)
            temp_max_age = min(3600, max_age_seconds)  # Máximo 1 hora
            if temp_dir.exists():
                for file_path in temp_dir.glob("*"):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > temp_max_age:
                        try:
                            file_path.unlink()
                            deleted_count += 1
                            self.stdout.write(f'   ✓ Eliminado temporal: {file_path.name}')
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(f'   ⚠️  Error eliminando temporal {file_path.name}: {e}')
                            )
            
            self.stdout.write(f'   📁 {deleted_count} archivos de audio eliminados')
            return deleted_count
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error en limpieza de audio: {e}')
            )
            return 0
    
    def _cleanup_expired_cache(self):
        """
        Limpia entradas de caché expiradas.
        """
        try:
            deleted_count = 0
            for cache_obj in ApiCache.objects.all():
                if cache_obj.is_expired():
                    cache_key = cache_obj.cache_key[:50]  # Mostrar solo primeros 50 chars
                    cache_obj.delete()
                    deleted_count += 1
                    self.stdout.write(f'   ✓ Caché eliminado: {cache_key}...')
            
            return deleted_count
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error limpiando caché: {e}')
            )
            return 0 