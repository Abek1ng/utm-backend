from sqlalchemy import Column, BigInteger, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    # flight_plan_id can be nullable if live telemetry w/o plan, but for this project, assume it's linked.
    # Or, as per schema, ondelete SET NULL if a flight plan is deleted but logs are kept.
    flight_plan_id = Column(Integer, ForeignKey("flight_plans.id", name="fk_telemetry_log_flight_plan_id", ondelete="SET NULL"), nullable=True, index=True)
    drone_id = Column(Integer, ForeignKey("drones.id", name="fk_telemetry_log_drone_id", ondelete="CASCADE"), nullable=False, index=True)
    
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude_m = Column(Float, nullable=False)
    speed_mps = Column(Float, nullable=True)
    heading_degrees = Column(Float, nullable=True) # 0-359.9
    status_message = Column(String(255), nullable=True) # e.g., "ON_SCHEDULE", "NFZ_ALERT"
    # created_at, updated_at from Base. deleted_at might not be relevant for telemetry.

    # Relationships
    flight_plan = relationship("FlightPlan", back_populates="telemetry_logs")
    drone = relationship("Drone", back_populates="telemetry_logs", foreign_keys=[drone_id])