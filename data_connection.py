import mysql.connector
from mysql.connector import Error
import redis
import random
import json
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

logging.basicConfig(level=logging.INFO)

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# MySQL read replicas
REPLICA_PORTS = [3308]

def connect_to_replica():
    random.shuffle(REPLICA_PORTS)
    for port in REPLICA_PORTS:
        try:
            conn = mysql.connector.connect(
                host='localhost',
                port=port,
                user='read_user',
                password='read_pass',
                database='main_db'
            )
            if conn.is_connected():
                logging.info(f"Connected to replica on port {port}")
                return conn
        except Error as e:
            logging.warning(f"Replica connection failed (port {port}): {e}")
    logging.error("All replica connections failed.")
    return None

def connect_to_master():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            port=3307,
            user='app_user',        
            password='app_user_pass',
            database='main_db'
        )
        if conn.is_connected():
            logging.info("Connected to master DB")
            return conn
    except Error as e:
        logging.error(f"Failed to connect to master DB: {e}")
    return None
def read_with_cache(sql_query, params=(), cache_key=None, ttl=60):
    if not cache_key:
        cache_key = f"query:{sql_query}:{json.dumps(params)}"
    try:
        cached = redis_client.get(cache_key)
        if cached:
            logging.info(f"Cache hit: {cache_key}")
            return json.loads(cached)
    except Exception as e:
        logging.warning(f"Redis error: {e}", exc_info=True)
    conn = connect_to_replica()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, params)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            redis_client.setex(cache_key, ttl, json.dumps(result))
            logging.info(f"Cached result for: {cache_key}")
            return result
        except Exception as e:
            logging.error(f"Query execution error: {e}", exc_info=True)
    return []

def read_without_cache(sql_query, params=()):
    conn = connect_to_replica()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, params)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            logging.info("Query executed without cache.")
            return result
        except Exception as e:
            logging.error(f"Query execution error: {e}", exc_info=True)
    return []

def execute_write(sql_query, params=()):
    conn = connect_to_master()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, params)
            conn.commit()
            cursor.close()
            conn.close()
            logging.info("Write operation successful.")
            return True
        except Exception as e:
            logging.error(f"Write operation failed: {e}", exc_info=True)
    return False

def call_procedure(proc_name, args=()):
    conn = connect_to_master()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.callproc(proc_name, args)
            conn.commit()
            cursor.close()
            conn.close()
            logging.info(f"Procedure `{proc_name}` called successfully.")
            return True
        except Exception as e:
            logging.error(f"Stored procedure `{proc_name}` failed: {e}", exc_info=True)
    return False

_mongo_client = None  # <-- This must be at the top level

def get_mongo_client():
    global _mongo_client
    if _mongo_client is not None:
        return _mongo_client
    
    uri = "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0"
    logging.info(f"Connecting to MongoDB with URI: {uri}")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")  
        _mongo_client = client
        return _mongo_client
    except Exception as e:
        logging.error(f"MongoDB connection failed: {e}")
        return None