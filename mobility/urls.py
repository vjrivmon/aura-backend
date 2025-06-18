"""
URLs para la aplicación Mobility.
Define los endpoints REST para el asistente de voz de movilidad urbana.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'mobility'

# ============================================================================
# ENDPOINTS REST - Implementados como funciones de vista
# ============================================================================

urlpatterns = [
    # ========================================================================
    # ENDPOINTS DE DATOS DE MOVILIDAD (Puente a APIs de Valencia)
    # ========================================================================
    
    # Parada más cercana - GET /api/mobility/parada-cercana?lat={lat}&lon={lon}
    path('parada-cercana/', views.parada_cercana, name='parada_cercana'),
    
    # Cálculo de rutas - GET /api/mobility/ruta?origen_lat={lat}&origen_lon={lon}&destino_lat={lat}&destino_lon={lon}
    path('ruta/', views.calcular_ruta, name='calcular_ruta'),
    
    # Estado del tráfico - GET /api/mobility/trafico?zona={nombre_barrio}
    path('trafico/', views.estado_trafico, name='estado_trafico'),
    
    # Información de accesibilidad - GET /api/mobility/accesibilidad?lugar={nombre}
    path('accesibilidad/', views.informacion_accesibilidad, name='informacion_accesibilidad'),
    
    # ========================================================================
    # ENDPOINT PRINCIPAL DE VOZ - Flujo completo STT -> NLP -> API -> TTS
    # ========================================================================
    
    # Consulta de voz completa - POST /api/mobility/consulta-voz
    # Implementa exactamente el flujo descrito en la guía técnica
    path('consulta-voz/', views.VoiceQueryView.as_view(), name='consulta_voz'),
    
    # ========================================================================
    # ENDPOINTS AUXILIARES
    # ========================================================================
    
    # Geocodificación - GET /api/mobility/geocodificar?direccion={texto}
    path('geocodificar/', views.geocodificar, name='geocodificar'),
    
    # Servir archivos de audio generados por TTS - GET /api/mobility/audio/{filename}
    path('audio/<str:filename>/', views.audio_file, name='audio_file'),
] 