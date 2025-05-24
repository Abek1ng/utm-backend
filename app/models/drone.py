import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum, BigInteger
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class DroneOwnerType(str, enum.Enum):
    ORGANIZATION = "ORGANIZATION"
    SOLO_PILOT = "SOLO_PILOT"

class DroneStatus(str, enum.Enum):
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    MAINTENANCE = "MAINTENANCE"
    UNKNOWN = "UNKNOWN"

class Drone(Base):
    __tablename__ = "drones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    serial_number = Column(String(100), unique=True, index=True, nullable=False)
    owner_type = Column(SAEnum(DroneOwnerType), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id", name="fk_drone_organization_id"), nullable=True)
    solo_owner_user_id = Column(Integer, ForeignKey("users.id", name="fk_drone_solo_owner_user_id"), nullable=True)
    current_status = Column(SAEnum(DroneStatus), nullable=False, default=DroneStatus.IDLE)
    # last_telemetry_id: Foreign key to telemetry_logs. Needs careful handling with Alembic if telemetry_logs table is defined later.
    # Alembic use_alter=True helps here.
    last_telemetry_id = Column(BigInteger, ForeignKey("telemetry_logs.id", name="fk_drone_last_telemetry_id", use_alter=True), nullable=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    # created_at, updated_at, deleted_at from Base

    # Relationships
    organization_owner = relationship("Organization", back_populates="owned_drones", foreign_keys=[organization_id])
    solo_owner_user = relationship("User", back_populates="owned_drones_solo", foreign_keys=[solo_owner_user_id])
    
    # Users assigned to this drone (M2M)
    assigned_users_through_link = relationship("UserDroneAssignment", back_populates="drone", lazy="selectin")

    flight_plans = relationship("FlightPlan", back_populates="drone", lazy="selectin")
    telemetry_logs = relationship("TelemetryLog", back_populates="drone", foreign_keys="[TelemetryLog.drone_id]", lazy="selectin") # All logs for this drone

    # Relationship for last_telemetry_id if you want to load the object
    # last_telemetry_point = relationship("TelemetryLog", foreign_keys=[last_telemetry_id])