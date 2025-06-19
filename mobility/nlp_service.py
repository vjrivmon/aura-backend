"""
Servicio de procesamiento de lenguaje natural para el asistente de voz.
Implementa comprensión de intenciones en español usando reglas y palabras clave.
Según la guía técnica, enfoque ligero y eficiente.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger('mobility')


@dataclass
class Intent:
    """
    Clase para representar una intención identificada.
    """
    name: str
    confidence: float
    entities: Dict[str, str]
    original_text: str


class SpanishNLPService:
    """
    Servicio de NLP especializado en español para movilidad urbana.
    Utiliza reglas y patrones para identificar intenciones según la guía técnica.
    """
    
    def __init__(self):
        self.intent_patterns = self._initialize_intent_patterns()
        self.location_patterns = self._initialize_location_patterns()
        self.transport_patterns = self._initialize_transport_patterns()
        self.stopwords = self._get_spanish_stopwords()
    
    def _initialize_intent_patterns(self) -> Dict[str, List[str]]:
        """
        Define patrones de palabras clave para cada tipo de intención.
        Implementa la lógica de reglas descrita en la guía técnica.
        """
        return {
            'parada_cercana': [
                r'\b(parada|paradero)\b.*\b(cerca|cercana|próxima|más cerca)\b',
                r'\b(dónde|donde)\b.*\b(parada|paradero|bus|autobús|metro)\b',
                r'\b(parada|paradero)\b.*\b(aquí|mi ubicación)\b',
                r'\b(más cerca|cercana)\b.*\b(parada|paradero)\b',
                r'\b(bus|autobús|metro)\b.*\b(cerca|cercano)\b',
                r'\b(transporte público)\b.*\b(cerca|cercano)\b',
                r'\b(emt)\b.*\b(parada|cercana)\b'
            ],
            'calculo_ruta': [
                r'\b(cómo|como)\b.*\b(llegar|llego|voy|ir)\b',
                r'\b(ruta|camino)\b.*\b(hacia|hasta|para)\b',
                r'\b(direcciones|indicaciones)\b.*\b(para|hasta)\b',
                r'\b(cómo)\b.*\b(puedo|puede)\b.*\b(llegar)\b',
                r'\b(ir)\b.*\b(desde|de)\b.*\b(hasta|a)\b',
                r'\b(navegar|dirigir)\b.*\b(hacia|hasta)\b',
                r'\b(mostrar|enseñar)\b.*\b(ruta|camino)\b'
            ],
            'estado_trafico': [
                r'\b(tráfico|trafico)\b',
                r'\b(circulación|congestión|atasco)\b',
                r'\b(cómo está)\b.*\b(tráfico|trafico|circulación)\b',
                r'\b(estado)\b.*\b(tráfico|trafico|vías|carreteras)\b',
                r'\b(fluye|fluye el tráfico|fluido)\b',
                r'\b(retenciones|atascos|embotellamientos)\b',
                r'\b(velocidad)\b.*\b(tráfico|circulación)\b'
            ],
            'info_accesibilidad': [
                r'\b(accesibilidad|accesible)\b',
                r'\b(silla de ruedas|discapacitados|movilidad reducida)\b',
                r'\b(adaptado|adaptados|barreras)\b',
                r'\b(rampas|ascensor|elevador)\b',
                r'\b(personas)\b.*\b(discapacidad|discapacitadas)\b',
                r'\b(acceso)\b.*\b(minusválidos|discapacitados)\b',
                r'\b(está adaptado|es accesible)\b'
            ],
            'saludo': [
                r'\b(hola|buenas|buenos días|buenas tardes|buenas noches)\b',
                r'\b(saludos|hey|qué tal)\b',
                r'\b(ayuda|ayúdame|puedes ayudar)\b'
            ],
            'despedida': [
                r'\b(adiós|hasta luego|nos vemos|chao|bye)\b',
                r'\b(gracias|muchas gracias|está bien|perfecto)\b',
                r'\b(eso es todo|nada más|ya está)\b'
            ]
        }
    
    def _initialize_location_patterns(self) -> List[str]:
        """
        Patrones para detectar ubicaciones y direcciones.
        """
        return [
            r'\b(calle|c/|avenida|av|plaza|pl|paseo)\s+([a-záéíóúñ\s]+)\b',
            r'\b(barrio|zona|distrito)\s+([a-záéíóúñ\s]+)\b',
            r'\b(en|cerca de|junto a|al lado de)\s+([a-záéíóúñ\s]+)\b',
            r'\b([a-záéíóúñ]+(?:\s+[a-záéíóúñ]+)*)\s*,?\s*valencia\b',
            # Barrios conocidos de Valencia
            r'\b(ruzafa|campanar|benimaclet|malvarosa|cabañal|russafa|ciutat vella)\b',
            r'\b(jesús|patraix|algirós|el carmen|xàtiva|colón)\b'
        ]
    
    def _initialize_transport_patterns(self) -> Dict[str, List[str]]:
        """
        Patrones para detectar medios de transporte específicos.
        """
        return {
            'public_transport': [r'\b(bus|autobús|metro|tranvía|emt|metrovalencia)\b'],
            'walking': [r'\b(andando|caminando|a pie|peatonal)\b'],
            'cycling': [r'\b(bicicleta|bici|valenbisi|ciclista)\b'],
            'car': [r'\b(coche|carro|automóvil|vehiculo|conducir)\b']
        }
    
    def _get_spanish_stopwords(self) -> List[str]:
        """
        Lista de palabras vacías en español.
        """
        return [
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le',
            'da', 'su', 'por', 'son', 'con', 'para', 'al', 'me', 'una', 'ti', 'él', 'del',
            'está', 'muy', 'todo', 'pero', 'más', 'hacer', 'fue', 'ser', 'hacer', 'pueden',
            'bien', 'aquí', 'donde', 'cómo', 'cuando', 'porque', 'qué', 'quién', 'cual'
        ]
    
    def process_query(self, text: str) -> Intent:
        """
        Procesa una consulta en español y determina la intención.
        Punto de entrada principal del servicio NLP.
        
        Args:
            text: Texto de la consulta del usuario
            
        Returns:
            Intent: Objeto con la intención identificada y entidades extraídas
        """
        # Normalizar texto
        normalized_text = self._normalize_text(text)
        
        # Identificar intención principal
        intent_name, confidence = self._classify_intent(normalized_text)
        
        # Extraer entidades según la intención
        entities = self._extract_entities(normalized_text, intent_name)
        
        logger.info(f"NLP - Texto: '{text}' -> Intención: {intent_name} (confianza: {confidence:.2f})")
        
        return Intent(
            name=intent_name,
            confidence=confidence,
            entities=entities,
            original_text=text
        )
    
    def _normalize_text(self, text: str) -> str:
        """
        Normaliza el texto para procesamiento.
        """
        # Convertir a minúsculas
        text = text.lower().strip()
        
        # Eliminar caracteres especiales conservando espacios y tildes
        text = re.sub(r'[^\w\sáéíóúñ]', ' ', text)
        
        # Normalizar espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _classify_intent(self, text: str) -> Tuple[str, float]:
        """
        Clasifica la intención usando patrones de regex.
        Implementa la lógica de reglas de la guía técnica.
        """
        intent_scores = {}
        
        # Evaluar cada patrón de intención
        for intent, patterns in self.intent_patterns.items():
            score = 0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    matches += 1
                    # Peso por especificidad del patrón
                    pattern_weight = len(pattern.split()) / 10.0  # Patrones más largos tienen mayor peso
                    score += 1.0 + pattern_weight
            
            if matches > 0:
                # Calcular confianza basada en número de coincidencias y peso
                confidence = min(score / len(patterns), 1.0)
                intent_scores[intent] = confidence
        
        # Si no hay coincidencias claras, clasificar como general
        if not intent_scores:
            return 'general', 0.3
        
        # Devolver la intención con mayor puntuación
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        return best_intent[0], best_intent[1]
    
    def _extract_entities(self, text: str, intent: str) -> Dict[str, str]:
        """
        Extrae entidades específicas según la intención identificada.
        """
        entities = {}
        
        # Extraer ubicaciones/direcciones para todas las intenciones relevantes
        if intent in ['parada_cercana', 'calculo_ruta', 'estado_trafico', 'info_accesibilidad']:
            locations = self._extract_locations(text)
            if locations:
                entities['ubicacion'] = locations[0]  # Tomar la primera ubicación encontrada
                if len(locations) > 1:
                    entities['destino'] = locations[1]  # Segunda ubicación como destino
        
        # Extraer medio de transporte preferido
        transport = self._extract_transport_mode(text)
        if transport:
            entities['medio_transporte'] = transport
        
        # Entidades específicas por intención
        if intent == 'estado_trafico':
            zona = self._extract_traffic_zone(text)
            if zona:
                entities['zona'] = zona
        
        elif intent == 'calculo_ruta':
            origen, destino = self._extract_route_points(text)
            if origen:
                entities['origen'] = origen
            if destino:
                entities['destino'] = destino
        
        elif intent == 'info_accesibilidad':
            lugar = self._extract_accessibility_place(text)
            if lugar:
                entities['lugar'] = lugar
        
        return entities
    
    def _extract_locations(self, text: str) -> List[str]:
        """
        Extrae ubicaciones y direcciones del texto.
        """
        locations = []
        
        for pattern in self.location_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    location = match.group(2).strip()
                elif len(match.groups()) >= 1:
                    location = match.group(1).strip()
                else:
                    location = match.group(0).strip()
                
                # Filtrar ubicaciones válidas (más de 2 caracteres, no solo números)
                if len(location) > 2 and not location.isdigit():
                    locations.append(location)
        
        return list(set(locations))  # Eliminar duplicados
    
    def _extract_transport_mode(self, text: str) -> Optional[str]:
        """
        Detecta el medio de transporte mencionado.
        """
        for mode, patterns in self.transport_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return mode
        return None
    
    def _extract_traffic_zone(self, text: str) -> Optional[str]:
        """
        Extrae la zona específica para consultas de tráfico.
        """
        # Buscar barrios conocidos de Valencia
        barrios_valencia = [
            'ruzafa', 'russafa', 'campanar', 'benimaclet', 'malvarosa', 'cabañal',
            'ciutat vella', 'jesús', 'patraix', 'algirós', 'el carmen', 'xàtiva',
            'colón', 'pérez galdós', 'gran vía', 'centro', 'mercado central'
        ]
        
        for barrio in barrios_valencia:
            if barrio.lower() in text.lower():
                return barrio.title()
        
        # Si no encuentra barrio específico, buscar patrones generales
        zona_patterns = [
            r'\ben\s+([a-záéíóúñ\s]+)\b',
            r'\bzona\s+([a-záéíóúñ\s]+)\b',
            r'\bbarrio\s+([a-záéíóúñ\s]+)\b'
        ]
        
        for pattern in zona_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                zona = match.group(1).strip()
                if len(zona) > 2:
                    return zona.title()
        
        return None
    
    def _extract_route_points(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extrae puntos de origen y destino para cálculo de rutas.
        """
        origen = None
        destino = None
        
        # Patrones para origen
        origen_patterns = [
            r'\bdesde\s+([a-záéíóúñ\s,]+?)(?:\s+hasta|\s+a\s|\s+hacia|\s*$)',
            r'\bde\s+([a-záéíóúñ\s,]+?)(?:\s+hasta|\s+a\s|\s+hacia|\s*$)',
            r'\bmi\s+ubicación\b',
            r'\baquí\b',
            r'\bdonde\s+estoy\b'
        ]
        
        # Patrones para destino
        destino_patterns = [
            r'\bhasta\s+([a-záéíóúñ\s,]+?)(?:\s*$|\s+en\s)',
            r'\ba\s+([a-záéíóúñ\s,]+?)(?:\s*$|\s+en\s)',
            r'\bhacia\s+([a-záéíóúñ\s,]+?)(?:\s*$|\s+en\s)',
            r'\bpara\s+([a-záéíóúñ\s,]+?)(?:\s*$|\s+en\s)'
        ]
        
        # Buscar origen
        for pattern in origen_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'ubicación' in match.group(0) or 'aquí' in match.group(0) or 'estoy' in match.group(0):
                    origen = 'ubicacion_actual'
                else:
                    origen = match.group(1).strip()
                break
        
        # Buscar destino
        for pattern in destino_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                destino = match.group(1).strip()
                break
        
        return origen, destino
    
    def _extract_accessibility_place(self, text: str) -> Optional[str]:
        """
        Extrae el lugar específico para consultas de accesibilidad.
        """
        # Buscar patrones que indiquen un lugar específico
        place_patterns = [
            r'\b(museo|teatro|cine|hospital|centro|biblioteca|parque)\s+([a-záéíóúñ\s]+)\b',
            r'\bel\s+([a-záéíóúñ\s]+)\s+es\s+accesible\b',
            r'\baccesibilidad\s+de\s+([a-záéíóúñ\s]+)\b',
            r'\ben\s+([a-záéíóúñ\s]+)\s+hay\s+acceso\b'
        ]
        
        for pattern in place_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                place = match.group(1).strip() if len(match.groups()) >= 1 else match.group(0).strip()
                if len(place) > 2:
                    return place.title()
        
        # Si no encuentra patrón específico, buscar ubicaciones generales
        locations = self._extract_locations(text)
        if locations:
            return locations[0]
        
        return None
    
    def format_response_text(self, intent: Intent, response_data: Dict) -> str:
        """
        Formatea la respuesta en texto natural para síntesis de voz.
        Convierte datos técnicos en texto comprensible para usuarios con discapacidad visual.
        """
        if intent.name == 'parada_cercana':
            return self._format_parada_response(response_data)
        elif intent.name == 'calculo_ruta':
            return self._format_ruta_response(response_data)
        elif intent.name == 'estado_trafico':
            return self._format_trafico_response(response_data)
        elif intent.name == 'info_accesibilidad':
            return self._format_accesibilidad_response(response_data)
        elif intent.name == 'saludo':
            return "Hola, soy tu asistente de movilidad urbana para Valencia. ¿En qué puedo ayudarte?"
        elif intent.name == 'despedida':
            return "¡Hasta luego! Que tengas un buen viaje."
        else:
            return "Lo siento, no he entendido tu consulta. ¿Podrías repetirla?"
    
    def _format_parada_response(self, data: Dict) -> str:
        """Formatea respuesta de parada cercana."""
        if data.get('error'):
            return f"Lo siento, {data['error'].lower()}"
        
        parada = data.get('parada_principal', {})
        if not parada:
            return "No encontré paradas de transporte público cerca de tu ubicación."
        
        nombre = parada.get('nombre', 'Parada')
        distancia = parada.get('distancia_m')
        lineas = parada.get('lineas', '')
        
        response = f"La parada más cercana es {nombre}"
        
        if distancia:
            if distancia < 100:
                response += f", está a unos {distancia} metros"
            else:
                response += f", está a unos {round(distancia/10)*10} metros"
        
        if lineas and lineas != 'N/D':
            response += f". Pasan las líneas {lineas}"
        
        return response + "."
    
    def _format_ruta_response(self, data: Dict) -> str:
        """Formatea respuesta de cálculo de ruta."""
        if data.get('error'):
            return f"No pude calcular la ruta: {data['error'].lower()}"
        
        distancia_km = data.get('distancia_total_km', 0)
        duracion_min = data.get('duracion_minutos', 0)
        instrucciones = data.get('instrucciones', [])
        
        response = f"La ruta tiene {distancia_km} kilómetros y tomará aproximadamente {int(duracion_min)} minutos. "
        
        if instrucciones:
            response += "Las direcciones son: "
            # Tomar solo las primeras 3 instrucciones para no sobrecargar al usuario
            for i, instruccion in enumerate(instrucciones[:3]):
                response += f"{i+1}. {instruccion}. "
            
            if len(instrucciones) > 3:
                response += "Continúa siguiendo las indicaciones GPS."
        
        return response
    
    def _format_trafico_response(self, data: Dict) -> str:
        """Formatea respuesta de estado del tráfico."""
        zona = data.get('zona', 'la zona consultada')
        estado = data.get('estado', 'desconocido')
        recomendacion = data.get('recomendacion', '')
        
        response = f"En {zona}, el tráfico está {estado}"
        
        if recomendacion:
            response += f". {recomendacion}"
        
        return response + "."
    
    def _format_accesibilidad_response(self, data: Dict) -> str:
        """Formatea respuesta de información de accesibilidad."""
        lugar = data.get('lugar', 'el lugar consultado')
        accesible = data.get('accesible', 'Desconocido')
        detalles = data.get('detalles_accesibilidad', '')
        
        if not data.get('encontrado', False):
            return f"No encontré información específica de accesibilidad para {lugar}. Te recomiendo contactar directamente con el lugar."
        
        response = f"Sobre la accesibilidad de {lugar}: "
        
        if accesible.lower() in ['sí', 'si', 'yes', 'accesible', 'adaptado']:
            response += "es accesible para personas con movilidad reducida"
        elif accesible.lower() in ['no', 'no accesible', 'no adaptado']:
            response += "no está completamente adaptado para personas con movilidad reducida"
        else:
            response += f"la información indica: {accesible}"
        
        if detalles:
            response += f". {detalles}"
        
        return response + "." 