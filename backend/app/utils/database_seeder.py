"""
Database seeder to populate initial data (5000 survey responses)
"""
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from app.database import get_db, init_db
from app.models.db_models import (
    SurveyResponse, User, UserRole, AutomationSystem, RespondentType
)
from app.services.auth_service import get_password_hash
from datetime import datetime, timedelta
import random


def generate_realistic_survey_data(n_samples=1052):
    """Generate realistic survey data matching colab.py structure - EXACTLY 1052 records"""
    np.random.seed(42)
    
    colleges = [
        'Patna Medical College (PMCH)',
        'Darbhanga Medical College (DMCH)',
        'Anugrah Narayan Magadh Medical College (ANMMC)',
        'Nalanda Medical College (NMCH)',
        'Shri Krishna Medical College (SKMCH)',
        'Jawaharlal Nehru Medical College (JLNMCH)',
        'Indira Gandhi Institute of Medical Sciences (IGIMS)',
        'Vardhman Institute of Medical Sciences (VIMS)',
        'Government Medical College Bettiah (GMCH)'
    ]
    
    college_tier = {
        'Patna Medical College (PMCH)': 'high',
        'Indira Gandhi Institute of Medical Sciences (IGIMS)': 'high',
        'Nalanda Medical College (NMCH)': 'medium',
        'Darbhanga Medical College (DMCH)': 'medium',
        'Shri Krishna Medical College (SKMCH)': 'medium',
        'Jawaharlal Nehru Medical College (JLNMCH)': 'medium',
        'Anugrah Narayan Magadh Medical College (ANMMC)': 'low',
        'Vardhman Institute of Medical Sciences (VIMS)': 'low',
        'Government Medical College Bettiah (GMCH)': 'low'
    }
    
    data = []
    
    for i in range(n_samples):
        college = np.random.choice(colleges)
        tier = college_tier[college]
        
        # Base scores based on tier
        if tier == 'high':
            base_infra = np.random.uniform(3.5, 5.0)
            base_satisfaction = np.random.uniform(7, 10)
            base_barrier = np.random.uniform(1, 2.5)
        elif tier == 'medium':
            base_infra = np.random.uniform(2.5, 4.0)
            base_satisfaction = np.random.uniform(5, 8)
            base_barrier = np.random.uniform(2, 4)
        else:  # low
            base_infra = np.random.uniform(1.5, 3.5)
            base_satisfaction = np.random.uniform(3, 6)
            base_barrier = np.random.uniform(3.5, 5)
        
        # Add noise
        hardware_quality = np.clip(base_infra + np.random.normal(0, 0.3), 1, 5)
        software_availability = np.clip(base_infra + np.random.normal(0, 0.3), 1, 5)
        internet_speed = np.clip(base_infra + np.random.normal(0, 0.4), 1, 5)
        digital_collection = np.clip(base_infra + np.random.normal(0, 0.3), 1, 5)
        
        # Satisfaction correlated with infrastructure
        overall_satisfaction = np.clip(
            base_satisfaction + (base_infra - 3) * 2 + np.random.normal(0, 0.5), 
            1, 10
        )
        service_efficiency = np.clip(
            overall_satisfaction + np.random.normal(0, 0.8), 
            1, 10
        )
        staff_helpfulness = np.clip(
            overall_satisfaction + np.random.normal(0, 1.0), 
            1, 10
        )
        
        # Barriers inversely correlated with infrastructure
        financial_barrier = np.clip(6 - base_infra + np.random.normal(0, 0.5), 1, 5)
        technical_barrier = np.clip(6 - base_infra + np.random.normal(0, 0.5), 1, 5)
        training_barrier = np.clip(6 - base_infra + np.random.normal(0, 0.6), 1, 5)
        policy_barrier = np.clip(6 - base_infra + np.random.normal(0, 0.5), 1, 5)
        
        # Calculate derived scores
        infrastructure_score = (hardware_quality + software_availability + internet_speed + digital_collection) / 4
        barrier_score = (financial_barrier + technical_barrier + training_barrier + policy_barrier) / 4
        
        # Other fields
        respondent_type = np.random.choice(
            ['Student', 'Faculty', 'Researcher', 'Library_Staff'], 
            p=[0.6, 0.2, 0.1, 0.1]
        )
        
        automation_system = np.random.choice(
            ['None', 'KOHA', 'SOUL', 'Other'],
            p=[0.3, 0.35, 0.25, 0.1] if tier == 'high' else 
              [0.5, 0.25, 0.15, 0.1] if tier == 'medium' else 
              [0.7, 0.15, 0.10, 0.05]
        )
        
        row = {
            'college': college,
            'college_tier': tier,
            'respondent_type': respondent_type,
            'hardware_quality': round(hardware_quality, 2),
            'software_availability': round(software_availability, 2),
            'internet_speed': round(internet_speed, 2),
            'digital_collection': round(digital_collection, 2),
            'automation_system': automation_system,
            'infrastructure_score': round(infrastructure_score, 2),
            'overall_satisfaction': round(overall_satisfaction, 2),
            'service_efficiency': round(service_efficiency, 2),
            'staff_helpfulness': round(staff_helpfulness, 2),
            'financial_barrier': round(financial_barrier, 2),
            'technical_barrier': round(technical_barrier, 2),
            'training_barrier': round(training_barrier, 2),
            'policy_barrier': round(policy_barrier, 2),
            'barrier_score': round(barrier_score, 2),
            'weekly_visits': int(np.clip(base_infra * 3 + np.random.normal(0, 2), 1, 15)),
            'ict_training_received': base_infra > 3.5 or np.random.choice([True, False], p=[0.3, 0.7]),
            'awareness_level': int(np.clip(base_infra + np.random.normal(0, 0.5), 1, 5)),
            'remote_access_available': base_infra > 3.5 or np.random.choice([True, False], p=[0.3, 0.7]),
            'digital_resource_usage': np.random.choice(
                ['Never', 'Rarely', 'Sometimes', 'Often', 'Always'],
                p=[0.05, 0.15, 0.3, 0.35, 0.15] if tier == 'high' else
                  [0.1, 0.25, 0.35, 0.2, 0.1] if tier == 'medium' else
                  [0.2, 0.35, 0.3, 0.1, 0.05]
            ),
            'pandemic_adaptation': np.random.choice(
                ['Poor', 'Fair', 'Good', 'Excellent'],
                p=[0.1, 0.2, 0.4, 0.3] if tier == 'high' else
                  [0.2, 0.4, 0.3, 0.1] if tier == 'medium' else
                  [0.4, 0.4, 0.15, 0.05]
            )
        }
        
        data.append(row)
    
    return pd.DataFrame(data)


