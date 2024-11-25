# app/config.py
from pymongo import MongoClient

# MongoDB connection using MongoDB Atlas URI
client = MongoClient("mongodb+srv://researchtestdb1:testUser123@cluster0.lvsx7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["vehicle_scheduling_db"]  # Specify the database name

from mongoengine import connect

# MongoDB connection (for local or MongoDB Atlas)
connect(
    db="vehicle_scheduling_db",  # Database name
   
    host="mongodb+srv://researchtestdb1:testUser123@cluster0.lvsx7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",  # Replace with your MongoDB URI
  
)

