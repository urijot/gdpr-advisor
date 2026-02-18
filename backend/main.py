from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
import shutil
import os

app = FastAPI()

# フロントエンド (http://localhost:5173) からのアクセスを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開発中は "*" (すべて許可) でOK
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# アップロードされたファイルを保存するフォルダを作成
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"Hello": "GDPR App Backend is running!"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # PDFからテキストを抽出
    text = ""
    try:
        reader = PdfReader(save_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        text = f"エラー: テキストを抽出できませんでした ({str(e)})"

    return {"filename": file.filename, "status": "success", "text": text}
