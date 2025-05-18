from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from processor import process_input
import os
import google.generativeai as genai

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (for home.html, index.html)
app.mount("/static", StaticFiles(directory="."), name="static")

genai.configure(api_key="AIzaSyDIDjSb2WZRAXmS5p6SfaM5HD49NOsO_NE")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse("home.html")

@app.get("/gemini-analyzer", response_class=HTMLResponse)
def gemini_analyzer():
    return FileResponse("index.html")

@app.post("/api/analyze")
async def analyze_media(request: Request):
    data = await request.json()
    source = data.get("source")
    prompt = data.get("prompt")
    if not source or not prompt:
        return JSONResponse({"error": "Missing source or prompt"}, status_code=400)
    result = process_input(source, prompt)
    return {"result": result}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), prompt: str = Form(...)):
    if not file or not prompt:
        return JSONResponse({"error": "Missing file or prompt"}, status_code=400)
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    result = process_input(temp_path, prompt)
    os.remove(temp_path)
    return {"result": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
