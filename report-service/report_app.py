from flask import Flask, jsonify, request, render_template
from flask_cors import CORS 
import os
from pymongo import MongoClient
import models
import json
from bson import ObjectId


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

def serialize_document(doc):
    """Converte recursivamente ObjectIds para strings"""
    if isinstance(doc, dict):
        return {key: serialize_document(value) for key, value in doc.items()}
    elif isinstance(doc, list):
        return [serialize_document(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc



app = Flask(__name__)
CORS(app)
app.json_encoder = JSONEncoder






# Conexão MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
DB_NAME = os.getenv("DB_NAME", "moodtracker")

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Testar conexão
    client.admin.command('ping')
    print(f"✅ Report Service conectado ao MongoDB: {MONGO_URI}/{DB_NAME}")
    
    # Inicializar models
    models.init_db(db)
    
except Exception as e:
    print(f"❌ Erro ao conectar MongoDB: {e}")
    exit(1)

@app.route('/')
def home():
    return jsonify({
        "message": "Report Service funcionando!",
        "service": "report-service",
        "port": 5001,
        "status": "OK",
        "endpoints": {
            "/reports/user_mood_stats/<user_id>": "Estatísticas JSON",
            "/reports/html/<user_id>": "Relatório HTML",
            "/test-db": "Testar conexão MongoDB",
            "/health": "Health check"
        }
    })

@app.route('/test-db')
def test_db():
    try:
        client.admin.command('ping')
        collections = db.list_collection_names()
        
        # Contar documentos
        counts = {}
        for collection in ['users', 'songs', 'mood_entries']:
            counts[collection] = db[collection].count_documents({})
        
        return jsonify({
            "status": "✅ MongoDB conectado!",
            "database": DB_NAME,
            "service": "report-service",
            "collections": collections,
            "document_counts": counts
        })
    except Exception as e:
        return jsonify({
            "status": "❌ Erro na conexão",
            "error": str(e)
        }), 500

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "report-service",
        "mongodb_connected": True
    })

#  ROTA PRINCIPAL DE RELATÓRIOS
@app.route('/reports/user_mood_stats/<user_id>', methods=['GET'])
def get_user_mood_statistics(user_id):
    """
    Retorna estatísticas de humor para um usuário específico.
    Permite filtrar por número de dias.
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        print(f"📊 Gerando relatório para usuário {user_id} (últimos {days} dias)")
        
        # Usar função do models
        stats = models.get_user_mood_stats(user_id, days=days)
        
        if 'error' in stats:
            print(f"❌ Erro nas estatísticas: {stats['error']}")
            return jsonify(stats), 400
        
        print(f"✅ Relatório gerado com sucesso: {stats['total_entries_period']} entradas")
        clean_stats = serialize_document(stats)
        return jsonify(clean_stats), 200

    except Exception as e:
        print(f"❌ Erro ao gerar relatório para o usuário {user_id}: {e}")
        return jsonify({"error": f"Erro interno ao gerar relatório: {str(e)}"}), 500

# ROTA HTML DO RELATÓRIO
@app.route('/reports/html/<user_id>', methods=['GET'])
def get_report_html(user_id):
    """
    Renderiza a página HTML do relatório para um usuário específico.
    O JavaScript na página fará a chamada para o endpoint JSON.
    """
    print(f" Renderizando página de relatório para usuário: {user_id}")
    return render_template('report.html', user_id=user_id)


@app.route('/reports/patients', methods=['GET'])
def list_all_patients():
    """Lista todos os pacientes para profissionais"""
    try:
        print(" Listando pacientes para profissional...")
        
        # Buscar apenas usuários do tipo 'patient'
        patients = list(db.users.find(
            {"user_type": "patient"}, 
            {"_id": 1, "username": 1, "email": 1, "created_at": 1}
        ))
        
        # Converter ObjectId para string
        for patient in patients:
            patient["_id"] = str(patient["_id"])
        
        print(f"✅ {len(patients)} pacientes encontrados")
        
        return jsonify({
            "patients": patients,
            "total": len(patients)
        })
    except Exception as e:
        print(f"❌ Erro ao listar pacientes: {e}")
        return jsonify({"error": str(e)}), 500



#  ROTA ADICIONAL: LISTAR USUÁRIOS PARA RELATÓRIOS
@app.route('/reports/users', methods=['GET'])
def list_users_for_reports():
    """Lista usuários disponíveis para relatórios"""
    try:
        users = models.list_all_users()
        return jsonify({
            "users": users,
            "total": len(users)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#  HANDLERS DE ERRO
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint não encontrado",
        "service": "report-service"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Erro interno do servidor",
        "service": "report-service"
    }), 500







if __name__ == '__main__':
    print("🚀 Iniciando Report Service...")
    print("📊 Endpoints disponíveis:")
    print("   GET  /                              - Info do serviço")
    print("   GET  /test-db                       - Testar MongoDB")
    print("   GET  /health                        - Health check")
    print("   GET  /reports/user_mood_stats/<id>  - Estatísticas JSON")
    print("   GET  /reports/html/<id>             - Relatório HTML")
    print("   GET  /reports/users                 - Listar usuários")
    
    app.run(host='0.0.0.0', port=5001, debug=True)