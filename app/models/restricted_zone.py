import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum, Float, JSON, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class NFZGeometryType(str, enum.Enum):
    CIRCLE = "CIRCLE"
    POLYGON = "POLYGON"

class RestrictedZone(Base):
    __tablename__ = "restricted_zones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True) # VARCHAR(1000) in schema
    geometry_type = Column(SAEnum(NFZGeometryType), nullable=False)
    definition_json = Column(JSON, nullable=False) # Stores center/radius for circle, or coordinates for polygon
    min_altitude_m = Column(Float, nullable=True)
    max_altitude_m = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_by_authority_id = Column(Integer, ForeignKey("users.id", name="fk_restricted_zone_creator_id"), nullable=False)
    # created_at, updated_at, deleted_at from Base

    # Relationships
    creator_authority = relationship("User", back_populates="created_restricted_zones", foreign_keys=[created_by_authority_id])