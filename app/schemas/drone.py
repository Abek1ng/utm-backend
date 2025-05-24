from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.drone import DroneOwnerType, DroneStatus # Import enums

# Shared properties
class DroneBase(BaseModel):
    brand: str
    model: str
    serial_number: str

# Properties to receive via API on creation
class DroneCreate(DroneBase):
    # Ownership is determined by authenticated user's role and this optional field
    organization_id: Optional[int] = None # If Org Admin registers for their org

# Properties to receive via API on update
class DroneUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    # serial_number: Optional[str] = None # Typically not updatable
    current_status: Optional[DroneStatus] = None

# Properties to return to client
class DroneRead(DroneBase):
    id: int
    owner_type: DroneOwnerType
    organization_id: Optional[int] = None
    solo_owner_user_id: Optional[int] = None
    current_status: DroneStatus
    last_seen_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserAssignToDrone(BaseModel):
    user_id_to_assign: int

class UserUnassignFromDrone(BaseModel):
    user_id_to_unassign: int

class UserDroneAssignmentRead(BaseModel):
    user_id: int
    drone_id: int
    assigned_at: datetime # This comes from Base.created_at in our model compromise

    class Config:
        from_attributes = True