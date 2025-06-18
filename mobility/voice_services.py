"""
Servicios de reconocimiento y síntesis de voz para el asistente de movilidad urbana.
Implementa STT con Vosk y TTS con gTTS según la guía técnica.
"""

import os
import json
import wave
import logging
import tempfile
from typing import Optional, Dict
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Importaciones de librerías de voz
try:
    import vosk
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logging.warning("Vosk no está disponible. Instalar con: pip install vosk")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logging.warning("gTTS no está disponible. Instalar con: pip install gtts")

try:
    from pydub import AudioSegment
    import speech_recognition as sr
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logging.warning("PyDub/SpeechRecognition no disponibles")

logger = logging.getLogger('mobility')


class VoskSTTService:
    """
    Servicio de Speech-to-Text usando Vosk.
    Implementa reconocimiento de voz offline en español según la guía técnica.
    """
    
    def __init__(self):
        self.model = None
        self.recognizer = None
        self.model_path = settings.VOSK_MODEL_PATH
        self.sample_rate = settings.VOSK_SAMPLE_RATE
        self._initialize_model()
    
    def _initialize_model(self):
        """
        Inicializa el modelo de Vosk en español.
        Descarga automáticamente si no existe.
        """
        if not VOSK_AVAILABLE:
            logger.error("Vosk no está disponible")
            return False
        
        try:
            # Verificar si el modelo existe
            if not os.path.exists(self.model_path):
                logger.warning(f"Modelo Vosk no encontrado en {self.model_path}")
                # Aquí se podría implementar descarga automática del modelo
                self._download_spanish_model()
            
            # Cargar modelo
            if os.path.exists(self.model_path):
                self.model = vosk.Model(str(self.model_path))
                self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
                logger.info("Modelo Vosk cargado correctamente")
                return True
            else:
                logger.error("No se pudo cargar el modelo Vosk")
                return False
                
        except Exception as e:
            logger.error(f"Error inicializando Vosk: {e}")
            return False
    
    def _download_spanish_model(self):
        """
        Descarga el modelo español de Vosk si no existe.
        Implementación simplificada - en producción usar un descargador más robusto.
        """
        import urllib.request
        import zipfile
        
        model_url = "https://alphacephei.com/vosk/models/vosk-model-es-0.42.zip"
        model_dir = Path(self.model_path).parent
        model_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            logger.info("Descargando modelo Vosk español...")
            zip_path = model_dir / "vosk-model-es.zip"
            
            urllib.request.urlretrieve(model_url, zip_path)
            
            # Extraer ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(model_dir)
            
            # Renombrar directorio extraído
            extracted_dir = model_dir / "vosk-model-es-0.42"
            if extracted_dir.exists():
                extracted_dir.rename(self.model_path)
            
            # Limpiar ZIP
            zip_path.unlink()
            
            logger.info("Modelo Vosk descargado y extraído correctamente")
            
        except Exception as e:
            logger.error(f"Error descargando modelo Vosk: {e}")
    
    def audio_to_text(self, audio_file_path: str) -> Dict:
        """
        Convierte un archivo de audio a texto usando Vosk.
        Implementa exactamente el ejemplo de la guía técnica.
        
        Args:
            audio_file_path: Ruta al archivo de audio (WAV mono 16kHz)
        
        Returns:
            Dict con el texto reconocido y metadatos
        """
        if not self.model or not self.recognizer:
            return {"error": "Modelo Vosk no inicializado", "text": ""}
        
        try:
            # Abrir archivo WAV como en la guía técnica
            with wave.open(audio_file_path, "rb") as wf:
                # Verificar formato de audio
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != self.sample_rate:
                    logger.warning(f"Formato de audio no óptimo: {wf.getnchannels()}ch, {wf.getsampwidth()}bytes, {wf.getframerate()}Hz")
                    # Intentar convertir formato
                    audio_file_path = self._convert_audio_format(audio_file_path)
                    if not audio_file_path:
                        return {"error": "No se pudo convertir formato de audio", "text": ""}
                    
                    # Reabrir archivo convertido
                    wf = wave.open(audio_file_path, "rb")
                
                # Procesar audio por chunks como en la guía
                text_parts = []
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        if result.get("text"):
                            text_parts.append(result["text"])
                
                # Obtener resultado final
                final_result = json.loads(self.recognizer.FinalResult())
                if final_result.get("text"):
                    text_parts.append(final_result["text"])
                
                # Combinar todo el texto
                full_text = " ".join(text_parts).strip()
                
                logger.info(f"STT Vosk - Texto reconocido: '{full_text}'")
                
                return {
                    "text": full_text,
                    "confidence": 0.9,  # Vosk no proporciona confidence directo
                    "engine": "vosk",
                    "language": "es",
                    "success": bool(full_text)
                }
                
        except Exception as e:
            logger.error(f"Error en STT Vosk: {e}")
            return {"error": str(e), "text": ""}
    
    def _convert_audio_format(self, input_path: str) -> Optional[str]:
        """
        Convierte audio a formato compatible con Vosk (WAV mono 16kHz).
        Usa pydub para la conversión.
        """
        if not PYDUB_AVAILABLE:
            logger.error("PyDub no disponible para conversión de audio")
            return None
        
        try:
            # Cargar audio con pydub
            audio = AudioSegment.from_file(input_path)
            
            # Convertir a mono 16kHz
            audio = audio.set_channels(1)  # Mono
            audio = audio.set_frame_rate(self.sample_rate)  # 16kHz
            audio = audio.set_sample_width(2)  # 16-bit
            
            # Guardar archivo convertido temporalmente
            temp_dir = settings.MEDIA_ROOT / "temp_audio"
            temp_dir.mkdir(exist_ok=True)
            
            converted_path = temp_dir / f"converted_{os.path.basename(input_path)}.wav"
            audio.export(str(converted_path), format="wav")
            
            logger.info(f"Audio convertido: {input_path} -> {converted_path}")
            return str(converted_path)
            
        except Exception as e:
            logger.error(f"Error convirtiendo audio: {e}")
            return None


