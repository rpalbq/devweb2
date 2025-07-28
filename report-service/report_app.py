from flask import Flask, jsonify, request, render_template, url_for
import os
from pymongo import MongoClient
import models 

app = Flask(__name__)

# Conexão MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
DB_NAME = os.getenv("DB_NAME", "moodtracker") 
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    models.init_db(db) 
    print(f" Report Service conectado ao MongoDB: {MONGO_URI}/{DB_NAME}")
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
            "service": "report-service",
            "collections": db.list_collection_names()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "report-service"
    })
    
    # rota p estatisticas de humor 
@app.route('/reports/user_mood_stats/<user_id>', methods=['GET'])
def get_user_mood_statistics(user_id):
    """
    Retorna estatísticas de humor para um usuário específico.
    Permite filtrar por número de dias.
    """
    try:
        days = request.args.get('days', 30, type=int) 
        
       
        stats = models.get_user_mood_stats(user_id, days=days) 
        
        if 'error' in stats:
            return jsonify(stats), 400
        
        return jsonify(stats), 200 

    except Exception as e:
        print(f"❌ Erro ao gerar relatório para o usuário {user_id}: {e}")
        return jsonify({"error": f"Erro interno ao gerar relatório: {str(e)}"}), 500
        
@app.route('/reports/html/<user_id>', methods=['GET'])
def get_report_html(user_id):
    """
    Renderiza a página HTML do relatório para um usuário específico.
    O JavaScript na página fará a chamada para o endpoint JSON.
    """
    return render_template('report.html', user_id=user_id) 


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
