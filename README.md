# 🎙️ Aura - Asistente de Voz para Movilidad Urbana Valencia

**Asistente de voz especializado en movilidad urbana para la ciudad de Valencia, España. Diseñado especialmente para personas con discapacidad visual.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.0%2B-green)](https://djangoproject.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Endpoints API](#-endpoints-api)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

## 🌟 Características

### Funcionalidades Principales

- **🎤 Reconocimiento de Voz Offline**: Utiliza Vosk con modelo en español
- **🔊 Síntesis de Voz**: Respuestas en audio natural usando gTTS
- **🗣️ NLP en Español**: Procesamiento de lenguaje natural especializado en consultas de movilidad
- **🌐 Integración con Datos Abiertos**: Conectado con las APIs del Ayuntamiento de Valencia
- **🚌 Consultas de Transporte**: Paradas cercanas, rutas, horarios
- **🚦 Información de Tráfico**: Estado en tiempo real por zonas
- **♿ Accesibilidad**: Información sobre accesibilidad de lugares públicos
- **📊 Panel de Administración**: Gestión completa vía Django Admin

### Consultas Soportadas

1. **Paradas de transporte cercanas**
   - "¿Dónde está la parada de autobús más cercana?"
   - "Parada de metro cerca de aquí"

2. **Cálculo de rutas**
   - "¿Cómo llego hasta el Mercado Central?"
   - "Ruta desde mi ubicación hasta la Ciudad de las Artes"

3. **Estado del tráfico**
   - "¿Cómo está el tráfico en Ruzafa?"
   - "Estado del tráfico en Valencia centro"

4. **Información de accesibilidad**
   - "¿Es accesible el Museo IVAM?"
   - "Información de accesibilidad de la Lonja"

## 🏗️ Arquitectura

### Diseño Simplificado

El proyecto sigue la **guía técnica de simplificación de arquitectura**:

- **Sin base de datos geoespacial**: Usa SQLite simple, elimina PostGIS
- **APIs como fuente de verdad**: Consulta directa a datos abiertos de Valencia
- **Backend como puente**: Actúa como intermediario inteligente
- **Caché mínimo**: Solo para optimizaciones de rendimiento

### Flujo de Funcionamiento

```
[Audio del usuario] 
    ↓ STT (Vosk)
[Texto reconocido] 
    ↓ NLP (SpanishNLPService)
[Intención + Entidades] 
    ↓ Servicios
[API Valencia + OSRM] 
    ↓ Formateo
[Respuesta en texto] 
    ↓ TTS (gTTS)
[Audio de respuesta]
```

### Componentes Principales

```
aura-backend/
├── config/                 # Configuración Django
├── core/                  # App básica (usuarios, auth)
├── mobility/              # 🎯 App principal del asistente
│   ├── services.py        # Integración APIs externas
│   ├── voice_services.py  # STT/TTS con Vosk y gTTS
│   ├── nlp_service.py     # Procesamiento lenguaje natural
│   ├── views.py          # Endpoints REST
│   └── models.py         # Modelos mínimos (logging, caché)
├── media/                # Archivos de audio generados
├── models/               # Modelos de Vosk
└── requirements.txt      # Dependencias
```

## 🚀 Instalación

### Prerrequisitos

- Python 3.8 o superior
- Git
- (Opcional) Entorno virtual

### Instalación Rápida

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd aura-backend
```

2. **Crear y activar entorno virtual**
```bash
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

3. **Instalación automática**
```bash
python setup_voice_assistant.py --install-deps --create-superuser
```

### Instalación Manual

Si prefieres instalar paso a paso:

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar base de datos
python manage.py makemigrations
python manage.py makemigrations core
python manage.py makemigrations mobility
python manage.py migrate

# 3. Crear superusuario
python manage.py createsuperuser

# 4. Crear directorios
mkdir -p media/audio media/temp_audio models logs
```

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` con la configuración:

```env
# Configuración Django
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# APIs externas (opcional)
VALENCIA_OPENDATA_API_KEY=
OSRM_API_KEY=

# Configuración de voz
VOSK_MODEL_LANGUAGE=es
TTS_LANGUAGE=es
TTS_SPEED=normal
```

### Configuración de Producción

Para producción, modifica `config/settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['tu-dominio.com']

# Configurar base de datos PostgreSQL si se desea
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'aura_voice_db',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🎯 Uso

### Iniciar el Servidor

```bash
python manage.py runserver
```

### Probar el Sistema

1. **Panel de Administración**: http://localhost:8000/admin/
2. **API de Parada Cercana**: 
   ```
   GET http://localhost:8000/api/mobility/parada-cercana/?lat=39.4699&lon=-0.3763
   ```
3. **Consulta de Voz Completa**:
   ```bash
   curl -X POST http://localhost:8000/api/mobility/consulta-voz/ \
     -F "audio_file=@consulta.wav" \
     -F "lat=39.4699" \
     -F "lon=-0.3763"
   ```

### Comandos de Gestión

```bash
# Limpiar archivos de audio antiguos
python manage.py cleanup_voice_files --force --max-age-hours=24

# Verificar configuración
python manage.py check

# Shell interactivo
python manage.py shell
```

## 📡 Endpoints API

### Endpoints de Datos de Movilidad

| Endpoint | Método | Descripción | Parámetros |
|----------|---------|-------------|------------|
| `/api/mobility/parada-cercana/` | GET | Parada más cercana | `lat`, `lon`, `radio` |
| `/api/mobility/ruta/` | GET | Calcular ruta | `origen_lat`, `origen_lon`, `destino_lat`, `destino_lon`, `modo` |
| `/api/mobility/trafico/` | GET | Estado del tráfico | `zona` |
| `/api/mobility/accesibilidad/` | GET | Info accesibilidad | `lugar` |

### Endpoint Principal de Voz

| Endpoint | Método | Descripción | Parámetros |
|----------|---------|-------------|------------|
| `/api/mobility/consulta-voz/` | POST | Consulta completa por voz | `audio_file`, `lat`, `lon` |

### Endpoints Auxiliares

| Endpoint | Método | Descripción | Parámetros |
|----------|---------|-------------|------------|
| `/api/mobility/geocodificar/` | GET | Convertir dirección a coordenadas | `direccion` |
| `/api/mobility/audio/<filename>/` | GET | Servir archivos de audio | - |

### Ejemplos de Uso

#### 1. Consultar Parada Cercana

```bash
curl "http://localhost:8000/api/mobility/parada-cercana/?lat=39.4699&lon=-0.3763"
```

**Respuesta:**
```json
{
  "parada_principal": {
    "nombre": "Plaza del Ayuntamiento",
    "distancia_m": 150,
    "lineas": "4, 6, 8, 9",
    "coordenadas": {"lat": 39.4699, "lon": -0.3763}
  },
  "paradas_alternativas": [...],
  "total_encontradas": 3
}
```

#### 2. Calcular Ruta

```bash
curl "http://localhost:8000/api/mobility/ruta/?origen_lat=39.4699&origen_lon=-0.3763&destino_lat=39.4754&destino_lon=-0.3802&modo=foot"
```

#### 3. Consulta de Voz Completa

```bash
curl -X POST http://localhost:8000/api/mobility/consulta-voz/ \
  -H "Authorization: Bearer tu-token-jwt" \
  -F "audio_file=@audio_consulta.wav" \
  -F "lat=39.4699" \
  -F "lon=-0.3763"
```

**Respuesta:**
```json
{
  "success": true,
  "recognized_text": "¿Dónde está la parada de autobús más cercana?",
  "intent": {
    "name": "parada_cercana",
    "confidence": 0.95,
    "entities": {"ubicacion": "ubicacion_actual"}
  },
  "response_text": "La parada más cercana está en Plaza del Ayuntamiento, a 150 metros. Pasan las líneas 4, 6, 8 y 9.",
  "audio_response": {
    "url": "/api/mobility/audio/tts_user123_1234567890_abc123.mp3",
    "filename": "tts_user123_1234567890_abc123.mp3"
  },
  "processing_time_seconds": 2.3
}
```

## 🔧 Desarrollo

### Estructura del Código

#### Servicios Principales

1. **`ValenciaOpenDataService`**: Integración con APIs de datos abiertos
2. **`VoiceServiceManager`**: Gestión de STT/TTS
3. **`SpanishNLPService`**: Procesamiento de lenguaje natural
4. **`RoutingService`**: Cálculo de rutas con OSRM
5. **`GeocodingService`**: Geocodificación de direcciones

#### Flujo de Desarrollo

1. **Añadir nueva funcionalidad**:
   - Crear patron NLP en `nlp_service.py`
   - Implementar lógica en `services.py`
   - Añadir endpoint en `views.py`
   - Actualizar URLs en `urls.py`

2. **Pruebas**:
   ```bash
   python manage.py test mobility
   ```

3. **Logging**:
   - Los logs se guardan en `logs/aura-voice.log`
   - Configuración en `settings.py`

### Agregar Nuevas Consultas

Para añadir un nuevo tipo de consulta (ej: "horarios"):

1. **NLP** - Añadir patrones en `nlp_service.py`:
```python
'consultar_horarios': [
    r'\b(horario|horarios)\b.*\b(bus|metro|autobús)\b',
    r'\b(a qué hora)\b.*\b(pasa|llega)\b',
]
```

2. **Servicio** - Implementar en `services.py`:
```python
def get_horarios_transporte(self, parada_id: str) -> Dict:
    # Lógica para obtener horarios
    pass
```

3. **Vista** - Añadir endpoint en `views.py`:
```python
@api_view(['GET'])
def consultar_horarios(request):
    # Implementación del endpoint
    pass
```

## 🧪 Testing

### Ejecutar Pruebas

```bash
# Todas las pruebas
python manage.py test

# Solo mobility
python manage.py test mobility

# Con cobertura
pip install coverage
coverage run manage.py test
coverage report
```

### Pruebas de Voz

```bash
# Probar reconocimiento de voz
python manage.py shell
>>> from mobility.voice_services import VoiceServiceManager
>>> vm = VoiceServiceManager()
>>> result = vm.speech_to_text("path/to/audio.wav")
>>> print(result)
```

## 📊 Monitoreo y Mantenimiento

### Métricas Disponibles

- **Consultas de voz**: Panel admin → Voice Queries
- **Rendimiento**: Tiempo de procesamiento promedio
- **Errores**: Logs en `logs/aura-voice.log`
- **Caché**: Estado en panel admin → Api Cache

### Mantenimiento Automático

```bash
# Limpiar archivos antiguos (ejecutar diariamente)
python manage.py cleanup_voice_files --cleanup-cache --max-age-hours=24

# Respaldo de base de datos
python manage.py dumpdata > backup.json
```

### Monitoreo de APIs Externas

El sistema incluye verificaciones automáticas de:
- Disponibilidad de API de Valencia
- Estado de OSRM
- Modelos de Vosk cargados

## 🤝 Contribuir

### Cómo Contribuir

1. Fork el proyecto
2. Crear una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

### Pautas de Desarrollo

- **Documentación**: Comentar código siguiendo estándares industriales
- **Testing**: Añadir pruebas para nuevas funcionalidades
- **Logging**: Usar el sistema de logging configurado
- **Internacionalización**: Mantener todo en español para Valencia

## 🔧 Troubleshooting

### Problemas Comunes

1. **Error "No module named 'vosk'"**
   ```bash
   pip install vosk
   ```

2. **Modelo Vosk no encontrado**
   - El modelo se descarga automáticamente en el primer uso
   - Verificar conexión a internet

3. **Error de permisos en archivos de audio**
   ```bash
   chmod 755 media/
   chmod 755 media/audio/
   ```

4. **gTTS sin conexión**
   - gTTS requiere conexión a internet
   - Para uso offline, implementar motor TTS local

### Logs y Debugging

```bash
# Ver logs en tiempo real
tail -f logs/aura-voice.log

# Debug en shell
python manage.py shell
>>> import logging
>>> logging.getLogger('mobility').setLevel(logging.DEBUG)
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- **Ayuntamiento de Valencia** por los datos abiertos
- **Proyecto Vosk** por el reconocimiento de voz offline
- **Google** por gTTS
- **OpenStreetMap** y **OSRM** por el routing
- **Comunidad Django** por el framework

---

**Desarrollado con ❤️ para mejorar la movilidad urbana en Valencia**

> Este proyecto forma parte del ecosistema Aura, diseñado para asistir a personas con discapacidad visual en su navegación urbana mediante tecnologías de voz e inteligencia artificial.

## 📞 Soporte

Para soporte técnico o consultas:
- 📧 Email: [soporte@aura-voice.com](mailto:soporte@aura-voice.com)
- 🐛 Issues: [GitHub Issues](https://github.com/tu-usuario/aura-backend/issues)
- 📖 Wiki: [Documentación extendida](https://github.com/tu-usuario/aura-backend/wiki)