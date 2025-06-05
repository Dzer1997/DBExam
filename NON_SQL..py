import pandas as pd
from pymongo import MongoClient
from pymongo import ReadPreference
from pymongo.errors import BulkWriteError



df = pd.read_csv("output_part_1.csv", low_memory=False)

df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]


for col in df.columns:
    try:
      
        df[col] = pd.to_datetime(df[col], errors='ignore')
    except Exception:
        pass
    try:
      
        df[col] = pd.to_numeric(df[col], errors='ignore')
    except Exception:
        pass

data = df.to_dict(orient="records")

client = MongoClient("mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0")
db = client["flights_db"]
collection = db["flight_data"]


# Check if collection already has data
if collection.count_documents({}) == 0:
    try:
        collection.insert_many(data)
        print("CSV inserted with all columns and auto-parsed types!")
    except BulkWriteError as bwe:
        print("Bulk write error:", bwe.details)
else:
    print("Data already exists, skipping insertion.")
