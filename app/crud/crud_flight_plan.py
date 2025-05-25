from typing import Optional, List, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql import func 
from app.crud.base import CRUDBase
from app.models.flight_plan import FlightPlan, FlightPlanStatus
from app.models.waypoint import Waypoint
from app.schemas.flight_plan import FlightPlanCreate, FlightPlanUpdate # FlightPlanUpdate for general updates
from app.schemas.waypoint import WaypointCreate


class CRUDFlightPlan(CRUDBase[FlightPlan, FlightPlanCreate, FlightPlanUpdate]):
    def create_with_waypoints(self, db: Session, *, obj_in: FlightPlanCreate, user_id: int, organization_id: Optional[int] = None, initial_status: FlightPlanStatus) -> FlightPlan:
        db_flight_plan = FlightPlan(
            user_id=user_id,
            drone_id=obj_in.drone_id,
            organization_id=organization_id, # Set if applicable
            planned_departure_time=obj_in.planned_departure_time,
            planned_arrival_time=obj_in.planned_arrival_time,
            notes=obj_in.notes,
            status=initial_status # Set by service layer
        )
        db.add(db_flight_plan)
        # Must flush to get flight_plan.id for waypoints
        db.flush() 
        
        for waypoint_in in obj_in.waypoints:
            db_waypoint = Waypoint(
                flight_plan_id=db_flight_plan.id,
                **waypoint_in.model_dump()
            )
            db.add(db_waypoint)
            
        db.commit()
        db.refresh(db_flight_plan)
        return db_flight_plan

    def get_multi_for_user_with_details(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100, status: Optional[FlightPlanStatus] = None, include_deleted: bool = False
    ) -> List[FlightPlan]:
        query = db.query(FlightPlan).options(
            selectinload(FlightPlan.drone),
            selectinload(FlightPlan.waypoints) # Load waypoints as well
        ).filter(FlightPlan.user_id == user_id)
        
        if not include_deleted:
            query = query.filter(FlightPlan.deleted_at.is_(None))
        if status:
            query = query.filter(FlightPlan.status == status)
        return query.order_by(FlightPlan.planned_departure_time.desc()).offset(skip).limit(limit).all()

    def get_flight_plan_with_details(self, db: Session, id: int, include_deleted: bool = False) -> Optional[FlightPlan]:
        query = db.query(FlightPlan).options(
            selectinload(FlightPlan.waypoints),
            selectinload(FlightPlan.drone),
            selectinload(FlightPlan.submitter_user)
        ).filter(FlightPlan.id == id)
        
        if not include_deleted:
            query = query.filter(FlightPlan.deleted_at.is_(None))
        return query.first()

    def get_multi_for_user_with_drone(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100, status: Optional[FlightPlanStatus] = None, include_deleted: bool = False
    ) -> List[FlightPlan]:
        query = db.query(FlightPlan).options(selectinload(FlightPlan.drone)).filter(FlightPlan.user_id == user_id)
        if not include_deleted:
            query = query.filter(FlightPlan.deleted_at.is_(None))
        if status:
            query = query.filter(FlightPlan.status == status)
        return query.order_by(FlightPlan.planned_departure_time.desc()).offset(skip).limit(limit).all()

    def get_multi_for_organization(
        self, db: Session, *, organization_id: int, skip: int = 0, limit: int = 100, status: Optional[FlightPlanStatus] = None, user_id: Optional[int] = None, include_deleted: bool = False
    ) -> List[FlightPlan]:
        query = db.query(FlightPlan).filter(FlightPlan.organization_id == organization_id)
        if not include_deleted:
            query = query.filter(FlightPlan.deleted_at.is_(None))
        if status:
            query = query.filter(FlightPlan.status == status)
        if user_id:
            query = query.filter(FlightPlan.user_id == user_id)
        return query.order_by(FlightPlan.planned_departure_time.desc()).offset(skip).limit(limit).all()

    def get_all_flight_plans_admin(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        status: Optional[FlightPlanStatus] = None,
        organization_id: Optional[int] = None,
        user_id: Optional[int] = None,
        include_deleted: bool = False
    ) -> List[FlightPlan]:
        query = db.query(FlightPlan)
        if not include_deleted:
            query = query.filter(FlightPlan.deleted_at.is_(None))
        
        if status:
            query = query.filter(FlightPlan.status == status)
        if organization_id is not None:
            query = query.filter(FlightPlan.organization_id == organization_id)
        if user_id is not None:
            query = query.filter(FlightPlan.user_id == user_id)
            
        return query.order_by(FlightPlan.planned_departure_time.desc()).offset(skip).limit(limit).all()

    def update_status(
        self, 
        db: Session, 
        *, 
        db_obj: FlightPlan, 
        new_status: FlightPlanStatus, 
        rejection_reason: Optional[str] = None,
        approver_id: Optional[int] = None, # User ID of approver
        is_org_approval: bool = False # Flag to set correct approver field
    ) -> FlightPlan:
        db_obj.status = new_status
        if rejection_reason:
            db_obj.rejection_reason = rejection_reason
        
        if new_status == FlightPlanStatus.APPROVED:
            db_obj.approved_at = func.now() # Using SQLAlchemy func
            if approver_id:
                if is_org_approval: # This logic might be more complex depending on workflow
                    db_obj.approved_by_organization_admin_id = approver_id
                else: # Authority approval (or solo pilot direct approval)
                    db_obj.approved_by_authority_admin_id = approver_id
        
        # If rejected, clear approval fields
        if new_status in [FlightPlanStatus.REJECTED_BY_ORG, FlightPlanStatus.REJECTED_BY_AUTHORITY]:
            db_obj.approved_at = None
            db_obj.approved_by_organization_admin_id = None
            db_obj.approved_by_authority_admin_id = None

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def start_flight(self, db: Session, *, db_obj: FlightPlan) -> FlightPlan:
        db_obj.status = FlightPlanStatus.ACTIVE
        db_obj.actual_departure_time = func.now()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def complete_flight(self, db: Session, *, db_obj: FlightPlan) -> FlightPlan:
        db_obj.status = FlightPlanStatus.COMPLETED
        db_obj.actual_arrival_time = func.now()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def cancel_flight(self, db: Session, *, db_obj: FlightPlan, cancelled_by_role: str, reason: Optional[str]=None) -> FlightPlan:
        if cancelled_by_role == "PILOT":
            db_obj.status = FlightPlanStatus.CANCELLED_BY_PILOT
        else: # ADMIN (Org or Authority)
            db_obj.status = FlightPlanStatus.CANCELLED_BY_ADMIN
        
        # Add cancellation reason to notes or a new field if desired
        if reason:
            db_obj.notes = f"{db_obj.notes or ''}\nCancellation Reason: {reason}".strip()

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_flight_history(self, db: Session, flight_plan_id: int, include_deleted: bool = False) -> Optional[FlightPlan]:
        query = db.query(FlightPlan).options(
            selectinload(FlightPlan.waypoints),
            selectinload(FlightPlan.telemetry_logs).order_by(Waypoint.sequence_order), # Order telemetry if needed by timestamp
            selectinload(FlightPlan.drone),
            selectinload(FlightPlan.submitter_user)
        ).filter(FlightPlan.id == flight_plan_id)

        if not include_deleted:
            query = query.filter(FlightPlan.deleted_at.is_(None))
        return query.first()


flight_plan = CRUDFlightPlan(FlightPlan)

# CRUD for Waypoint (if needed separately, usually managed via FlightPlan)
from app.crud.base import CRUDBase
from app.models.waypoint import Waypoint
from app.schemas.waypoint import WaypointCreate, WaypointUpdate

class CRUDWaypoint(CRUDBase[Waypoint, WaypointCreate, WaypointUpdate]):
    def get_by_flight_plan_id(self, db: Session, *, flight_plan_id: int) -> List[Waypoint]:
        return db.query(Waypoint).filter(Waypoint.flight_plan_id == flight_plan_id).order_by(Waypoint.sequence_order).all()

waypoint = CRUDWaypoint(Waypoint)