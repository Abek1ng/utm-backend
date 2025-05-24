from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.models.user import UserRole
from app.models.drone import DroneOwnerType, DroneStatus

router = APIRouter()

@router.post("/", response_model=schemas.DroneRead, status_code=status.HTTP_201_CREATED)
def create_drone(
    *,
    db: Session = Depends(deps.get_db),
    drone_in: schemas.DroneCreate,
    current_user: models.User = Depends(deps.get_current_active_user), # SOLO_PILOT or ORGANIZATION_ADMIN
) -> Any:
    """
    Register a new drone. Ownership is determined by the authenticated user's role and input.
    """
    if current_user.role not in [UserRole.SOLO_PILOT, UserRole.ORGANIZATION_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Solo Pilots or Organization Admins can register drones.",
        )

    if crud.drone.get_by_serial_number(db, serial_number=drone_in.serial_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Drone with this serial number already exists.",
        )

    owner_type: DroneOwnerType
    solo_owner_user_id: Optional[int] = None
    organization_id_for_drone: Optional[int] = None # Renamed to avoid conflict

    if current_user.role == UserRole.SOLO_PILOT:
        if drone_in.organization_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo pilots cannot assign drones to an organization during creation.",
            )
        owner_type = DroneOwnerType.SOLO_PILOT
        solo_owner_user_id = current_user.id
    
    elif current_user.role == UserRole.ORGANIZATION_ADMIN:
        if drone_in.organization_id is not None and drone_in.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization admin can only register drones for their own organization.",
            )
        owner_type = DroneOwnerType.ORGANIZATION
        organization_id_for_drone = current_user.organization_id
        if not organization_id_for_drone: # Should not happen if role is ORG_ADMIN
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Org Admin has no organization ID.")
    else: # Should be caught by initial role check
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid role for drone creation.")

    db_drone = models.Drone(
        **drone_in.model_dump(exclude={"organization_id"}), # Exclude if it was just for validation
        owner_type=owner_type,
        solo_owner_user_id=solo_owner_user_id,
        organization_id=organization_id_for_drone,
        current_status=DroneStatus.IDLE # Default status
    )
    db.add(db_drone)
    db.commit()
    db.refresh(db_drone)
    return db_drone


@router.get("/my", response_model=List[schemas.DroneRead])
def list_my_drones(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: models.User = Depends(deps.get_current_active_user), # Any authenticated role
) -> Any:
    """
    List drones relevant to the authenticated user:
    - Solo Pilot: Lists drones where solo_owner_user_id matches.
    - Org Pilot: Lists drones assigned to them within their org.
    - Org Admin: Lists all drones within their organization.
    """
    is_org_admin = current_user.role == UserRole.ORGANIZATION_ADMIN
    
    drones = crud.drone.get_multi_drones_for_user(
        db, 
        user_id=current_user.id, 
        organization_id=current_user.organization_id, # Pass org_id for org users
        is_org_admin=is_org_admin,
        skip=skip, 
        limit=limit
    )
    return drones


@router.get("/admin/all", response_model=List[schemas.DroneRead])
def list_all_drones_admin(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    organization_id: Optional[int] = Query(None),
    status: Optional[DroneStatus] = Query(None),
    current_user: models.User = Depends(deps.get_current_authority_admin), # Authority Admin Only
) -> Any:
    """
    List ALL drones in the system (Authority Admin only).
    """
    drones = crud.drone.get_all_drones_admin(
        db, 
        skip=skip, 
        limit=limit, 
        organization_id=organization_id, 
        status=status
    )
    return drones


