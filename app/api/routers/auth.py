from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import UserRole # For setting roles

router = APIRouter()

@router.post("/register/solo-pilot", response_model=schemas.UserRead)
def register_solo_pilot(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreateSolo,
) -> Any:
    """
    Registers a new independent (solo) pilot.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    if user_in.iin and crud.user.get_by_iin(db, iin=user_in.iin):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this IIN already exists in the system.",
        )
    
    user_create_internal = schemas.UserCreate(
        **user_in.model_dump(),
        role=UserRole.SOLO_PILOT, # Set role
        # password field is already in UserCreateSolo and thus in user_in
    )
    user = crud.user.create(db, obj_in=user_create_internal)
    return user

@router.post("/register/organization-admin", response_model=schemas.OrganizationAdminRegisterResponse)
def register_organization_admin(
    *,
    db: Session = Depends(deps.get_db),
    org_admin_in: schemas.OrganizationAdminRegister,
) -> Any:
    """
    Registers a new organization AND its primary admin user. Transactional.
    """
    # Check if admin email or IIN already exists
    admin_user = crud.user.get_by_email(db, email=org_admin_in.admin_email)
    if admin_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An admin with this email already exists.",
        )
    if org_admin_in.admin_iin and crud.user.get_by_iin(db, iin=org_admin_in.admin_iin):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An admin with this IIN already exists.",
        )

    # Check if organization name or BIN already exists
    if crud.organization.get_by_name(db, name=org_admin_in.org_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An organization with this name already exists.",
        )
    if crud.organization.get_by_bin(db, bin_val=org_admin_in.bin): # Use bin_val to avoid conflict
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An organization with this BIN already exists.",
        )

    try:
        # Create Admin User first
        admin_user_data = schemas.UserCreate(
            email=org_admin_in.admin_email,
            password=org_admin_in.admin_password,
            full_name=org_admin_in.admin_full_name,
            phone_number=org_admin_in.admin_phone_number,
            iin=org_admin_in.admin_iin,
            role=UserRole.ORGANIZATION_ADMIN,
            # organization_id will be set after org is created and admin is linked
        )
        created_admin_user = crud.user.create(db, obj_in=admin_user_data)

        # Create Organization
        org_data = schemas.OrganizationCreate( # Assuming OrganizationCreate schema exists
            name=org_admin_in.org_name,
            bin=org_admin_in.bin,
            company_address=org_admin_in.company_address,
            city=org_admin_in.city,
            admin_id=created_admin_user.id # Link admin to organization
        )
        created_org = crud.organization.create(db, obj_in=org_data)

        # Link admin user to the organization
        created_admin_user.organization_id = created_org.id
        db.add(created_admin_user)
        db.commit()
        db.refresh(created_admin_user)
        db.refresh(created_org) # Refresh org to get admin_user relationship if defined

        return {"organization": created_org, "admin_user": created_admin_user}

    except Exception as e:
        db.rollback() # Rollback in case of any error during the transaction
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register organization admin: {str(e)}"
        )


@router.post("/register/organization-pilot", response_model=schemas.UserRead)
def register_organization_pilot(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreateOrganizationPilot,
) -> Any:
    """
    Registers a new pilot who will be a member of an existing organization.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists.",
        )
    if user_in.iin and crud.user.get_by_iin(db, iin=user_in.iin):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this IIN already exists.",
        )
    
    organization = crud.organization.get(db, id=user_in.organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )
    if not organization.is_active:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot register pilot for an inactive organization.",
        )

    user_create_internal = schemas.UserCreate(
        **user_in.model_dump(exclude={"organization_id"}), # Exclude org_id as it's passed separately
        role=UserRole.ORGANIZATION_PILOT,
        organization_id=user_in.organization_id, # Set organization_id
    )
    user = crud.user.create(db, obj_in=user_create_internal)
    return user


@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Username is the email.
    """
    user = crud.user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}