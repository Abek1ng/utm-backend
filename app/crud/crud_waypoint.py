from typing import List
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.waypoint import Waypoint
from app.schemas.waypoint import WaypointCreate, WaypointUpdate

class CRUDWaypoint(CRUDBase[Waypoint, WaypointCreate, WaypointUpdate]):
    def get_by_flight_plan_id(self, db: Session, *, flight_plan_id: int) -> List[Waypoint]:
        return db.query(Waypoint).filter(Waypoint.flight_plan_id == flight_plan_id).order_by(Waypoint.sequence_order).all()

waypoint = CRUDWaypoint(Waypoint)