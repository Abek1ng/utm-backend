import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class UserRole(str, enum.Enum):
    AUTHORITY_ADMIN = "AUTHORITY_ADMIN"
    ORGANIZATION_ADMIN = "ORGANIZATION_ADMIN"
    ORGANIZATION_PILOT = "ORGANIZATION_PILOT"
    SOLO_PILOT = "SOLO_PILOT"

class User(Base):
    __tablename__ = "users" # Explicitly set as per db_scheme.md

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), unique=True, index=True, nullable=True)
    iin = Column(String(12), unique=True, index=True, nullable=True) # Kazakhstani ID
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id", name="fk_user_organization_id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    # created_at, updated_at, deleted_at from Base

    # Relationships
    organization = relationship("Organization", back_populates="users", foreign_keys=[organization_id])
    
    # Drones owned by solo pilot
    owned_drones_solo = relationship(
        "Drone",
        foreign_keys="[Drone.solo_owner_user_id]",
        back_populates="solo_owner_user",
        lazy="selectin" # Or "joined" if frequently accessed
    )
    
    # Drones assigned to this user (M2M)
    assigned_drones_through_link = relationship("UserDroneAssignment", back_populates="user", lazy="selectin")

    submitted_flight_plans = relationship("FlightPlan", foreign_keys="[FlightPlan.user_id]", back_populates="submitter_user", lazy="selectin")
    
    # For flight plan approvals
    organization_approved_flight_plans = relationship(
        "FlightPlan",
        foreign_keys="[FlightPlan.approved_by_organization_admin_id]",
        back_populates="organization_approver",
        lazy="selectin"
    )
    authority_approved_flight_plans = relationship(
        "FlightPlan",
        foreign_keys="[FlightPlan.approved_by_authority_admin_id]",
        back_populates="authority_approver",
        lazy="selectin"
    )
    
    created_restricted_zones = relationship(
        "RestrictedZone",
        foreign_keys="[RestrictedZone.created_by_authority_id]",
        back_populates="creator_authority",
        lazy="selectin"
    )

    # For organization admin link
    # If an organization has one admin, this relationship is on the Organization model
    # admin_of_organization = relationship("Organization", back_populates="admin_user", uselist=False)