from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from bson import Binary
import gridfs

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['imageDB']  # Name your database
try:
    client = MongoClient('mongodb://localhost:27017/')
    # Try to get server information to confirm connection
    client.server_info()
    print("Connected to MongoDB successfully!")
    
    db = client['imageDB']
    fs = gridfs.GridFS(db)  # Create a GridFS instance

except Exception as e:
    print("Failed to connect to MongoDB:", e)
fs = gridfs.GridFS(db)  # Create a GridFS instance
try:
    # List files in GridFS to check if fs is working
    print("Files in GridFS:", list(db.fs.files.find()))
    print("GridFS connection is successful!")
except Exception as e:
    print("GridFS connection failed:", e)
# Route to render the HTML file
@app.route('/')
def index():
    return render_template('index.html')  # Ensure index.html is in the templates folder

# Route to handle the file upload
@app.route('/upload', methods=['POST'])
def upload_image():
    # Get the file from the form
    file = request.files['image']
    
    # Check if the file is valid
    if file and file.content_type.startswith('image/'):
        # Save the file to MongoDB GridFS
        file_id = fs.put(file, filename=file.filename, content_type=file.content_type)
        
        return jsonify({'message': 'Image uploaded successfully!', 'file_id': str(file_id)}), 200
    else:
        return jsonify({'error': 'Invalid file type. Please upload an image.'}), 400
    

from flask import send_file
import io

@app.route('/image/<file_id>', methods=['GET'])
def get_image(file_id):
    try:
        # Retrieve the image file from GridFS using the file_id
        file = fs.get(file_id)
        
        # Send the file content to the client as an image
        return send_file(io.BytesIO(file.read()), mimetype=file.content_type)
    except Exception as e:
        return jsonify({'error': 'Image not found or retrieval error: ' + str(e)}), 404
    
from flask import send_file
import io

@app.route('/latest-image', methods=['GET'])
def get_latest_image():
    try:
        # Find the most recent file in GridFS based on uploadDate
        latest_file = db.fs.files.find_one(sort=[("uploadDate", -1)])
        
        if not latest_file:
            return jsonify({'error': 'No images found in the database.'}), 404
        
        # Retrieve the file from GridFS using its file_id
        file_id = latest_file['_id']
        file = fs.get(file_id)
        
        # Send the file content as an image response
        return send_file(io.BytesIO(file.read()), mimetype=file.content_type)
    
    except Exception as e:
        return jsonify({'error': 'Error retrieving the latest image: ' + str(e)}), 500

# Route to display the latest image in an HTML template
@app.route('/view-latest-image')
def view_latest_image():
    return render_template('view_latest_image.html')


if __name__ == '__main__':
    app.run(debug=True)
