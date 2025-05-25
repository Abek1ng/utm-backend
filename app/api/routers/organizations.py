from app.crud.user_drone_assignment import user_drone_assignment
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from pydantic import BaseModel
from typing import List, Optional, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.api import deps
from app.models.user import UserRole

router = APIRouter()

class PilotDroneResponse(BaseModel):
    pilot: schemas.UserRead
    assigned_drone: Optional[schemas.DroneRead] = None

    class Config:
        orm_mode = True

@router.get(
    "/me/user-drone",
    response_model=List[PilotDroneResponse],
    status_code=status.HTTP_200_OK,
    summary="List pilots in your org + their assigned drones"
)
def list_my_org_user_drones(
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_organization_admin),
) -> Any:
    """
    For the Org-Admin in your token, return every Organization-Pilot
    in that same org, along with their assigned drone (if any).
    """
    org_id = current_admin.organization_id  # guaranteed by Depends

    # 1) grab all pilots in this org
    pilots = crud.user.get_multi_users(
        db,
        organization_id=org_id,
        role=UserRole.ORGANIZATION_PILOT,
        skip=0,
        limit=1000,
    )

    # 2) for each pilot, see if there's an assignment record
    out: List[PilotDroneResponse] = []
    for p in pilots:
        assigns = user_drone_assignment.get_multi(db, user_id=p.id)
        if assigns:
            # take the first assignment
            drone = crud.drone.get(db, id=assigns[0].drone_id)
        else:
            drone = None

        out.append(PilotDroneResponse(pilot=p, assigned_drone=drone))

    return out

@router.get("/", response_model=List[schemas.OrganizationRead])
def read_organizations(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    # Authorization: Primarily for Authority Admin.
    # Org Admins might see their own if they forgot ID, but /users/me is better.
    # If this endpoint is for pilot registration selection, it might need broader access.
    # For now, restrict to Authority Admin as per endpoint spec.
    current_user: models.User = Depends(deps.get_current_authority_admin),
) -> Any:
    """
    List all organizations (Authority Admin only). Supports pagination.
    """
    organizations = crud.organization.get_multi_organizations(db, skip=skip, limit=limit)
    return organizations