class GoogleTTSService:
    """
    Servicio de Text-to-Speech usando gTTS.
    Implementa síntesis de voz en español según la guía técnica.
    """
    
    def __init__(self):
        self.language = settings.TTS_LANGUAGE
        self.tld = settings.TTS_TLD
        self.output_dir = settings.AUDIO_OUTPUT_DIR
        
        # Crear directorio de salida si no existe
        os.makedirs(self.output_dir, exist_ok=True)
    
    def text_to_audio(self, text: str, slow: bool = False, 
                     user_id: Optional[str] = None) -> Dict:
        """
        Convierte texto a audio usando gTTS.
        Implementa exactamente el ejemplo de la guía técnica.
        
        Args:
            text: Texto a convertir a voz
            slow: Si usar velocidad lenta
            user_id: ID del usuario (para organización de archivos)
        
        Returns:
            Dict con información del archivo de audio generado
        """
        if not GTTS_AVAILABLE:
            return {"error": "gTTS no está disponible"}
        
        if not text.strip():
            return {"error": "Texto vacío"}
        
        try:
            # Crear objeto gTTS como en la guía técnica
            tts = gTTS(text=text, lang=self.language, tld=self.tld, slow=slow)
            
            # Generar nombre de archivo único
            import hashlib
            import time
            
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            timestamp = int(time.time())
            filename = f"tts_{user_id or 'anonymous'}_{timestamp}_{text_hash}.mp3"
            
            file_path = self.output_dir / filename
            
            # Guardar archivo como en la guía
            tts.save(str(file_path))
            
            logger.info(f"TTS generado: {filename} para texto: '{text[:50]}...'")
            
            # Calcular tamaño del archivo
            file_size = os.path.getsize(file_path)
            
            return {
                "success": True,
                "file_path": str(file_path),
                "filename": filename,
                "file_size_bytes": file_size,
                "text": text,
                "language": self.language,
                "engine": "gtts",
                "url": f"{settings.MEDIA_URL}audio/{filename}"
            }
            
        except Exception as e:
            logger.error(f"Error en TTS gTTS: {e}")
            return {"error": str(e)}
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Limpia archivos de audio antiguos para ahorrar espacio.
        
        Args:
            max_age_hours: Edad máxima de archivos en horas
        """
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            deleted_count = 0
            for file_path in self.output_dir.glob("tts_*.mp3"):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    file_path.unlink()
                    deleted_count += 1
            
            logger.info(f"Limpiados {deleted_count} archivos de audio antiguos")
            
        except Exception as e:
            logger.error(f"Error limpiando archivos: {e}")


class FallbackSTTService:
    """
    Servicio de STT alternativo usando Google Web Speech API.
    Se usa cuando Vosk no está disponible o falla.
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer() if PYDUB_AVAILABLE else None
    
    def audio_to_text(self, audio_file_path: str) -> Dict:
        """
        Convierte audio a texto usando Google Web Speech API.
        Fallback cuando Vosk no funciona.
        """
        if not self.recognizer:
            return {"error": "SpeechRecognition no disponible", "text": ""}
        
        try:
            # Usar SpeechRecognition para procesar el archivo
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
            
            # Usar Google Web Speech API (gratuita con limitaciones)
            text = self.recognizer.recognize_google(audio, language="es-ES")
            
            logger.info(f"STT Fallback - Texto reconocido: '{text}'")
            
            return {
                "text": text,
                "confidence": 0.8,  # Estimado
                "engine": "google_web",
                "language": "es-ES",
                "success": True
            }
            
        except sr.UnknownValueError:
            return {"error": "No se pudo entender el audio", "text": ""}
        except sr.RequestError as e:
            return {"error": f"Error en servicio de reconocimiento: {e}", "text": ""}
        except Exception as e:
            logger.error(f"Error en STT Fallback: {e}")
            return {"error": str(e), "text": ""}


