from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from app.models.restricted_zone import NFZGeometryType # Import enum

# Shared properties
class RestrictedZoneBase(BaseModel):
    name: str
    description: Optional[str] = None
    geometry_type: NFZGeometryType
    definition_json: Dict[str, Any] # e.g., {"center_lat": ..., "radius_m": ...} or {"coordinates": ...}
    min_altitude_m: Optional[float] = Field(default=None, ge=0)
    max_altitude_m: Optional[float] = Field(default=None, ge=0) # Could be validated against min_alt

# Properties to receive via API on creation
class RestrictedZoneCreate(RestrictedZoneBase):
    pass

# Properties to receive via API on update
class RestrictedZoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    geometry_type: Optional[NFZGeometryType] = None
    definition_json: Optional[Dict[str, Any]] = None
    min_altitude_m: Optional[float] = None
    max_altitude_m: Optional[float] = None
    is_active: Optional[bool] = None

# Properties to return to client
class RestrictedZoneRead(RestrictedZoneBase):
    id: int
    is_active: bool
    created_by_authority_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True