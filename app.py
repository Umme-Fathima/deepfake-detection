from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from tensorflow.keras.models import load_model # type: ignore
import os
import mysql.connector
from datetime import datetime
import uuid  # For generating unique filenames
from dotenv import load_dotenv  # For environment variables
import gdown


# Load environment variables (create a .env file with DB credentials)
load_dotenv()

import gdown

# Define model file path
model_path = "best_discriminator.h5"

# Google Drive file ID (Replace with your actual file ID)
file_id = "1wJby5533dTnjCc0nmdS6E15R3O_nESrM"  
gdrive_url = f"https://drive.google.com/uc?id={file_id}"

# Download the model if it doesn't exist
if not os.path.exists(model_path):
    print("Downloading model from Google Drive...")
    gdown.download(gdrive_url, model_path, quiet=False)

# Load the model after downloading
model = load_model(model_path)
print("Model loaded successfully!")


# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Function to preprocess the image
def preprocess_image(image, target_size=(224, 224)):
    img = cv2.resize(image, target_size)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    return img

# Function to analyze video and make predictions
def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    fake_count = 0
    real_count = 0
    total_frames = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = preprocess_image(frame)
        prediction = model.predict(image, verbose=0)

        total_frames += 1
        if prediction[0][0] > 0.7:  # Ensure correct indexing
            fake_count += 1
        else:
            real_count += 1

    cap.release()

    fake_confidence = fake_count / total_frames if total_frames > 0 else 0
    real_confidence = real_count / total_frames if total_frames > 0 else 0
    result = "Fake" if fake_confidence > real_confidence else "Real"

    return {
        'prediction': f"The video is {result}.",
        'fakeConfidence': fake_confidence,
        'realConfidence': real_confidence
    }

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Route for video upload and prediction
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Generate a unique filename to prevent overwriting
    unique_filename = str(uuid.uuid4()) + "_" + file.filename
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(video_path)

    # Analyze the video and return prediction
    result = analyze_video(video_path)
    return jsonify(result)

# Database connection
# Load environment variables
load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Route to handle feedback submission
@app.route('/feedback', methods=['POST'])
def save_feedback():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    feedback = data.get("feedback")

    if not name or not email or not feedback:
        return jsonify({"success": False, "message": "All fields are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO feedback (name, email, message, timestamp) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (name, email, feedback, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True, "message": "Feedback submitted successfully!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Get PORT from environment
    app.run(host="0.0.0.0", port=port)
