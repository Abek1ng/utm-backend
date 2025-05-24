from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.models.user import UserRole

router = APIRouter()

# --- Endpoints under /admin/nfz (Authority Admin Only) ---

@router.post("/admin/nfz/", response_model=schemas.RestrictedZoneRead, status_code=status.HTTP_201_CREATED)
def create_nfz(
    *,
    db: Session = Depends(deps.get_db),
    nfz_in: schemas.RestrictedZoneCreate,
    current_admin: models.User = Depends(deps.get_current_authority_admin),
) -> Any:
    """
    Create a new No-Fly Zone (Authority Admin only).
    """
    # Check for duplicate name if names should be unique
    existing_nfz = crud.restricted_zone.get_by_name(db, name=nfz_in.name)
    if existing_nfz:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A No-Fly Zone with the name '{nfz_in.name}' already exists.",
        )
    
    # TODO: Add validation for nfz_in.definition_json based on nfz_in.geometry_type
    # e.g., circle needs center_lat, center_lon, radius_m
    # polygon needs coordinates: List[List[List[float]]]

    db_nfz = models.RestrictedZone(
        **nfz_in.model_dump(),
        created_by_authority_id=current_admin.id,
        is_active=True # Default to active on creation
    )
    db.add(db_nfz)
    db.commit()
    db.refresh(db_nfz)
    return db_nfz


@router.get("/admin/nfz/", response_model=List[schemas.RestrictedZoneRead])
def list_nfzs_admin(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    is_active: Optional[bool] = Query(None),
    current_admin: models.User = Depends(deps.get_current_authority_admin),
) -> Any:
    """
    List all No-Fly Zones (Authority Admin view, can see inactive/deleted).
    """
    # include_deleted=True could be an option if admin needs to see soft-deleted ones
    nfzs = crud.restricted_zone.get_multi_zones_admin(
        db, skip=skip, limit=limit, is_active=is_active, include_deleted=False # Set to True to see soft-deleted
    )
    return nfzs


@router.get("/admin/nfz/{zone_id}", response_model=schemas.RestrictedZoneRead)
def get_nfz_by_id_admin(
    zone_id: int,
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_authority_admin),
) -> Any:
    """
    Get details of a specific NFZ (Authority Admin only).
    """
    # include_deleted=True if admin should be able to fetch soft-deleted NFZ by ID
    nfz = crud.restricted_zone.get(db, id=zone_id, include_deleted=False) 
    if not nfz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No-Fly Zone not found")
    return nfz


@router.put("/admin/nfz/{zone_id}", response_model=schemas.RestrictedZoneRead)
def update_nfz(
    zone_id: int,
    nfz_in: schemas.RestrictedZoneUpdate,
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_authority_admin),
) -> Any:
    """
    Update an existing NFZ (Authority Admin only).
    """
    db_nfz = crud.restricted_zone.get(db, id=zone_id)
    if not db_nfz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No-Fly Zone not found")

    update_data = nfz_in.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] != db_nfz.name:
        existing_nfz_name = crud.restricted_zone.get_by_name(db, name=update_data["name"])
        if existing_nfz_name and existing_nfz_name.id != zone_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NFZ name already taken.")

    # TODO: Add validation for definition_json if geometry_type is also changing or if definition_json is updated.

    updated_nfz = crud.restricted_zone.update(db, db_obj=db_nfz, obj_in=update_data)
    return updated_nfz


@router.delete("/admin/nfz/{zone_id}", response_model=schemas.RestrictedZoneRead, status_code=status.HTTP_200_OK)
def delete_nfz(
    zone_id: int,
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_authority_admin),
) -> Any:
    """
    Soft delete an NFZ (Authority Admin only).
    """
    db_nfz = crud.restricted_zone.get(db, id=zone_id)
    if not db_nfz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No-Fly Zone not found")

    # Soft delete also marks it as inactive
    deleted_nfz = crud.restricted_zone.soft_remove(db, id=zone_id)
    if not deleted_nfz: # Should not happen if get() found it
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NFZ not found during delete.")
    
    if deleted_nfz.is_active: # Ensure it's marked inactive
        deleted_nfz.is_active = False
        db.add(deleted_nfz)
        db.commit()
        db.refresh(deleted_nfz)
        
    return deleted_nfz


# --- Public/Authenticated Read Endpoint for NFZ map display ---
@router.get("/nfz/", response_model=List[schemas.RestrictedZoneRead])
def list_active_nfzs_for_map(
    db: Session = Depends(deps.get_db),
    # No specific authentication for this, public or any authenticated user
    # current_user: models.User = Depends(deps.get_current_active_user), # If auth required
) -> Any:
    """
    List active No-Fly Zones for map display (Public or Authenticated).
    """
    active_nfzs = crud.restricted_zone.get_all_active_zones(db)
    return active_nfzs