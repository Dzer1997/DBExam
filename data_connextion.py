import pandas as pd
import mysql.connector
from mysql.connector import Error

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='db_examv2',
            user='root',
            password=''
        )
        if connection.is_connected():
            print("Successfully connected to the database")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
    

def test_connection():
    connection = connect_to_database()
    if connection:
        # If connection is successful, close it
        connection.close()
        print("Connection closed.")
    else:
        print("Failed to connect to the database.")

if __name__ == "__main__":
    test_connection()