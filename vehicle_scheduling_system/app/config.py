# app/config.py
from pymongo import MongoClient

# MongoDB connection using MongoDB Atlas URI
client = MongoClient(
            "mongodb+srv://intothejungle:Kjhgfdsa08#@intothejungle.vfm0u.mongodb.net/?retryWrites=true&w=majority&appName=IntoTheJungle"
)
db = client["IntothejungleDB"] # Specify the database name

from mongoengine import connect

# MongoDB connection (for local or MongoDB Atlas)
connect(
    db="IntothejungleDB",  # Database name
   
    host="mongodb+srv://intothejungle:Kjhgfdsa08#@intothejungle.vfm0u.mongodb.net/?retryWrites=true&w=majority&appName=IntoTheJungle",  # Replace with your MongoDB URI
  
)

