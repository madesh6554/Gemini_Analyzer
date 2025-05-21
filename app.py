from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import logging
from processor import process_input
from werkzeug.utils import secure_filename
import mimetypes
import requests
import cv2
import numpy as np
from PIL import Image
import io
from config import Config

# Configure logging
logging.basicConfig(
    filename='logs/gemini_analyzer.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
app.config['ALLOWED_EXTENSIONS'] = Config.ALLOWED_EXTENSIONS

# Ensure required directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'demo'), exist_ok=True)
os.makedirs('logs', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def is_valid_image_url(url):
    try:
        response = requests.head(url, timeout=5)
        content_type = response.headers.get('content-type', '').lower()
        return 'image' in content_type
    except Exception as e:
        logger.error(f"Error validating image URL: {str(e)}")
        return False

def validate_file_size(file):
    """Validate file size before processing"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > app.config['MAX_CONTENT_LENGTH']:
        raise ValueError(f"File size exceeds maximum limit of {app.config['MAX_CONTENT_LENGTH'] / (1024*1024)}MB")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        source_type = request.form.get('source_type')
        prompt = request.form.get('prompt', 'Describe what you see in this media.')
        
        if not source_type:
            return jsonify({'error': 'Source type is required'}), 400
            
        if source_type == 'url':
            source = request.form.get('url')
            if not source:
                return jsonify({'error': 'URL is required'}), 400
            if not is_valid_image_url(source):
                return jsonify({'error': 'Invalid image URL or image not accessible'}), 400
            result = process_input(source, prompt)
            
        elif source_type == 'youtube':
            source = request.form.get('youtube_url')
            if not source:
                return jsonify({'error': 'YouTube URL is required'}), 400
            result = process_input(source, prompt)
            
        elif source_type == 'file':
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400
                
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
                
            if not allowed_file(file.filename):
                return jsonify({'error': f'File type not allowed. Allowed types: {", ".join(app.config["ALLOWED_EXTENSIONS"])}'}), 400
            
            try:
                validate_file_size(file)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
                
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                result = process_input(filepath, prompt)
            finally:
                # Clean up the uploaded file
                if os.path.exists(filepath):
                    os.remove(filepath)
        else:
            return jsonify({'error': 'Invalid source type'}), 400
            
        return jsonify({'result': result})
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in analyze endpoint: {error_msg}")
        if "rate limit" in error_msg.lower():
            return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
        elif "invalid" in error_msg.lower():
            return jsonify({'error': 'Invalid file format or corrupted file'}), 400
        elif "size" in error_msg.lower():
            return jsonify({'error': 'File size too large'}), 400
        else:
            return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/preview/<path:url>')
def preview(url):
    """Handle media preview requests"""
    try:
        if url.startswith('http'):
            # For external URLs, validate and return
            if is_valid_image_url(url):
                return jsonify({'url': url})
            return jsonify({'error': 'Invalid image URL'}), 400
        else:
            # For local files
            return send_from_directory(app.config['UPLOAD_FOLDER'], url)
    except Exception as e:
        logger.error(f"Error in preview endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 404

@app.route('/sign')
def sign_language():
    return render_template('sign.html')

@app.route('/analyze_sign', methods=['POST'])
def analyze_sign():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        # Read the image file
        image_bytes = file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # TODO: Add sign language detection logic here
        # For now, return a placeholder response
        return jsonify({
            'result': 'Sign language detection will be implemented here',
            'confidence': 0.0
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_sign endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/static/demo/<path:filename>')
def serve_demo_video(filename):
    return send_from_directory(os.path.join(app.static_folder, 'demo'), filename)

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001) 