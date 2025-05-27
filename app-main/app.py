from flask import Flask, jsonify, request
import os
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

# Importar models
import models

app = Flask(__name__)

#Conexão MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
DB_NAME = os.getenv("DB_NAME", "moodtracker")

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Testar conexão
    client.admin.command('ping')
    print(f"✅ Conectado ao MongoDB: {MONGO_URI}")
    print(f"✅ Database: {DB_NAME}")
    
    models.init_db(db)
    
except Exception as e:
    print(f"Erro ao conectar MongoDB: {e}")
    exit(1)

#Rotas

@app.route('/')
def home():
    return jsonify({
        "message": "🎵 API funcionando",
        "service": "app-main",
        "port": 5000,
        "status": "OK",
        "endpoints": {
            "users": "/users",
            "songs": "/songs", 
            "moods": "/moods",
            "test": "/test-db"
        }
    })

@app.route('/test-db')
def test_db():
    try:
        # Testar conexão
        client.admin.command('ping')
        collections = db.list_collection_names()
        
        #Contar documentos
        counts = {}
        for collection in ['users', 'songs', 'mood_entries']:
            counts[collection] = db[collection].count_documents({})
        
        return jsonify({
            "status": "✅ MongoDB conectado!",
            "database": DB_NAME,
            "collections": collections,
            "document_counts": counts
        })
    except Exception as e:
        return jsonify({
            "status": "❌ Erro na conexão",
            "error": str(e)
        }), 500

#Rotas dos Usuarios

@app.route('/users', methods=['POST'])
def create_user():
    """Criar novo usuário"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data:
            return jsonify({"error": "JSON é obrigatório"}), 400
        
        required_fields = ['username', 'email', 'password']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({
                "error": f"Campos obrigatórios: {', '.join(missing_fields)}"
            }), 400
        
        # Hash da senha
        password_hash = generate_password_hash(data['password'])
        
        # Criar usuário usando models
        result = models.create_user(
            username=data['username'],
            email=data['email'],
            password_hash=password_hash
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500




@app.route('/users', methods=['GET'])
def list_users():
    """Listar todos os usuários"""
    try:
        users = models.list_all_users() #Depende de uma função do models
        return jsonify({
            "users": users,
            "total": len(users)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Buscar usuário específico"""
    try:
        user = models.get_user_by_id(user_id)
        if user:
            # Remover senha da resposta
            user.pop('password_hash', None)
            return jsonify({"user": user})
        else:
            return jsonify({"error": "Usuário não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Atualizar usuário"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON é obrigatório"}), 400   
        
        result = models.update_user(user_id, **data)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Deletar usuário"""
    try:
        result = models.delete_user(user_id)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Rotas das musicas

@app.route('/songs', methods=['POST'])
def create_song():
    """Criar nova música"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON é obrigatório"}), 400
        
        required_fields = ['title', 'artist', 'spotify_url']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({
                "error": f"Campos obrigatórios: {', '.join(missing_fields)}"
            }), 400
        
        result = models.create_song(
            title=data['title'],
            artist=data['artist'],
            spotify_url=data['spotify_url'],
            genres=data.get('genres', [])
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/songs', methods=['GET'])
def list_songs():
    """Listar músicas"""
    try:
        limit = request.args.get('limit', 50, type=int)
        songs = models.list_songs(limit=limit)
        
        return jsonify({
            "songs": songs,
            "total": len(songs),
            "limit": limit
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/songs/<song_id>', methods=['GET'])
def get_song(song_id):
    """Buscar música específica"""
    try:
        song = models.get_song(song_id)
        if song:
            return jsonify({"song": song})
        else:
            return jsonify({"error": "Música não encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/songs/<song_id>', methods=['PUT'])
def update_song(song_id):
    """Atualizar música"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON é obrigatório"}), 400
        
        result = models.update_song(song_id, **data)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/songs/<song_id>', methods=['DELETE'])
def delete_song(song_id):
    """Deletar música"""
    try:
        result = models.delete_song(song_id)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Rotas dos moods

@app.route('/moods', methods=['POST'])
def create_mood():
    """Criar entrada de humor"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON é obrigatório"}), 400
        
        required_fields = ['user_id', 'emoji', 'song_id']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({
                "error": f"Campos obrigatórios: {', '.join(missing_fields)}"
            }), 400
        
        result = models.create_mood_entry(
            user_id=data['user_id'],
            emoji=data['emoji'],
            song_id=data['song_id'],
            comment=data.get('comment', '')
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
        
@app.route('/moods/user/<user_id>', methods=['GET'])
def get_user_moods(user_id):
    """Buscar humores de um usuário"""
    try:
        limit = request.args.get('limit', 20, type=int)
        detailed = request.args.get('detailed', 'false').lower() == 'true'
        
        if detailed:
            # Com informações das músicas
            moods = models.get_mood_entries_with_songs(user_id, limit=limit)
        else:
            # Apenas as entradas
            moods = models.list_mood_entries(user_id, limit=limit)
        
        return jsonify({
            "moods": moods,
            "total": len(moods),
            "user_id": user_id,
            "detailed": detailed
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
        

@app.route('/moods/<mood_id>', methods=['GET'])
def get_mood(mood_id):
    """Buscar entrada de humor específica"""
    try:
        mood = models.get_mood_entry(mood_id)
        if mood:
            return jsonify({"mood": mood})
        else:
            return jsonify({"error": "Entrada não encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/moods/<mood_id>', methods=['PUT'])
def update_mood(mood_id):
    """Atualizar entrada de humor"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON é obrigatório"}), 400
        
        result = models.update_mood_entry(mood_id, **data)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/moods/<mood_id>', methods=['DELETE'])
def delete_mood(mood_id):
    """Deletar entrada de humor"""
    try:
        result = models.delete_mood_entry(mood_id)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
        
        
        # Estatísticas

@app.route('/stats/user/<user_id>')
def get_user_stats(user_id):
    """Estatísticas do usuário"""
    try:
        days = request.args.get('days', 30, type=int)
        stats = models.get_user_mood_stats(user_id, days=days)
        
        if 'error' in stats:
            return jsonify(stats), 400
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Parte de login/acesso

@app.route('/auth/login', methods=['POST'])
def login():
    """Login do usuário"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email e senha são obrigatórios"}), 400
        
        # Buscar usuário
        user = models.get_user_by_email(data['email'])
        if not user:
            return jsonify({"error": "Credenciais inválidas"}), 401
        
        # Verificar senha
        if not check_password_hash(user['password_hash'], data['password']):
            return jsonify({"error": "Credenciais inválidas"}), 401
        
        # Remover senha da resposta
        user.pop('password_hash', None)
        
        return jsonify({
            "success": True,
            "message": "Login realizado com sucesso!",
            "user": user
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# erros 

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint não encontrado"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Método não permitido"}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Erro interno do servidor"}), 500


#Execução do app
if __name__ == '__main__':
    print("🚀 Iniciando MoodTracker API...")
    print("📊 Endpoints disponíveis:")
    print("   GET  /                    - Info da API")
    print("   GET  /test-db             - Testar MongoDB")
    print("   POST /users               - Criar usuário")
    print("   GET  /users               - Listar usuários")
    print("   POST /songs               - Criar música")
    print("   GET  /songs               - Listar músicas")
    print("   POST /moods               - Criar mood entry")
    print("   GET  /moods/user/<id>     - Moods do usuário")
    print("   GET  /stats/user/<id>     - Estatísticas")
    print("   POST /auth/login          - Login")
    
    app.run(host='0.0.0.0', port=5000, debug=True)