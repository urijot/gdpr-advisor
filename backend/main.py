from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from google import genai
import shutil
import os

app = FastAPI()

# Allow requests from the frontend (http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini client from environment variable GEMINI_API_KEY
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Create directory for uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "GDPR App Backend is running!"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text from PDF
    text = ""
    try:
        reader = PdfReader(save_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        text = f"Error: could not extract text ({str(e)})"

    # Run GDPR analysis with Gemini
    analysis = ""
    if not gemini_client:
        analysis = "Error: GEMINI_API_KEY is not set. Check the environment variable."
    elif text and not text.startswith("Error:"):
        try:
            prompt = (
                "You are a GDPR (General Data Protection Regulation) expert. "
                "Analyze the following document and identify potential GDPR risks concisely in English:\n\n"
                + text[:50000]
            )
            response = await gemini_client.aio.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
            )
            analysis = response.text
        except Exception as e:
            analysis = f"AI analysis error: {str(e)}"

    return {
        "filename": file.filename,
        "status": "success",
        "text": text,
        "analysis": analysis,
    }
