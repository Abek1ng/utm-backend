from typing import List, Any, Optional
import asyncio
from app.crud import telemetry_log as crud_telemetry_log
from app.models.drone import DroneOwnerType # For Remote ID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.models.user import UserRole
from app.models.flight_plan import FlightPlanStatus
from app.crud import flight_plan as crud_flight_plan
from app.crud import drone as crud_drone # For Remote ID

router = APIRouter()

@router.get("/weather", response_model=schemas.WeatherInfo)
async def get_weather_info(
    lat: float = Query(..., description="Latitude for weather forecast"),
    lon: float = Query(..., description="Longitude for weather forecast"),
    current_user: models.User = Depends(deps.get_current_active_user), # Authenticated users
) -> Any:
    """
    Get weather information for a given location. (Placeholder - requires external API integration)
    """
    # This is a placeholder. You would integrate with a real weather API here.
    # Example: OpenWeatherMap, WeatherAPI.com, etc.
    # For now, returning dummy data.
    from datetime import datetime, timezone
    import random

    # Simulate API call
    await asyncio.sleep(0.1) # Simulate network latency

    return schemas.WeatherInfo(
        lat=lat,
        lon=lon,
        temp=random.uniform(10, 30), # Celsius
        wind_speed=random.uniform(1, 10), # m/s
        wind_direction=random.uniform(0, 359), # degrees
        conditions_summary=random.choice(["Clear", "Cloudy", "Light Rain", "Sunny"]),
        timestamp=datetime.now(timezone.utc)
    )

@router.get("/remoteid/active-flights", response_model=List[schemas.RemoteIdBroadcast])
async def get_active_flights_remote_id(
    db: Session = Depends(deps.get_db),
    # Authorization: Public or AUTHORITY_ADMIN as per spec
    # For now, let's make it require Authority Admin to align with potential sensitivity
    # If public, remove current_user dependency or use an optional one.
    current_user: Optional[models.User] = Depends(deps.get_current_active_user), # Make it optional for public access
) -> Any:
    """
    Get a list of currently active flights with their emulated Remote ID data.
    (Placeholder - requires fetching live telemetry and formatting)
    """
    # If strict Authority Admin access:
    # current_admin: models.User = Depends(deps.get_current_authority_admin)

    # If public, but want to log if an admin accesses:
    if current_user and current_user.role == UserRole.AUTHORITY_ADMIN:
        print("Authority Admin accessed Remote ID endpoint.")
    # If public access is not desired without any auth, make current_user non-optional.


    # 1. Get all active flight plans
    active_flight_plans = crud_flight_plan.get_all_flight_plans_admin(
        db, status=FlightPlanStatus.ACTIVE, limit=1000 # Get all active
    )

    remote_id_broadcasts: List[schemas.RemoteIdBroadcast] = []

    for fp in active_flight_plans:
        # 2. For each active flight, get its latest telemetry
        latest_telemetry = crud_telemetry_log.get_latest_log_for_drone(db, drone_id=fp.drone_id)
        db_drone = crud_drone.get(db, id=fp.drone_id) # Get drone for serial number

        if latest_telemetry and db_drone:
            operator_id = None
            if db_drone.owner_type == DroneOwnerType.SOLO_PILOT and db_drone.solo_owner_user_id:
                operator_id = f"SOLO-{db_drone.solo_owner_user_id}" # Example proxy
            elif db_drone.owner_type == DroneOwnerType.ORGANIZATION and db_drone.organization_id:
                operator_id = f"ORG-{db_drone.organization_id}" # Example proxy

            broadcast = schemas.RemoteIdBroadcast(
                drone_serial_number=db_drone.serial_number,
                current_lat=latest_telemetry.latitude,
                current_lon=latest_telemetry.longitude,
                current_alt=latest_telemetry.altitude_m,
                timestamp=latest_telemetry.timestamp,
                operator_id_proxy=operator_id,
                # control_station_location_proxy: Placeholder, would need pilot's location if available
            )
            remote_id_broadcasts.append(broadcast)
            
    return remote_id_broadcasts

# Need to import asyncio for the weather endpoint
