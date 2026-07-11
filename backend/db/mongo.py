"""MongoDB connection using PyMongo."""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
DB_NAME     = os.getenv("DB_NAME", "mi_prediction")

client = MongoClient(MONGODB_URI)
db     = client[DB_NAME]

# Collections
users_col       = db["users"]
predictions_col = db["predictions"]
