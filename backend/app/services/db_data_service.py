"""
Database-backed data service for survey responses
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.database import get_db
from app.models.db_models import SurveyResponse, User, RespondentType
from app.models.schemas import SurveyResponseCreate, FilterParams, SummaryStatistics


class DBDataService:
    """Database-backed data service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_response(self, response_data: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a new survey response"""
        from app.models.db_models import AutomationSystem, RespondentType
        
        # Map automation system
        automation_map = {
            'None': AutomationSystem.NONE,
            'KOHA': AutomationSystem.KOHA,
            'SOUL': AutomationSystem.SOUL,
            'Other': AutomationSystem.OTHER
        }
        
        # Map respondent type
        respondent_map = {
            'librarian': RespondentType.LIBRARY_STAFF,
            'user': RespondentType.STUDENT,
            'Student': RespondentType.STUDENT,
            'Faculty': RespondentType.FACULTY,
            'Researcher': RespondentType.RESEARCHER,
            'Library_Staff': RespondentType.LIBRARY_STAFF
        }
        
        # Calculate infrastructure score
        infra = response_data.get('infrastructure', {})
        infrastructure_score = (
            infra.get('hardware_quality', 3) +
            infra.get('software_availability', 3) +
            infra.get('internet_speed', 3) +
            infra.get('digital_collection', 3)
        ) / 4
        
        # Calculate barrier score
        barriers = response_data.get('barriers', {})
        barrier_score = (
            barriers.get('financial_barrier', 3) +
            barriers.get('technical_barrier', 3) +
            barriers.get('training_barrier', 3) +
            barriers.get('policy_barrier', 3)
        ) / 4
        
        # Get college name
        college_name = response_data.get('college_name', response_data.get('college_id', 'Unknown'))
        
        # Create response
        db_response = SurveyResponse(
            user_id=user_id,
            college=college_name,
            college_tier=None,  # Can be calculated later
            respondent_type=respondent_map.get(
                response_data.get('respondent', {}).get('type', 'user'),
                RespondentType.STUDENT
            ),
            respondent_name=response_data.get('respondent', {}).get('name'),
            respondent_position=response_data.get('respondent', {}).get('position'),
            respondent_email=response_data.get('respondent', {}).get('email'),
            hardware_quality=float(infra.get('hardware_quality', 3)),
            software_availability=float(infra.get('software_availability', 3)),
            internet_speed=float(infra.get('internet_speed', 3)),
            digital_collection=float(infra.get('digital_collection', 3)),
            automation_system=automation_map.get(
                infra.get('automation_system', 'None'),
                AutomationSystem.NONE
            ),
            infrastructure_score=float(infrastructure_score),
            overall_satisfaction=float(response_data.get('service_quality', {}).get('overall_satisfaction', 5)),
            service_efficiency=float(response_data.get('service_quality', {}).get('service_efficiency', 5)),
            staff_helpfulness=float(response_data.get('service_quality', {}).get('staff_helpfulness', 5)),
            financial_barrier=float(barriers.get('financial_barrier', 3)),
            technical_barrier=float(barriers.get('technical_barrier', 3)),
            training_barrier=float(barriers.get('training_barrier', 3)),
            policy_barrier=float(barriers.get('policy_barrier', 3)),
            barrier_score=float(barrier_score),
            weekly_visits=int(response_data.get('additional_info', {}).get('weekly_visits', 0)),
            ict_training_received=bool(response_data.get('additional_info', {}).get('ict_training_received', False)),
            awareness_level=int(response_data.get('additional_info', {}).get('awareness_level', 3)),
            remote_access_available=bool(response_data.get('additional_info', {}).get('remote_access_available', False)),
            comments=response_data.get('additional_info', {}).get('comments'),
        )
        
        self.db.add(db_response)
        self.db.commit()
        self.db.refresh(db_response)
        
        # Return in the expected schema format
        return self._convert_to_schema_format(db_response)
    
    def _convert_to_schema_format(self, db_response: SurveyResponse) -> Dict[str, Any]:
        """Convert database model to Pydantic schema format"""
        # Extract college ID from college name (e.g., "Patna Medical College (PMCH)" -> "1")
        college_id_map = {
            'Patna Medical College (PMCH)': '1',
            'Darbhanga Medical College (DMCH)': '2',
            'Anugrah Narayan Magadh Medical College (ANMMC)': '3',
            'Nalanda Medical College (NMCH)': '4',
            'Shri Krishna Medical College (SKMCH)': '5',
            'Jawaharlal Nehru Medical College (JLNMCH)': '6',
            'Indira Gandhi Institute of Medical Sciences (IGIMS)': '7',
            'Vardhman Institute of Medical Sciences (VIMS)': '8',
            'Government Medical College Bettiah (GMCH)': '9',
        }
        college_id = '1'  # Default
        for name, cid in college_id_map.items():
            if name in db_response.college:
                college_id = cid
                break
        
        # Map respondent type
        respondent_type_map = {
            'Student': 'user',
            'Faculty': 'user',
            'Researcher': 'user',
            'Library_Staff': 'librarian',
        }
        resp_type_value = db_response.respondent_type.value if db_response.respondent_type else 'Student'
        respondent_type = respondent_type_map.get(resp_type_value, 'user')
        
        return {
            'id': str(db_response.id),
            'collegeId': college_id,
            'collegeName': db_response.college,
            'respondent': {
                'type': respondent_type,
                'name': db_response.respondent_name or 'Unknown',
                'position': db_response.respondent_position or '',
                'email': db_response.respondent_email,
            },
            'infrastructure': {
                'hardwareQuality': int(db_response.hardware_quality),
                'softwareAvailability': int(db_response.software_availability),
                'internetSpeed': int(db_response.internet_speed),
                'digitalCollection': int(db_response.digital_collection),
                'automationSystem': db_response.automation_system.value if db_response.automation_system else 'None',
            },
            'serviceQuality': {
                'overallSatisfaction': int(db_response.overall_satisfaction),
                'serviceEfficiency': int(db_response.service_efficiency),
                'staffHelpfulness': int(db_response.staff_helpfulness),
            },
            'barriers': {
                'financialBarrier': int(db_response.financial_barrier),
                'technicalBarrier': int(db_response.technical_barrier),
                'trainingBarrier': int(db_response.training_barrier),
                'policyBarrier': int(db_response.policy_barrier),
            },
            'additionalInfo': {
                'weeklyVisits': db_response.weekly_visits,
                'ictTrainingReceived': db_response.ict_training_received,
                'remoteAccessAvailable': db_response.remote_access_available,
                'comments': db_response.comments,
            },
            'submittedAt': db_response.submitted_at.isoformat() if db_response.submitted_at else datetime.now().isoformat(),
            'updatedAt': db_response.updated_at.isoformat() if db_response.updated_at else None,
        }
    
    def get_all_responses(self, filters: Optional[FilterParams] = None, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all responses with optional filtering"""
        try:
            query = self.db.query(SurveyResponse)
            
            if filters:
                if filters.college_ids:
                    query = query.filter(SurveyResponse.college.in_(filters.college_ids))
                
                if filters.respondent_types:
                    # Convert string types to enum values
                    enum_types = []
                    for rt in filters.respondent_types:
                        try:
                            enum_types.append(RespondentType[rt.upper()])
                        except (KeyError, AttributeError):
                            # Try direct match
                            try:
                                enum_types.append(RespondentType(rt))
                            except ValueError:
                                pass
                    if enum_types:
                        query = query.filter(SurveyResponse.respondent_type.in_(enum_types))
                
                if filters.start_date:
                    query = query.filter(SurveyResponse.submitted_at >= filters.start_date)
                
                if filters.end_date:
                    query = query.filter(SurveyResponse.submitted_at <= filters.end_date)
            
            query = query.order_by(SurveyResponse.submitted_at.desc())
            
            # Apply limit - default to all records if not specified
            if limit:
                query = query.limit(limit).offset(offset)
            
            responses = query.all()
            result = []
            for r in responses:
                try:
                    result.append(self._convert_to_schema_format(r))
                except Exception as e:
                    # Log error but continue processing other responses
                    print(f"Error converting response {r.id} to schema format: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            return result
        except Exception as e:
            print(f"Error in get_all_responses: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_response_by_id(self, response_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific response by ID"""
        response = self.db.query(SurveyResponse).filter(SurveyResponse.id == response_id).first()
        return response.to_dict() if response else None
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Calculate summary statistics"""
        total = self.db.query(func.count(SurveyResponse.id)).scalar()
        
        if total == 0:
            return {
                'totalResponses': 0,
                'averageInfrastructureScore': 0.0,
                'averageSatisfaction': 0.0,
                'criticalBarriersCount': 0,
                'collegesCount': 0,
                'responsesByCollege': {},
                'responsesByType': {'librarian': 0, 'user': 0},
            }
        
        # Average scores
        avg_infra = self.db.query(func.avg(SurveyResponse.infrastructure_score)).scalar() or 0.0
        avg_satisfaction = self.db.query(func.avg(SurveyResponse.overall_satisfaction)).scalar() or 0.0
        
        # Critical barriers (barrier score >= 4)
        critical_barriers = self.db.query(func.count(SurveyResponse.id)).filter(
            SurveyResponse.barrier_score >= 4.0
        ).scalar()
        
        # Colleges count
        colleges_count = self.db.query(func.count(func.distinct(SurveyResponse.college))).scalar()
        
        # Responses by college
        responses_by_college = {}
        college_counts = self.db.query(
            SurveyResponse.college,
            func.count(SurveyResponse.id).label('count')
        ).group_by(SurveyResponse.college).all()
        
        for college, count in college_counts:
            responses_by_college[college] = count
        
        # Responses by type - map to frontend format
        responses_by_type = {'librarian': 0, 'user': 0}
        type_counts = self.db.query(
            SurveyResponse.respondent_type,
            func.count(SurveyResponse.id).label('count')
        ).group_by(SurveyResponse.respondent_type).all()
        
        type_map = {
            'Library_Staff': 'librarian',
            'Student': 'user',
            'Faculty': 'user',
            'Researcher': 'user',
        }
        
        for resp_type, count in type_counts:
            type_value = resp_type.value if hasattr(resp_type, 'value') else str(resp_type)
            mapped_type = type_map.get(type_value, 'user')
            responses_by_type[mapped_type] = responses_by_type.get(mapped_type, 0) + count
        
        return {
            'totalResponses': total,
            'averageInfrastructureScore': round(float(avg_infra), 2),
            'averageSatisfaction': round(float(avg_satisfaction), 2),
            'criticalBarriersCount': critical_barriers,
            'collegesCount': colleges_count,
            'responsesByCollege': responses_by_college,
            'responsesByType': responses_by_type,
        }
    
    def get_count(self) -> int:
        """Get total count of responses"""
        return self.db.query(func.count(SurveyResponse.id)).scalar()


# Global function to get service instance
def get_data_service(db: Session = None) -> DBDataService:
    """Get data service instance"""
    if db is None:
        db = next(get_db())
    return DBDataService(db)
