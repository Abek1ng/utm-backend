from typing import Optional, List, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.drone import Drone, DroneStatus
from app.models.user_drone_assignment import UserDroneAssignment
from app.schemas.drone import DroneCreate, DroneUpdate

class CRUDDrone(CRUDBase[Drone, DroneCreate, DroneUpdate]):
    def get_by_serial_number(self, db: Session, *, serial_number: str, include_deleted: bool = False) -> Optional[Drone]:
        query = db.query(Drone).filter(Drone.serial_number == serial_number)
        if not include_deleted:
            query = query.filter(Drone.deleted_at.is_(None))
        return query.first()

    def get_multi_drones_for_user(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        organization_id: Optional[int] = None, # For org admin/pilot
        is_org_admin: bool = False,
        skip: int = 0, 
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[Drone]:
        query = db.query(Drone)
        if not include_deleted:
            query = query.filter(Drone.deleted_at.is_(None))

        if is_org_admin and organization_id is not None:
            # Org admin sees all drones in their organization
            query = query.filter(Drone.organization_id == organization_id)
        elif organization_id is not None: # Org pilot
            # Org pilot sees drones assigned to them in their organization
            query = query.join(UserDroneAssignment, UserDroneAssignment.drone_id == Drone.id)\
                         .filter(UserDroneAssignment.user_id == user_id)\
                         .filter(Drone.organization_id == organization_id) # Ensure drone is in their org
        else: # Solo pilot
            query = query.filter(Drone.solo_owner_user_id == user_id)
        
        return query.order_by(Drone.id).offset(skip).limit(limit).all()

    def get_multi_drones_for_organization(
        self, db: Session, *, organization_id: int, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> List[Drone]:
        query = db.query(Drone).filter(Drone.organization_id == organization_id)
        if not include_deleted:
            query = query.filter(Drone.deleted_at.is_(None))
        return query.order_by(Drone.id).offset(skip).limit(limit).all()

    def get_all_drones_admin(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
        status: Optional[DroneStatus] = None,
        include_deleted: bool = False
    ) -> List[Drone]:
        query = db.query(Drone)
        if not include_deleted:
            query = query.filter(Drone.deleted_at.is_(None))
        
        if organization_id is not None:
            query = query.filter(Drone.organization_id == organization_id)
        if status:
            query = query.filter(Drone.current_status == status)
            
        return query.order_by(Drone.id).offset(skip).limit(limit).all()

drone = CRUDDrone(Drone)


class CRUDUserDroneAssignment(CRUDBase[UserDroneAssignment, Any, Any]): # Schemas not strictly needed for base
    def get_assignment(self, db: Session, *, user_id: int, drone_id: int) -> Optional[UserDroneAssignment]:
        # UserDroneAssignment does not have 'deleted_at' in its strict schema definition
        return db.query(UserDroneAssignment).filter(
            UserDroneAssignment.user_id == user_id,
            UserDroneAssignment.drone_id == drone_id
        ).first()

    def assign_user_to_drone(self, db: Session, *, user_id: int, drone_id: int) -> UserDroneAssignment:
        # Check if already assigned
        existing_assignment = self.get_assignment(db, user_id=user_id, drone_id=drone_id)
        if existing_assignment:
            return existing_assignment # Or raise error if re-assigning is not allowed

        db_obj = UserDroneAssignment(user_id=user_id, drone_id=drone_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def unassign_user_from_drone(self, db: Session, *, user_id: int, drone_id: int) -> Optional[UserDroneAssignment]:
        db_obj = self.get_assignment(db, user_id=user_id, drone_id=drone_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj # Return the deleted object or None

    def get_assignments_for_drone(self, db: Session, *, drone_id: int) -> List[UserDroneAssignment]:
        return db.query(UserDroneAssignment).filter(UserDroneAssignment.drone_id == drone_id).all()

    def get_assignments_for_user(self, db: Session, *, user_id: int) -> List[UserDroneAssignment]:
        return db.query(UserDroneAssignment).filter(UserDroneAssignment.user_id == user_id).all()

user_drone_assignment = CRUDUserDroneAssignment(UserDroneAssignment)