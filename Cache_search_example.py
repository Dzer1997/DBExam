from data_connextion import connect_to_database, connect_to_redis

# Etabler forbindelser
db_conn = connect_to_database()
redis_conn = connect_to_redis()

def search_users_by_name(name, db_conn, redis_conn):
    cache_key = f"search:name:{name.lower()}"

    # Check cache først
    cached_result = redis_conn.get(cache_key)
    if cached_result:
        print("Resultat hentet fra Redis-cache")
        return eval(cached_result)

    # Ellers søg i MySQL
    cursor = db_conn.cursor()
    query = "SELECT user_id, email FROM Users WHERE email LIKE %s"
    cursor.execute(query, (f"%{name}%",))
    result = cursor.fetchall()

    # Gem resultat i Redis (cache i 60 sekunder)
    redis_conn.setex(cache_key, 60, str(result))
    print("Resultat hentet fra MySQL og gemt i cache")
    return result

# Brug funktionen først
if db_conn and redis_conn:
    result = search_users_by_name("Lars", db_conn, redis_conn)
    print(result)

    # Luk forbindelserne bagefter
    db_conn.close()
    redis_conn.close()
