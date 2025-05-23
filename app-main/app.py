from flask import Flask, jsonify
import os
from pymongo import MongoClient

app = Flask(__name__)

# Conexão MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
try:
    client = MongoClient(MONGO_URI)
    db = client["moodtracker"]
    print(f" Conectado ao MongoDB: {MONGO_URI}")
except Exception as e:
    print(f" Erro ao conectar MongoDB: {e}")

@app.route('/')
def home():
    return jsonify({
        "message": "App Main funcionando!",
        "service": "app-main",
        "port": 5000,
        "status": "OK"
    })

@app.route('/test-db')
def test_db():
    try:
        # Testar conexão
        db.admin.command('ping')
        return jsonify({
            "database": "MongoDB conectado!",
            "collections": db.list_collection_names()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)