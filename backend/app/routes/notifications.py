"""
Notification routes for users
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.db_models import Notification, User
from app.services.auth_service import get_current_active_user

router = APIRouter()


@router.get("/")
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user notifications"""
    try:
        query = db.query(Notification).filter(
            Notification.user_id == current_user.id
        )
        
        if unread_only:
            query = query.filter(Notification.read == False)
        
        query = query.order_by(Notification.created_at.desc())
        
        total = query.count()
        notifications = query.offset(skip).limit(limit).all()
        
        return {
            'total': total,
            'unread_count': db.query(Notification).filter(
                Notification.user_id == current_user.id,
                Notification.read == False
            ).count(),
            'notifications': [n.to_dict() for n in notifications]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unread/count")
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    try:
        count = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.read == False
        ).count()
        
        return {'count': count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.read = True
        db.commit()
        
        return {'success': True, 'message': 'Notification marked as read'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-all-read")
async def mark_all_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    try:
        db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.read == False
        ).update({'read': True})
        
        db.commit()
        
        return {'success': True, 'message': 'All notifications marked as read'}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        db.delete(notification)
        db.commit()
        
        return {'success': True, 'message': 'Notification deleted'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
