from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Shared properties
class WaypointBase(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude_m: float = Field(..., gt=0) # Altitude above ground level
    sequence_order: int = Field(..., ge=0)

# Properties to receive via API on creation
class WaypointCreate(WaypointBase):
    pass

# Properties to receive via API on update (if waypoints are updatable post-creation)
class WaypointUpdate(WaypointBase):
    pass

# Properties to return to client
class WaypointRead(WaypointBase):
    id: int
    flight_plan_id: int
    # created_at: datetime # from Base, if needed
    # updated_at: datetime # from Base, if needed

    class Config:
        from_attributes = True