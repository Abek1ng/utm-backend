import app
from pydantic import BaseModel, EmailStr, constr, Field
from typing import Optional, List, Annotated, TYPE_CHECKING
from datetime import datetime
from app.models.user import UserRole # Import the enum from models
if TYPE_CHECKING:
    from app.schemas.organization import OrganizationRead
# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[Annotated[str, constr(max_length=20)]] = None
    iin: Optional[Annotated[str, constr(min_length=12, max_length=12)]] = None # Kazakhstani IIN

# Properties to receive via API on creation (generic)
class UserCreate(UserBase):
    password: str
    role: UserRole
    organization_id: Optional[int] = None
    
# Properties for Solo Pilot Registration
class UserCreateSolo(UserBase):
    password: str

# Properties for Organization Pilot Registration
class UserCreateOrganizationPilot(UserBase):
    password: str
    organization_id: int

# Properties for Organization Admin Registration (part of OrganizationAdminRegister)
class AdminUserCreateForOrg(UserBase):
    password: str # Renamed from admin_password for consistency

# Properties to receive via API on update
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[Annotated[str, constr(max_length=20)]] = None
    current_password: Optional[str] = None # Required if changing password
    new_password: Optional[str] = None

# Properties to return to client
class UserRead(UserBase):
    id: int
    role: UserRole
    is_active: bool
    organization_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# For registering an organization and its admin
class OrganizationAdminRegister(BaseModel):
    org_name: str
    bin: Annotated[str, constr(min_length=12, max_length=12)]
    company_address: str
    city: str
    admin_full_name: str
    admin_email: EmailStr
    admin_password: str
    admin_phone_number: Optional[Annotated[str, constr(max_length=20)]] = None
    admin_iin: Optional[Annotated[str, constr(min_length=12, max_length=12)]] = None

class OrganizationAdminRegisterResponse(BaseModel):
    organization: "OrganizationRead" # Use fully qualified forward ref for clarity
    admin_user: UserRead

class UserStatusUpdate(BaseModel):
    is_active: bool
    
from app.schemas.organization import OrganizationRead # Import the actual class for Pydantic to resolve
OrganizationAdminRegisterResponse.model_rebuild()