from datetime import datetime
from bson import ObjectId
from typing import Optional, Dict, Any, List

# Variável global para receber instância do db
db = None

def init_db(database_instance):
    """Inicializar a conexão do banco no models"""
    global db
    db = database_instance
    print("✅ Models inicializado com sucesso!")

# USsuarios

def create_user(username: str, email: str, password_hash: str) -> Dict[str, Any]:
    """Criar usuário"""
    try:
        # Criar usuário
        now = datetime.utcnow()
        result = db.users.insert_one({
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "active": True,
            "created_at": now,
            "updated_at": now
        })
        
        return {
            "success": True, 
            "user_id": str(result.inserted_id),
            "message": "Usuário criado com sucesso!"
        }
        
    except Exception as e:
        return {"error": f"Erro ao criar usuário: {str(e)}"}


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Buscar usuário por ID com tratamento de erro"""
    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])  # Converter Id para string
        return user
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Buscar usuário por email"""
    try:
        user = db.users.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        print(f"Erro ao buscar usuário por email: {e}")
        return None

def update_user(user_id: str, **fields) -> Dict[str, Any]:
    """Atualizar usuário"""
    try:
        fields["updated_at"] = datetime.utcnow()
        res = db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": fields}
        )
        
        if res.modified_count > 0:
            return {"success": True, "message": "Usuário atualizado!"}
        else:
            return {"error": "Usuário não encontrado ou nenhum campo alterado"}
            
    except Exception as e:
        return {"error": f"Erro ao atualizar usuário: {str(e)}"}


def delete_user(user_id: str) -> Dict[str, Any]:
    """Deletar usuário"""
    try:
        res = db.users.delete_one({"_id": ObjectId(user_id)})
        
        if res.deleted_count > 0:
            return {"success": True, "message": "Usuário deletado!"}
        else:
            return {"error": "Usuário não encontrado"}
            
    except Exception as e:
        return {"error": f"Erro ao deletar usuário: {str(e)}"}

# Música
def create_song(title: str, artist: str, spotify_url: str, genres: List[str] = None) -> Dict[str, Any]:
    """Criar música """
    try:
        # Validações
        if len(title) < 1:
            return {"error": "Título é obrigatório"}
        
        if len(artist) < 1:
            return {"error": "Artista é obrigatório"}
        
        # Verificar se música já existe
        existing = db.songs.find_one({"title": title, "artist": artist})
        if existing:
            return {"error": "Música já cadastrada"}
        
        now = datetime.utcnow()
        doc = {
            "title": title,
            "artist": artist,
            "spotify_url": spotify_url,
            "genres": genres or [],
            "play_count": 0,  # Contador de reproduções
            "created_at": now,
            "updated_at": now
        }
        
        result = db.songs.insert_one(doc)
        return {
            "success": True,
            "song_id": str(result.inserted_id),
            "message": "Música criada com sucesso!"
        }
        
    except Exception as e:
        return {"error": f"Erro ao criar música: {str(e)}"}



def search_songs(query: str) -> List[Dict[str, Any]]:
    """Buscar músicas por título ou artista"""
    try:
        songs = []
        search_filter = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"artist": {"$regex": query, "$options": "i"}}
            ]
        }
        
        for song in db.songs.find(search_filter):
            song["_id"] = str(song["_id"])
            songs.append(song)
        return songs
    except Exception as e:
        print(f"Erro ao buscar músicas: {e}")
        return []


def update_song(song_id: str, **fields) -> Dict[str, Any]:
    """Atualizar música"""
    try:
        fields["updated_at"] = datetime.utcnow()
        res = db.songs.update_one(
            {"_id": ObjectId(song_id)},
            {"$set": fields}
        )
        
        if res.modified_count > 0:
            return {"success": True, "message": "Música atualizada!"}
        else:
            return {"error": "Música não encontrada"}
            
    except Exception as e:
        return {"error": f"Erro ao atualizar música: {str(e)}"}


