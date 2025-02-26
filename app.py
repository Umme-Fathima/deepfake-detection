from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import os
import mysql.connector
from datetime import datetime
import uuid  # For generating unique filenames
from dotenv import load_dotenv  # For environment variables
import gdown
import tensorflow as tf  # Ensure TensorFlow is imported at the start

# Load environment variables (create a .env file with DB credentials)
load_dotenv()

# Define model file paths
model_path = "best_discriminator.h5"
tflite_model_path = "best_discriminator.tflite"

# Google Drive file ID (Replace with your actual file ID)
file_id = "1wJby5533dTnjCc0nmdS6E15R3O_nESrM"  
gdrive_url = f"https://drive.google.com/uc?id={file_id}"

# Download the model if it doesn't exist
if not os.path.exists(model_path):
    try:
        print("📥 Downloading model from Google Drive...")
        gdown.download(gdrive_url, model_path, quiet=False)
        print("✅ Model downloaded successfully!")
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        exit(1)  # Stop execution if model download fails

# Convert H5 model to TFLite if not already converted
if not os.path.exists(tflite_model_path):
    try:
        print("🔄 Converting model to TFLite format...")
        model = tf.keras.models.load_model(model_path)  # Load H5 model
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        tflite_model = converter.convert()

        with open(tflite_model_path, "wb") as f:
            f.write(tflite_model)

        print("✅ TFLite model saved successfully!")
    except Exception as e:
        print(f"❌ Error converting model to TFLite: {e}")
        exit(1)

import tensorflow.lite as tflite  # ✅ Import TensorFlow Lite

def load_tflite_model():
    """Load and return a TensorFlow Lite model interpreter."""
    global interpreter  # Optional: If using it in multiple places
    interpreter = tflite.Interpreter(model_path=tflite_model_path)  # ✅ Correct
    interpreter.allocate_tensors()  # ✅ Allocate tensors for inference
    print("✅ TFLite model loaded successfully!")
    return interpreter

# Load the TFLite model
interpreter = load_tflite_model()

print("TFLite model loaded successfully!")


# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Function to preprocess the image
def preprocess_image(image, target_size=(224, 224)):
    img = cv2.resize(image, target_size)  # Resize image to match model input size
    img = img / 255.0  # Normalize to [0,1] range
    img = np.array(img, dtype=np.float32)  # ✅ Explicitly set data type to float32
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    return img


# Function to analyze video and make predictions
# Function to analyze video and make predictions using TFLite model
def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    fake_count = 0
    real_count = 0
    total_frames = 0

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = np.array(preprocess_image(frame), dtype=np.float32)  # ✅ Explicit conversion


        # Run inference
        interpreter.set_tensor(input_details[0]['index'], image)
        interpreter.invoke()
        prediction = interpreter.get_tensor(output_details[0]['index'])

        total_frames += 1
        if prediction[0][0] > 0.7:
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
