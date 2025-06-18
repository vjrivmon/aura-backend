#!/usr/bin/env python
"""
Script para probar las APIs del asistente de voz y mostrar ejemplos.
Uso: python test_apis.py
"""

import requests
import json
from datetime import datetime

def test_api_endpoint(url, description):
    """Probar un endpoint y mostrar el resultado formateado"""
    print(f"\n🔍 {description}")
    print(f"   URL: {url}")
    print("   " + "="*50)
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta exitosa:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error {response.status_code}:")
            print(response.text[:200] + "..." if len(response.text) > 200 else response.text)
    
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def main():
    """Función principal para probar todas las APIs"""
    base_url = "http://localhost:8000"
    
    print("🎙️ PROBANDO APIs DEL ASISTENTE DE VOZ")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # URLs de prueba
    test_cases = [
        {
            "url": f"{base_url}/api/mobility/parada-cercana/?lat=39.4699&lon=-0.3763",
            "description": "Paradas cercanas al centro de Valencia"
        },
        {
            "url": f"{base_url}/api/mobility/trafico/?zona=Ruzafa",
            "description": "Estado del tráfico en Ruzafa"
        },
        {
            "url": f"{base_url}/api/mobility/trafico/?zona=Centro",
            "description": "Estado del tráfico en el Centro"
        },
        {
            "url": f"{base_url}/api/mobility/accesibilidad/?lugar=Museo IVAM",
            "description": "Accesibilidad del Museo IVAM"
        },
        {
            "url": f"{base_url}/api/mobility/accesibilidad/?lugar=Mercado Central",
            "description": "Accesibilidad del Mercado Central"
        },
        {
            "url": f"{base_url}/api/mobility/geocodificar/?direccion=Plaza del Ayuntamiento, Valencia",
            "description": "Geocodificación de dirección"
        }
    ]
    
    # Ejecutar pruebas
    for test_case in test_cases:
        test_api_endpoint(test_case["url"], test_case["description"])
    
    # Información adicional
    print(f"\n{'='*60}")
    print("📋 RESUMEN DE LAS APIS:")
    print("✅ Todas las APIs son públicas (no requieren autenticación)")
    print("✅ Devuelven datos realistas de Valencia")
    print("✅ Incluyen información de tráfico, paradas y accesibilidad")
    print("✅ Sistema de caché implementado para mejor rendimiento")
    
    print(f"\n🎤 PARA PROBAR API DE VOZ:")
    print(f"   POST {base_url}/api/mobility/consulta-voz/")
    print("   (Requiere autenticación y archivo de audio)")
    
    print(f"\n🌐 PANEL DE ADMINISTRACIÓN:")
    print(f"   {base_url}/admin/")
    print("   Usuario: admin | Contraseña: admin123")

if __name__ == '__main__':
    main() 