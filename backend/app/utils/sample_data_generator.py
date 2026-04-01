"""
Sample data generator for testing purposes.
Generates realistic survey response data.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any


def generate_sample_responses(count: int = 50) -> List[Dict[str, Any]]:
    """Generate sample survey responses."""
    
    colleges = [
        {'id': '1', 'name': 'Darbhanga Medical College'},
        {'id': '2', 'name': 'Indira Gandhi Institute of Medical Sciences'},
        {'id': '3', 'name': 'Patna Medical College and Hospital'},
        {'id': '4', 'name': 'Nalanda Medical College and Hospital'},
        {'id': '5', 'name': 'Jawaharlal Nehru Medical College'},
        {'id': '6', 'name': 'Vardhman Institute of Medical Sciences'},
        {'id': '7', 'name': 'Anugrah Narayan Magadh Medical College'},
        {'id': '8', 'name': 'Sri Krishna Medical College and Hospital'},
        {'id': '9', 'name': 'Government Medical College'},
    ]
    
    automation_systems = ['None', 'KOHA', 'SOUL', 'Other']
    respondent_types = ['librarian', 'user']
    positions = [
        'Librarian', 'Assistant Librarian', 'Library Staff',
        'Faculty Member', 'Student', 'Researcher'
    ]
    
    responses = []
    
    for i in range(count):
        college = random.choice(colleges)
        respondent_type = random.choice(respondent_types)
        
        # Generate infrastructure scores (biased towards lower scores for realism)
        hardware = random.choices([1, 2, 3, 4, 5], weights=[10, 20, 30, 25, 15])[0]
        software = random.choices([1, 2, 3, 4, 5], weights=[15, 25, 30, 20, 10])[0]
        internet = random.choices([1, 2, 3, 4, 5], weights=[20, 30, 25, 15, 10])[0]
        digital = random.choices([1, 2, 3, 4, 5], weights=[25, 30, 25, 15, 5])[0]
        
        # Service quality (correlated with infrastructure)
        avg_infra = (hardware + software + internet + digital) / 4
        base_satisfaction = max(1, min(10, int(avg_infra * 2 + random.randint(-2, 2))))
        
        response = {
            'college_id': college['id'],
            'college_name': college['name'],
            'respondent': {
                'type': respondent_type,
                'name': f'Respondent {i+1}',
                'position': random.choice(positions),
            },
            'infrastructure': {
                'hardware_quality': hardware,
                'software_availability': software,
                'internet_speed': internet,
                'digital_collection': digital,
                'automation_system': random.choice(automation_systems),
            },
            'service_quality': {
                'overall_satisfaction': base_satisfaction,
                'service_efficiency': max(1, min(10, base_satisfaction + random.randint(-1, 1))),
                'staff_helpfulness': max(1, min(10, base_satisfaction + random.randint(-1, 2))),
            },
            'barriers': {
                'financial_barrier': random.choices([1, 2, 3, 4, 5], weights=[5, 15, 30, 30, 20])[0],
                'technical_barrier': random.choices([1, 2, 3, 4, 5], weights=[10, 20, 30, 25, 15])[0],
                'training_barrier': random.choices([1, 2, 3, 4, 5], weights=[5, 15, 25, 35, 20])[0],
                'policy_barrier': random.choices([1, 2, 3, 4, 5], weights=[10, 20, 30, 25, 15])[0],
            },
            'additional_info': {
                'weekly_visits': random.randint(0, 50),
                'ict_training_received': random.choice([True, False]),
                'remote_access_available': random.choice([True, False]),
                'comments': f'Sample comment {i+1}' if random.random() > 0.7 else '',
            },
            'submitted_at': (datetime.now() - timedelta(days=random.randint(0, 90))).isoformat(),
        }
        
        responses.append(response)
    
    return responses


if __name__ == '__main__':
    # Generate and print sample data
    samples = generate_sample_responses(20)
    print(f"Generated {len(samples)} sample responses")
    print("\nFirst response:")
    import json
    print(json.dumps(samples[0], indent=2))
