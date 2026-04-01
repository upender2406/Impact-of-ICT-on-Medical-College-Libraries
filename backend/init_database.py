"""
Initialize and seed the database
Run this script to create the database and populate it with 5000 entries
"""
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db, get_db
from app.utils.database_seeder import seed_database

if __name__ == "__main__":
    print("=" * 80)
    print("DATABASE INITIALIZATION & SEEDING")
    print("=" * 80)
    
    try:
        # Initialize database tables
        print("\nStep 1: Creating database tables...")
        init_db()
        
        # Seed database with initial data
        print("\nStep 2: Seeding database with 5000 entries...")
        db = next(get_db())
        try:
            seed_database(db)
        finally:
            db.close()
        
        print("\n" + "=" * 80)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("=" * 80)
        print("\nDefault accounts created:")
        print("   Admin: admin@ictsurvey.com / admin123")
        print("   User:  user@ictsurvey.com / user123")
        print("\nDatabase location: backend/database/ict_survey.db")
        print("\nYou can now start the backend server!")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