@router.get("/{drone_id}", response_model=schemas.DroneRead)
def read_drone_by_id(
    drone_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get details for a specific drone.
    Authorization: Authority Admin, or owner/assignee.
    """
    db_drone = crud.drone.get(db, id=drone_id)
    if not db_drone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drone not found")

    # Authorization check
    can_view = False
    if current_user.role == UserRole.AUTHORITY_ADMIN:
        can_view = True
    elif current_user.role == UserRole.SOLO_PILOT:
        if db_drone.owner_type == DroneOwnerType.SOLO_PILOT and db_drone.solo_owner_user_id == current_user.id:
            can_view = True
    elif current_user.role == UserRole.ORGANIZATION_ADMIN:
        if db_drone.owner_type == DroneOwnerType.ORGANIZATION and db_drone.organization_id == current_user.organization_id:
            can_view = True
    elif current_user.role == UserRole.ORGANIZATION_PILOT:
        if db_drone.owner_type == DroneOwnerType.ORGANIZATION and db_drone.organization_id == current_user.organization_id:
            # Check if pilot is assigned to this drone
            assignment = crud.user_drone_assignment.get_assignment(db, user_id=current_user.id, drone_id=drone_id)
            if assignment:
                can_view = True
    
    if not can_view:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this drone")
        
    return db_drone


@router.put("/{drone_id}", response_model=schemas.DroneRead)
def update_drone(
    drone_id: int,
    drone_in: schemas.DroneUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update drone details. Serial number typically not updatable.
    Authorization: Authority Admin, or owner (Solo Pilot or Org Admin for their org's drones).
    """
    db_drone = crud.drone.get(db, id=drone_id)
    if not db_drone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drone not found")

    can_update = False
    if current_user.role == UserRole.AUTHORITY_ADMIN:
        can_update = True
    elif current_user.role == UserRole.SOLO_PILOT:
        if db_drone.owner_type == DroneOwnerType.SOLO_PILOT and db_drone.solo_owner_user_id == current_user.id:
            can_update = True
    elif current_user.role == UserRole.ORGANIZATION_ADMIN:
        if db_drone.owner_type == DroneOwnerType.ORGANIZATION and db_drone.organization_id == current_user.organization_id:
            can_update = True
            
    if not can_update:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this drone")

    # Prevent serial number update if drone_in contains it and it's different
    update_data = drone_in.model_dump(exclude_unset=True)
    if "serial_number" in update_data and update_data["serial_number"] != db_drone.serial_number:
        # Typically, serial number is immutable after creation or only changeable by Authority Admin.
        if current_user.role != UserRole.AUTHORITY_ADMIN:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Serial number cannot be changed by this user.")
        # If Authority Admin is changing it, ensure it's not taken by another drone
        existing_drone_sn = crud.drone.get_by_serial_number(db, serial_number=update_data["serial_number"])
        if existing_drone_sn and existing_drone_sn.id != drone_id:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New serial number already exists.")
    elif "serial_number" in update_data: # If SN is same or not provided for update
        del update_data["serial_number"]


    updated_drone = crud.drone.update(db, db_obj=db_drone, obj_in=update_data)
    return updated_drone


@router.delete("/{drone_id}", response_model=schemas.DroneRead, status_code=status.HTTP_200_OK)
def delete_drone(
    drone_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Soft delete a drone.
    Authorization: Authority Admin, or owner.
    """
    db_drone = crud.drone.get(db, id=drone_id)
    if not db_drone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drone not found")

    can_delete = False
    if current_user.role == UserRole.AUTHORITY_ADMIN:
        can_delete = True
    elif current_user.role == UserRole.SOLO_PILOT:
        if db_drone.owner_type == DroneOwnerType.SOLO_PILOT and db_drone.solo_owner_user_id == current_user.id:
            can_delete = True
    elif current_user.role == UserRole.ORGANIZATION_ADMIN:
        if db_drone.owner_type == DroneOwnerType.ORGANIZATION and db_drone.organization_id == current_user.organization_id:
            can_delete = True
            
    if not can_delete:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this drone")

    # TODO: Consider implications: active flights, assignments?
    # For MVP, just soft delete.
    if db_drone.current_status == DroneStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete an active drone. Complete or cancel its flights first.")

    deleted_drone = crud.drone.soft_remove(db, id=drone_id)
    if not deleted_drone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drone not found during delete.")
    return deleted_drone


@router.post("/{drone_id}/assign-user", response_model=schemas.UserDroneAssignmentRead)
def assign_user_to_drone(
    drone_id: int,
    assignment_in: schemas.UserAssignToDrone,
    db: Session = Depends(deps.get_db),
    current_org_admin: models.User = Depends(deps.get_current_organization_admin),
) -> Any:
    """
    Assign an organization pilot to a drone within the same organization (Org Admin Only).
    """
    db_drone = crud.drone.get(db, id=drone_id)
    if not db_drone or db_drone.organization_id != current_org_admin.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drone not found or does not belong to your organization.")

    user_to_assign = crud.user.get(db, id=assignment_in.user_id_to_assign)
    if not user_to_assign or \
       user_to_assign.organization_id != current_org_admin.organization_id or \
       user_to_assign.role != UserRole.ORGANIZATION_PILOT: # Ensure assigning an Org Pilot
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User to assign not found, not an Organization Pilot, or does not belong to your organization."
        )
    if not user_to_assign.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot assign an inactive user.")

    existing_assignment = crud.user_drone_assignment.get_assignment(db, user_id=user_to_assign.id, drone_id=drone_id)
    if existing_assignment:
        # Return existing assignment or raise error if re-assignment is not desired
        # For now, return existing.
        return existing_assignment
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already assigned to this drone.")

    assignment = crud.user_drone_assignment.assign_user_to_drone(
        db, user_id=user_to_assign.id, drone_id=drone_id
    )
    return assignment


@router.delete("/{drone_id}/unassign-user", status_code=status.HTTP_204_NO_CONTENT)
def unassign_user_from_drone(
    drone_id: int,
    unassignment_in: schemas.UserUnassignFromDrone, # Body for consistency, though user_id could be path param
    db: Session = Depends(deps.get_db),
    current_org_admin: models.User = Depends(deps.get_current_organization_admin),
) -> None:
    """
    Unassign an organization pilot from a drone (Org Admin Only).
    """
    db_drone = crud.drone.get(db, id=drone_id)
    if not db_drone or db_drone.organization_id != current_org_admin.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drone not found or does not belong to your organization.")

    user_to_unassign_id = unassignment_in.user_id_to_unassign
    user_to_unassign = crud.user.get(db, id=user_to_unassign_id)
    if not user_to_unassign or user_to_unassign.organization_id != current_org_admin.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User to unassign not found or does not belong to your organization."
        )

    assignment = crud.user_drone_assignment.get_assignment(db, user_id=user_to_unassign_id, drone_id=drone_id)
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not assigned to this drone.")

    crud.user_drone_assignment.unassign_user_from_drone(db, user_id=user_to_unassign_id, drone_id=drone_id)
    return None # FastAPI will return 204 No Content