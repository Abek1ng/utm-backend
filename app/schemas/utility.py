from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class WeatherInfo(BaseModel):
    # Example fields, adjust based on actual weather API response
    lat: float
    lon: float
    temp: float # Celsius
    wind_speed: float # m/s
    wind_direction: float # degrees
    conditions_summary: str
    timestamp: datetime

class RemoteIdBroadcast(BaseModel):
    drone_serial_number: str
    current_lat: float
    current_lon: float # Corrected from lon
    current_alt: float # Corrected from alt
    timestamp: datetime
    operator_id_proxy: Optional[str] = None # e.g., masked user ID or org ID
    control_station_location_proxy: Optional[Dict[str, float]] = None # e.g., {"lat": ..., "lon": ...}