import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client.get_database("app")

artists_collection = db["artists"]
new_events_collection = db["newevents"]
emailevents_collection = db["emailevents"]
users_collection = db["users"]