@router.get("/{organization_id}", response_model=schemas.OrganizationReadWithDetails)
def read_organization_by_id(
    organization_id: int = Path(..., title="The ID of the organization to get"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get details for a specific organization.
    Authorization: Authority Admin, or Organization Admin (if organization_id matches their org).
    """
    org = crud.organization.get(db, id=organization_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    if current_user.role == UserRole.AUTHORITY_ADMIN:
        pass # Authority admin can see any organization
    elif current_user.role == UserRole.ORGANIZATION_ADMIN:
        if current_user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this organization's details.",
            )
    else: # Other roles (e.g., pilots) generally shouldn't access this directly unless specified
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access organization details.",
        )
    
    # Populate OrganizationReadWithDetails if needed
    # For example, load admin_user details
    admin_user_details = None
    if org.admin_id:
        admin_user_details = crud.user.get(db, id=org.admin_id)

    # This is a basic example; you might want to load lists of users, drones etc.
    # into OrganizationReadWithDetails based on further requirements.
    return schemas.OrganizationReadWithDetails(
        **schemas.OrganizationRead.model_validate(org).model_dump(),
        admin_user=admin_user_details if admin_user_details else None
        # users=[], drones=[] # Populate these if your schema expects them
    )


@router.put("/{organization_id}", response_model=schemas.OrganizationRead)
def update_organization(
    organization_id: int,
    org_in: schemas.OrganizationUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update organization details (Org Admin for their own org, or Authority Admin).
    """
    org = crud.organization.get(db, id=organization_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    can_update_all_fields = False
    if current_user.role == UserRole.AUTHORITY_ADMIN:
        can_update_all_fields = True
    elif current_user.role == UserRole.ORGANIZATION_ADMIN:
        if current_user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this organization.",
            )
        # Org Admin can update limited fields. `new_admin_id` might be restricted or require special handling.
        if org_in.new_admin_id and org_in.new_admin_id != org.admin_id:
             # Check if the new admin belongs to this organization and has ORG_ADMIN role
            new_admin_user = crud.user.get(db, id=org_in.new_admin_id)
            if not new_admin_user or \
               new_admin_user.organization_id != organization_id or \
               new_admin_user.role != UserRole.ORGANIZATION_ADMIN:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid new admin ID or new admin not suitable.")
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update organization details.",
        )

    update_data = org_in.model_dump(exclude_unset=True)
    
    # If Org Admin is updating and not all fields are allowed, filter update_data
    if not can_update_all_fields and current_user.role == UserRole.ORGANIZATION_ADMIN:
        allowed_fields_for_org_admin = {"name", "company_address", "city"} # Example
        # BIN is usually immutable or changed by Authority. `new_admin_id` handled above.
        update_data = {k: v for k, v in update_data.items() if k in allowed_fields_for_org_admin or k == "new_admin_id"}


    # Check for uniqueness if name or BIN is being changed
    if "name" in update_data and update_data["name"] != org.name:
        existing_org_name = crud.organization.get_by_name(db, name=update_data["name"])
        if existing_org_name and existing_org_name.id != organization_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization name already taken.")
    
    if "bin" in update_data and update_data["bin"] != org.bin:
        if not can_update_all_fields: # Org admins typically cannot change BIN
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization Admin cannot change BIN.")
        existing_org_bin = crud.organization.get_by_bin(db, bin_val=update_data["bin"])
        if existing_org_bin and existing_org_bin.id != organization_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization BIN already in use.")

    if "new_admin_id" in update_data:
        org.admin_id = update_data.pop("new_admin_id") # Update admin_id directly on model

    updated_org = crud.organization.update(db, db_obj=org, obj_in=update_data)
    return updated_org


@router.delete("/{organization_id}", response_model=schemas.OrganizationRead, status_code=status.HTTP_200_OK)
def delete_organization(
    organization_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_authority_admin), # Authority Admin Only
) -> Any:
    """
    Soft delete an organization (Authority Admin only).
    Cascading implications (users, drones, flights) need careful consideration for a full implementation.
    MVP: Mark org as deleted, prevent new activity.
    """
    org_to_delete = crud.organization.get(db, id=organization_id)
    if not org_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # TODO: Implement cascading logic if required (e.g., deactivate users, drones of this org)
    # For MVP, just soft delete the organization.
    # It might also be good to disassociate the admin_id or mark users as inactive.
    # For now, simple soft delete.
    
    # Example: Deactivate all users of this organization
    # users_in_org = crud.user.get_multi_users(db, organization_id=organization_id, limit=1000) # Get all
    # for user_in_org in users_in_org:
    #     crud.user.set_user_status(db, user_id=user_in_org.id, is_active=False)

    deleted_org = crud.organization.soft_remove(db, id=organization_id)
    if not deleted_org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found during delete.")
    
    # Mark organization as inactive as well upon soft delete
    deleted_org.is_active = False
    db.add(deleted_org)
    db.commit()
    db.refresh(deleted_org)

    return deleted_org


@router.get("/{organization_id}/users", response_model=List[schemas.UserRead])
def list_organization_users(
    organization_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all users belonging to a specific organization.
    Authorization: Authority Admin, or Organization Admin (if organization_id matches their org).
    """
    org = crud.organization.get(db, id=organization_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    if current_user.role == UserRole.AUTHORITY_ADMIN:
        pass
    elif current_user.role == UserRole.ORGANIZATION_ADMIN:
        if current_user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to list users for this organization.",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to list organization users.",
        )

    users = crud.user.get_multi_users(db, organization_id=organization_id, skip=skip, limit=limit)
    return users


@router.get("/{organization_id}/drones", response_model=List[schemas.DroneRead])
def list_organization_drones(
    organization_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all drones belonging to a specific organization.
    Authorization: Authority Admin, or Organization Admin (if organization_id matches their org).
    """
    org = crud.organization.get(db, id=organization_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    if current_user.role == UserRole.AUTHORITY_ADMIN:
        pass
    elif current_user.role == UserRole.ORGANIZATION_ADMIN:
        if current_user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to list drones for this organization.",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to list organization drones.",
        )

    drones = crud.drone.get_multi_drones_for_organization(
        db, organization_id=organization_id, skip=skip, limit=limit
    )
    return drones