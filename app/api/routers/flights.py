from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.models.user import UserRole
from app.models.flight_plan import FlightPlanStatus
from app.services import flight_service # Use the service instance

router = APIRouter()

@router.post("/", response_model=schemas.FlightPlanRead, status_code=status.HTTP_201_CREATED)
def submit_new_flight_plan(
    *,
    db: Session = Depends(deps.get_db),
    flight_plan_in: schemas.FlightPlanCreate,
    current_user: models.User = Depends(deps.get_current_pilot), # SOLO_PILOT or ORGANIZATION_PILOT
) -> Any:
    """
    Submit a new flight plan.
    Backend sets initial status based on submitter's role. NFZ pre-check performed.
    """
    try:
        created_flight_plan = flight_service.submit_flight_plan(
            db, flight_plan_in=flight_plan_in, submitter=current_user
        )
        # Eager load waypoints for the response
        db.refresh(created_flight_plan, attribute_names=['waypoints'])
        return created_flight_plan
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e: # Catch other unexpected errors
        print(f"Error processing flight plan: {e}")  # Log the error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing flight plan.")


@router.get("/my", response_model=List[schemas.FlightPlanRead])
def list_my_flight_plans(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    status_filter: Optional[FlightPlanStatus] = Query(None, alias="status"), # Use alias for query param
    current_user: models.User = Depends(deps.get_current_pilot),
) -> Any:
    """
    List flight plans submitted by the currently authenticated user (Pilot).
    """
    flight_plans = crud.flight_plan.get_multi_for_user(
        db, user_id=current_user.id, skip=skip, limit=limit, status=status_filter
    )
    return flight_plans


@router.get("/organization", response_model=List[schemas.FlightPlanRead])
def list_organization_flight_plans(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    status_filter: Optional[FlightPlanStatus] = Query(None, alias="status"),
    user_id_filter: Optional[int] = Query(None, alias="user_id"),
    current_org_admin: models.User = Depends(deps.get_current_organization_admin),
) -> Any:
    """
    List all flight plans associated with the Organization Admin's organization.
    """
    if not current_org_admin.organization_id: # Should be guaranteed by dependency
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Admin not linked to an organization.")
        
    flight_plans = crud.flight_plan.get_multi_for_organization(
        db, 
        organization_id=current_org_admin.organization_id, 
        skip=skip, 
        limit=limit, 
        status=status_filter,
        user_id=user_id_filter
    )
    return flight_plans


@router.get("/admin/all", response_model=List[schemas.FlightPlanRead])
def list_all_flight_plans_admin(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    status_filter: Optional[FlightPlanStatus] = Query(None, alias="status"),
    organization_id_filter: Optional[int] = Query(None, alias="organization_id"),
    user_id_filter: Optional[int] = Query(None, alias="user_id"),
    current_authority_admin: models.User = Depends(deps.get_current_authority_admin),
) -> Any:
    """
    List ALL flight plans in the system (Authority Admin Only).
    """
    flight_plans = crud.flight_plan.get_all_flight_plans_admin(
        db,
        skip=skip,
        limit=limit,
        status=status_filter,
        organization_id=organization_id_filter,
        user_id=user_id_filter
    )
    return flight_plans


