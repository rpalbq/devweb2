from flask import Flask, jsonify
import os
from pymongo import MongoClient

app = Flask(__name__)

# Conexão MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
try:
    client = MongoClient(MONGO_URI)
    db = client["moodtracker"]
    print(f" Report Service conectado ao MongoDB: {MONGO_URI}")
except Exception as e:
    print(f" Erro ao conectar MongoDB: {e}")

@app.route('/')
def home():
    return jsonify({
        "message": "Report Service funcionando!",
        "service": "report-service",
        "port": 5001,
        "status": "OK"
    })

@app.route('/test-db')
def test_db():
    try:
        db.admin.command('ping')
        return jsonify({
            "database": "MongoDB conectadi",
            "service": "report-service"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "report-service"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

    