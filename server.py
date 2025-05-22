from flask import Flask, request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
import os
import json
from processor import process_input
from config import Config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import mimetypes
import google.generativeai as genai
import requests
from functools import wraps
import cv2
import numpy as np
from PIL import Image
import io
import time

app = Flask(__name__, static_folder='static')

# Set up CORS
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Configure from environment variables
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB default
app.config['ALLOWED_EXTENSIONS'] = os.environ.get('ALLOWED_EXTENSIONS', 'jpg,jpeg,png,gif,mp4').split(',')

# Configure port
port = int(os.environ.get('PORT', 5000))

# Initialize Google Generative AI with API key from environment
api_key = os.environ.get('GOOGLE_API_KEY', '')
if not api_key:
    print("Warning: GOOGLE_API_KEY not set. Using default configuration for local development")
    # For local development, use the API key from .env file
    load_dotenv()
    api_key = os.environ.get('GOOGLE_API_KEY', '')
    if not api_key:
        print("Warning: No API key found. Using default configuration")
        # Use default configuration for testing
        genai.configure(api_key='')
    else:
        genai.configure(api_key=api_key)
else:
    genai.configure(api_key=api_key)

# Set up rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

# Set up rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

# Rate limiting middleware
rate_limits = {}

def rate_limit():
    # Temporarily disable rate limiting for testing
    return True

# API Key validation
def validate_api_key():
    # Temporarily disable API key validation for testing
    return True

# Before request middleware
@app.before_request
def before_request():
    if not rate_limit():
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    if request.path.startswith('/api/') and not validate_api_key():
        return jsonify({'error': 'Invalid API key'}), 401

# Error handling
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def is_valid_image_url(url):
    try:
        response = requests.head(url, timeout=5)
        content_type = response.headers.get('content-type', '').lower()
        return 'image' in content_type
    except:
        return False



@app.route('/about')
def about():
    return send_from_directory('.', 'about.html')

@app.route('/docs')
def docs():
    return send_from_directory('.', 'docs.html')

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/gemini-analyzer')
def gemini_analyzer():
    return send_from_directory('.', 'index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_media():
    try:
        source_type = request.form.get('source_type')
        prompt = request.form.get('prompt', 'Describe what you see in this media.')
        
        if source_type == 'url':
            source = request.form.get('url')
            if not source:
                return jsonify({'error': 'URL is required'}), 400
            # Validate image URL
            if not is_valid_image_url(source):
                return jsonify({'error': 'Invalid image URL or image not accessible'}), 400
            result = process_input(source, prompt)
            
        elif source_type == 'file':
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400
                
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
                
            if not allowed_file(file.filename):
                return jsonify({'error': 'File type not allowed'}), 400
                
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        prompt = request.form.get('prompt')
        
        if not file or not prompt:
            return jsonify({'error': 'Missing file or prompt'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
            
        # Save the file temporarily
        temp_path = os.path.join('temp', file.filename)
        os.makedirs('temp', exist_ok=True)
        file.save(temp_path)
        
        try:
            # Process the file
            result = process_input(temp_path, prompt)
            
            # If it's an image, create a preview URL
            if file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                with open(temp_path, 'rb') as f:
                    img_data = f.read()
                return jsonify({
                    'result': result,
                    'preview_url': f'/api/preview/{file.filename}'
                })
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        return jsonify({'result': result})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preview/<path:filename>')
def preview(filename):
    """Handle media preview requests"""
    try:
        if filename.startswith('http'):
            # For external URLs, validate and return
            if is_valid_image_url(filename):
                return jsonify({'url': filename})
            return jsonify({'error': 'Invalid image URL'}), 400
        else:
            # For local files
            return send_from_directory('temp', filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=True) 