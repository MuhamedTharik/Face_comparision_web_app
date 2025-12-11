from flask import Flask, render_template, request, jsonify, redirect, url_for
import cv2
import numpy as np
import face_recognition
import base64
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Internship']
collection = db['person']


def capture_and_compare(base64_image):
    # Decode base64 image
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
                        "dept":document.get('dept')
                    }
        return jsonify({"error": "Face not detected"}), 400
    else:
        return jsonify({"error": "Face not detected"}), 400


# Dummy database for demonstration
users = {'E0222057': '8675','E0222016':'tharik2004'}

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

    # Check if any of the parameters are None (indicating no face detected)
    if None in (name, Uid, age, gender,dept):
        return render_template('details.html', message="No face detected")
    else:
        # Pass the extracted parameters to the template
        return render_template('details.html', name=name, Uid=Uid, age=age, gender=gender)

if __name__ == '__main__':
    app.run(debug=True)