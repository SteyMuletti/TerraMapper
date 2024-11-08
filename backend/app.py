# app.py
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Set up a directory for uploads
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Basic route for testing
@app.route('/')
def index():
    return render_template('index.html')  # A simple HTML page for the frontend

# Flight Planning Endpoint (POST)
@app.route('/plan-flight', methods=['POST'])
def plan_flight():
    if request.is_json:
        data = request.get_json()
        # Here, you'd process the flight path data (waypoints, start/end locations)
        # For simplicity, we'll just return the received data as a JSON response
        return jsonify({"status": "success", "data": data}), 200
    return jsonify({"status": "error", "message": "Invalid data format."}), 400

# Image Upload Endpoint (POST)
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part."}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file."}), 400
    
    # Save the uploaded file
    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)
    
    # Process the image here (e.g., pass to OpenDroneMap or similar)
    # For now, we'll just return the file name for confirmation
    return jsonify({"status": "success", "filename": filename}), 200

# Process Map Endpoint (POST)
@app.route('/process-map', methods=['POST'])
def process_map():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part."}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file."}), 400
    
    # Placeholder for image processing (OpenDroneMap or other tools)
    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)
    
    # Here, you would process the map image (return processed data or map link)
    # For now, we return a success message with a placeholder result
    return jsonify({"status": "success", "message": "Map processed successfully.", "filename": filename}), 200

if __name__ == '__main__':
    # Make sure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.run(debug=True)

