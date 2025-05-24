from typing import Optional, List
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.restricted_zone import RestrictedZone
from app.schemas.restricted_zone import RestrictedZoneCreate, RestrictedZoneUpdate

class CRUDRestrictedZone(CRUDBase[RestrictedZone, RestrictedZoneCreate, RestrictedZoneUpdate]):
    def get_by_name(self, db: Session, *, name: str, include_deleted: bool = False) -> Optional[RestrictedZone]:
        query = db.query(RestrictedZone).filter(RestrictedZone.name == name)
        if not include_deleted:
            query = query.filter(RestrictedZone.deleted_at.is_(None))
        return query.first()

    def get_all_active_zones(self, db: Session) -> List[RestrictedZone]:
        # Active means is_active = True AND not soft-deleted
        return db.query(RestrictedZone)\
                 .filter(RestrictedZone.is_active == True, RestrictedZone.deleted_at.is_(None))\
                 .all()

    def get_multi_zones_admin(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None,
        include_deleted: bool = False # For admin to see soft-deleted ones
    ) -> List[RestrictedZone]:
        query = db.query(RestrictedZone)
        if not include_deleted: # Default behavior for list is to exclude soft-deleted
             query = query.filter(RestrictedZone.deleted_at.is_(None))
        
        if is_active is not None:
            query = query.filter(RestrictedZone.is_active == is_active)
            
        return query.order_by(RestrictedZone.id).offset(skip).limit(limit).all()

restricted_zone = CRUDRestrictedZone(RestrictedZone)