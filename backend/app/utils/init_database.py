"""
Initialize database on startup
"""
from app.database import init_db, get_db
from app.utils.database_seeder import seed_database


def initialize_database():
    """Initialize and seed database if needed"""
    try:
        # Initialize database tables
        init_db()
        
        # Seed database with initial data
        db = next(get_db())
        try:
            seed_database(db)
        finally:
            db.close()
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
