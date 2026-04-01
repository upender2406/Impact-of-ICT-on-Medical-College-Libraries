"""
Admin routes for model management and retraining
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.services.training_service import training_service
from app.services.db_data_service import get_data_service
from app.database import get_db
from app.services.auth_service import require_admin
from app.models.db_models import User, SurveyResponse as SurveyResponseDB
import pandas as pd

router = APIRouter()


@router.get("/training/status")
async def get_training_status(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get current training status and metrics.
    Shows data count, last training time, and model performance.
    """
    try:
        db_service = get_data_service(db)
        status = training_service.get_training_status()
        
        # Get current data count from database service
        current_count = db_service.get_count()
        should_retrain, new_entries = training_service.update_data_count(current_count)
        
        # Calculate entries until next auto-retrain
        if status['last_training_data_count'] == 0:
            # Never trained - need 100 entries minimum
            entries_until_retrain = max(0, 100 - current_count)
        else:
            # Calculate next retrain threshold
            last_count = status['last_training_data_count']
            next_threshold = ((last_count // 100) + 1) * 100
            entries_until_retrain = max(0, next_threshold - current_count)
        
        # Update status with latest data count
        status.update({
            'current_data_count': current_count,
            'new_entries_since_training': new_entries,
            'entries_until_retrain': entries_until_retrain,
            'should_retrain': should_retrain,
            'next_auto_retrain_at': status['last_training_data_count'] + training_service.retrain_threshold if status['last_training_data_count'] > 0 else 100
        })
        
        return {
            'status': 'success',
            'data': status
        }
    except Exception as e:
        print(f"Error in get_training_status: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/training/retrain")
async def retrain_models(
    background_tasks: BackgroundTasks, 
    force: bool = False,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Manually trigger model retraining.
    
    Args:
        force: If True, retrain even if threshold not met
        
    Returns:
        Training status and metrics
    """
    try:
        # Get all data from database service
        db_service = get_data_service(db)
        all_responses = db_service.get_all_responses()
        
        if len(all_responses) < 100:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data for training. Need at least 100 entries, got {len(all_responses)}"
            )
        
        # Convert to DataFrame
        df = pd.DataFrame(all_responses)
        
        # Check if retraining is needed
        current_count = len(all_responses)
        should_retrain, new_entries = training_service.update_data_count(current_count)
        
        if not force and not should_retrain:
            return {
                'status': 'skipped',
                'message': f'Retraining not needed. Only {new_entries} new entries since last training. Need {training_service.retrain_threshold} entries.',
                'new_entries': new_entries,
                'threshold': training_service.retrain_threshold
            }
        
        # Start training (can be done in background)
        result = training_service.train_models(df, force=force)
        
        return {
            'status': 'success',
            'message': 'Model retraining completed',
            'result': result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/training/retrain/background")
async def retrain_models_background(
    background_tasks: BackgroundTasks, 
    force: bool = False,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Trigger model retraining in background (non-blocking).
    
    Args:
        force: If True, retrain even if threshold not met
        
    Returns:
        Immediate response with job ID
    """
    try:
        db_service = get_data_service(db)
        all_responses = db_service.get_all_responses()
        
        if len(all_responses) < 100:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data for training. Need at least 100 entries, got {len(all_responses)}"
            )
        
        df = pd.DataFrame(all_responses)
        current_count = len(all_responses)
        should_retrain, new_entries = training_service.update_data_count(current_count)
        
        if not force and not should_retrain:
            return {
                'status': 'skipped',
                'message': f'Retraining not needed. Only {new_entries} new entries.',
                'new_entries': new_entries
            }
        
        # Add background task
        background_tasks.add_task(training_service.train_models, df, force)
        
        return {
            'status': 'started',
            'message': 'Model retraining started in background',
            'job_id': f'training_{current_count}',
            'estimated_time': '2-5 minutes'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entries")
async def get_user_entries(
    status: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all user entries for admin review."""
    try:
        from app.models.db_models import SubmissionStatus
        
        query = db.query(SurveyResponseDB)
        
        # Filter by status if provided
        if status:
            status_map = {
                'pending': SubmissionStatus.PENDING,
                'approved': SubmissionStatus.APPROVED,
                'rejected': SubmissionStatus.REJECTED
            }
            if status.lower() in status_map:
                query = query.filter(SurveyResponseDB.status == status_map[status.lower()])
        
        # Filter by user if provided
        if user_id:
            query = query.filter(SurveyResponseDB.user_id == user_id)
        
        entries = query.order_by(SurveyResponseDB.submitted_at.desc()).all()
        
        entry_data = []
        for entry in entries:
            # Get user info
            user = db.query(User).filter(User.id == entry.user_id).first()
            
            entry_data.append({
                'id': entry.id,
                'user_id': entry.user_id,
                'user_email': user.email if user else 'Unknown',
                'user_name': user.full_name if user else 'Unknown',
                'college': entry.college,
                'status': entry.status.value if entry.status else 'pending',
                'submitted_at': entry.submitted_at.isoformat() if entry.submitted_at else None,
                'reviewed_at': entry.reviewed_at.isoformat() if entry.reviewed_at else None,
                'reviewer_id': entry.reviewed_by,
                'infrastructure_score': float(entry.infrastructure_score) if entry.infrastructure_score else 0,
                'overall_satisfaction': float(entry.overall_satisfaction) if entry.overall_satisfaction else 0,
                'service_efficiency': float(entry.service_efficiency) if entry.service_efficiency else 0,
                'comments': entry.comments
            })
        
        return {
            'status': 'success',
            'entries': entry_data,
            'total_count': len(entry_data),
            'pending_count': len([e for e in entry_data if e['status'] == 'pending']),
            'approved_count': len([e for e in entry_data if e['status'] == 'approved']),
            'rejected_count': len([e for e in entry_data if e['status'] == 'rejected'])
        }
    except Exception as e:
        print(f"Error in get_user_entries: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/entries/{entry_id}/approve")
async def approve_entry(
    entry_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve a user entry."""
    try:
        from app.models.db_models import SubmissionStatus
        from datetime import datetime
        
        entry = db.query(SurveyResponseDB).filter(SurveyResponseDB.id == entry_id).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        entry.status = SubmissionStatus.APPROVED
        entry.reviewed_by = current_user.id
        entry.reviewed_at = datetime.utcnow()
        
        db.commit()
        
        return {
            'status': 'success',
            'message': f'Entry {entry_id} approved successfully'
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/entries/{entry_id}/reject")
async def reject_entry(
    entry_id: int,
    reason: str = Query(..., description="Reason for rejection"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Reject a user entry."""
    try:
        from app.models.db_models import SubmissionStatus
        from datetime import datetime
        
        entry = db.query(SurveyResponseDB).filter(SurveyResponseDB.id == entry_id).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        entry.status = SubmissionStatus.REJECTED
        entry.reviewed_by = current_user.id
        entry.reviewed_at = datetime.utcnow()
        entry.rejection_reason = reason
        
        db.commit()
        
        return {
            'status': 'success',
            'message': f'Entry {entry_id} rejected successfully'
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/entries/{entry_id}")
async def delete_entry(
    entry_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user entry."""
    try:
        entry = db.query(SurveyResponseDB).filter(SurveyResponseDB.id == entry_id).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        # Get user info for logging
        user = db.query(User).filter(User.id == entry.user_id).first()
        user_email = user.email if user else 'Unknown'
        
        db.delete(entry)
        db.commit()
        
        return {
            'status': 'success',
            'message': f'Entry {entry_id} from user {user_email} deleted successfully'
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/entries/bulk-action")
async def bulk_action_entries(
    entry_ids: List[int],
    action: str = Query(..., description="Action: approve, reject, delete"),
    reason: Optional[str] = Query(None, description="Reason for rejection (required for reject action)"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Perform bulk action on multiple entries."""
    try:
        from app.models.db_models import SubmissionStatus
        from datetime import datetime
        
        if action == 'reject' and not reason:
            raise HTTPException(status_code=400, detail="Reason is required for reject action")
        
        entries = db.query(SurveyResponseDB).filter(SurveyResponseDB.id.in_(entry_ids)).all()
        
        if not entries:
            raise HTTPException(status_code=404, detail="No entries found")
        
        processed_count = 0
        
        for entry in entries:
            if action == 'approve':
                entry.status = SubmissionStatus.APPROVED
                entry.reviewed_by = current_user.id
                entry.reviewed_at = datetime.utcnow()
                processed_count += 1
            elif action == 'reject':
                entry.status = SubmissionStatus.REJECTED
                entry.reviewed_by = current_user.id
                entry.reviewed_at = datetime.utcnow()
                entry.rejection_reason = reason
                processed_count += 1
            elif action == 'delete':
                db.delete(entry)
                processed_count += 1
        
        db.commit()
        
        return {
            'status': 'success',
            'message': f'Bulk {action} completed on {processed_count} entries'
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training/metrics")
async def get_training_metrics(
    current_user: User = Depends(require_admin)
):
    """
    Get detailed training metrics from last training.
    """
    try:
        status = training_service.get_training_status()
        metrics = status.get('last_training_metrics', {})
        
        return {
            'status': 'success',
            'metrics': metrics,
            'training_info': {
                'last_training_time': status.get('last_training_time'),
                'total_trainings': status.get('total_training_count', 0),
                'data_count_at_training': status.get('last_training_data_count', 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def get_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users for admin management."""
    try:
        users = db.query(User).all()
        user_data = []
        
        for user in users:
            # Count user's responses
            response_count = db.query(func.count(SurveyResponseDB.id)).filter(
                SurveyResponseDB.user_id == user.id
            ).scalar() or 0
            
            user_data.append({
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'full_name': user.full_name,
                'role': user.role.value if user.role else 'user',
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': None,  # Field doesn't exist in model yet
                'response_count': response_count
            })
        
        return {
            'status': 'success',
            'users': user_data,
            'total_count': len(user_data)
        }
    except Exception as e:
        print(f"Error in get_users: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user and all their responses."""
    try:
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Don't allow deleting admin users
        if user.role and user.role.value == 'admin':
            raise HTTPException(status_code=403, detail="Cannot delete admin users")
        
        # Delete user's responses first
        response_count = db.query(SurveyResponseDB).filter(SurveyResponseDB.user_id == user_id).count()
        db.query(SurveyResponseDB).filter(SurveyResponseDB.user_id == user_id).delete()
        
        # Delete user's notifications
        from app.models.db_models import Notification
        db.query(Notification).filter(Notification.user_id == user_id).delete()
        
        # Delete user
        db.delete(user)
        db.commit()
        
        return {
            'status': 'success',
            'message': f'User {user.email} and {response_count} responses deleted successfully'
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user active status."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_active = is_active
        db.commit()
        
        return {
            'status': 'success',
            'message': f'User {user.email} {"activated" if is_active else "deactivated"} successfully'
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/check-retrain")
async def check_and_retrain(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Check if retraining is needed based on new data entries.
    This endpoint should be called after new data is added.
    """
    try:
        db_service = get_data_service(db)
        current_count = db_service.get_count()
        should_retrain, new_entries = training_service.update_data_count(current_count)
        
        if should_retrain:
            # Auto-retrain in background
            all_responses = db_service.get_all_responses()
            df = pd.DataFrame(all_responses)
            
            background_tasks.add_task(training_service.train_models, df, force=False)
            
            return {
                'status': 'retraining',
                'message': f'Auto-retraining triggered: {new_entries} new entries detected',
                'new_entries': new_entries,
                'threshold': training_service.retrain_threshold
            }
        else:
            return {
                'status': 'ok',
                'message': f'No retraining needed. {new_entries} new entries, need {training_service.retrain_threshold}',
                'new_entries': new_entries,
                'entries_until_retrain': training_service.retrain_threshold - new_entries
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
