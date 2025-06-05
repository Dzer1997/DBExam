import pandas as pd
from pymongo import MongoClient
from pymongo.errors import BulkWriteError

# Load CSV
df = pd.read_csv("output_part_1.csv", low_memory=False)

# Clean column names: strip, lowercase, replace spaces with underscores
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Try to convert columns to datetime or numeric where possible
for col in df.columns:
    try:
        df[col] = pd.to_datetime(df[col], errors='ignore')
    except Exception:
        pass
    try:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    except Exception:
        pass

# Convert DataFrame to list of dictionaries for MongoDB insertion
data = df.to_dict(orient="records")

# Connect to local MongoDB instance
client = MongoClient("mongodb://mongo:27017")

# Select database and collection
db = client["flights_db"]
collection = db["flight_data"]

# Insert data into MongoDB collection with error handling
try:
    result = collection.insert_many(data)
    print(f"Inserted {len(result.inserted_ids)} documents successfully.")
except BulkWriteError as bwe:
    print("Bulk write error occurred:", bwe.details)
except Exception as e:
    print("An error occurred:", str(e))