def delete_song(song_id: str) -> Dict[str, Any]:
    """Deletar música"""
    try:
        res = db.songs.delete_one({"_id": ObjectId(song_id)})
        
        if res.deleted_count > 0:
            return {"success": True, "message": "Música deletada!"}
        else:
            return {"error": "Música não encontrada"}
            
    except Exception as e:
        return {"error": f"Erro ao deletar música: {str(e)}"}

# Entrada de humor

def create_mood_entry(user_id: str, emoji: str, song_id: str, comment: str = "") -> Dict[str, Any]:
    """Criar entrada de humor"""
    try:
        # Validações
        if not user_id or not emoji or not song_id:
            return {"error": "user_id, emoji e song_id são obrigatórios"}
        
        # Verificar se usuário existe
        if not get_user_by_id(user_id):
            return {"error": "Usuário não encontrado"}
        
        # Verificar se música existe
        if not get_song(song_id):
            return {"error": "Música não encontrada"}
        
        now = datetime.utcnow()
        doc = {
            "user_id": ObjectId(user_id),
            "song_id": ObjectId(song_id),
            "emoji": emoji,
            "comment": comment,
            "date": now.strftime("%Y-%m-%d"),  # Data apenas (para agrupamentos)
            "created_at": now,
            "updated_at": now
        }
        
        result = db.mood_entries.insert_one(doc)
        
        # Incrementar contador de reprodução da música
        db.songs.update_one(
            {"_id": ObjectId(song_id)},
            {"$inc": {"play_count": 1}}
        )
        
        return {
            "success": True,
            "mood_id": str(result.inserted_id),
            "message": "Humor registrado com sucesso!"
        }
        
    except Exception as e:
        return {"error": f"Erro ao criar entrada de humor: {str(e)}"}


def list_mood_entries(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Listar entradas de humor de um usuário"""
    try:
        entries = []
        for entry in db.mood_entries.find({"user_id": ObjectId(user_id)}).sort("created_at", -1).limit(limit):
            entry["_id"] = str(entry["_id"])
            entry["user_id"] = str(entry["user_id"])
            entry["song_id"] = str(entry["song_id"])
            entries.append(entry)
        return entries
    except Exception as e:
        print(f"Erro ao listar entradas de humor: {e}")
        return []


def get_user_mood_stats(user_id: str, days: int = 30) -> Dict[str, Any]:
    """Estatísticas de humor do usuário"""
    try:
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Pipeline de agregação para estatísticas
        pipeline = [
            {"$match": {
                "user_id": ObjectId(user_id),
                "created_at": {"$gte": start_date}
            }},
            {"$group": {
                "_id": "$emoji",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        mood_distribution = list(db.mood_entries.aggregate(pipeline))
        total_entries = sum(item["count"] for item in mood_distribution)
        
        # Estatísticas gerais
        total_all_time = db.mood_entries.count_documents({"user_id": ObjectId(user_id)})
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_entries_period": total_entries,
            "total_entries_all_time": total_all_time,
            "mood_distribution": mood_distribution,
            "most_common_mood": mood_distribution[0]["_id"] if mood_distribution else None,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Erro ao gerar estatísticas: {str(e)}"}


def update_mood_entry(entry_id: str, **fields) -> Dict[str, Any]:
    """Atualizar humor"""
    try:
        fields["updated_at"] = datetime.utcnow()
        res = db.mood_entries.update_one(
            {"_id": ObjectId(entry_id)},
            {"$set": fields}
        )
        
        if res.modified_count > 0:
            return {"success": True, "message": "Entrada atualizada!"}
        else:
            return {"error": "Entrada não encontrada"}
            
    except Exception as e:
        return {"error": f"Erro ao atualizar entrada: {str(e)}"}


def delete_mood_entry(entry_id: str) -> Dict[str, Any]:
    """Deletar humor"""
    try:
        res = db.mood_entries.delete_one({"_id": ObjectId(entry_id)})
        
        if res.deleted_count > 0:
            return {"success": True, "message": "Entrada deletada!"}
        else:
            return {"error": "Entrada não encontrada"}
            
    except Exception as e:
        return {"error": f"Erro ao deletar entrada: {str(e)}"}