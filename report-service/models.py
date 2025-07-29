from datetime import datetime
from bson import ObjectId
from typing import Optional, Dict, Any, List

# Variável global para receber instância do db
db = None

def init_db(database_instance):
    """Inicializar a conexão do banco no models"""
    global db
    db = database_instance
    print("✅ Report Models inicializado com sucesso!")

#  USUÁRIOS

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Buscar usuário por ID com tratamento de erro"""
    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None

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

#  MÚSICAS

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

def list_songs(limit: int = 50) -> List[Dict[str, Any]]:
    """Listar músicas"""
    try:
        songs = []
        for song in db.songs.find().limit(limit):
            song["_id"] = str(song["_id"])
            songs.append(song)
        return songs
    except Exception as e:
        print(f"Erro ao listar músicas: {e}")
        return []

#  ENTRADAS DE HUMOR

def get_mood_entry(mood_id: str) -> Optional[Dict[str, Any]]:
    """Buscar entrada de mood por ID"""
    try:
        mood = db.mood_entries.find_one({"_id": ObjectId(mood_id)})
        if mood:
            mood["_id"] = str(mood["_id"])
            mood["user_id"] = str(mood["user_id"])
            if mood.get("song_id"):
                mood["song_id"] = str(mood["song_id"])
            else:
                mood["song_id"] = None
        return mood
    except Exception as e:
        print(f"Erro ao buscar mood: {e}")
        return None

def list_mood_entries(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Listar entradas de humor de um usuário"""
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

#  FUNÇÃO PRINCIPAL DE ESTATÍSTICAS
def get_user_mood_stats(user_id: str, days: int = 30) -> Dict[str, Any]:
    """
     Estatísticas de humor do usuário - VERSÃO COMPLETA PARA RELATÓRIOS
    """
    try:
        from datetime import timedelta
        
        print(f"📊 Gerando estatísticas para usuário {user_id} (últimos {days} dias)")
        
        # Verificar se usuário existe
        user = get_user_by_id(user_id)
        if not user:
            return {"error": "Usuário não encontrado"}
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Pipeline de agregação para distribuição de humor
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
        total_entries_period = sum(item["count"] for item in mood_distribution)
        
        # Estatísticas gerais (todos os tempos)
        total_all_time = db.mood_entries.count_documents({"user_id": ObjectId(user_id)})
        
        # Humor mais comum
        most_common_mood = mood_distribution[0]["_id"] if mood_distribution else None
        
        # Estatísticas adicionais para relatórios
        unique_days_with_entries = len(list(db.mood_entries.distinct("date", {
            "user_id": ObjectId(user_id),
            "created_at": {"$gte": start_date}
        })))
        
        # Músicas mais associadas aos humores
        songs_pipeline = [
            {"$match": {
                "user_id": ObjectId(user_id),
                "created_at": {"$gte": start_date},
                "song_id": {"$exists": True, "$ne": None}
            }},
            {"$lookup": {
                "from": "songs",
                "localField": "song_id",
                "foreignField": "_id",
                "as": "song_info"
            }},
            {"$unwind": "$song_info"},
            {"$group": {
                "_id": "$song_id",
                "count": {"$sum": 1},
                "song_title": {"$first": "$song_info.title"},
                "song_artist": {"$first": "$song_info.artist"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        
        top_songs = list(db.mood_entries.aggregate(songs_pipeline))
        
        result = {
            "user_id": user_id,
            "user_info": {
                "username": user.get("username", "Usuário"),
                "email": user.get("email", ""),
                "user_type": user.get("user_type", "patient")
            },
            "period_days": days,
            "total_entries_period": total_entries_period,
            "total_entries_all_time": total_all_time,
            "unique_days_with_entries": unique_days_with_entries,
            "mood_distribution": mood_distribution,
            "most_common_mood": most_common_mood,
            "top_songs": top_songs,
            "generated_at": datetime.utcnow().isoformat(),
            "report_summary": {
                "activity_level": "Alto" if total_entries_period > 20 else "Médio" if total_entries_period > 10 else "Baixo",
                "consistency": f"{unique_days_with_entries}/{days} dias com registros",
                "mood_variety": len(mood_distribution)
            }
        }
        
        print(f"✅ Estatísticas geradas: {total_entries_period} entradas no período")
        return result
        
    except Exception as e:
        print(f"❌ Erro ao gerar estatísticas: {e}")
        return {"error": f"Erro ao gerar estatísticas: {str(e)}"}

# FUNÇÃO ADICIONAL: COMPARAR PERÍODOS
def compare_mood_periods(user_id: str, days1: int = 30, days2: int = 60) -> Dict[str, Any]:
    """Comparar humor entre dois períodos diferentes"""
    try:
        period1 = get_user_mood_stats(user_id, days1)
        period2 = get_user_mood_stats(user_id, days2)
        
        if 'error' in period1 or 'error' in period2:
            return {"error": "Erro ao comparar períodos"}
        
        # Calcular diferenças
        entries_diff = period1['total_entries_period'] - period2['total_entries_period']
        
        return {
            "user_id": user_id,
            "comparison": {
                "period1": f"Últimos {days1} dias",
                "period2": f"Últimos {days2} dias", 
                "entries_period1": period1['total_entries_period'],
                "entries_period2": period2['total_entries_period'],
                "difference": entries_diff,
                "trend": "Aumentou" if entries_diff > 0 else "Diminuiu" if entries_diff < 0 else "Manteve"
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Erro ao comparar períodos: {str(e)}"}