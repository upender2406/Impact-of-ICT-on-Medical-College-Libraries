"""
Admin approval routes for managing submissions
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from app.database import get_db
from app.models.db_models import (
    SurveyResponse, User, Notification, AuditLog,
    SubmissionStatus, NotificationType
)
from app.services.auth_service import require_admin, get_current_active_user
from pydantic import BaseModel

router = APIRouter()


class ApprovalAction(BaseModel):
    """Model for approval actions"""
    action: str  # approve, reject, request_revision
    notes: Optional[str] = None


class BulkApprovalAction(BaseModel):
    """Model for bulk approval actions"""
    submission_ids: List[int]
    action: str  # approve, reject
    notes: Optional[str] = None


@router.get("/pending")
async def get_pending_submissions(
    skip: int = 0,
    limit: int = 50,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all pending submissions for admin review"""
    try:
        query = db.query(SurveyResponse).filter(
            SurveyResponse.status == SubmissionStatus.PENDING
        ).order_by(SurveyResponse.submitted_at.desc())
        
        total = query.count()
        submissions = query.offset(skip).limit(limit).all()
        
        return {
            'total': total,
            'submissions': [s.to_dict() for s in submissions],
            'page': skip // limit + 1,
            'pages': (total + limit - 1) // limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending/count")
async def get_pending_count(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get count of pending submissions"""
    try:
        count = db.query(SurveyResponse).filter(
            SurveyResponse.status == SubmissionStatus.PENDING
        ).count()
        
        return {'count': count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/submission/{submission_id}")
async def get_submission_details(
    submission_id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific submission"""
    try:
        submission = db.query(SurveyResponse).filter(
            SurveyResponse.id == submission_id
        ).first()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Get submitter info
        submitter = None
        if submission.user_id:
            user = db.query(User).filter(User.id == submission.user_id).first()
            if user:
                submitter = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name
                }
        
        # Get reviewer info if reviewed
        reviewer = None
        if submission.reviewed_by:
            rev_user = db.query(User).filter(User.id == submission.reviewed_by).first()
            if rev_user:
                reviewer = {
                    'id': rev_user.id,
                    'username': rev_user.username,
                    'full_name': rev_user.full_name
                }
        
        return {
            'submission': submission.to_dict(),
            'submitter': submitter,
            'reviewer': reviewer
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submission/{submission_id}/approve")
async def approve_submission(
    submission_id: int,
    action: ApprovalAction,
    request: Request,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve a submission"""
    try:
        submission = db.query(SurveyResponse).filter(
            SurveyResponse.id == submission_id
        ).first()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        if submission.status != SubmissionStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Submission is already {submission.status.value}"
            )
        
        # Update submission
        submission.status = SubmissionStatus.APPROVED
        submission.reviewed_by = current_admin.id
        submission.reviewed_at = datetime.utcnow()
        submission.review_notes = action.notes
        
        # Create notification for user
        if submission.user_id:
            notification = Notification(
                user_id=submission.user_id,
                type=NotificationType.APPROVAL,
                title="Submission Approved",
                message=f"Your survey submission for {submission.college} has been approved.",
                link=f"/submissions/{submission_id}"
            )
            db.add(notification)
        
        # Create audit log
        audit_log = AuditLog(
            admin_id=current_admin.id,
            action="approve_submission",
            target_type="submission",
            target_id=submission_id,
            details=json.dumps({
                'notes': action.notes,
                'college': submission.college
            }),
            ip_address=request.client.host if request.client else None
        )
        db.add(audit_log)
        
        db.commit()
        db.refresh(submission)
        
        return {
            'success': True,
            'message': 'Submission approved successfully',
            'submission': submission.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submission/{submission_id}/reject")
async def reject_submission(
    submission_id: int,
    action: ApprovalAction,
    request: Request,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Reject a submission"""
    try:
        submission = db.query(SurveyResponse).filter(
            SurveyResponse.id == submission_id
        ).first()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        if submission.status != SubmissionStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Submission is already {submission.status.value}"
            )
        
        # Update submission
        submission.status = SubmissionStatus.REJECTED
        submission.reviewed_by = current_admin.id
        submission.reviewed_at = datetime.utcnow()
        submission.review_notes = action.notes or "Submission rejected"
        
        # Create notification for user
        if submission.user_id:
            notification = Notification(
                user_id=submission.user_id,
                type=NotificationType.REJECTION,
                title="Submission Rejected",
                message=f"Your survey submission for {submission.college} has been rejected. Reason: {action.notes or 'Not specified'}",
                link=f"/submissions/{submission_id}"
            )
            db.add(notification)
        
        # Create audit log
        audit_log = AuditLog(
            admin_id=current_admin.id,
            action="reject_submission",
            target_type="submission",
            target_id=submission_id,
            details=json.dumps({
                'notes': action.notes,
                'college': submission.college
            }),
            ip_address=request.client.host if request.client else None
        )
        db.add(audit_log)
        
        db.commit()
        db.refresh(submission)
        
        return {
            'success': True,
            'message': 'Submission rejected',
            'submission': submission.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submission/{submission_id}/request-revision")
async def request_revision(
    submission_id: int,
    action: ApprovalAction,
    request: Request,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Request revision for a submission"""
    try:
        submission = db.query(SurveyResponse).filter(
            SurveyResponse.id == submission_id
        ).first()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        if submission.status != SubmissionStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Submission is already {submission.status.value}"
            )
        
        # Update submission
        submission.status = SubmissionStatus.REVISION_REQUESTED
        submission.reviewed_by = current_admin.id
        submission.reviewed_at = datetime.utcnow()
        submission.review_notes = action.notes or "Revision requested"
        
        # Create notification for user
        if submission.user_id:
            notification = Notification(
                user_id=submission.user_id,
                type=NotificationType.REVISION_REQUEST,
                title="Revision Requested",
                message=f"Please revise your survey submission for {submission.college}. Notes: {action.notes or 'See details'}",
                link=f"/submissions/{submission_id}"
            )
            db.add(notification)
        
        # Create audit log
        audit_log = AuditLog(
            admin_id=current_admin.id,
            action="request_revision",
            target_type="submission",
            target_id=submission_id,
            details=json.dumps({
                'notes': action.notes,
                'college': submission.college
            }),
            ip_address=request.client.host if request.client else None
        )
        db.add(audit_log)
        
        db.commit()
        db.refresh(submission)
        
        return {
            'success': True,
            'message': 'Revision requested',
            'submission': submission.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-action")
async def bulk_approval_action(
    bulk_action: BulkApprovalAction,
    request: Request,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Perform bulk approval/rejection"""
    try:
        if bulk_action.action not in ['approve', 'reject']:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        submissions = db.query(SurveyResponse).filter(
            SurveyResponse.id.in_(bulk_action.submission_ids),
            SurveyResponse.status == SubmissionStatus.PENDING
        ).all()
        
        if not submissions:
            raise HTTPException(status_code=404, detail="No pending submissions found")
        
        status = SubmissionStatus.APPROVED if bulk_action.action == 'approve' else SubmissionStatus.REJECTED
        notif_type = NotificationType.APPROVAL if bulk_action.action == 'approve' else NotificationType.REJECTION
        
        updated_count = 0
        for submission in submissions:
            submission.status = status
            submission.reviewed_by = current_admin.id
            submission.reviewed_at = datetime.utcnow()
            submission.review_notes = bulk_action.notes
            
            # Create notification
            if submission.user_id:
                notification = Notification(
                    user_id=submission.user_id,
                    type=notif_type,
                    title=f"Submission {bulk_action.action.title()}d",
                    message=f"Your survey submission for {submission.college} has been {bulk_action.action}d.",
                    link=f"/submissions/{submission.id}"
                )
                db.add(notification)
            
            updated_count += 1
        
        # Create audit log
        audit_log = AuditLog(
            admin_id=current_admin.id,
            action=f"bulk_{bulk_action.action}",
            target_type="submission",
            target_id=0,  # Bulk action
            details=json.dumps({
                'count': updated_count,
                'submission_ids': bulk_action.submission_ids,
                'notes': bulk_action.notes
            }),
            ip_address=request.client.host if request.client else None
        )
        db.add(audit_log)
        
        db.commit()
        
        return {
            'success': True,
            'message': f'{updated_count} submissions {bulk_action.action}d',
            'count': updated_count
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_approval_history(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get approval history"""
    try:
        query = db.query(SurveyResponse).filter(
            SurveyResponse.status != SubmissionStatus.PENDING
        )
        
        if status:
            try:
                status_enum = SubmissionStatus(status)
                query = query.filter(SurveyResponse.status == status_enum)
            except ValueError:
                pass
        
        query = query.order_by(SurveyResponse.reviewed_at.desc())
        
        total = query.count()
        submissions = query.offset(skip).limit(limit).all()
        
        return {
            'total': total,
            'submissions': [s.to_dict() for s in submissions],
            'page': skip // limit + 1,
            'pages': (total + limit - 1) // limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
