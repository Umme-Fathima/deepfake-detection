from flask import Flask, render_template, request, jsonify, send_file
import cv2
import numpy as np
from tensorflow.keras.models import load_model # type: ignore
import os
import mysql.connector
from datetime import datetime

# Load the model
model = load_model('best_discriminator.h5')

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
    

    # Variables to track predictions
    fake_count = 0
    real_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Preprocess the frame
        image = preprocess_image(frame)

        # Make prediction with verbose=0 to suppress output
        prediction = model.predict(image, verbose=0)

        # Count predictions
        if prediction[0] > 0.7:
            fake_count += 1
        else:
            real_count += 1

    cap.release()

    # Final prediction based on majority voting
    if fake_count > real_count:
        return "The video is fake."
    else:
        return "The video is real."

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Route for video upload and prediction
@app.route('/predict', methods=['POST'])
def predict():
    # Check if a video file is part of the POST request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Save the uploaded file to the server
    
    video_path = os.path.join('uploads', file.filename)
    file.save(video_path)

    # Analyze the video and make prediction
    result = analyze_video(video_path)
    cap=cv2.VideoCapture(video_path)
    fake_count=0
    real_count=0
    total_frames=0

    while cap.isOpened():
        ret,frame=cap.read()
        if not ret:
            break

        image=preprocess_image(frame)

        prediction=model.predict(image,verbose=0)
        total_frames+=1

        if prediction[0]>0.7:
            fake_count+=1
        else:
            real_count+=1
    cap.release()


    fake_confidence=fake_count/total_frames
    real_confidence=real_count/total_frames

    if fake_confidence>real_confidence:
        prediction="Fake"
    else:
        prediction="Real"
    return jsonify({
        'prediction': f"The video is {prediction}.",
        'fakeConfidence': fake_confidence,
        'realConfidence': real_confidence
    })

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ummefathima@30",
        database="feedback_db"
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
    app.run(debug=True)

