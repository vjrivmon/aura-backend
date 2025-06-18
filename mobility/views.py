"""
Vistas para los endpoints REST del asistente de voz de movilidad urbana.
Implementa los endpoints como puente hacia las APIs de Valencia según la guía técnica.
"""

import os
import time
import logging
from typing import Dict, Optional

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponse, FileResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, JSONParser

from .services import ValenciaOpenDataService, RoutingService, GeocodingService
from .voice_services import VoiceServiceManager
from .nlp_service import SpanishNLPService
from .models import VoiceQuery, UserPreferences

logger = logging.getLogger('mobility')


# ============================================================================
# ENDPOINTS DE DATOS DE MOVILIDAD (Puente a APIs de Valencia)
# ============================================================================

@api_view(['GET'])
@permission_classes([])  # API pública según guía técnica
def parada_cercana(request):
    """
    Endpoint GET /api/parada-cercana?lat={lat}&lon={lon}
    Implementa exactamente el ejemplo de la guía técnica.
    """
    lat = request.query_params.get('lat')
    lon = request.query_params.get('lon')
    
    if not lat or not lon:
        return Response(
            {"error": "Faltan coordenadas lat/lon"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return Response(
            {"error": "Coordenadas inválidas"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Usar el servicio como en la guía técnica
    valencia_service = ValenciaOpenDataService()
    result = valencia_service.get_parada_cercana(lat, lon)
    
    if result.get('error'):
        return Response(result, status=status.HTTP_404_NOT_FOUND)
    
    # Registrar consulta para analíticas (solo si hay usuario autenticado)
    if request.user.is_authenticated:
        try:
            VoiceQuery.objects.create(
                user=request.user,
                query_type='parada_cercana',
                original_text=f"Consulta parada cercana: {lat}, {lon}",
                response_text=str(result),
                processing_time=0.1,
                success=True,
                latitude=lat,
                longitude=lon
            )
        except Exception as e:
            logger.warning(f"Error registrando consulta: {e}")
    
    return Response(result)


@api_view(['GET'])
@permission_classes([])  # API pública según guía técnica
def calcular_ruta(request):
    """
    Endpoint GET /api/ruta?origen_lat={lat}&origen_lon={lon}&destino_lat={lat}&destino_lon={lon}
    Calcula ruta entre dos puntos usando OSRM.
    """
    origen_lat = request.query_params.get('origen_lat')
    origen_lon = request.query_params.get('origen_lon')
    destino_lat = request.query_params.get('destino_lat')
    destino_lon = request.query_params.get('destino_lon')
    modo = request.query_params.get('modo', 'foot')  # foot, driving, cycling
    
    # Validar parámetros
    required_params = [origen_lat, origen_lon, destino_lat, destino_lon]
    if not all(required_params):
        return Response(
            {"error": "Faltan parámetros: origen_lat, origen_lon, destino_lat, destino_lon"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        origen = (float(origen_lat), float(origen_lon))
        destino = (float(destino_lat), float(destino_lon))
    except ValueError:
        return Response(
            {"error": "Coordenadas inválidas"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Calcular ruta usando OSRM
    routing_service = RoutingService()
    result = routing_service.calcular_ruta(origen, destino, modo)
    
    if result.get('error'):
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    # Registrar consulta (solo si hay usuario autenticado)
    if request.user.is_authenticated:
        try:
            VoiceQuery.objects.create(
                user=request.user,
                query_type='calculo_ruta',
                original_text=f"Ruta desde {origen} hasta {destino}",
                response_text=result.get('resumen', ''),
                processing_time=0.2,
                success=True,
                latitude=origen[0],
                longitude=origen[1]
            )
        except Exception as e:
            logger.warning(f"Error registrando consulta: {e}")
    
    return Response(result)


@api_view(['GET'])
@permission_classes([])  # API pública según guía técnica
def estado_trafico(request):
    """
    Endpoint GET /api/trafico?zona={nombre_barrio}
    Obtiene estado del tráfico en una zona específica.
    """
    zona = request.query_params.get('zona')
    
    if not zona:
        return Response(
            {"error": "Falta parámetro: zona"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Consultar estado del tráfico
    valencia_service = ValenciaOpenDataService()
    result = valencia_service.get_estado_trafico(zona)
    
    # Registrar consulta (solo si hay usuario autenticado)
    if request.user.is_authenticated:
        try:
            VoiceQuery.objects.create(
                user=request.user,
                query_type='estado_trafico',
                original_text=f"Estado tráfico en {zona}",
                response_text=result.get('detalle', ''),
                processing_time=0.1,
                success=True
            )
        except Exception as e:
            logger.warning(f"Error registrando consulta: {e}")
    
    return Response(result)


@api_view(['GET'])
@permission_classes([])  # API pública según guía técnica
def informacion_accesibilidad(request):
    """
    Endpoint GET /api/accesibilidad?lugar={nombre}
    Obtiene información de accesibilidad para un lugar.
    """
    lugar = request.query_params.get('lugar')
    
    if not lugar:
        return Response(
            {"error": "Falta parámetro: lugar"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Consultar información de accesibilidad
    valencia_service = ValenciaOpenDataService()
    result = valencia_service.get_informacion_accesibilidad(lugar)
    
    # Registrar consulta (solo si hay usuario autenticado)
    if request.user.is_authenticated:
        try:
            VoiceQuery.objects.create(
                user=request.user,
                query_type='info_accesibilidad',
                original_text=f"Accesibilidad de {lugar}",
                response_text=str(result),
                processing_time=0.1,
                success=True
            )
        except Exception as e:
            logger.warning(f"Error registrando consulta: {e}")
    
    return Response(result)


# ============================================================================
# ENDPOINT PRINCIPAL DE VOZ - Flujo completo STT -> NLP -> API -> TTS
# ============================================================================

@method_decorator(csrf_exempt, name='dispatch')
class VoiceQueryView(APIView):
    """
    Endpoint principal para consultas de voz.
    Implementa el flujo completo descrito en la guía técnica:
    Audio -> STT -> NLP -> API correspondiente -> TTS -> Respuesta audio
    """
    parser_classes = [MultiPartParser, JSONParser]
    permission_classes = [IsAuthenticated]
    
    def __init__(self):
        super().__init__()
        self.voice_manager = VoiceServiceManager()
        self.nlp_service = SpanishNLPService()
        self.valencia_service = ValenciaOpenDataService()
        self.routing_service = RoutingService()
        self.geocoding_service = GeocodingService()
    
    def post(self, request):
        """
        POST /api/consulta-voz
        Procesa una consulta de voz completa.
        
        Esperado en request:
        - audio_file: Archivo de audio (WAV/MP3/OGG)
        - lat: Latitud actual del usuario (opcional)
        - lon: Longitud actual del usuario (opcional)
        """
        start_time = time.time()
        
        # Validar archivo de audio
        audio_file = request.FILES.get('audio_file')
        if not audio_file:
            return Response(
                {"error": "Se requiere un archivo de audio"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener ubicación del usuario si está disponible
        user_lat = request.data.get('lat')
        user_lon = request.data.get('lon')
        user_location = None
        if user_lat and user_lon:
            try:
                user_location = (float(user_lat), float(user_lon))
            except ValueError:
                logger.warning("Coordenadas de usuario inválidas")
        
        try:
            # Paso 1: Guardar archivo de audio temporalmente
            temp_audio_path = self._save_temp_audio(audio_file)
            
            # Paso 2: STT - Convertir voz a texto
            stt_result = self.voice_manager.speech_to_text(temp_audio_path)
            
            if not stt_result.get('success') or not stt_result.get('text'):
                error_response = self._create_error_response(
                    "No se pudo entender el audio", 
                    request.user.id, 
                    start_time
                )
                self._cleanup_temp_file(temp_audio_path)
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
            
            recognized_text = stt_result['text']
            logger.info(f"Texto reconocido: '{recognized_text}'")
            
            # Paso 3: NLP - Identificar intención
            intent = self.nlp_service.process_query(recognized_text)
            
            # Paso 4: Procesar según la intención identificada
            response_data = self._process_intent(intent, user_location)
            
            # Paso 5: Formatear respuesta en texto natural
            response_text = self.nlp_service.format_response_text(intent, response_data)
            
            # Paso 6: TTS - Convertir respuesta a audio
            user_prefs = self._get_user_preferences(request.user)
            voice_speed = user_prefs.voice_speed if user_prefs else 'normal'
            
            tts_result = self.voice_manager.text_to_speech(
                response_text, 
                str(request.user.id), 
                voice_speed
            )
            
            # Calcular tiempo de procesamiento
            processing_time = time.time() - start_time
            
            # Registrar consulta completa
            self._log_voice_query(
                request.user,
                intent,
                recognized_text,
                response_text,
                processing_time,
                user_location,
                True
            )
            
            # Limpiar archivo temporal
            self._cleanup_temp_file(temp_audio_path)
            
            # Respuesta completa
            return Response({
                "success": True,
                "recognized_text": recognized_text,
                "intent": {
                    "name": intent.name,
                    "confidence": intent.confidence,
                    "entities": intent.entities
                },
                "response_text": response_text,
                "audio_response": tts_result,
                "processing_time_seconds": round(processing_time, 2),
                "data": response_data
            })
            
        except Exception as e:
            logger.error(f"Error procesando consulta de voz: {e}")
            error_response = self._create_error_response(
                "Error interno procesando la consulta", 
                request.user.id, 
                start_time
            )
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _save_temp_audio(self, audio_file) -> str:
        """
        Guarda el archivo de audio temporalmente para procesamiento.
        """
        temp_dir = settings.MEDIA_ROOT / "temp_audio"
        temp_dir.mkdir(exist_ok=True)
        
        filename = f"voice_query_{int(time.time())}_{audio_file.name}"
        temp_path = temp_dir / filename
        
        with open(temp_path, 'wb') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)
        
        return str(temp_path)
    
    def _process_intent(self, intent, user_location: Optional[tuple]) -> Dict:
        """
        Procesa la intención identificada y llama al servicio correspondiente.
        Implementa la lógica de enrutamiento según la guía técnica.
        """
        if intent.name == 'parada_cercana':
            return self._handle_parada_cercana(intent, user_location)
        
        elif intent.name == 'calculo_ruta':
            return self._handle_calculo_ruta(intent, user_location)
        
        elif intent.name == 'estado_trafico':
            return self._handle_estado_trafico(intent)
        
        elif intent.name == 'info_accesibilidad':
            return self._handle_info_accesibilidad(intent)
        
        elif intent.name in ['saludo', 'despedida']:
            return {"tipo": "conversacional", "intent": intent.name}
        
        else:
            return {
                "error": "No entendí tu consulta", 
                "sugerencia": "Puedes preguntar sobre paradas cercanas, rutas, tráfico o accesibilidad"
            }
    
    def _handle_parada_cercana(self, intent, user_location) -> Dict:
        """
        Maneja consultas de paradas cercanas.
        """
        # Si hay ubicación específica en la consulta, geocodificarla
        if intent.entities.get('ubicacion'):
            geo_result = self.geocoding_service.geocodificar_direccion(intent.entities['ubicacion'])
            if not geo_result.get('error'):
                lat, lon = geo_result['latitud'], geo_result['longitud']
            elif user_location:
                lat, lon = user_location
            else:
                return {"error": "No se pudo determinar la ubicación"}
        elif user_location:
            lat, lon = user_location
        else:
            return {"error": "Se necesita tu ubicación para encontrar paradas cercanas"}
        
        return self.valencia_service.get_parada_cercana(lat, lon)
    
    def _handle_calculo_ruta(self, intent, user_location) -> Dict:
        """
        Maneja consultas de cálculo de rutas.
        """
        origen_coords = None
        destino_coords = None
        
        # Determinar coordenadas de origen
        origen = intent.entities.get('origen')
        if origen == 'ubicacion_actual' and user_location:
            origen_coords = user_location
        elif origen:
            geo_result = self.geocoding_service.geocodificar_direccion(origen)
            if not geo_result.get('error'):
                origen_coords = (geo_result['latitud'], geo_result['longitud'])
        elif user_location:
            origen_coords = user_location
        
        # Determinar coordenadas de destino
        destino = intent.entities.get('destino') or intent.entities.get('ubicacion')
        if destino:
            geo_result = self.geocoding_service.geocodificar_direccion(destino)
            if not geo_result.get('error'):
                destino_coords = (geo_result['latitud'], geo_result['longitud'])
        
        if not origen_coords or not destino_coords:
            return {"error": "No se pudieron determinar origen y destino para la ruta"}
        
        # Determinar modo de transporte
        modo = 'foot'  # Por defecto a pie
        transport = intent.entities.get('medio_transporte')
        if transport == 'car':
            modo = 'driving'
        elif transport == 'cycling':
            modo = 'cycling'
        
        return self.routing_service.calcular_ruta(origen_coords, destino_coords, modo)
    
    def _handle_estado_trafico(self, intent) -> Dict:
        """
        Maneja consultas de estado del tráfico.
        """
        zona = intent.entities.get('zona')
        if not zona:
            zona = "Valencia centro"  # Zona por defecto
        
        return self.valencia_service.get_estado_trafico(zona)
    
    def _handle_info_accesibilidad(self, intent) -> Dict:
        """
        Maneja consultas de información de accesibilidad.
        """
        lugar = intent.entities.get('lugar')
        if not lugar:
            return {"error": "No especificaste qué lugar quieres consultar"}
        
        return self.valencia_service.get_informacion_accesibilidad(lugar)
    
    def _get_user_preferences(self, user) -> Optional[UserPreferences]:
        """
        Obtiene las preferencias del usuario.
        """
        try:
            return UserPreferences.objects.get(user=user)
        except UserPreferences.DoesNotExist:
            return None
    
    def _create_error_response(self, error_message: str, user_id: int, start_time: float) -> Dict:
        """
        Crea una respuesta de error con audio TTS.
        """
        tts_result = self.voice_manager.text_to_speech(error_message, str(user_id))
        processing_time = time.time() - start_time
        
        return {
            "success": False,
            "error": error_message,
            "audio_response": tts_result,
            "processing_time_seconds": round(processing_time, 2)
        }
    
    def _log_voice_query(self, user, intent, original_text: str, response_text: str, 
                        processing_time: float, location: Optional[tuple], success: bool):
        """
        Registra la consulta de voz para analíticas.
        """
        try:
            VoiceQuery.objects.create(
                user=user,
                query_type=intent.name,
                original_text=original_text,
                response_text=response_text,
                processing_time=processing_time,
                success=success,
                latitude=location[0] if location else None,
                longitude=location[1] if location else None
            )
        except Exception as e:
            logger.warning(f"Error registrando consulta de voz: {e}")
    
    def _cleanup_temp_file(self, filepath: str):
        """
        Elimina archivo temporal.
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            logger.warning(f"Error eliminando archivo temporal: {e}")


# ============================================================================
# ENDPOINTS AUXILIARES
# ============================================================================

@api_view(['GET'])
@permission_classes([])  # API pública según guía técnica
def geocodificar(request):
    """
    Endpoint para geocodificar direcciones.
    GET /api/geocodificar?direccion={texto}
    """
    direccion = request.query_params.get('direccion')
    
    if not direccion:
        return Response(
            {"error": "Falta parámetro: direccion"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    geocoding_service = GeocodingService()
    result = geocoding_service.geocodificar_direccion(direccion)
    
    if result.get('error'):
        return Response(result, status=status.HTTP_404_NOT_FOUND)
    
    return Response(result)


@api_view(['GET'])
@permission_classes([])  # Acceso público a archivos de audio generados
def audio_file(request, filename):
    """
    Endpoint para servir archivos de audio generados por TTS.
    GET /api/audio/{filename}
    """
    try:
        file_path = settings.AUDIO_OUTPUT_DIR / filename
        if file_path.exists() and filename.startswith('tts_'):
            return FileResponse(
                open(file_path, 'rb'),
                content_type='audio/mpeg',
                as_attachment=False
            )
        else:
            return Response(
                {"error": "Archivo no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        logger.error(f"Error sirviendo archivo de audio: {e}")
        return Response(
            {"error": "Error interno"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 