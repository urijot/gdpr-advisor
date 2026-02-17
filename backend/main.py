from fastapi import FastAPI, File, UploadFile
import shutil
import os

app = FastAPI()

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
    return {"filename": file.filename, "status": "success", "path": save_path}
