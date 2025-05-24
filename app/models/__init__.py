from .user import User, UserRole  # UserRole enum needs to be accessible
from .organization import Organization
from .drone import Drone, DroneOwnerType, DroneStatus # Enums
from .user_drone_assignment import UserDroneAssignment
from .flight_plan import FlightPlan, FlightPlanStatus # Enum
from .waypoint import Waypoint
from .telemetry_log import TelemetryLog
from .restricted_zone import RestrictedZone, NFZGeometryType # Enum

# This helps Alembic find all models
from app.db.base_class import Base