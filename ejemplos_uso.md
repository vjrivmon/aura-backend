# 🎙️ Ejemplos de Uso - Asistente de Voz de Movilidad Urbana

## 🚀 URLs Funcionales

### 1. Paradas Cercanas
```
GET http://localhost:8000/api/mobility/parada-cercana/?lat=39.4699&lon=-0.3763
```

**Respuesta esperada:**
```json
{
  "parada_principal": {
    "nombre": "Plaza del Ayuntamiento",
    "distancia_m": 120,
    "lineas": ["4", "6", "8", "9", "11"],
    "coordenadas": {"lat": 39.4699, "lon": -0.3763},
    "tiempo_llegada": "2-8 min"
  },
  "paradas_alternativas": [...],
  "total_encontradas": 3,
  "zona_detectada": "Valencia"
}
```

### 2. Estado del Tráfico
```
GET http://localhost:8000/api/mobility/trafico/?zona=Ruzafa
```

**Respuesta esperada:**
```json
{
  "zona": "Ruzafa",
  "estado": "moderado",
  "velocidad_promedio_kmh": 25.5,
  "descripcion": "Tráfico típico en zona residencial con comercios",
  "recomendacion": "Tráfico normal, tiempo de viaje estándar"
}
```

### 3. Información de Accesibilidad
```
GET http://localhost:8000/api/mobility/accesibilidad/?lugar=Museo IVAM
```

**Respuesta esperada:**
```json
{
  "lugar": "Museo IVAM",
  "encontrado": true,
  "accesible": "Totalmente accesible",
  "detalles_accesibilidad": "Acceso por rampa, ascensores, baños adaptados",
  "direccion": "Guillem de Castro, 118, Valencia",
  "telefono": "963 176 500"
}
```

## 🔧 Cómo Probar

1. **Asegúrate de que el servidor esté corriendo:**
   ```bash
   python manage.py runserver
   ```

2. **Prueba las URLs directamente en el navegador o con el script:**
   ```bash
   python test_apis.py
   ```

3. **Accede al panel de administración:**
   - URL: http://localhost:8000/admin/
   - Usuario: `admin`
   - Contraseña: `admin123`

## 🎤 API de Voz (Requiere Autenticación)

```bash
curl -X POST http://localhost:8000/api/mobility/consulta-voz/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "audio_file=@consulta.wav" \
  -F "lat=39.4699" \
  -F "lon=-0.3763"
```

## 📊 Datos Incluidos

### Zonas de Tráfico Soportadas:
- Ruzafa
- Campanar  
- Centro
- Malvarossa
- Benimaclet

### Lugares con Datos de Accesibilidad:
- Museo IVAM
- Mercado Central
- Ayuntamiento
- Estación Norte
- Ciudad de las Artes y Ciencias

### Coordenadas de Prueba:
- **Centro Valencia:** 39.4699, -0.3763
- **Ruzafa:** 39.4741, -0.3649
- **Malvarossa:** 39.4582, -0.3311

## 🔍 Funcionalidades Implementadas

✅ **APIs REST públicas** para consultas básicas  
✅ **Datos realistas** basados en Valencia  
✅ **Sistema de caché** para optimización  
✅ **Manejo de errores** robusto  
✅ **Logging** completo para debug  
✅ **Panel administrativo** Django  
✅ **Autenticación JWT** para API de voz  
✅ **Procesamiento de voz** (STT + TTS)  
✅ **NLP en español** para intenciones  

## 🐛 Solución de Problemas

### Error 404:
- Verificar que el servidor esté iniciado
- Comprobar que la URL esté bien escrita

### Error 500:
- Revisar logs en terminal
- Verificar configuración de base de datos

### APIs sin datos:
- Es normal - las APIs usan datos simulados realistas
- Los datos se generan según patrones típicos de Valencia 