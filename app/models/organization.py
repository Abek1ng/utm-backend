from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    bin = Column(String(12), unique=True, index=True, nullable=False) # Business ID Number
    company_address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id", name="fk_organization_admin_id"), unique=True, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    # created_at, updated_at, deleted_at from Base

    # Relationships
    users = relationship("User", back_populates="organization", foreign_keys="[User.organization_id]")
    admin_user = relationship("User", foreign_keys=[admin_id]) # , back_populates="admin_of_organization"
    
    # Drones owned by this organization
    owned_drones = relationship(
        "Drone",
        foreign_keys="[Drone.organization_id]",
        back_populates="organization_owner",
        lazy="selectin"
    )

    # Flight plans related to this organization (indirectly via users or drones)
    # This can be complex to model directly if not explicitly linked.
    # We can query flight plans where flight_plan.organization_id is set.
    flight_plans = relationship("FlightPlan", back_populates="organization", foreign_keys="[FlightPlan.organization_id]")