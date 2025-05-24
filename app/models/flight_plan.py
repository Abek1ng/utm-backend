import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class FlightPlanStatus(str, enum.Enum):
    PENDING_ORG_APPROVAL = "PENDING_ORG_APPROVAL"
    PENDING_AUTHORITY_APPROVAL = "PENDING_AUTHORITY_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED_BY_ORG = "REJECTED_BY_ORG"
    REJECTED_BY_AUTHORITY = "REJECTED_BY_AUTHORITY"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED_BY_PILOT = "CANCELLED_BY_PILOT"
    CANCELLED_BY_ADMIN = "CANCELLED_BY_ADMIN"

class FlightPlan(Base):
    __tablename__ = "flight_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", name="fk_flight_plan_user_id"), nullable=False) # Submitter
    drone_id = Column(Integer, ForeignKey("drones.id", name="fk_flight_plan_drone_id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id", name="fk_flight_plan_organization_id"), nullable=True)
    
    planned_departure_time = Column(DateTime(timezone=True), nullable=False)
    planned_arrival_time = Column(DateTime(timezone=True), nullable=False)
    actual_departure_time = Column(DateTime(timezone=True), nullable=True)
    actual_arrival_time = Column(DateTime(timezone=True), nullable=True)
    
    status = Column(SAEnum(FlightPlanStatus), nullable=False, index=True)
    notes = Column(Text, nullable=True) # VARCHAR(1000) in schema, Text is more flexible
    rejection_reason = Column(String(500), nullable=True)
    
    approved_by_organization_admin_id = Column(Integer, ForeignKey("users.id", name="fk_flight_plan_org_admin_id"), nullable=True)
    approved_by_authority_admin_id = Column(Integer, ForeignKey("users.id", name="fk_flight_plan_auth_admin_id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True) # Final approval time
    # created_at, updated_at, deleted_at from Base

    # Relationships
    submitter_user = relationship("User", foreign_keys=[user_id], back_populates="submitted_flight_plans")
    drone = relationship("Drone", back_populates="flight_plans")
    organization = relationship("Organization", back_populates="flight_plans", foreign_keys=[organization_id])
    
    organization_approver = relationship("User", foreign_keys=[approved_by_organization_admin_id], back_populates="organization_approved_flight_plans")
    authority_approver = relationship("User", foreign_keys=[approved_by_authority_admin_id], back_populates="authority_approved_flight_plans")
    
    waypoints = relationship("Waypoint", back_populates="flight_plan", cascade="all, delete-orphan", lazy="selectin")
    telemetry_logs = relationship("TelemetryLog", back_populates="flight_plan", cascade="all, delete-orphan", lazy="selectin") # Or set null on delete