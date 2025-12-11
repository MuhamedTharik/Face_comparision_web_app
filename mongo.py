from flask import Flask, render_template, request
from pymongo import MongoClient
import base64
import face_recognition
import numpy as np
import io

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['Internship']  
collection = db['person']  

def image_to_base64(image_data):
    return base64.b64encode(image_data).decode('utf-8')

def generate_face_encodings(image_data):
    image = face_recognition.load_image_file(io.BytesIO(image_data))  # Convert NumPy array to file-like object
    face_encodings = face_recognition.face_encodings(image)
    return face_encodings[0].tolist() if face_encodings else None

@app.route('/')
def index():
    return render_template('mongo.html')

@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        Uid = request.form['Uid']
        gender = request.form['gender']

        # Get the base64-encoded image data from the form
        img_data_base64 = request.form['photo'].split(",")[1]  # Remove the data:image/jpeg;base64, prefix

        # Decode the base64-encoded image data to bytes
        image_data_bytes = base64.b64decode(img_data_base64)

        # Convert the image data bytes to a NumPy array
        image_data = np.frombuffer(image_data_bytes, dtype=np.uint8)

        # Insert data into MongoDB
        result = collection.insert_one({
            'name': name,
            'age': age,
            'Uid': Uid,
            'gender': gender,
            'image_data': image_to_base64(image_data),
            'face_encodings': generate_face_encodings(image_data)
        })

        return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)