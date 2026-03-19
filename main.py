from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/test-get', methods=['GET'])
def test_get():
    # Solo devolvemos un mensaje simple
    return jsonify({
        "mensaje": "comunicacion activa",
        "status": "ok"
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
