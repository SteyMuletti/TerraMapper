from flask import Flask, render_template, request, jsonify
import os
import subprocess

app = Flask(__name__)

# Directory where uploaded images are stored
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed_maps'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/process_map', methods=['POST'])
def process_map():
    """Endpoint to handle image uploads for processing with OpenDroneMap"""
    if 'images' not in request.files:
        return jsonify({"message": "No images uploaded"}), 400

    # Save uploaded images
    images = request.files.getlist('images')
    image_paths = []
    for image in images:
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(image_path)
        image_paths.append(image_path)

    # Command to run OpenDroneMap
    odm_command = [
        'docker', 'run', '--rm', '-v', f"{os.path.abspath(UPLOAD_FOLDER)}:/datasets/code",
        '-v', f"{os.path.abspath(PROCESSED_FOLDER)}:/datasets/processed", 'opendronemap/odm', '--project-path', '/datasets'
    ]

    # Execute ODM command
    try:
        subprocess.run(odm_command, check=True)
        # Assuming ODM output saved to PROCESSED_FOLDER
        processed_map = os.path.join(PROCESSED_FOLDER, 'odm_orthophoto', 'odm_orthophoto.tif')
        if os.path.exists(processed_map):
            return jsonify({"message": "Map processed successfully", "map_url": "/processed_maps/odm_orthophoto.tif"})
        else:
            return jsonify({"message": "Map processing failed"}), 500
    except subprocess.CalledProcessError as e:
        print(f"ODM processing error: {e}")
        return jsonify({"message": "Error processing map with OpenDroneMap"}), 500

# Serve processed maps
@app.route('/processed_maps/<filename>')
def get_processed_map(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
