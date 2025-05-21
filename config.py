import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Configuration
    API_KEY = os.getenv('GEMINI_API_KEY')
    API_CREDENTIALS = {
        'api_key': API_KEY,
        'api_base_url': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
    }
    API_URL = os.getenv('GEMINI_API_URL', 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent')
    
    # Security Settings
    MAX_REQUESTS_PER_HOUR = 1000
    RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
    
    # File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'webm', 'ogg'}
    UPLOAD_FOLDER = 'uploads'
    
    # CORS Settings
    CORS_ORIGINS = ['http://localhost:5000', 'https://gemini-analyzer.onrender.com']
    
    # Error Handling Settings
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    # Logging Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'gemini_analyzer.log'
