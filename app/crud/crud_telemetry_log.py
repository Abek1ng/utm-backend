from typing import List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.crud.base import CRUDBase
from app.models.telemetry_log import TelemetryLog
from app.schemas.telemetry import TelemetryLogCreate # TelemetryLogUpdate not typical

class CRUDTelemetryLog(CRUDBase[TelemetryLog, TelemetryLogCreate, Any]): # Update schema is Any
    def create_log(self, db: Session, *, obj_in: TelemetryLogCreate) -> TelemetryLog:
        # Direct creation, no complex logic here usually
        return super().create(db, obj_in=obj_in)

    def get_logs_for_flight(
        self, db: Session, *, flight_plan_id: int, limit: Optional[int] = None
    ) -> List[TelemetryLog]:
        query = db.query(TelemetryLog)\
                  .filter(TelemetryLog.flight_plan_id == flight_plan_id)\
                  .order_by(TelemetryLog.timestamp.asc()) # Asc for chronological order
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_latest_log_for_drone(self, db: Session, *, drone_id: int) -> Optional[TelemetryLog]:
        return db.query(TelemetryLog)\
                 .filter(TelemetryLog.drone_id == drone_id)\
                 .order_by(TelemetryLog.timestamp.desc())\
                 .first()

telemetry_log = CRUDTelemetryLog(TelemetryLog)