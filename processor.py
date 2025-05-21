import yt_dlp
import requests
import tempfile
import mimetypes
import os
import time
from urllib.parse import urlparse
from config import Config
import google.generativeai as genai

def analyze_media(file_path: str, prompt: str) -> str:
    """Core analysis function with improved MIME detection"""
    try:
        # Get MIME type with multiple fallbacks
        mime_type = (
            mimetypes.guess_type(file_path)[0] or 
            'image/jpeg' if file_path.lower().endswith(('.jpg', '.jpeg')) else
            'image/png' if file_path.lower().endswith('.png') else
            'video/mp4'
        )
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > Config.MAX_CONTENT_LENGTH:
            raise Exception("File too large. Maximum size is 16MB")
            
        with open(file_path, 'rb') as f:
            media_data = f.read()

        # Using the latest Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare the media content
        media_part = {
            "mime_type": mime_type,
            "data": media_data
        }
        
        # Prepare the text prompt
        text_part = {
            "text": prompt
        }
        
        # Generate content
        response = model.generate_content(
            contents=[media_part, text_part],
            generation_config={
                "temperature": 0.4,
                "top_p": 0.8,
                "top_k": 32,
                "max_output_tokens": 2048,
            }
        )
        
        if not response.text:
            raise Exception("No response generated from the model")
            
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "429" in error_msg:
            raise Exception("Rate limit exceeded. Please wait before trying again.")
        elif "invalid" in error_msg.lower():
            raise Exception("Invalid file format or corrupted file")
        elif "size" in error_msg.lower():
            raise Exception("File size too large. Maximum size is 16MB")
        else:
            raise Exception(f"Analysis Error: {error_msg}")

def process_input(source: str, prompt: str, max_retries=3) -> str:
    """Universal processor for all input types including YouTube"""
    for attempt in range(max_retries):
        try:
            if is_youtube_url(source):
                return process_youtube(source, prompt)
            elif is_direct_url(source):
                return process_direct_url(source, prompt)
            else:
                return process_local_file(source, prompt)
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 30  # Increasing wait time between retries
                    print(f"Rate limit hit. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
            return f"Error: {str(e)}"
    return "Error: Maximum retries exceeded"

# Helper functions
def is_youtube_url(url: str) -> bool:
    """Check if URL is from YouTube"""
    return any(domain in url for domain in ['youtube.com', 'youtu.be'])

def is_direct_url(url: str) -> bool:
    """Check if URL is a direct media link"""
    return urlparse(url).scheme in ('http', 'https')

def process_youtube(url: str, prompt: str) -> str:
    """Handle YouTube URLs with yt-dlp"""
    temp_path = None
    temp_dir = tempfile.mkdtemp()
    ydl_opts = {
        'quiet': True,
        'noplaylist': True,
        'no_warnings': True,
        'extract_flat': False,
        'merge_output_format': 'mp4'
    }

    try:
        # Convert shorts URL to regular YouTube URL if needed
        if '/shorts/' in url:
            video_id = url.split('/shorts/')[1].split('?')[0]
            url = f'https://www.youtube.com/watch?v={video_id}'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            temp_path = ydl.prepare_filename(info)
            
            if not os.path.exists(temp_path):
                raise Exception("Failed to download video")
                
            return analyze_media(temp_path, prompt)
    except Exception as e:
        if "ffmpeg" in str(e).lower():
            raise Exception("FFmpeg is required for video processing. Please install FFmpeg on your system.")
        raise Exception(f"YouTube Error: {str(e)}")
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        if os.path.exists(temp_dir):
            try:
                os.rmdir(temp_dir)
            except:
                pass

def process_direct_url(url: str, prompt: str) -> str:
    """Handle direct media URLs with proper image support"""
    temp_path = None
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        # Get MIME type and size from headers first
        response = requests.head(url, allow_redirects=True, headers=headers)
        content_type = response.headers.get('Content-Type', '').split(';')[0].strip()
        content_length = int(response.headers.get('Content-Length', 0))
        
        # Check file size
        if content_length > Config.MAX_CONTENT_LENGTH:
            return "File too large. Maximum size is 16MB"
            
        # Create temp file with proper extension
        ext = mimetypes.guess_extension(content_type) or '.tmp'
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as f:
            # Download content
            response = requests.get(url, stream=True, timeout=30, headers=headers)
            response.raise_for_status()
            
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
            temp_path = f.name

        return analyze_media(temp_path, prompt)
    except Exception as e:
        return f"URL Error: {str(e)}"
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
    """Handle local file uploads"""
    if not os.path.exists(file_path):
        return "Error: File not found"
    
    return analyze_media(file_path, prompt)

# Test with an image
if __name__ == "__main__":
    print("Testing with a sample image...")
    result = process_input(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png",
        "Describe what you see in this image."
    )
    print("\nResult:", result)