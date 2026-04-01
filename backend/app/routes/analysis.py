from fastapi import APIRouter
from app.services.data_service import data_service
import numpy as np

router = APIRouter()


@router.get("/infrastructure")
async def get_infrastructure_analysis():
    """Get infrastructure analysis."""
    responses = data_service.get_all_responses()
    
    if not responses:
        return {'data': [], 'summary': {}}
    
    # Group by college
    college_data = {}
    for r in responses:
        college_id = r.get('college_id')
        if college_id not in college_data:
            college_data[college_id] = []
        
        infra = r.get('infrastructure', {})
        score = (
            infra.get('hardware_quality', 0) +
            infra.get('software_availability', 0) +
            infra.get('internet_speed', 0) +
            infra.get('digital_collection', 0)
        ) / 4
        college_data[college_id].append(score)
    
    # Calculate averages
    analysis = []
    for college_id, scores in college_data.items():
        analysis.append({
            'college_id': college_id,
            'average_score': float(np.mean(scores)),
            'count': len(scores),
        })
    
    return {'data': analysis, 'summary': {'total_colleges': len(analysis)}}


@router.get("/satisfaction")
async def get_satisfaction_analysis():
    """Get satisfaction analysis."""
    responses = data_service.get_all_responses()
    
    if not responses:
        return {'data': [], 'summary': {}}
    
    satisfaction_scores = [
        r.get('service_quality', {}).get('overall_satisfaction', 0)
        for r in responses
    ]
    
    return {
        'data': satisfaction_scores,
        'summary': {
            'mean': float(np.mean(satisfaction_scores)),
            'median': float(np.median(satisfaction_scores)),
            'std': float(np.std(satisfaction_scores)),
        }
    }


@router.get("/barriers")
async def get_barrier_analysis():
    """Get barrier analysis."""
    responses = data_service.get_all_responses()
    
    if not responses:
        return {'data': [], 'summary': {}}
    
    barriers = {
        'financial': [],
        'technical': [],
        'training': [],
        'policy': [],
    }
    
    for r in responses:
        b = r.get('barriers', {})
        barriers['financial'].append(b.get('financial_barrier', 0))
        barriers['technical'].append(b.get('technical_barrier', 0))
        barriers['training'].append(b.get('training_barrier', 0))
        barriers['policy'].append(b.get('policy_barrier', 0))
    
    summary = {}
    for key, values in barriers.items():
        summary[key] = {
            'mean': float(np.mean(values)),
            'max': float(np.max(values)),
            'critical_count': sum(1 for v in values if v >= 4),
        }
    
    return {'data': barriers, 'summary': summary}


@router.get("/correlation")
async def get_correlation_matrix():
    """Get correlation matrix."""
    responses = data_service.get_all_responses()
    
    if not responses:
        # Return identity matrix if no data
        return [[1.0] * 10 for _ in range(10)]
    
    # Extract features
    features = []
    for r in responses:
        infra = r.get('infrastructure', {})
        service = r.get('service_quality', {})
        barriers = r.get('barriers', {})
        
        features.append([
            infra.get('hardware_quality', 0),
            infra.get('software_availability', 0),
            infra.get('internet_speed', 0),
            infra.get('digital_collection', 0),
            service.get('overall_satisfaction', 0),
            service.get('service_efficiency', 0),
            barriers.get('financial_barrier', 0),
            barriers.get('technical_barrier', 0),
            barriers.get('training_barrier', 0),
            barriers.get('policy_barrier', 0),
        ])
    
    # Calculate correlation matrix
    if len(features) > 1:
        matrix = np.corrcoef(np.array(features).T)
        return matrix.tolist()
    else:
        return [[1.0] * 10 for _ in range(10)]


@router.get("/hypothesis-tests")
async def get_hypothesis_tests():
    """Get hypothesis test results."""
    # Placeholder for hypothesis testing
    return {
        'tests': [
            {
                'name': 'Infrastructure vs Satisfaction',
                'p_value': 0.05,
                'significant': True,
                'conclusion': 'There is a significant positive correlation',
            }
        ]
    }
