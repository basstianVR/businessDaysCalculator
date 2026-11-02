from http.server import BaseHTTPRequestHandler
from datetime import datetime, timedelta
import holidays
import json

from api.jira_revert_field import handle_post as handle_jira_revert


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))

            if content_length == 0:
                self._send_response(400, {"error": "El cuerpo de la petición está vacío"})
                return

            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))

            if "jira-revert-field" in self.path:
                handle_jira_revert(body, self._send_response)
                return

            start_str = body.get('startDate')
            end_str = body.get('endDate')

            if not start_str or not end_str:
                self._send_response(200, {"dias_habiles": 0})
                return

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

            self._send_response(200, {"resultado": resultado})

        except Exception as e:
            self._send_response(500, {"error": str(e)})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _send_response(self, code, payload):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())
