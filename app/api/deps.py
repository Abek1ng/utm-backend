from typing import Generator, Optional, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.token import TokenPayload
from app.crud import user as crud_user

reusable_http_bearer = HTTPBearer(auto_error=True)

def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(reusable_http_bearer),
) -> User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("sub") is None:
            raise credentials_exception
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise credentials_exception

    user_id = token_data.sub
    if user_id is None:
        raise credentials_exception

    user = crud_user.get(db, id=int(user_id))
    if not user:
        raise credentials_exception
    if not crud_user.is_active(user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    return user

# Role-specific dependencies (unchanged except for get_current_user signature)
def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user

def get_current_authority_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.AUTHORITY_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges (Authority Admin required).",
        )
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

def get_current_organization_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ORGANIZATION_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges (Organization Admin required).",
        )
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization Admin not associated with an organization.")
    return current_user

def get_current_organization_member(current_user: User = Depends(get_current_user)) -> User:
    """For either Org Admin or Org Pilot"""
    if current_user.role not in [UserRole.ORGANIZATION_ADMIN, UserRole.ORGANIZATION_PILOT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user must be an Organization Admin or Organization Pilot.",
        )
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not associated with an organization.")
    return current_user

def get_current_pilot(current_user: User = Depends(get_current_user)) -> User:
    """For Solo Pilot or Organization Pilot"""
    if current_user.role not in [UserRole.SOLO_PILOT, UserRole.ORGANIZATION_PILOT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user must be a Pilot (Solo or Organization).",
        )
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

def verify_organization_access(
    organization_id_in_path: int,
    current_user: User = Depends(get_current_organization_admin)
) -> None:
    if current_user.organization_id != organization_id_in_path:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this organization's resources."
        )

def verify_user_in_organization(
    user_to_check_id: int,
    current_org_admin: User = Depends(get_current_organization_admin),
    db: Session = Depends(get_db)
) -> User:
    user = crud_user.get(db, id=user_to_check_id)
    if not user or user.organization_id != current_org_admin.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or does not belong to this organization."
        )
    return user