import sys

sys.path.append('c:/users/as/appdata/local/programs/python/python312/lib/site-packages')

from flask import Flask, render_template, request
import os
import face_recognition
import shutil

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
KNOWN_FACES_FOLDER = 'known_faces'

# Load known face encodings and filenames
known_face_encodings = []
known_face_filenames = []

for filename in os.listdir(KNOWN_FACES_FOLDER):
    image = face_recognition.load_image_file(os.path.join(KNOWN_FACES_FOLDER, filename))
    encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(encoding)
    known_face_filenames.append(os.path.splitext(filename)[0])  # Get filename without extension

def clear_uploads_folder():
    # Clear the uploads folder
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        clear_uploads_folder()

        if 'file' not in request.files:
            return render_template('index.html', error='No file part')

        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No selected file')

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Load uploaded image and encode faces
        unknown_image = face_recognition.load_image_file(file_path)
        unknown_encoding = face_recognition.face_encodings(unknown_image)

        if len(unknown_encoding) == 0:
            return render_template('index.html', error='No face detected in the uploaded image')

        unknown_encoding = unknown_encoding[0]

        # Compare face encodings with known faces
        matches = face_recognition.compare_faces(known_face_encodings, unknown_encoding)

        # Check if any match found
        for filename, match in zip(known_face_filenames, matches):
            if match:
                return render_template('result.html', result='Person Name: ' + filename)

        return render_template('result.html', result='Not Match')

    return render_template('index.html', error='')

if __name__ == '__main__':
    app.run(debug=True)
