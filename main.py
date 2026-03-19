import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuración desde variables de entorno (por seguridad)
JIRA_DOMAIN = os.environ.get("JIRA_DOMAIN")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL")
JIRA_TOKEN = os.environ.get("JIRA_TOKEN")

@app.route('/calcular', methods=['POST'])
def calcular():
    data = request.json
    # 1. Extraer datos enviados por Jira Automation
    issue_key = data.get('issueKey')
    valor_a = float(data.get('valorA', 0))
    valor_b = float(data.get('valorB', 0))

    # 2. TU LÓGICA COMPLEJA
    # Ejemplo: Un cálculo que Jira no puede hacer (ej. raíz cuadrada del producto)
    import math
    resultado = math.sqrt(valor_a * valor_b)

    # 3. Devolver el valor a Jira vía API REST
    url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{issue_key}"
    auth = (JIRA_EMAIL, JIRA_TOKEN)
    
    # IMPORTANTE: Cambia 'customfield_100XX' por el ID real de tu campo en Jira
    payload = {
        "fields": {
            "customfield_10030": round(resultado, 2) 
        }
    }
    
    response = requests.put(url, json=payload, auth=auth)
    
    return jsonify({
        "status": "procesado",
        "issue": issue_key,
        "jira_api_status": response.status_code
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)