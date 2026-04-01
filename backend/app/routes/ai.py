"""
AI/ML prediction routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from app.services.ml_service import ml_service
from app.services.auth_service import get_current_active_user
from app.models.db_models import User
from pydantic import BaseModel

router = APIRouter()


class PredictionRequest(BaseModel):
    infrastructure_score: float
    barrier_score: float
    college_id: str
    automation_system: str
    awareness_level: int
    weekly_visits: int = 5
    ict_training_received: bool = False
    remote_access_available: bool = False
    hardware_quality: float = None
    internet_speed: float = None
    digital_collection: float = None


class ScenarioRequest(BaseModel):
    current: PredictionRequest
    proposed: PredictionRequest


@router.post("/predict/satisfaction")
async def predict_satisfaction(
    request: PredictionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Predict satisfaction level using AI model."""
    try:
        # Convert request to features dict
        features = {
            'infrastructure_score': request.infrastructure_score,
            'barrier_score': request.barrier_score,
            'college_id': request.college_id,
            'automation_system': request.automation_system,
            'awareness_level': request.awareness_level,
            'weekly_visits': request.weekly_visits,
            'ict_training_received': request.ict_training_received,
            'remote_access_available': request.remote_access_available,
        }
        
        # Add individual infrastructure components if provided
        if request.hardware_quality is not None:
            features['hardware_quality'] = request.hardware_quality
        if request.internet_speed is not None:
            features['internet_speed'] = request.internet_speed
        if request.digital_collection is not None:
            features['digital_collection'] = request.digital_collection
        
        prediction = ml_service.predict_satisfaction(features)
        return {
            'status': 'success',
            'prediction': prediction
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/efficiency")
async def predict_efficiency(
    request: PredictionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Predict service efficiency using AI model."""
    try:
        # Convert request to features dict
        features = {
            'infrastructure_score': request.infrastructure_score,
            'barrier_score': request.barrier_score,
            'college_id': request.college_id,
            'automation_system': request.automation_system,
            'awareness_level': request.awareness_level,
            'weekly_visits': request.weekly_visits,
            'ict_training_received': request.ict_training_received,
            'remote_access_available': request.remote_access_available,
        }
        
        # Add individual infrastructure components if provided
        if request.hardware_quality is not None:
            features['hardware_quality'] = request.hardware_quality
        if request.internet_speed is not None:
            features['internet_speed'] = request.internet_speed
        if request.digital_collection is not None:
            features['digital_collection'] = request.digital_collection
        
        prediction = ml_service.predict_efficiency(features)
        return {
            'status': 'success',
            'prediction': prediction
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate/scenario")
async def simulate_scenario(
    request: ScenarioRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Simulate scenario comparison using AI models."""
    try:
        # Convert current state to features dict
        current_features = {
            'infrastructure_score': request.current.infrastructure_score,
            'barrier_score': request.current.barrier_score,
            'college_id': request.current.college_id,
            'automation_system': request.current.automation_system,
            'awareness_level': request.current.awareness_level,
            'weekly_visits': request.current.weekly_visits,
            'ict_training_received': request.current.ict_training_received,
            'remote_access_available': request.current.remote_access_available,
        }
        
        # Convert proposed state to features dict
        proposed_features = {
            'infrastructure_score': request.proposed.infrastructure_score,
            'barrier_score': request.proposed.barrier_score,
            'college_id': request.proposed.college_id,
            'automation_system': request.proposed.automation_system,
            'awareness_level': request.proposed.awareness_level,
            'weekly_visits': request.proposed.weekly_visits,
            'ict_training_received': request.proposed.ict_training_received,
            'remote_access_available': request.proposed.remote_access_available,
        }
        
        simulation = ml_service.simulate_scenario(current_features, proposed_features)
        return {
            'status': 'success',
            'simulation': simulation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/{college_id}")
async def get_recommendations(
    college_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get AI-powered recommendations for a college."""
    try:
        # Get college data (simplified - in real app would fetch from database)
        college_data = {
            'college_id': college_id,
            'infrastructure_score': 3.0,  # Would be fetched from database
            'barrier_score': 3.0,
            'automation_system': 'None',
            'awareness_level': 5,
            'ict_training_received': False,
            'remote_access_available': False,
        }
        
        recommendations = ml_service.get_recommendations(college_data)
        return {
            'status': 'success',
            'recommendations': recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clusters")
async def get_college_clusters(
    current_user: User = Depends(get_current_active_user)
):
    """Get college clustering analysis."""
    try:
        clusters = ml_service.get_college_clusters()
        return {
            'status': 'success',
            'clusters': clusters
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/status")
async def get_model_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get AI model status and information."""
    try:
        status = {
            'models_loaded': ml_service.models is not None,
            'satisfaction_classifier': ml_service.satisfaction_classifier is not None,
            'efficiency_regressor': ml_service.efficiency_regressor is not None,
            'college_clusterer': ml_service.college_clusterer is not None,
            'model_path': str(ml_service.model_path),
            'feature_count': {
                'classifier': len(ml_service.feature_cols_class) if ml_service.feature_cols_class else 0,
                'regressor': len(ml_service.feature_cols_reg) if ml_service.feature_cols_reg else 0,
            }
        }
        return {
            'status': 'success',
            'model_status': status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))