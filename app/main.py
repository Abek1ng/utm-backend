from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router as api_v1_router
from app.api.routers import telemetry
from app.core.config import settings
from app.db.session import SessionLocal

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS setup
if hasattr(settings, 'BACKEND_CORS_ORIGINS') and settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_v1_router, prefix=settings.API_V1_STR)
app.include_router(telemetry.router)

@app.on_event("startup")
async def startup_event():
    print("Application startup...")
    # Import here to avoid circular imports
    from app.db.init_db import init_db
    
    db = SessionLocal()
    try:
        init_db(db)
        print("Initial database setup complete.")
    except Exception as e:
        print(f"Error during initial DB setup: {e}")
    finally:
        db.close()
    print("UTM API started successfully.")

@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "message": f"Welcome to {settings.PROJECT_NAME}!"}