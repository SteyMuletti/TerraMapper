from flask import Flask, request, jsonify
import os
import subprocess
import shutil

app = Flask(__name__)

# Folder to temporarily store uploaded images
UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Folder to store processed maps
PROCESSED_MAP_FOLDER = 'processed_maps/'
if not os.path.exists(PROCESSED_MAP_FOLDER):
    os.makedirs(PROCESSED_MAP_FOLDER)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        file = request.files['image']
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filename)

        # Run ODM processing
        processed_map = process_image_with_odm(filename)
        
        # Return the processed map URL (assuming ODM saved it in the 'processed_maps' folder)
        map_url = f"/{processed_map}"
        return jsonify({"map_url": map_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

def process_image_with_odm(image_path):
    # This is where you trigger ODM to process the image
    # This command will vary based on your ODM installation and image processing script
    output_path = os.path.join(PROCESSED_MAP_FOLDER, os.path.basename(image_path) + "_processed.tif")
    
    cmd = ["python3", "run_odm.py", image_path, "--output", output_path]
    subprocess.run(cmd, check=True)
    
    return output_path

if __name__ == '__main__':
    app.run(debug=True)
