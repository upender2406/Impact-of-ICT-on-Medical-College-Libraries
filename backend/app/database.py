"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment variable (Neon PostgreSQL)
# Fallback to SQLite for local development if not set
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./database/ict_survey.db"  # Fallback to SQLite"
)

# Remove SQLite-specific connection args if using PostgreSQL
if DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgresql+psycopg2://"):
    # PostgreSQL connection (Neon)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        echo=False  # Set to True for SQL query logging
    )
else:
    # SQLite fallback (for local development)
    from pathlib import Path
    DATABASE_DIR = Path(__file__).parent.parent / "database"
    DATABASE_DIR.mkdir(exist_ok=True)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=False
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at: {DATABASE_URL}")
