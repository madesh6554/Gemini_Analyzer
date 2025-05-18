# Gemini Analyzer

An AI-powered media analysis tool that uses Google's Gemini model to analyze images, videos, and YouTube content.

## Features

- Multi-format media analysis (images, videos, YouTube)
- Real-time AI analysis using Google's Gemini model
- Drag-and-drop file upload
- URL-based content analysis
- Customizable analysis prompts
- Responsive web interface
- About and Documentation sections
- Interactive Interface: Drag-and-drop functionality and real-time previews
- Detailed Analysis: Comprehensive analysis results with visual feedback

## Technical Stack

- **Frontend**: HTML5, TailwindCSS, JavaScript
- **Backend**: Flask (Python)
- **AI Integration**: Google Gemini AI
- **Video Processing**: OpenCV
- **Media Handling**: YouTube API integration

## Deployment Guide

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- FFmpeg (for video processing)
- Google Gemini API Key

### Local Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd gemini-analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp .env.example .env
```

5. Edit `.env` with your API key:
```
GEMINI_API_KEY=your_api_key_here
```

6. Run the development server:
```bash
python server.py
```

7. Open your browser and navigate to `http://localhost:5000`

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t gemini-analyzer .
```

2. Run the container:
```bash
docker run -d \
    -p 5000:5000 \
    -e GEMINI_API_KEY=your_api_key_here \
    gemini-analyzer
```

3. Access the application at `http://localhost:5000`

### Production Deployment

#### Using Docker Compose

1. Create a `docker-compose.yml`:
```yaml
version: '3'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    restart: always
```

2. Deploy with Docker Compose:
```bash
docker-compose up -d
```

#### Using Gunicorn (Production WSGI Server)

1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Run with Gunicorn:
```bash
GEMINI_API_KEY=your_api_key_here gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

### Environment Variables

- `GEMINI_API_KEY`: Google Gemini API key
- `PORT`: Application port (default: 5000)
- `DEBUG`: Debug mode (True/False)
- `MAX_REQUESTS_PER_HOUR`: Rate limiting
- `RATE_LIMIT_WINDOW`: Rate limiting window in seconds
- `MAX_CONTENT_LENGTH`: Maximum file size in bytes
- `ALLOWED_EXTENSIONS`: Allowed file extensions
- `CORS_ORIGINS`: Allowed CORS origins
- `LOG_LEVEL`: Logging level
- `LOG_FILE`: Log file path

### Security Features

- API key validation
- Rate limiting (1000 requests/hour per IP)
- CORS restrictions
- File type validation
- Size limits enforcement
- Input sanitization
- Error handling and logging

### Monitoring and Logging

The application logs are written to `gemini_analyzer.log` with configurable log level.

### Maintenance

#### Updating Dependencies

1. Update requirements.txt:
```bash
pip freeze > requirements.txt
```

2. Update Docker image:
```bash
docker build -t gemini-analyzer:latest .
```

#### Backup

1. Backup environment variables:
```bash
cp .env .env.backup
```

2. Backup logs:
```bash
cp gemini_analyzer.log gemini_analyzer.log.backup
```

## API Documentation

### Endpoints

- `GET /` - Home page
- `GET /about` - About page
- `GET /docs` - Documentation page
- `POST /api/analyze` - Analyze media content
- `POST /api/upload` - Upload files
- `GET /api/preview` - Preview media content

### Request Format

```json
{
    "source_type": "file/url",
    "file": "binary file data",
    "url": "media URL",
    "prompt": "analysis prompt"
}
```

### Response Format

```json
{
    "result": "analysis result",
    "preview_url": "optional preview URL",
    "error": "error message if any"
}
```

## Error Handling

- 400 Bad Request - Invalid input
- 401 Unauthorized - Invalid API key
- 403 Forbidden - Rate limit exceeded
- 404 Not Found - Resource not found
- 500 Internal Server Error - Server error

## Security

- File type validation
- Size limits enforcement
- Input sanitization
- API key management
- Rate limiting
- CORS restrictions

## License

MIT License

## Overview
Gemini Analyzer is an AI-powered media analysis tool that leverages Google's Gemini AI to analyze images, videos, and YouTube content. The application provides a modern, user-friendly interface for uploading and analyzing various types of media content.

## Features
- **Multi-format media analysis (images, videos, YouTube)**
- **Real-time AI analysis using Google's Gemini model**
- **Drag-and-drop file upload**
- **URL-based content analysis**
- **Customizable analysis prompts**
- **Responsive web interface**
- **About and Documentation sections**
- **Interactive Interface**: Drag-and-drop functionality and real-time previews
- **Detailed Analysis**: Comprehensive analysis results with visual feedback

## Technical Stack
- **Frontend**: HTML5, TailwindCSS, JavaScript
- **Backend**: FastAPI (Python)
- **AI Integration**: Google Gemini AI
- **Video Processing**: OpenCV
- **Media Handling**: YouTube API integration

## Setup

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

3. Open your browser and navigate to `http://localhost:8000`

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t gemini-analyzer .
```

2. Run the container:
```bash
docker run -d -p 8000:8000 gemini-analyzer
```

3. Access the application at `http://localhost:8000`

## Project Structure

```
gemini-analyzer/
├── about.html         # About page
├── docs.html          # Documentation page
├── index.html         # Main application page
├── main.py          # FastAPI server
├── processor.py       # Media processing logic
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
└── uploads/           # Directory for uploaded files
```

## API Documentation

### Endpoints

- `GET /` - Home page
- `GET /about` - About page
- `GET /docs` - Documentation page
- `POST /api/analyze` - Analyze media content
- `POST /api/upload` - Upload files
- `GET /api/preview` - Preview media content

### Request Format

```json
{
    "source_type": "file/url",
    "file": "binary file data",
    "url": "media URL",
    "prompt": "analysis prompt"
}
```

### Response Format

```json
{
    "result": "analysis result",
    "preview_url": "optional preview URL",
    "error": "error message if any"
}
```

## Error Handling

- 400 Bad Request - Invalid input
- 404 Not Found - Resource not found
- 500 Internal Server Error - Server error

## Security

- File type validation
- Size limits enforcement
- Input sanitization
- API key management

## Usage
1. Upload media through drag-and-drop or file selection
2. Or enter a YouTube URL for analysis
3. Add an analysis prompt (optional)
4. Click "Analyze Media" to process
5. View results in the preview section

## API Endpoints
- `/api/upload`: Upload and analyze media files
- `/api/analyze`: Analyze media from URLs

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details. 