class VoiceServiceManager:
    """
    Gestor principal de servicios de voz.
    Coordina STT y TTS con fallbacks automáticos.
    """
    
    def __init__(self):
        self.stt_primary = VoskSTTService()
        self.stt_fallback = FallbackSTTService()
        self.tts_service = GoogleTTSService()
    
    def speech_to_text(self, audio_file_path: str) -> Dict:
        """
        Convierte voz a texto con fallback automático.
        """
        # Intentar Vosk primero
        if self.stt_primary.model:
            result = self.stt_primary.audio_to_text(audio_file_path)
            if result.get("success") and result.get("text"):
                return result
        
        # Fallback a Google Web Speech
        logger.info("Usando STT fallback")
        return self.stt_fallback.audio_to_text(audio_file_path)
    
    def text_to_speech(self, text: str, user_id: Optional[str] = None, 
                      voice_speed: str = "normal") -> Dict:
        """
        Convierte texto a voz con configuración de velocidad.
        """
        slow = (voice_speed == "slow")
        return self.tts_service.text_to_audio(text, slow=slow, user_id=user_id)
    
    def process_voice_query(self, audio_file_path: str, user_id: Optional[str] = None) -> Dict:
        """
        Procesa una consulta de voz completa: STT -> texto -> respuesta -> TTS.
        Flujo principal del asistente de voz.
        """
        try:
            # Paso 1: Convertir voz a texto
            stt_result = self.speech_to_text(audio_file_path)
            
            if not stt_result.get("success") or not stt_result.get("text"):
                error_msg = "No se pudo entender la consulta de voz"
                tts_result = self.text_to_speech(error_msg, user_id)
                return {
                    "success": False,
                    "error": error_msg,
                    "stt_result": stt_result,
                    "tts_result": tts_result
                }
            
            return {
                "success": True,
                "recognized_text": stt_result["text"],
                "stt_result": stt_result,
                "ready_for_nlp": True
            }
            
        except Exception as e:
            logger.error(f"Error procesando consulta de voz: {e}")
            error_msg = "Error interno procesando la consulta"
            tts_result = self.text_to_speech(error_msg, user_id)
            return {
                "success": False,
                "error": error_msg,
                "tts_result": tts_result
            } 