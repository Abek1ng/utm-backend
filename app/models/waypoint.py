from sqlalchemy import Column, Integer, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Waypoint(Base):
    __tablename__ = "waypoints"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    flight_plan_id = Column(Integer, ForeignKey("flight_plans.id", name="fk_waypoint_flight_plan_id", ondelete="CASCADE"), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude_m = Column(Float, nullable=False) # AGL
    sequence_order = Column(Integer, nullable=False)
    # created_at, updated_at from Base. deleted_at might not be relevant if waypoints are immutable once plan is set.

    # Relationships
    flight_plan = relationship("FlightPlan", back_populates="waypoints")

    __table_args__ = (
        Index("ix_waypoint_flight_plan_id_sequence_order", "flight_plan_id", "sequence_order", unique=True),
    )