# This file can be empty or used to import services for easier access
from .flight_service import FlightService
from .nfz_service import NFZService
from .telemetry_service import TelemetryService, ConnectionManager

flight_service = FlightService()
nfz_service = NFZService()
telemetry_service = TelemetryService() # The instance for simulation
connection_manager = ConnectionManager() # The instance for WebSocket connections