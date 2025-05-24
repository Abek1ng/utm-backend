from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.security import get_password_hash, verify_password
from app.models.user import UserRole

router = APIRouter()

@router.get("/me", response_model=schemas.UserRead)
def read_users_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=schemas.UserRead)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    if user_in.new_password:
        if not user_in.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is required to set a new password.",
            )
        if not verify_password(user_in.current_password, current_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")
    
    # Prevent users from changing their role or is_active status via this endpoint
    update_data = user_in.model_dump(exclude_unset=True)
    if "role" in update_data:
        del update_data["role"]
    if "is_active" in update_data:
        del update_data["is_active"]
    if "organization_id" in update_data: # Users cannot change their org this way
        del update_data["organization_id"]

    user = crud.user.update(db, db_obj=current_user, obj_in=update_data)
    return user

@router.get("/", response_model=List[schemas.UserRead])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    role: Optional[UserRole] = Query(None),
    organization_id: Optional[int] = Query(None),
    current_user: models.User = Depends(deps.get_current_authority_admin), # Admin Only
) -> Any:
    """
    Retrieve users (Admin only). Supports pagination and filtering.
    """
    users = crud.user.get_multi_users(
        db, skip=skip, limit=limit, role=role, organization_id=organization_id
    )
    return users

@router.get("/{user_id}", response_model=schemas.UserRead)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_authority_admin), # Admin Only
) -> Any:
    """
    Get a specific user by ID (Admin only).
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/{user_id}/status", response_model=schemas.UserRead)
def update_user_status(
    user_id: int,
    user_status_in: schemas.UserStatusUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_authority_admin), # Admin Only
) -> Any:
    """
    Activate or deactivate a user account (Admin only).
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Prevent deactivating the last authority admin if needed (more complex logic)
    # For now, allow deactivation.

    updated_user = crud.user.set_user_status(db, user_id=user_id, is_active=user_status_in.is_active)
    return updated_user

@router.delete("/{user_id}", response_model=schemas.UserRead, status_code=status.HTTP_200_OK) # Or 204 No Content
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_authority_admin), # Admin Only
) -> Any:
    """
    Soft delete a user (Admin only).
    """
    user_to_delete = crud.user.get(db, id=user_id)
    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user_to_delete.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admins cannot delete themselves.")

    # Consider implications: what happens to their drones, flights, etc.?
    # For MVP, soft delete marks them. Further logic might be needed to handle associated resources.
    
    # Soft delete the user
    deleted_user = crud.user.soft_remove(db, id=user_id)
    if not deleted_user: # Should not happen if get() found the user
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found during delete.")

    # To return 204 No Content, change response_model to None and return Response(status_code=204)
    return deleted_user