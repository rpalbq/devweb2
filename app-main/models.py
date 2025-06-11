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

        existing = db.users.find_one({"email": email})
        if existing:
          return {"error": "E-mail já utilizado"}  

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
def create_song(title: str, artist: str, spotify_url: str, user_id: str = None, genres: List[str] = None) -> Dict[str, Any]:
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
            "user_id": ObjectId(user_id) if user_id else None,  # responsavel por ter mood registrado privado
            "genres": genres or [],
            "play_count": 0, 
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

def create_mood_entry(user_id: str, emoji: str, song_id: str = None, comment: str = "") -> Dict[str, Any]:
    """Criar entrada de humor"""
    try:
        # Validações
        if not user_id or not emoji: 
            return {"error": "user_id e emoji são obrigatórios"}  
        # Verificar se usuário existe
        if not get_user_by_id(user_id):
            return {"error": "Usuário não encontrado"}
        
        # Verificar música APENAS se fornecida
        if song_id and not get_song(song_id):  # ← ADICIONAR song_id check
            return {"error": "Música não encontrada"}
        
        now = datetime.utcnow()
        doc = {
            "user_id": ObjectId(user_id),
            "emoji": emoji,
            "comment": comment,
            "date": now.strftime("%Y-%m-%d"),
            "created_at": now,
            "updated_at": now
        }
        
        # Adicionar song_id APENAS se fornecido
        if song_id:
            doc["song_id"] = ObjectId(song_id)
        
        result = db.mood_entries.insert_one(doc)
        
        # Incrementar contador APENAS se tiver música
        if song_id:
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
    try:
        entries = []
        for entry in db.mood_entries.find({"user_id": ObjectId(user_id)}).sort("created_at", -1).limit(limit):
            entry["_id"] = str(entry["_id"])
            entry["user_id"] = str(entry["user_id"])
            
            # Só converter song_id se existir
            if "song_id" in entry and entry["song_id"]:
                entry["song_id"] = str(entry["song_id"])
            else:
                entry["song_id"] = None
                
            entries.append(entry)
        return entries
    except Exception as e:
        print(f"Erro ao listar entradas de humor: {e}")
        return []
        
        
        
def get_mood_entries_with_songs(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Buscar entradas de humor com informações das músicas (JOIN)"""
    try:
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id)}},
            {"$sort": {"created_at": -1}},
            {"$limit": limit},
            {"$lookup": {
                "from": "songs",
                "localField": "song_id",
                "foreignField": "_id", 
                "as": "song_info"
            }},
            {"$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user_info"
            }}
        ]
        
        results = []
        for entry in db.mood_entries.aggregate(pipeline):
            entry["_id"] = str(entry["_id"])
            entry["user_id"] = str(entry["user_id"])
            if "song_id" in entry and entry["song_id"]:
                 entry["song_id"] = str(entry["song_id"])
            else:
                  entry["song_id"] = None
            
            # Adicionar info da música e usuário
            if entry["song_info"]:
                entry["song"] = entry["song_info"][0]
                entry["song"]["_id"] = str(entry["song"]["_id"])
            
            if entry["user_info"]:
                entry["user"] = {"username": entry["user_info"][0]["username"]}
            
            # Limpar campos auxiliares
            entry.pop("song_info", None)
            entry.pop("user_info", None)
            
            results.append(entry)
        
        return results
        
    except Exception as e:
        print(f"Erro ao buscar entradas com músicas: {e}")
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
    

def get_song(song_id: str) -> Optional[Dict[str, Any]]:
    """Buscar música por ID"""
    try:
        song = db.songs.find_one({"_id": ObjectId(song_id)})
        if song:
            song["_id"] = str(song["_id"])
        return song
    except Exception as e:
        print(f"Erro ao buscar música: {e}")
        return None

def list_songs(user_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    try:
        songs = []
        
        # Filtro: só músicas do usuário ou globais (sem user_id)
        if user_id:
            filter_query = {
                "$or": [
                    {"user_id": ObjectId(user_id)},  # Músicas do usuário
                    {"user_id": None}                # Músicas globais
                ]
            }
        else:
            filter_query = {}
        
        for song in db.songs.find(filter_query).limit(limit):
            song["_id"] = str(song["_id"])
            songs.append(song)
        return songs
    except Exception as e:
        print(f"Erro ao listar músicas: {e}")
        return []

def list_all_users() -> List[Dict[str, Any]]:
    """Listar todos os usuários"""
    try:
        users = []
        for user in db.users.find():
            user["_id"] = str(user["_id"])
            user.pop('password_hash', None)  # Remover senha por segurança
            users.append(user)
        return users
    except Exception as e:
        print(f"Erro ao listar usuários: {e}")
        return []

def get_mood_entry(mood_id: str) -> Optional[Dict[str, Any]]:
    """Buscar entrada de mood por ID"""
    try:
        mood = db.mood_entries.find_one({"_id": ObjectId(mood_id)})
        if mood:
            mood["_id"] = str(mood["_id"])
            mood["user_id"] = str(mood["user_id"])
            mood["song_id"] = str(mood["song_id"])
        return mood
    except Exception as e:
        print(f"Erro ao buscar mood: {e}")
        return None