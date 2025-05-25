# app/crud/user_drone_assignments.py
from typing import List, Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user_drone_assignment import UserDroneAssignment
from app.schemas.user_drone_assignment import UserDroneAssignmentCreate, UserDroneAssignmentUpdate

class CRUDUserDroneAssignment(
    CRUDBase[UserDroneAssignment, UserDroneAssignmentCreate, UserDroneAssignmentUpdate]
):
    def get_assignment(
        self, db: Session, *, user_id: int, drone_id: int
    ) -> Optional[UserDroneAssignment]:
        return (
            db.query(UserDroneAssignment)
            .filter(
                UserDroneAssignment.user_id == user_id,
                UserDroneAssignment.drone_id == drone_id,
                UserDroneAssignment.deleted_at.is_(None),
            )
            .first()
        )

    def get_multi(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[UserDroneAssignment]:
        return (
            db.query(UserDroneAssignment)
            .filter(
                UserDroneAssignment.user_id == user_id,
                UserDroneAssignment.deleted_at.is_(None),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

user_drone_assignment = CRUDUserDroneAssignment(UserDroneAssignment)
