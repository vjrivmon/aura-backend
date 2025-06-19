"""
Modelos para la aplicación Mobility.
Según la guía técnica, mantenemos la base de datos mínima.
Estos modelos sirven principalmente para logging y caché temporal opcional.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class VoiceQuery(models.Model):
    """
    Modelo para registrar las consultas de voz realizadas por los usuarios.
    Útil para analíticas y mejora del servicio.
    """
    QUERY_TYPES = [
        ('parada_cercana', 'Parada más cercana'),
        ('calculo_ruta', 'Cálculo de ruta'),
        ('estado_trafico', 'Estado del tráfico'),
        ('info_accesibilidad', 'Información de accesibilidad'),
        ('general', 'Consulta general'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="voice_queries",
        verbose_name="Usuario"
    )
    query_type = models.CharField(
        max_length=20,
        choices=QUERY_TYPES,
        verbose_name="Tipo de consulta"
    )
    original_text = models.TextField(
        verbose_name="Texto original (STT)",
        help_text="Texto obtenido del reconocimiento de voz"
    )
    response_text = models.TextField(
        verbose_name="Respuesta generada",
        help_text="Texto de respuesta antes de TTS"
    )
    processing_time = models.FloatField(
        verbose_name="Tiempo de procesamiento (segundos)",
        help_text="Tiempo total desde STT hasta TTS"
    )
    success = models.BooleanField(
        default=True,
        verbose_name="Consulta exitosa"
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Mensaje de error"
    )
    latitude = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Latitud de consulta"
    )
    longitude = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Longitud de consulta"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de consulta"
    )

    class Meta:
        verbose_name = "Consulta de Voz"
        verbose_name_plural = "Consultas de Voz"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.get_query_type_display()} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"


class ApiCache(models.Model):
    """
    Modelo opcional para caché temporal de respuestas de APIs externas.
    Evita realizar consultas repetidas a APIs de Valencia en corto tiempo.
    Solo para datos que no cambian frecuentemente (ej: paradas, lugares).
    """
    cache_key = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Clave de caché",
        help_text="Identificador único para la consulta cacheada"
    )
    cache_data = models.JSONField(
        verbose_name="Datos cacheados",
        help_text="Respuesta de la API almacenada en formato JSON"
    )
    expiry_time = models.DateTimeField(
        verbose_name="Hora de expiración",
        help_text="Momento en que el caché expira"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    class Meta:
        verbose_name = "Caché de API"
        verbose_name_plural = "Cachés de API"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Cache: {self.cache_key[:50]}..."

    def is_expired(self):
        """
        Verifica si el caché ha expirado.
        """
        return timezone.now() > self.expiry_time

    @classmethod
    def get_cache(cls, key):
        """
        Obtiene un valor del caché si existe y no ha expirado.
        """
        try:
            cache_obj = cls.objects.get(cache_key=key)
            if not cache_obj.is_expired():
                return cache_obj.cache_data
            else:
                # Eliminar caché expirado
                cache_obj.delete()
                return None
        except cls.DoesNotExist:
            return None

    @classmethod
    def set_cache(cls, key, data, expiry_minutes=30):
        """
        Establece un valor en el caché con tiempo de expiración.
        """
        expiry_time = timezone.now() + timezone.timedelta(minutes=expiry_minutes)
        
        # Actualizar o crear
        cache_obj, created = cls.objects.update_or_create(
            cache_key=key,
            defaults={
                'cache_data': data,
                'expiry_time': expiry_time
            }
        )
        return cache_obj


class UserPreferences(models.Model):
    """
    Preferencias del usuario para el asistente de voz.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="mobility_preferences",
        verbose_name="Usuario"
    )
    preferred_transport = models.CharField(
        max_length=20,
        choices=[
            ('walking', 'A pie'),
            ('cycling', 'Bicicleta'),
            ('public_transport', 'Transporte público'),
            ('car', 'Coche'),
        ],
        default='walking',
        verbose_name="Medio de transporte preferido"
    )
    max_walking_distance = models.IntegerField(
        default=500,
        verbose_name="Distancia máxima a pie (metros)",
        help_text="Distancia máxima que está dispuesto a caminar"
    )
    voice_speed = models.CharField(
        max_length=10,
        choices=[
            ('slow', 'Lenta'),
            ('normal', 'Normal'),
            ('fast', 'Rápida'),
        ],
        default='normal',
        verbose_name="Velocidad de voz"
    )
    include_accessibility_info = models.BooleanField(
        default=True,
        verbose_name="Incluir información de accesibilidad",
        help_text="Si incluir automáticamente información de accesibilidad en las respuestas"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Preferencias de Usuario"
        verbose_name_plural = "Preferencias de Usuarios"

    def __str__(self):
        return f"Preferencias de {self.user.username}" 