@router.get("/{flight_plan_id}", response_model=schemas.FlightPlanReadWithWaypoints)
def read_flight_plan_by_id(
    flight_plan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get details of a specific flight plan, including waypoints.
    Authorization: Authority Admin, submitter, or relevant Org Admin.
    """
    db_flight_plan = crud.flight_plan.get_flight_plan_with_details(db, id=flight_plan_id)
    if not db_flight_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flight plan not found")

    can_view = False
    if current_user.role == UserRole.AUTHORITY_ADMIN:
        can_view = True
    elif current_user.id == db_flight_plan.user_id: # Submitter
        can_view = True
    elif current_user.role == UserRole.ORGANIZATION_ADMIN and \
         db_flight_plan.organization_id == current_user.organization_id:
        can_view = True
    
    if not can_view:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this flight plan")
        
    return db_flight_plan


@router.put("/{flight_plan_id}/status", response_model=schemas.FlightPlanRead)
def update_flight_plan_status_endpoint( # Renamed to avoid conflict with service method
    flight_plan_id: int,
    status_update_in: schemas.FlightPlanStatusUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user), # Org Admin or Authority Admin
) -> Any:
    """
    Update the status of a flight plan.
    - Org Admin: Can change PENDING_ORG_APPROVAL to PENDING_AUTHORITY_APPROVAL or REJECTED_BY_ORG.
    - Authority Admin: Can change PENDING_AUTHORITY_APPROVAL to APPROVED or REJECTED_BY_AUTHORITY.
    """
    if current_user.role not in [UserRole.ORGANIZATION_ADMIN, UserRole.AUTHORITY_ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authorized to update flight plan status.")

    try:
        updated_flight_plan = flight_service.update_flight_plan_status(
            db,
            flight_plan_id=flight_plan_id,
            new_status=status_update_in.status,
            actor=current_user,
            rejection_reason=status_update_in.rejection_reason
        )
        db.refresh(updated_flight_plan, attribute_names=['waypoints']) # Ensure waypoints are loaded if schema needs them
        return updated_flight_plan
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log error e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating flight plan status.")


@router.put("/{flight_plan_id}/start", response_model=schemas.FlightPlanRead)
def start_flight_endpoint( # Renamed
    flight_plan_id: int,
    db: Session = Depends(deps.get_db),
    current_pilot: models.User = Depends(deps.get_current_pilot), # Submitting Pilot
) -> Any:
    """
    Pilot starts an APPROVED flight. Sets status to ACTIVE, triggers telemetry simulation.
    """
    try:
        started_flight_plan = flight_service.start_flight(
            db, flight_plan_id=flight_plan_id, pilot=current_pilot
        )
        db.refresh(started_flight_plan, attribute_names=['waypoints'])
        return started_flight_plan
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log error e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error starting flight.")


@router.put("/{flight_plan_id}/cancel", response_model=schemas.FlightPlanRead)
def cancel_flight_endpoint( # Renamed
    flight_plan_id: int,
    cancel_in: schemas.FlightPlanCancel,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user), # Pilot, Org Admin, or Auth Admin
) -> Any:
    """
    Pilot or Admin cancels a flight.
    """
    if current_user.role not in [UserRole.SOLO_PILOT, UserRole.ORGANIZATION_PILOT, UserRole.ORGANIZATION_ADMIN, UserRole.AUTHORITY_ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authorized to cancel flight plans.")
    
    try:
        cancelled_flight_plan = flight_service.cancel_flight(
            db,
            flight_plan_id=flight_plan_id,
            actor=current_user,
            reason=cancel_in.reason
        )
        db.refresh(cancelled_flight_plan, attribute_names=['waypoints'])
        return cancelled_flight_plan
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log error e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error cancelling flight.")


@router.get("/{flight_plan_id}/history", response_model=schemas.FlightPlanHistory)
def get_flight_plan_history(
    flight_plan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user), # Auth Admin, submitter, relevant Org Admin
) -> Any:
    """
    Get the planned waypoints and all recorded telemetry logs for a completed or active flight.
    """
    db_flight_plan = crud.flight_plan.get_flight_history(db, flight_plan_id=flight_plan_id) # This method loads waypoints and telemetry
    
    if not db_flight_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flight plan not found")

    can_view = False
    if current_user.role == UserRole.AUTHORITY_ADMIN:
        can_view = True
    elif current_user.id == db_flight_plan.user_id: # Submitter
        can_view = True
    elif current_user.role == UserRole.ORGANIZATION_ADMIN and \
         db_flight_plan.organization_id == current_user.organization_id:
        can_view = True
    
    if not can_view:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this flight plan history")

    # Ensure all necessary data is loaded for FlightPlanReadWithWaypoints
    # The get_flight_history CRUD method should handle this with selectinload
    
    # Convert to FlightPlanReadWithWaypoints
    flight_plan_details_schema = schemas.FlightPlanReadWithWaypoints.model_validate(db_flight_plan)
    
    # Telemetry logs are already loaded by crud.flight_plan.get_flight_history
    actual_telemetry_schema = [schemas.TelemetryLogRead.model_validate(log) for log in db_flight_plan.telemetry_logs]

    return schemas.FlightPlanHistory(
        flight_plan_details=flight_plan_details_schema,
        actual_telemetry=actual_telemetry_schema
    )