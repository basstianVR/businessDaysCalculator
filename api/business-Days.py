from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import holidays
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Obtener los parámetros de la URL
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        
        start_str = query.get('startDate', [None])[0]
        end_str = query.get('endDate', [None])[0]
        
        # 2. Validar que existan las fechas
        if not start_str or not end_str:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Faltan los parametros startDate o endDate"}).encode())
            return
            
        try:
            # 3. Tu lógica original intacta
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
            
            # 4. Devolver la respuesta en formato JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            # Permitir CORS por si lo consultas desde el frontend
            self.send_header('Access-Control-Allow-Origin', '*') 
            self.end_headers()
            self.wfile.write(json.dumps({"dias_habiles": resultado}).encode())
            
        except Exception as e:
            # Manejo de errores por si envían fechas con mal formato
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
