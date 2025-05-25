from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.flight_plan import FlightPlanStatus # Import enum
from app.schemas.waypoint import WaypointCreate, WaypointRead
from app.schemas.drone import DroneRead
from app.schemas.user import UserRead
from app.schemas.telemetry import TelemetryLogRead # Forward reference

# Shared properties
class FlightPlanBase(BaseModel):
    drone_id: int
    planned_departure_time: datetime
    planned_arrival_time: datetime
    notes: Optional[str] = None

# Properties to receive via API on creation
class FlightPlanCreate(FlightPlanBase):
    waypoints: List[WaypointCreate]

# Properties to receive via API on update (e.g., by pilot before approval)
# This is not explicitly in endpoints.md but could be useful
class FlightPlanUpdate(BaseModel):
    planned_departure_time: Optional[datetime] = None
    planned_arrival_time: Optional[datetime] = None
    notes: Optional[str] = None
    waypoints: Optional[List[WaypointCreate]] = None # Allow updating waypoints before approval

# Properties to return to client
class FlightPlanRead(FlightPlanBase):
    id: int
    user_id: int # Submitter
    organization_id: Optional[int] = None
    status: FlightPlanStatus
    actual_departure_time: Optional[datetime] = None
    actual_arrival_time: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    approved_by_organization_admin_id: Optional[int] = None
    approved_by_authority_admin_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    drone: Optional[DroneRead] = None  # Uncomment this line
    # submitter_user: Optional[UserRead] = None # Can be added

    class Config:
        from_attributes = True

class FlightPlanReadWithWaypoints(FlightPlanRead):
    waypoints: List[WaypointRead] = []
    drone: Optional[DroneRead] = None # Example of richer data
    submitter_user: Optional[UserRead] = None # Example

class FlightPlanStatusUpdate(BaseModel):
    status: FlightPlanStatus
    rejection_reason: Optional[str] = None

class FlightPlanCancel(BaseModel):
    reason: Optional[str] = None

class FlightPlanHistory(BaseModel):
    flight_plan_details: FlightPlanReadWithWaypoints
    # planned_waypoints: List[WaypointRead] # Already in FlightPlanReadWithWaypoints
    actual_telemetry: List["TelemetryLogRead"] # Forward reference

# Resolve forward reference
FlightPlanHistory.model_rebuild()