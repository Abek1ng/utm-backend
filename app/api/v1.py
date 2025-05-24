from fastapi import APIRouter

from app.api.routers import auth, users, organizations, drones, flights, nfz, utility
# Telemetry router (for WebSocket) is usually added in main.py directly to the app.
# If telemetry.py also had HTTP routes, it would be included here.

api_router = APIRouter()

# Include each router with its prefix
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(drones.router, prefix="/drones", tags=["Drones"])
api_router.include_router(flights.router, prefix="/flights", tags=["Flight Plans"])

# The nfz.py router contains routes starting with /admin/nfz and /nfz, so no prefix needed here.
api_router.include_router(nfz.router, tags=["No-Fly Zones (NFZ)"])

# The utility.py router contains routes like /weather and /remoteid/active-flights, so no prefix needed here.
api_router.include_router(utility.router, tags=["Utilities"])