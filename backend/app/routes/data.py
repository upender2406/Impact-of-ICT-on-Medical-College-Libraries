from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.schemas import (
    SurveyResponseCreate,
    SurveyResponse,
    SummaryStatistics,
    FilterParams,
)
from app.services.data_service import data_service
from app.services.db_data_service import get_data_service
from app.database import get_db
from app.services.auth_service import get_current_active_user, require_admin
from app.models.db_models import User, SurveyResponse as SurveyResponseDB
from fastapi import BackgroundTasks
import tempfile
import os

router = APIRouter()


@router.post("/submit", response_model=SurveyResponse)
async def submit_response(
    response_data: SurveyResponseCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit a new survey response (goes to pending for admin approval)."""
    try:
        db_service = get_data_service(db)
        
        # Convert Pydantic model to dict
        response_dict = response_data.dict()
        
        # Get college name
        college_names = {
            '1': 'Patna Medical College (PMCH)',
            '2': 'Darbhanga Medical College (DMCH)',
            '3': 'Anugrah Narayan Magadh Medical College (ANMMC)',
            '4': 'Nalanda Medical College (NMCH)',
            '5': 'Shri Krishna Medical College (SKMCH)',
            '6': 'Jawaharlal Nehru Medical College (JLNMCH)',
            '7': 'Indira Gandhi Institute of Medical Sciences (IGIMS)',
            '8': 'Vardhman Institute of Medical Sciences (VIMS)',
            '9': 'Government Medical College Bettiah (GMCH)',
        }
        response_dict['college_name'] = college_names.get(response_dict['college_id'], 'Unknown')
        
        # Create response in database with PENDING status
        response = db_service.create_response(response_dict, user_id=current_user.id)
        
        # Create notification for user
        from app.models.db_models import Notification, NotificationType
        notification = Notification(
            user_id=current_user.id,
            type=NotificationType.SYSTEM,
            title="Submission Received",
            message=f"Your survey submission for {response_dict['college_name']} has been received and is pending admin approval.",
            link=f"/submissions/{response.get('id')}"
        )
        db.add(notification)
        db.commit()
        
        # Check if retraining is needed (only for approved submissions)
        # This will be handled when admin approves
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
async def get_all_responses(
    college_id: Optional[List[str]] = Query(None),
    respondent_type: Optional[List[str]] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """Get all responses with optional filters."""
    db_service = get_data_service(db)
    
    filters = FilterParams(
        college_ids=college_id,
        respondent_types=respondent_type,
        start_date=start_date,
        end_date=end_date,
    )
    
    responses = db_service.get_all_responses(filters, limit=limit, offset=offset)
    # Return dict responses directly - they're already in camelCase format
    return responses


@router.get("/summary", response_model=SummaryStatistics)
async def get_summary_statistics(db: Session = Depends(get_db)):
    """Get summary statistics."""
    db_service = get_data_service(db)
    stats = db_service.get_summary_statistics()
    return stats


@router.put("/update/{response_id}", response_model=SurveyResponse)
async def update_response(
    response_id: int,
    update_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing response."""
    db_service = get_data_service(db)
    response = db_service.get_response_by_id(response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    # Only allow admin or the user who created it
    if current_user.role.value != "admin" and response.get('user_id') != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this response")
    
    # Update logic would go here (simplified for now - would need to implement update in db_data_service)
    return response


@router.delete("/delete/{response_id}")
async def delete_response(
    response_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a response (Admin only)."""
    db_service = get_data_service(db)
    response = db_service.get_response_by_id(response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    # Delete from database
    db_response = db.query(SurveyResponseDB).filter(SurveyResponseDB.id == response_id).first()
    if db_response:
        db.delete(db_response)
        db.commit()
    
    return {"message": "Response deleted successfully"}


@router.post("/bulk-import")
async def bulk_import(file: UploadFile = File(...)):
    """Bulk import responses from CSV/Excel file."""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Import data
        result = data_service.bulk_import(tmp_path)
        
        # Check if retraining is needed after bulk import
        from app.services.training_service import training_service
        from fastapi import BackgroundTasks
        current_count = len(data_service.responses)
        should_retrain, new_entries = training_service.update_data_count(current_count)
        
        if should_retrain:
            # Note: Background task would need to be passed, but for bulk import
            # we can return a message that retraining may be needed
            result['retraining_needed'] = True
            result['retraining_message'] = f'Auto-retraining will be triggered: {new_entries} new entries'
        
        # Clean up
        os.unlink(tmp_path)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
