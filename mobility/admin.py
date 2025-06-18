"""
Configuración del panel de administración para la aplicación Mobility.
Permite gestionar consultas de voz, preferencias de usuario y caché de APIs.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from .models import VoiceQuery, ApiCache, UserPreferences


@admin.register(VoiceQuery)
class VoiceQueryAdmin(admin.ModelAdmin):
    """
    Administración de consultas de voz.
    Proporciona visión completa de las interacciones del asistente.
    """
    list_display = [
        'id', 'user', 'query_type', 'success_status', 'processing_time', 
        'location_info', 'created_at'
    ]
    list_filter = [
        'query_type', 'success', 'created_at', 'user__is_staff'
    ]
    search_fields = [
        'user__username', 'original_text', 'response_text'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'query_type', 'success', 'created_at')
        }),
        ('Contenido de la Consulta', {
            'fields': ('original_text', 'response_text')
        }),
        ('Métricas', {
            'fields': ('processing_time',)
        }),
        ('Ubicación', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Errores', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )
    
    def success_status(self, obj):
        """
        Muestra el estado de éxito con iconos coloridos.
        """
        if obj.success:
            return format_html(
                '<span style="color: green;">✓ Exitosa</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">✗ Error</span>'
            )
    success_status.short_description = 'Estado'
    
    def location_info(self, obj):
        """
        Muestra información de ubicación si está disponible.
        """
        if obj.latitude and obj.longitude:
            return format_html(
                '<a href="https://www.google.com/maps?q={},{}" target="_blank">'
                '📍 {:.4f}, {:.4f}</a>',
                obj.latitude, obj.longitude, obj.latitude, obj.longitude
            )
        return "Sin ubicación"
    location_info.short_description = 'Ubicación'
    
    def get_queryset(self, request):
        """
        Optimiza consultas incluyendo información del usuario.
        """
        return super().get_queryset(request).select_related('user')


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """
    Administración de preferencias de usuario.
    """
    list_display = [
        'user', 'preferred_transport', 'voice_speed', 
        'include_accessibility_info', 'updated_at'
    ]
    list_filter = [
        'preferred_transport', 'voice_speed', 'include_accessibility_info'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Preferencias de Transporte', {
            'fields': ('preferred_transport', 'max_walking_distance')
        }),
        ('Preferencias de Voz', {
            'fields': ('voice_speed', 'include_accessibility_info')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ApiCache)
class ApiCacheAdmin(admin.ModelAdmin):
    """
    Administración del caché de APIs.
    Permite monitorear y gestionar el caché de datos externos.
    """
    list_display = [
        'cache_key_short', 'cache_size', 'expiry_status', 
        'created_at', 'expiry_time'
    ]
    list_filter = ['created_at']
    search_fields = ['cache_key']
    readonly_fields = ['created_at']
    actions = ['clear_expired_cache', 'clear_all_cache']
    
    fieldsets = (
        ('Información del Caché', {
            'fields': ('cache_key', 'expiry_time', 'created_at')
        }),
        ('Datos', {
            'fields': ('cache_data',),
            'classes': ('collapse',)
        }),
    )
    
    def cache_key_short(self, obj):
        """
        Muestra una versión corta de la clave de caché.
        """
        if len(obj.cache_key) > 50:
            return obj.cache_key[:47] + "..."
        return obj.cache_key
    cache_key_short.short_description = 'Clave de Caché'
    
    def cache_size(self, obj):
        """
        Muestra el tamaño aproximado de los datos cacheados.
        """
        import json
        try:
            size_bytes = len(json.dumps(obj.cache_data))
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        except:
            return "N/D"
    cache_size.short_description = 'Tamaño'
    
    def expiry_status(self, obj):
        """
        Muestra si el caché ha expirado o está vigente.
        """
        if obj.is_expired():
            return format_html(
                '<span style="color: red;">⏰ Expirado</span>'
            )
        else:
            return format_html(
                '<span style="color: green;">✓ Vigente</span>'
            )
    expiry_status.short_description = 'Estado'
    
    def clear_expired_cache(self, request, queryset):
        """
        Acción para limpiar caché expirado.
        """
        deleted_count = 0
        for cache_obj in queryset:
            if cache_obj.is_expired():
                cache_obj.delete()
                deleted_count += 1
        
        self.message_user(
            request, 
            f"Se eliminaron {deleted_count} entradas de caché expiradas."
        )
    clear_expired_cache.short_description = "Limpiar caché expirado"
    
    def clear_all_cache(self, request, queryset):
        """
        Acción para limpiar todo el caché seleccionado.
        """
        deleted_count = queryset.count()
        queryset.delete()
        
        self.message_user(
            request, 
            f"Se eliminaron {deleted_count} entradas de caché."
        )
    clear_all_cache.short_description = "Limpiar caché seleccionado"


# ============================================================================
# PERSONALIZACIÓN DEL SITIO DE ADMINISTRACIÓN
# ============================================================================

# Personalizar títulos del admin
admin.site.site_header = "Aura - Asistente de Voz Urbana"
admin.site.site_title = "Aura Admin"
admin.site.index_title = "Panel de Administración - Movilidad Urbana Valencia" 