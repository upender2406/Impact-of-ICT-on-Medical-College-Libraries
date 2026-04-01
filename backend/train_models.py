"""
Train ML models using data from the database.
Run this after importing data to generate the .pkl model file.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
from app.database import SessionLocal
from app.models.db_models import SurveyResponse
from app.services.training_service import training_service

def train():
    db = SessionLocal()
    try:
        responses = db.query(SurveyResponse).all()
        print(f"Loaded {len(responses)} survey responses from database")

        if len(responses) < 100:
            print(f"ERROR: Need at least 100 entries, got {len(responses)}")
            sys.exit(1)

        data = [r.to_dict() for r in responses]
        df = pd.DataFrame(data)
        print(f"DataFrame shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")

        result = training_service.train_models(df, force=True)
        print(f"\nResult: {result['status']}")
        if result['status'] == 'success':
            print(f"Training info: {result.get('training_info', {})}")
        else:
            print(f"Error: {result.get('message', 'unknown')}")
    finally:
        db.close()

if __name__ == "__main__":
    train()
