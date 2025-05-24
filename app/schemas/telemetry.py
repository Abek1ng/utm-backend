from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Shared properties for DB log
class TelemetryLogBase(BaseModel):
    timestamp: datetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude_m: float
    speed_mps: Optional[float] = Field(default=None, ge=0)
    heading_degrees: Optional[float] = Field(default=None, ge=0, le=360)
    status_message: Optional[str] = None

# Properties to receive for creating a log entry (usually internal)
class TelemetryLogCreate(TelemetryLogBase):
    flight_plan_id: Optional[int] = None # Can be null if not tied to a plan initially
    drone_id: int

# Properties to return to client for a log entry
class TelemetryLogRead(TelemetryLogBase):
    id: int # BigInt in DB, int here is fine for Pydantic
    flight_plan_id: Optional[int] = None
    drone_id: int
    created_at: datetime # from Base

    class Config:
        from_attributes = True

# Message format for WebSocket broadcast
class LiveTelemetryMessage(BaseModel):
    flight_id: int # flight_plan_id
    drone_id: int
    lat: float
    lon: float
    alt: float # altitude_m
    timestamp: datetime
    speed: Optional[float] = None # speed_mps
    heading: Optional[float] = None # heading_degrees
    # status: str # e.g., "ON_SCHEDULE/ALERT_NFZ/SIGNAL_LOST" -> from TelemetryLog.status_message
    status_message: Optional[str] = None