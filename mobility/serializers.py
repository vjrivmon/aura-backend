"""
Serializadores para la aplicación Mobility.
Define la serialización de modelos y validación de datos para la API REST.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import VoiceQuery, ApiCache, UserPreferences


class VoiceQuerySerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo VoiceQuery.
    Incluye información completa de las consultas de voz para analíticas.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    query_type_display = serializers.CharField(source='get_query_type_display', read_only=True)
    
    class Meta:
        model = VoiceQuery
        fields = [
            'id', 'user', 'user_username', 'query_type', 'query_type_display',
            'original_text', 'response_text', 'processing_time', 'success',
            'error_message', 'latitude', 'longitude', 'created_at'
        ]
        read_only_fields = ['created_at']


class UserPreferencesSerializer(serializers.ModelSerializer):
    """
    Serializador para las preferencias del usuario.
    """
    class Meta:
        model = UserPreferences
        fields = [
            'user', 'preferred_transport', 'max_walking_distance',
            'voice_speed', 'include_accessibility_info',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """
        Crea preferencias del usuario autenticado.
        """
        request = self.context['request']
        validated_data['user'] = request.user
        return super().create(validated_data)


class VoiceQueryRequestSerializer(serializers.Serializer):
    """
    Serializador para validar requests de consultas de voz.
    """
    audio_file = serializers.FileField(
        help_text="Archivo de audio en formato WAV, MP3 u OGG"
    )
    lat = serializers.FloatField(
        required=False, 
        min_value=-90, 
        max_value=90,
        help_text="Latitud actual del usuario"
    )
    lon = serializers.FloatField(
        required=False, 
        min_value=-180, 
        max_value=180,
        help_text="Longitud actual del usuario"
    )
    
    def validate_audio_file(self, value):
        """
        Valida el archivo de audio.
        """
        # Verificar tamaño (máximo 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("El archivo de audio no puede exceder 10MB")
        
        # Verificar extensión
        valid_extensions = ['.wav', '.mp3', '.ogg', '.m4a']
        file_extension = '.' + value.name.split('.')[-1].lower()
        
        if file_extension not in valid_extensions:
            raise serializers.ValidationError(
                f"Formato no soportado. Use: {', '.join(valid_extensions)}"
            )
        
        return value


class VoiceQueryResponseSerializer(serializers.Serializer):
    """
    Serializador para las respuestas de consultas de voz.
    """
    success = serializers.BooleanField()
    recognized_text = serializers.CharField(required=False)
    intent = serializers.DictField(required=False)
    response_text = serializers.CharField(required=False)
    audio_response = serializers.DictField(required=False)
    processing_time_seconds = serializers.FloatField(required=False)
    data = serializers.DictField(required=False)
    error = serializers.CharField(required=False)


class ParadaCercanaRequestSerializer(serializers.Serializer):
    """
    Serializador para requests de parada cercana.
    """
    lat = serializers.FloatField(min_value=-90, max_value=90)
    lon = serializers.FloatField(min_value=-180, max_value=180)
    radio = serializers.IntegerField(min_value=50, max_value=2000, default=300)


class RutaRequestSerializer(serializers.Serializer):
    """
    Serializador para requests de cálculo de ruta.
    """
    origen_lat = serializers.FloatField(min_value=-90, max_value=90)
    origen_lon = serializers.FloatField(min_value=-180, max_value=180)
    destino_lat = serializers.FloatField(min_value=-90, max_value=90)
    destino_lon = serializers.FloatField(min_value=-180, max_value=180)
    modo = serializers.ChoiceField(
        choices=['foot', 'driving', 'cycling'], 
        default='foot'
    )


class TraficoRequestSerializer(serializers.Serializer):
    """
    Serializador para requests de estado del tráfico.
    """
    zona = serializers.CharField(max_length=100)


class AccesibilidadRequestSerializer(serializers.Serializer):
    """
    Serializador para requests de información de accesibilidad.
    """
    lugar = serializers.CharField(max_length=200)


class GeocodificarRequestSerializer(serializers.Serializer):
    """
    Serializador para requests de geocodificación.
    """
    direccion = serializers.CharField(max_length=300)
    valencia_bias = serializers.BooleanField(default=True) 