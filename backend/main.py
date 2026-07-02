import logging
import os
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

from database import SessionLocal, GdprChunk, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allowed frontend origins. Defaults to local dev; in production set
# FRONTEND_ORIGIN to the deployed frontend URL (comma-separated for multiple).
_default_origins = "http://localhost:5173"
allowed_origins = [
    o.strip()
    for o in os.environ.get("FRONTEND_ORIGIN", _default_origins).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


@app.on_event("startup")
def startup():
    for attempt in range(10):
        try:
            init_db()
            logger.info("Database initialized successfully.")
            return
        except Exception as exc:
            logger.warning("DB not ready (attempt %d/10): %s", attempt + 1, exc)
            time.sleep(3)
    logger.error("Could not connect to the database after 10 attempts.")


class AdviceRequest(BaseModel):
    idea: str


@app.get("/")
def read_root():
    return {"message": "GDPR Advisor Backend is running!"}


@app.post("/advice")
async def get_advice(request: AdviceRequest):
    if not gemini_client:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set.")

    # 1. Embed the service idea
    embed_result = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=request.idea,
    )
    query_embedding = embed_result.embeddings[0].values

    # 2. Retrieve top-5 most relevant GDPR articles via cosine similarity
    db = SessionLocal()
    try:
        relevant = (
            db.query(GdprChunk)
            .order_by(GdprChunk.embedding.cosine_distance(query_embedding))
            .limit(5)
            .all()
        )
    finally:
        db.close()

    if not relevant:
        raise HTTPException(
            status_code=503,
            detail=(
                "GDPR data not found in the database. "
                "Please run: docker compose exec backend python ingest.py"
            ),
        )

    context = "\n\n---\n\n".join(
        f"{chunk.article}:\n{chunk.text}" for chunk in relevant
    )

    # 3. Generate GDPR compliance advice
    prompt = (
        "You are a GDPR compliance advisor. "
        "Based only on the GDPR articles provided below, analyze whether "
        "the described service idea raises any potential compliance issues. "
        "Be specific about which articles apply and why. "
        "Always remind the user that this is not legal advice.\n\n"
        f"RELEVANT GDPR ARTICLES:\n{context}\n\n"
        f"SERVICE IDEA:\n{request.idea}\n\n"
        "Format your response in Markdown using the following ## headings exactly:\n"
        "## Summary\n"
        "(1-2 sentence overview)\n\n"
        "## Potential GDPR Concerns\n"
        "(bullet points)\n\n"
        "## Relevant Articles\n"
        "(which articles apply and why)\n\n"
        "## Recommendations\n"
        "(actionable steps)\n\n"
        "## Disclaimer\n"
        "(not legal advice reminder)"
    )

    response = await gemini_client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return {
        "advice": response.text,
        "relevant_articles": [c.article for c in relevant],
    }
