from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RespondentType(str, Enum):
    librarian = "librarian"
    user = "user"


class AutomationSystem(str, Enum):
    none = "None"
    koha = "KOHA"
    soul = "SOUL"
    other = "Other"


class InfrastructureAssessment(BaseModel):
    hardwareQuality: int = Field(ge=1, le=5, alias='hardware_quality', description="Hardware quality score (1-5)")
    softwareAvailability: int = Field(ge=1, le=5, alias='software_availability', description="Software availability score (1-5)")
    internetSpeed: int = Field(ge=1, le=5, alias='internet_speed', description="Internet speed score (1-5)")
    digitalCollection: int = Field(ge=1, le=5, alias='digital_collection', description="Digital collection score (1-5)")
    automationSystem: AutomationSystem = Field(alias='automation_system', description="Automation system in use")
    
    model_config = ConfigDict(populate_by_name=True)


class ServiceQuality(BaseModel):
    overallSatisfaction: int = Field(ge=1, le=10, alias='overall_satisfaction', description="Overall satisfaction (1-10)")
    serviceEfficiency: int = Field(ge=1, le=10, alias='service_efficiency', description="Service efficiency (1-10)")
    staffHelpfulness: int = Field(ge=1, le=10, alias='staff_helpfulness', description="Staff helpfulness (1-10)")
    
    model_config = ConfigDict(populate_by_name=True)


class BarriersAssessment(BaseModel):
    financialBarrier: int = Field(ge=1, le=5, alias='financial_barrier', description="Financial barrier (1-5)")
    technicalBarrier: int = Field(ge=1, le=5, alias='technical_barrier', description="Technical barrier (1-5)")
    trainingBarrier: int = Field(ge=1, le=5, alias='training_barrier', description="Training barrier (1-5)")
    policyBarrier: int = Field(ge=1, le=5, alias='policy_barrier', description="Policy barrier (1-5)")
    
    model_config = ConfigDict(populate_by_name=True)


class AdditionalInfo(BaseModel):
    weeklyVisits: int = Field(ge=0, alias='weekly_visits', description="Weekly visits count")
    ictTrainingReceived: bool = Field(alias='ict_training_received', description="ICT training received")
    remoteAccessAvailable: bool = Field(alias='remote_access_available', description="Remote access available")
    awarenessLevel: int = Field(default=3, ge=1, le=5, alias='awareness_level', description="ICT awareness level (1-5)")
    comments: Optional[str] = Field(None, description="Additional comments")
    
    model_config = ConfigDict(populate_by_name=True)


class Respondent(BaseModel):
    type: RespondentType
    name: str
    position: str
    email: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)


class SurveyResponseCreate(BaseModel):
    college_id: str
    respondent: Respondent
    infrastructure: InfrastructureAssessment
    service_quality: ServiceQuality
    barriers: BarriersAssessment
    additional_info: AdditionalInfo


class SurveyResponse(BaseModel):
    id: str
    collegeId: str = Field(alias='college_id')
    collegeName: str = Field(alias='college_name')
    respondent: Respondent
    infrastructure: InfrastructureAssessment
    serviceQuality: ServiceQuality = Field(alias='service_quality')
    barriers: BarriersAssessment
    additionalInfo: AdditionalInfo = Field(alias='additional_info')
    submittedAt: datetime = Field(alias='submitted_at')
    updatedAt: Optional[datetime] = Field(None, alias='updated_at')
    
    model_config = ConfigDict(populate_by_name=True)  # Allow both snake_case and camelCase


class PredictionRequest(BaseModel):
    infrastructureScore: float = Field(ge=1, le=5, alias='infrastructure_score')
    barrierScore: float = Field(ge=1, le=5, alias='barrier_score')
    collegeId: str = Field(alias='college_id')
    automationSystem: str = Field(alias='automation_system')
    awarenessLevel: float = Field(ge=1, le=10, alias='awareness_level')
    
    model_config = ConfigDict(populate_by_name=True)


class SatisfactionPrediction(BaseModel):
    prediction: str  # "Low", "Medium", "High"
    confidence: float
    probabilities: Dict[str, float]
    featureImportance: List[Dict[str, Any]] = Field(alias='feature_importance')
    
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=False)


class EfficiencyPrediction(BaseModel):
    predictedScore: float = Field(alias='predicted_score')
    confidenceInterval: Dict[str, float] = Field(alias='confidence_interval')
    improvementPotential: float = Field(alias='improvement_potential')
    suggestions: List[str]
    
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=False)


class ScenarioSimulation(BaseModel):
    currentScore: float = Field(alias='current_score')
    predictedScore: float = Field(alias='predicted_score')
    improvement: float
    improvementPercentage: float = Field(alias='improvement_percentage')
    estimatedCost: float = Field(alias='estimated_cost')
    roi: float
    timelineMonths: int = Field(alias='timeline_months')
    
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=False)


class SummaryStatistics(BaseModel):
    totalResponses: int
    averageInfrastructureScore: float
    averageSatisfaction: float
    criticalBarriersCount: int
    collegesCount: int
    responsesByCollege: Dict[str, int]
    responsesByType: Dict[str, int]


class FilterParams(BaseModel):
    college_ids: Optional[List[str]] = None
    respondent_types: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ReportOptions(BaseModel):
    template_id: str
    college_ids: List[str]
    sections: List[str]
    include_charts: bool = True
    language: str = "en"
    branding: Optional[Dict[str, Any]] = None


# Authentication schemas
class UserCreate(BaseModel):
    email: str = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    full_name: Optional[str] = Field(None, description="Full name")
    role: Optional[str] = Field("user", description="User role: 'user' or 'admin'")


class UserLogin(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="Password")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True