from sqlalchemy import create_engine, Column, Integer, String, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://user:password@db:5432/gdprdb"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class GdprChunk(Base):
    __tablename__ = "gdpr_chunks"

    id = Column(Integer, primary_key=True, index=True)
    article = Column(String(50))
    title = Column(String(255))
    text = Column(Text)
    source = Column(String(255))
    embedding = Column(Vector(3072))


def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
