import pandas as pd
import mysql.connector
from mysql.connector import Error
import redis

def connect_to_redis():
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("Successfully connected to Redis")
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"Redis connection error: {e}")
        return None

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='db_examv2',
            user='root',
            password=''
        )
        if connection.is_connected():
            print("Successfully connected to MySQL")
            return connection
    except Error as e:
        print(f"MySQL connection error: {e}")
        return None

def test_connections():
    db = connect_to_database()
    redis_client = connect_to_redis()

    if db:
        db.close()
        print("MySQL connection closed")

    if redis_client:
        redis_client.close()
        print("Redis connection closed")

if __name__ == "__main__":
    test_connections()
