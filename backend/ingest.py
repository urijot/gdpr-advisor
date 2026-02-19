#!/usr/bin/env python3
"""
Ingestion script: reads all PDFs from the data/ directory,
splits them by article, generates embeddings, and stores them in pgvector.

Usage (run inside the backend container):
  docker compose exec backend python ingest.py

Place your PDF files in backend/data/ before running.
"""

import os
import re
import sys
import time
from pathlib import Path

from pypdf import PdfReader
from google import genai

from database import SessionLocal, GdprChunk, init_db

DATA_DIR = Path(__file__).parent / "data"


def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def split_by_article(full_text: str, source: str) -> list[dict]:
    # Normalize ligature/spacing artifacts from PDF extraction (e.g. "Ar ticle" -> "Article")
    full_text = re.sub(r"Ar\s+ticle", "Article", full_text)
    pattern = re.compile(r"(Article\s+\d+\b[^\n]*)", re.IGNORECASE)
    parts = pattern.split(full_text)
    chunks = []
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        match = re.search(r"Article\s+(\d+)", header, re.IGNORECASE)
        article_label = f"Article {match.group(1)}" if match else "Unknown"
        combined = f"{header}\n\n{body}"
        if len(combined.strip()) > 80:
            chunks.append({
                "article": article_label,
                "title": header[:250],
                "text": combined[:3000],
                "source": source,
            })
    return chunks


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("Error: GEMINI_API_KEY is not set.")

    if not DATA_DIR.exists() or not any(DATA_DIR.glob("*.pdf")):
        sys.exit(
            f"Error: No PDF files found in {DATA_DIR}.\n"
            "Place your PDF files there and re-run this script."
        )

    client = genai.Client(api_key=api_key)
    init_db()
    db = SessionLocal()

    try:
        pdf_files = sorted(DATA_DIR.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF file(s): {[f.name for f in pdf_files]}")

        total_stored = 0
        for pdf_path in pdf_files:
            source = pdf_path.stem
            already = db.query(GdprChunk).filter(GdprChunk.source == source).count()
            if already > 0:
                print(f"  [{pdf_path.name}] Already ingested ({already} chunks). Skipping.")
                continue

            print(f"  [{pdf_path.name}] Extracting text...")
            full_text = extract_text(pdf_path)
            chunks = split_by_article(full_text, source)
            print(f"  [{pdf_path.name}] Split into {len(chunks)} article chunks. Embedding...")

            for i, chunk in enumerate(chunks, 1):
                print(f"    [{i}/{len(chunks)}] {chunk['article']}")
                while True:
                    try:
                        result = client.models.embed_content(
                            model="gemini-embedding-001",
                            contents=chunk["text"],
                        )
                        break
                    except Exception as e:
                        msg = str(e)
                        if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                            import re as _re
                            wait_match = _re.search(r"retry in (\d+)", msg, _re.IGNORECASE)
                            wait_sec = int(wait_match.group(1)) + 5 if wait_match else 65
                            print(f"    Rate limit hit. Waiting {wait_sec}s...")
                            time.sleep(wait_sec)
                        else:
                            raise
                embedding = result.embeddings[0].values
                db.add(GdprChunk(
                    article=chunk["article"],
                    title=chunk["title"],
                    text=chunk["text"],
                    source=source,
                    embedding=embedding,
                ))
                if i % 10 == 0:
                    db.commit()
                time.sleep(0.7)

            db.commit()
            total_stored += len(chunks)
            print(f"  [{pdf_path.name}] Done. {len(chunks)} chunks stored.")

        print(f"\nIngestion complete! {total_stored} new chunks stored in total.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
