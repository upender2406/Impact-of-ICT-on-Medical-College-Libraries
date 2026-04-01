"""
Database models using SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"


class SubmissionStatus(str, enum.Enum):
    """Submission status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


class NotificationType(str, enum.Enum):
    """Notification type enumeration"""
    APPROVAL = "approval"
    REJECTION = "rejection"
    REVISION_REQUEST = "revision_request"
    SYSTEM = "system"


class AutomationSystem(str, enum.Enum):
    """Automation system enumeration"""
    NONE = "None"
    KOHA = "KOHA"
    SOUL = "SOUL"
    OTHER = "Other"


class RespondentType(str, enum.Enum):
    """Respondent type enumeration"""
    STUDENT = "Student"
    FACULTY = "Faculty"
    RESEARCHER = "Researcher"
    LIBRARY_STAFF = "Library_Staff"


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    survey_responses = relationship("SurveyResponse", back_populates="user", foreign_keys="SurveyResponse.user_id")
    reviewed_responses = relationship("SurveyResponse", back_populates="reviewer", foreign_keys="SurveyResponse.reviewed_by")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="admin", cascade="all, delete-orphan")


class SurveyResponse(Base):
    """Survey response model with approval workflow"""
    __tablename__ = "survey_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Approval workflow
    status = Column(SQLEnum(SubmissionStatus), default=SubmissionStatus.PENDING, nullable=False, index=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    
    # College information
    college = Column(String(200), nullable=False, index=True)
    college_tier = Column(String(50), nullable=True)
    
    # Respondent information
    respondent_type = Column(SQLEnum(RespondentType), nullable=False)
    respondent_name = Column(String(200), nullable=True)
    respondent_position = Column(String(200), nullable=True)
    respondent_email = Column(String(255), nullable=True)
    
    # Infrastructure scores (1-5)
    hardware_quality = Column(Float, nullable=False)
    software_availability = Column(Float, nullable=False)
    internet_speed = Column(Float, nullable=False)
    digital_collection = Column(Float, nullable=False)
    automation_system = Column(SQLEnum(AutomationSystem), default=AutomationSystem.NONE, nullable=False)
    
    # Calculated infrastructure score
    infrastructure_score = Column(Float, nullable=False, index=True)
    
    # Service quality scores (1-10)
    overall_satisfaction = Column(Float, nullable=False, index=True)
    service_efficiency = Column(Float, nullable=False, index=True)
    staff_helpfulness = Column(Float, nullable=False)
    
    # Barrier scores (1-5)
    financial_barrier = Column(Float, nullable=False)
    technical_barrier = Column(Float, nullable=False)
    training_barrier = Column(Float, nullable=False)
    policy_barrier = Column(Float, nullable=False)
    
    # Calculated barrier score
    barrier_score = Column(Float, nullable=False, index=True)
    
    # Additional information
    weekly_visits = Column(Integer, default=0, nullable=False)
    ict_training_received = Column(Boolean, default=False, nullable=False)
    awareness_level = Column(Integer, default=3, nullable=False)
    remote_access_available = Column(Boolean, default=False, nullable=False)
    digital_resource_usage = Column(String(50), nullable=True)
    pandemic_adaptation = Column(String(50), nullable=True)
    comments = Column(Text, nullable=True)
    
    # AI-generated fields
    anomaly_score = Column(Float, nullable=True)  # 0-1, higher = more anomalous
    quality_score = Column(Float, nullable=True)  # 0-100, data quality rating
    
    # Timestamps
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="survey_responses", foreign_keys=[user_id])
    reviewer = relationship("User", back_populates="reviewed_responses", foreign_keys=[reviewed_by])
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status.value if self.status else None,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'review_notes': self.review_notes,
            'version': self.version,
            'college': self.college,
            'college_tier': self.college_tier,
            'respondent_type': self.respondent_type.value if self.respondent_type else None,
            'respondent_name': self.respondent_name,
            'respondent_position': self.respondent_position,
            'hardware_quality': self.hardware_quality,
            'software_availability': self.software_availability,
            'internet_speed': self.internet_speed,
            'digital_collection': self.digital_collection,
            'automation_system': self.automation_system.value if self.automation_system else None,
            'infrastructure_score': self.infrastructure_score,
            'overall_satisfaction': self.overall_satisfaction,
            'service_efficiency': self.service_efficiency,
            'staff_helpfulness': self.staff_helpfulness,
            'financial_barrier': self.financial_barrier,
            'technical_barrier': self.technical_barrier,
            'training_barrier': self.training_barrier,
            'policy_barrier': self.policy_barrier,
            'barrier_score': self.barrier_score,
            'weekly_visits': self.weekly_visits,
            'ict_training_received': self.ict_training_received,
            'awareness_level': self.awareness_level,
            'remote_access_available': self.remote_access_available,
            'digital_resource_usage': self.digital_resource_usage,
            'pandemic_adaptation': self.pandemic_adaptation,
            'comments': self.comments,
            'anomaly_score': self.anomaly_score,
            'quality_score': self.quality_score,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Notification(Base):
    """Notification model for user alerts"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(500), nullable=True)  # Link to related resource
    read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type.value if self.type else None,
            'title': self.title,
            'message': self.message,
            'link': self.link,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class AuditLog(Base):
    """Audit log for admin actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)  # approve, reject, delete, etc.
    target_type = Column(String(50), nullable=False)  # submission, user, etc.
    target_id = Column(Integer, nullable=False)
    details = Column(Text, nullable=True)  # JSON string with additional details
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    admin = relationship("User", back_populates="audit_logs")
    
    def to_dict(self):
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
