from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from google import genai
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

# Geminiクライアントの設定
client = None
if "GEMINI_API_KEY" in os.environ:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

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

    # GeminiでGDPR分析を実行
    analysis = ""
    if text and not text.startswith("エラー") and client:
        try:
            # Gemini 1.5 Flash モデルを使用 (高速・安価・長文対応)
            prompt = f"あなたはGDPR（EU一般データ保護規則）の専門家です。以下のドキュメントのリスクを日本語で簡潔に分析してください:\n\n{text[:50000]}" # Geminiならもっと長くてもOK
            
            # 新しいライブラリでの非同期呼び出し
            response = await client.aio.models.generate_content(model='gemini-1.5-flash', contents=prompt)
            analysis = response.text
        except Exception as e:
            analysis = f"AI分析エラー: APIキーが設定されていないか、エラーが発生しました ({str(e)})"

    return {"filename": file.filename, "status": "success", "text": text, "analysis": analysis}
