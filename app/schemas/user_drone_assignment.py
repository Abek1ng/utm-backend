# app/schemas/user_drone_assignment.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class UserDroneAssignmentBase(BaseModel):
    user_id: int
    drone_id: int

class UserDroneAssignmentCreate(UserDroneAssignmentBase):
    pass

class UserDroneAssignmentUpdate(BaseModel):
    # any updatable fields, e.g. deleted_at
    deleted_at: Optional[datetime] = None

class UserDroneAssignmentRead(UserDroneAssignmentBase):
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        orm_mode = True
