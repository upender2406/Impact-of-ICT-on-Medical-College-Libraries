
import sys
import random
import string
import secrets
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db, get_db
from app.services.auth_service import create_user
from app.models.schemas import UserCreate
from app.models.db_models import UserRole

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_random_user():
    db = next(get_db())
    try:
        username = f"user_{generate_random_string()}"
        email = f"{username}@example.com"
        password = secrets.token_urlsafe(10)
        full_name = f"Random User {generate_random_string(4)}"
        
        user_data = UserCreate(
            email=email,
            username=username,
            password=password,
            full_name=full_name,
            role="user"
        )
        
        create_user(db, user_data, role=UserRole.USER)
        
        print("\n" + "="*50)
        print("NEW RANDOM USER CREATED")
        print("="*50)
        print(f"Email:    {email}")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Name:     {full_name}")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"Error creating user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_random_user()
