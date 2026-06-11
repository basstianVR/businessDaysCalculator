from http.server import BaseHTTPRequestHandler
from datetime import datetime, timedelta
import holidays
import json

class handler(BaseHTTPRequestHandler):
    
    # Cambiamos do_GET por do_POST
    def do_POST(self):
        try:
            # 1. Leer la longitud del cuerpo (body) que nos envían
            content_length = int(self.headers.get('Content-Length', 0))
            
            if content_length == 0:
                self._send_response(400, {"error": "El cuerpo de la petición está vacío"})
                return
                
            # 2. Leer y decodificar el JSON del cuerpo
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
            
            # 3. Extraer las variables tal como lo hacían tus apps
            start_str = body.get('startDate')
            end_str = body.get('endDate')
            
            # 4. Validar (si no hay fechas, devolvemos 0 como en tu código original)
            if not start_str or not end_str:
                self._send_response(200, {"dias_habiles": 0})
                return
            
            # 5. Tu lógica original matemática intacta
            d1 = datetime.strptime(start_str.split('T')[0], '%Y-%m-%d').date()
            d2 = datetime.strptime(end_str.split('T')[0], '%Y-%m-%d').date()

            festivos_co = holidays.country_holidays('CO')

            es_negativo = d2 < d1
            fecha_inicio = d2 if es_negativo else d1
            fecha_fin = d1 if es_negativo else d2

            dias_habiles = 0
            curr = fecha_inicio

            while curr < fecha_fin:
                if curr.weekday() < 5 and curr not in festivos_co:
                    dias_habiles += 1
                curr += timedelta(days=1)

            resultado = -dias_habiles if es_negativo else dias_habiles
            
            # 6. Devolver el resultado
            self._send_response(200, {"dias_habiles": resultado})
            
        except Exception as e:
            self._send_response(500, {"error": str(e)})

    # Esta función responde a los navegadores/apps si preguntan por permisos (CORS)
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    # Función auxiliar para no repetir código al enviar respuestas
    def _send_response(self, code, payload):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())