def seed_database(db: Session):
    """Seed database with initial data"""
    print("Seeding database...")
    
    # Check if data already exists
    existing_count = db.query(SurveyResponse).count()
    if existing_count > 0:
        print(f"Database already has {existing_count} entries. Skipping seed.")
        return
    
    # Create default admin user
    admin_email = "admin@ictsurvey.com"
    admin_user = db.query(User).filter(User.email == admin_email).first()
    if not admin_user:
        admin_user = User(
            email=admin_email,
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print("Created default admin user (admin@ictsurvey.com / admin123)")
    
    # Create default regular user
    user_email = "user@ictsurvey.com"
    regular_user = db.query(User).filter(User.email == user_email).first()
    if not regular_user:
        regular_user = User(
            email=user_email,
            username="user",
            hashed_password=get_password_hash("user123"),
            full_name="Test User",
            role=UserRole.USER,
            is_active=True
        )
        db.add(regular_user)
        db.commit()
        print("Created default user (user@ictsurvey.com / user123)")
    
    # Generate survey data
    print("Generating 1052 survey responses...")
    df = generate_realistic_survey_data(n_samples=1052)
    
    # Map respondent types
    respondent_type_map = {
        'Student': RespondentType.STUDENT,
        'Faculty': RespondentType.FACULTY,
        'Researcher': RespondentType.RESEARCHER,
        'Library_Staff': RespondentType.LIBRARY_STAFF
    }
    
    # Map automation systems
    automation_map = {
        'None': AutomationSystem.NONE,
        'KOHA': AutomationSystem.KOHA,
        'SOUL': AutomationSystem.SOUL,
        'Other': AutomationSystem.OTHER
    }
    
    # Insert survey responses in batches
    batch_size = 100
    total_rows = len(df)
    
    for i in range(0, total_rows, batch_size):
        batch = df.iloc[i:i+batch_size]
        responses = []
        
        for _, row in batch.iterrows():
            response = SurveyResponse(
                college=row['college'],
                college_tier=row['college_tier'],
                respondent_type=respondent_type_map.get(row['respondent_type'], RespondentType.STUDENT),
                hardware_quality=float(row['hardware_quality']),
                software_availability=float(row['software_availability']),
                internet_speed=float(row['internet_speed']),
                digital_collection=float(row['digital_collection']),
                automation_system=automation_map.get(row['automation_system'], AutomationSystem.NONE),
                infrastructure_score=float(row['infrastructure_score']),
                overall_satisfaction=float(row['overall_satisfaction']),
                service_efficiency=float(row['service_efficiency']),
                staff_helpfulness=float(row['staff_helpfulness']),
                financial_barrier=float(row['financial_barrier']),
                technical_barrier=float(row['technical_barrier']),
                training_barrier=float(row['training_barrier']),
                policy_barrier=float(row['policy_barrier']),
                barrier_score=float(row['barrier_score']),
                weekly_visits=int(row['weekly_visits']),
                ict_training_received=bool(row['ict_training_received']),
                awareness_level=int(row['awareness_level']),
                remote_access_available=bool(row['remote_access_available']),
                digital_resource_usage=row.get('digital_resource_usage'),
                pandemic_adaptation=row.get('pandemic_adaptation'),
            )
            responses.append(response)
        
        db.add_all(responses)
        db.commit()
        
        print(f"  Inserted batch {i//batch_size + 1}/{(total_rows-1)//batch_size + 1} ({min(i+batch_size, total_rows)}/{total_rows} rows)")
    
    print(f"Database seeded successfully with {total_rows} survey responses!")


if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Get database session
    db = next(get_db())
    
    try:
        seed_database(db)
    except Exception as e:
        print(f"Error seeding database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
