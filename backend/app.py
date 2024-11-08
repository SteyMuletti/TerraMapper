from flask import Flask, request, jsonify, send_from_directory
import os
import subprocess

app = Flask(__name__)

# Directories for uploaded images and processed maps
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed_maps'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/api/start_flight', methods=['POST'])
def start_flight():
    """Endpoint to start a flight with specified waypoints, speeds, and rotations."""
    data = request.get_json()
    waypoints = data.get('waypoints', [])
    speeds = data.get('speeds', [])
    rotations = data.get('rotations', [])

    if not waypoints:
        return jsonify({"message": "No waypoints provided"}), 400

    # Placeholder logic to initiate the flight; replace with SDK-specific code
    try:
        print("Starting flight with waypoints:", waypoints)
        print("Speeds:", speeds, "Rotations:", rotations)
        # Flight SDK logic would go here
        return jsonify({"message": "Flight started successfully"})
    except Exception as e:
        print("Flight start error:", e)
        return jsonify({"message": "Failed to start flight"}), 500

@app.route('/process_map', methods=['POST'])
def process_map():
    """Endpoint to handle image uploads for processing with OpenDroneMap."""
    if 'images' not in request.files:
        return jsonify({"message": "No images uploaded"}), 400

    # Save uploaded images
    images = request.files.getlist('images')
    image_paths = []
    for image in images:
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(image_path)
        image_paths.append(image_path)

    # Command to run OpenDroneMap (ODM) for processing
    odm_command = [
        'docker', 'run', '--rm',
        '-v', f"{os.path.abspath(UPLOAD_FOLDER)}:/datasets/code",
        '-v', f"{os.path.abspath(PROCESSED_FOLDER)}:/datasets/processed",
        'opendronemap/odm', '--project-path', '/datasets'
    ]

    # Execute the ODM command and process the images
    try:
        subprocess.run(odm_command, check=True)
        processed_map = os.path.join(PROCESSED_FOLDER, 'odm_orthophoto', 'odm_orthophoto.tif')
        if os.path.exists(processed_map):
            return jsonify({"message": "Map processed successfully", "map_url": "/processed_maps/odm_orthophoto.tif"})
        else:
            return jsonify({"message": "Map processing failed"}), 500
    except subprocess.CalledProcessError as e:
        print("ODM processing error:", e)
        return jsonify({"message": "Error processing map with OpenDroneMap"}), 500

# Serve processed maps
@app.route('/processed_maps/<filename>')
def get_processed_map(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
