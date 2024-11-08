from flask import Flask, request, jsonify, send_from_directory
import os
import subprocess
import shutil
from werkzeug.utils import secure_filename
import logging
from datetime import datetime
import uuid
from typing import Tuple, Optional
import mimetypes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Config:
    """Configuration class for the application."""
    UPLOAD_FOLDER = 'uploads/'
    PROCESSED_MAP_FOLDER = 'processed_maps/'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ODM_SCRIPT_PATH = 'run_odm.py'  # Path to ODM processing script

class ImageProcessor:
    """Handles image processing operations using ODM."""
    
    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed."""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """Generate a unique filename while preserving the original extension."""
        ext = os.path.splitext(original_filename)[1]
        return f"{uuid.uuid4()}{ext}"

    @staticmethod
    def process_with_odm(image_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Process image with ODM and return status, output path, and error message.
        
        Returns:
            Tuple containing (success_status, output_path, error_message)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"processed_{timestamp}.tif"
            output_path = os.path.join(Config.PROCESSED_MAP_FOLDER, output_filename)

            cmd = [
                "python3",
                Config.ODM_SCRIPT_PATH,
                image_path,
                "--output",
                output_path
            ]
            
            # Run ODM process with timeout
            process = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if os.path.exists(output_path):
                return True, output_path, None
            else:
                return False, None, "Output file was not created"
                
        except subprocess.TimeoutExpired:
            return False, None, "Processing timeout exceeded"
        except subprocess.CalledProcessError as e:
            return False, None, f"ODM processing failed: {e.stderr}"
        except Exception as e:
            return False, None, f"Processing error: {str(e)}"

# Initialize Flask application
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Create necessary folders
for folder in [Config.UPLOAD_FOLDER, Config.PROCESSED_MAP_FOLDER]:
    os.makedirs(folder, exist_ok=True)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    """
    Handle image upload and processing.
    
    Expected format: multipart/form-data with 'image' field
    Returns: JSON with processed map URL or error message
    """
    try:
        # Check if image file is present in request
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        if not file or not file.filename:
            return jsonify({"error": "No selected file"}), 400

        # Validate file type
        if not ImageProcessor.allowed_file(file.filename):
            return jsonify({
                "error": f"Invalid file type. Allowed types: {', '.join(Config.ALLOWED_EXTENSIONS)}"
            }), 400

        # Generate secure filename and save file
        filename = ImageProcessor.generate_unique_filename(secure_filename(file.filename))
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Process image with ODM
        success, output_path, error_msg = ImageProcessor.process_with_odm(filepath)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        if not success:
            return jsonify({"error": error_msg}), 500

        # Generate public URL for the processed map
        map_url = f"/maps/{os.path.basename(output_path)}"
        return jsonify({
            "status": "success",
            "map_url": map_url
        }), 200

    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/maps/<filename>')
def serve_map(filename):
    """Serve processed maps."""
    return send_from_directory(Config.PROCESSED_MAP_FOLDER, filename)

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file size exceeded error."""
    return jsonify({
        "error": f"File too large. Maximum size is {Config.MAX_CONTENT_LENGTH // (1024 * 1024)}MB"
    }), 413

if __name__ == '__main__':
    app.run(debug=False)  # Set debug=False in production
