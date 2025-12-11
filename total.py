from flask import Flask, render_template, request, jsonify, redirect, url_for
import cv2
import numpy as np
import face_recognition
import base64
from pymongo import MongoClient
import io

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Internship']
collection = db['person']

# Function to convert image data to base64
def image_to_base64(image_data):
    return base64.b64encode(image_data).decode('utf-8')

# Function to generate face encodings
def generate_face_encodings(image_data):
    image = face_recognition.load_image_file(io.BytesIO(image_data))
    face_encodings = face_recognition.face_encodings(image)
    return face_encodings[0].tolist() if face_encodings else None

# Dummy database for demonstration
users = {'E0222057': '8675','E0222016':'3721'}

# Capture and compare function
def capture_and_compare(base64_image):
    image_data = base64.b64decode(base64_image.split(',')[1])
    nparr = np.frombuffer(image_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(frame_rgb)

    if face_locations:
        face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)
        for document in collection.find():
            database_face_encoding = document.get('face_encodings')
            if database_face_encoding is not None:
                matches = face_recognition.compare_faces([database_face_encoding], face_encodings[0], tolerance=0.5)
                if any(matches):
                    return {
                        "name": document.get('name'),
                        "Uid": document.get('Uid'),
                        "age": document.get('age'),
                        "gender": document.get('gender'),
                        "dept" : document.get('deptm')
                    }
        return jsonify({"error": "Face not detected"}), 400
    else:
        return jsonify({"error": "Face not detected"}), 400

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check if username and password match
    if username in users and users[username] == password:
        # If match, redirect to index page (where face recognition system resides)
        return redirect(url_for('index'))
    else:
        # If not match, redirect back to login page
        return redirect(url_for('login'))

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/capture_photo', methods=['POST'])
def capture_photo():
    base64_image = request.json.get('image')
    if base64_image:
        result = capture_and_compare(base64_image)
        return result
    else:
        return jsonify({"error": "No image data received"}), 400

@app.route('/details')
def details():
    # Extract query parameters from the URL
    name = request.args.get('name')
    Uid = request.args.get('Uid')
    age = request.args.get('age')
    gender = request.args.get('gender')
    dept = request.args.get('deptm')

    # Check if any of the parameters are None (indicating no face detected)
    if None in (name, Uid, age, gender):
        return render_template('details.html', message="No face detected")
    else:
        # Pass the extracted parameters to the template
        return render_template('details.html', name=name, Uid=Uid, age=age, gender=gender,dept=dept)

@app.route('/register')
def mongo():
    # Render mongo.html template
    return render_template('mongo.html')


client = MongoClient('mongodb://localhost:27017/')
db = client['Internship']  # Your database name
collection = db['person']  # Your collection name

def image_to_base64(image_data):
    return base64.b64encode(image_data).decode('utf-8')

def generate_face_encodings(image_data):
    image = face_recognition.load_image_file(io.BytesIO(image_data))  # Convert NumPy array to file-like object
    face_encodings = face_recognition.face_encodings(image)
    return face_encodings[0].tolist() if face_encodings else None

@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        Uid = request.form['Uid']
        gender = request.form['gender']
        dept = request.form['deptm']

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
            'dept' : dept,
            'image_data': image_to_base64(image_data),
            'face_encodings': generate_face_encodings(image_data)
        })

        return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)