from pydantic import BaseModel, Field
from typing import Optional, List, Annotated
from datetime import datetime
from app.schemas.user import UserRead # For admin_user and users list
# Shared properties
class OrganizationBase(BaseModel):
    name: str
    bin: Annotated[str, Field(min_length=12, max_length=12)]
    company_address: str
    city: str

# Properties to receive via API on creation (handled by /auth/register/organization-admin)
# class OrganizationCreate(OrganizationBase):
#     admin_id: Optional[int] = None # Set after admin user is created

# Properties to receive via API on update
class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    bin: Optional[str] = None
    company_address: Optional[str] = None
    city: Optional[str] = None
    new_admin_id: Optional[int] = None # To change the organization admin

# Properties to return to client
class OrganizationRead(OrganizationBase):
    id: int
    admin_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # admin_user: Optional[UserRead] = None # Can be added if needed

    class Config:
        from_attributes = True

class OrganizationReadWithDetails(OrganizationRead):
    # users: List[UserRead] = [] # Example: list of pilots
    # drones: List["DroneRead"] = [] # Example: list of drones
    admin_user: Optional[UserRead] = None
    # Add more details as needed based on endpoint III.2
    pass

# For OrganizationAdminRegisterResponse to resolve forward reference
from app.schemas.user import UserRead

class OrganizationCreate(OrganizationBase): # Ensure this schema is properly defined
    admin_id: Optional[int] = None

