from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import gridfs

app = Flask(__name__)

# Initialize MongoDB connection and GridFS instance
try:
    client = MongoClient('mongodb://localhost:27017/')
    client.server_info()  # Test the connection
    print("Connected to MongoDB successfully!")
    
    db = client['imageDB']  # Connect to the 'imageDB' database
    fs = gridfs.GridFS(db)  # Create a GridFS instance
except Exception as e:
    print("Failed to connect to MongoDB:", e)
    fs = None  # Handle failed connection

