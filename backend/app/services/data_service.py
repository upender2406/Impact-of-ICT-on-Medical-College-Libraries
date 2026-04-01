from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from app.models.schemas import SurveyResponse, SummaryStatistics, FilterParams


class DataService:
    """
    Service for managing survey response data.
    In production, this would interact with Supabase/PostgreSQL.
    For now, we'll use in-memory storage.
    """
    
    def __init__(self):
        self.responses: List[Dict[str, Any]] = []
    
    def create_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new survey response."""
        response_id = f"resp_{len(self.responses) + 1}_{datetime.now().timestamp()}"
        
        response = {
            'id': response_id,
            **response_data,
            'submitted_at': datetime.now().isoformat(),
            'updated_at': None,
        }
        
        self.responses.append(response)
        return response
    
    def get_all_responses(self, filters: Optional[FilterParams] = None) -> List[Dict[str, Any]]:
        """Get all responses with optional filtering."""
        filtered = self.responses.copy()
        
        if filters:
            if filters.college_ids:
                filtered = [r for r in filtered if r.get('college_id') in filters.college_ids]
            
            if filters.respondent_types:
                filtered = [r for r in filtered if r.get('respondent', {}).get('type') in filters.respondent_types]
            
            if filters.start_date:
                filtered = [r for r in filtered if r.get('submitted_at', '') >= filters.start_date]
            
            if filters.end_date:
                filtered = [r for r in filtered if r.get('submitted_at', '') <= filters.end_date]
        
        return filtered
    
    def get_response_by_id(self, response_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific response by ID."""
        return next((r for r in self.responses if r.get('id') == response_id), None)
    
    def update_response(self, response_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing response."""
        response = self.get_response_by_id(response_id)
        if response:
            response.update(update_data)
            response['updated_at'] = datetime.now().isoformat()
            return response
        return None
    
    def delete_response(self, response_id: str) -> bool:
        """Delete a response."""
        initial_count = len(self.responses)
        self.responses = [r for r in self.responses if r.get('id') != response_id]
        return len(self.responses) < initial_count
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Calculate summary statistics."""
        if not self.responses:
            return {
                'total_responses': 0,
                'average_infrastructure_score': 0.0,
                'average_satisfaction': 0.0,
                'critical_barriers_count': 0,
                'colleges_count': 0,
                'responses_by_college': {},
                'responses_by_type': {'librarian': 0, 'user': 0},
            }
        
        # Calculate infrastructure scores
        infra_scores = []
        for r in self.responses:
            infra = r.get('infrastructure', {})
            score = (
                infra.get('hardware_quality', 0) +
                infra.get('software_availability', 0) +
                infra.get('internet_speed', 0) +
                infra.get('digital_collection', 0)
            ) / 4
            infra_scores.append(score)
        
        avg_infra = sum(infra_scores) / len(infra_scores) if infra_scores else 0
        
        # Calculate satisfaction scores
        satisfaction_scores = [
            r.get('service_quality', {}).get('overall_satisfaction', 0)
            for r in self.responses
        ]
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
        
        # Count critical barriers (score >= 4)
        critical_barriers = 0
        for r in self.responses:
            barriers = r.get('barriers', {})
            if any([
                barriers.get('financial_barrier', 0) >= 4,
                barriers.get('technical_barrier', 0) >= 4,
                barriers.get('training_barrier', 0) >= 4,
                barriers.get('policy_barrier', 0) >= 4,
            ]):
                critical_barriers += 1
        
        # Responses by college
        responses_by_college: Dict[str, int] = {}
        for r in self.responses:
            college_id = r.get('college_id', 'unknown')
            responses_by_college[college_id] = responses_by_college.get(college_id, 0) + 1
        
        # Responses by type
        responses_by_type = {'librarian': 0, 'user': 0}
        for r in self.responses:
            resp_type = r.get('respondent', {}).get('type', 'user')
            if resp_type in responses_by_type:
                responses_by_type[resp_type] += 1
        
        return {
            'total_responses': len(self.responses),
            'average_infrastructure_score': round(avg_infra, 2),
            'average_satisfaction': round(avg_satisfaction, 2),
            'critical_barriers_count': critical_barriers,
            'colleges_count': len(responses_by_college),
            'responses_by_college': responses_by_college,
            'responses_by_type': responses_by_type,
        }
    
    def bulk_import(self, file_path: str) -> Dict[str, Any]:
        """Import responses from CSV/Excel file."""
        try:
            # Try Excel first
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
            
            imported = 0
            errors = []
            
            for idx, row in df.iterrows():
                try:
                    # Map columns to response structure
                    response_data = {
                        'college_id': str(row.get('college_id', '')),
                        'college_name': str(row.get('college_name', '')),
                        'respondent': {
                            'type': row.get('respondent_type', 'user'),
                            'name': str(row.get('respondent_name', '')),
                            'position': str(row.get('respondent_position', '')),
                        },
                        'infrastructure': {
                            'hardware_quality': int(row.get('hardware_quality', 3)),
                            'software_availability': int(row.get('software_availability', 3)),
                            'internet_speed': int(row.get('internet_speed', 3)),
                            'digital_collection': int(row.get('digital_collection', 3)),
                            'automation_system': str(row.get('automation_system', 'None')),
                        },
                        'service_quality': {
                            'overall_satisfaction': int(row.get('overall_satisfaction', 5)),
                            'service_efficiency': int(row.get('service_efficiency', 5)),
                            'staff_helpfulness': int(row.get('staff_helpfulness', 5)),
                        },
                        'barriers': {
                            'financial_barrier': int(row.get('financial_barrier', 3)),
                            'technical_barrier': int(row.get('technical_barrier', 3)),
                            'training_barrier': int(row.get('training_barrier', 3)),
                            'policy_barrier': int(row.get('policy_barrier', 3)),
                        },
                        'additional_info': {
                            'weekly_visits': int(row.get('weekly_visits', 0)),
                            'ict_training_received': bool(row.get('ict_training_received', False)),
                            'remote_access_available': bool(row.get('remote_access_available', False)),
                            'comments': str(row.get('comments', '')),
                        },
                    }
                    
                    self.create_response(response_data)
                    imported += 1
                except Exception as e:
                    errors.append({'row': idx + 1, 'error': str(e)})
            
            return {'imported': imported, 'errors': errors}
        except Exception as e:
            return {'imported': 0, 'errors': [{'row': 0, 'error': str(e)}]}


# Global data service instance
data_service = DataService()
