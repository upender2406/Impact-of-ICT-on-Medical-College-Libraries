from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from app.models.schemas import (
    PredictionRequest,
    SatisfactionPrediction,
    EfficiencyPrediction,
    ScenarioSimulation,
)
from app.services.ml_service import ml_service
from app.database import get_db
from app.models.db_models import SurveyResponse as SurveyResponseDB

router = APIRouter()


@router.post("/satisfaction", response_model=SatisfactionPrediction, response_model_by_alias=False)
async def predict_satisfaction(request: PredictionRequest):
    """Predict satisfaction level."""
    try:
        features = {
            'infrastructure_score': request.infrastructureScore,
            'barrier_score': request.barrierScore,
            'college_id': request.collegeId,
            'automation_system': request.automationSystem,
            'awareness_level': request.awarenessLevel,
        }
        
        prediction = ml_service.predict_satisfaction(features)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/efficiency", response_model=EfficiencyPrediction, response_model_by_alias=False)
async def predict_efficiency(request: PredictionRequest):
    """Predict service efficiency."""
    try:
        features = {
            'infrastructure_score': request.infrastructureScore,
            'barrier_score': request.barrierScore,
            'college_id': request.collegeId,
            'automation_system': request.automationSystem,
            'awareness_level': request.awarenessLevel,
        }
        
        prediction = ml_service.predict_efficiency(features)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from pydantic import BaseModel

class ScenarioRequest(BaseModel):
    current: PredictionRequest
    proposed: PredictionRequest

@router.post("/scenario", response_model=ScenarioSimulation, response_model_by_alias=False)
async def simulate_scenario(request: ScenarioRequest):
    """Simulate impact of proposed changes."""
    try:
        current_features = {
            'infrastructure_score': request.current.infrastructureScore,
            'barrier_score': request.current.barrierScore,
            'college_id': request.current.collegeId,
            'automation_system': request.current.automationSystem,
            'awareness_level': request.current.awarenessLevel,
        }
        
        proposed_features = {
            'infrastructure_score': request.proposed.infrastructureScore,
            'barrier_score': request.proposed.barrierScore,
            'college_id': request.proposed.collegeId,
            'automation_system': request.proposed.automationSystem,
            'awareness_level': request.proposed.awarenessLevel,
        }
        
        simulation = ml_service.simulate_scenario(current_features, proposed_features)
        return simulation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clusters")
async def get_college_clusters():
    """Get college clusters using the clustering model."""
    try:
        clusters = ml_service.get_college_clusters()
        return clusters
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations")
async def get_recommendations(
    college_id: str = Query(...),
    db: Session = Depends(get_db),
):
    """Get AI-powered recommendations for a college."""
    try:
        from sqlalchemy import func as sqlfunc

        # Fetch real aggregate data for this college from the database
        row = (
            db.query(
                sqlfunc.avg(SurveyResponseDB.infrastructure_score).label("infrastructure_score"),
                sqlfunc.avg(SurveyResponseDB.barrier_score).label("barrier_score"),
                sqlfunc.avg(SurveyResponseDB.overall_satisfaction).label("overall_satisfaction"),
                sqlfunc.avg(SurveyResponseDB.service_efficiency).label("service_efficiency"),
                sqlfunc.avg(SurveyResponseDB.hardware_quality).label("hardware_quality"),
                sqlfunc.avg(SurveyResponseDB.software_availability).label("software_availability"),
                sqlfunc.avg(SurveyResponseDB.internet_speed).label("internet_speed"),
                sqlfunc.avg(SurveyResponseDB.digital_collection).label("digital_collection"),
                sqlfunc.avg(SurveyResponseDB.awareness_level).label("awareness_level"),
            )
            .filter(SurveyResponseDB.college.contains(college_id))
            .first()
        )

        if row and row.infrastructure_score is not None:
            college_data = {
                "college_id": college_id,
                "infrastructure_score": float(row.infrastructure_score),
                "barrier_score": float(row.barrier_score),
                "overall_satisfaction": float(row.overall_satisfaction),
                "service_efficiency": float(row.service_efficiency),
                "hardware_quality": float(row.hardware_quality),
                "software_availability": float(row.software_availability),
                "internet_speed": float(row.internet_speed),
                "digital_collection": float(row.digital_collection),
                "awareness_level": float(row.awareness_level),
                "ict_training_received": False,
            }
        else:
            college_data = {
                "college_id": college_id,
                "infrastructure_score": 3,
                "barrier_score": 3,
                "overall_satisfaction": 5,
                "service_efficiency": 5,
                "ict_training_received": False,
            }

        recommendations = ml_service.get_recommendations(college_data)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
