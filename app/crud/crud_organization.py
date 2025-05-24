from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.crud.base import CRUDBase
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate # OrganizationCreate might not be used directly

class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationUpdate]):
    def get_by_name(self, db: Session, *, name: str, include_deleted: bool = False) -> Optional[Organization]:
        query = db.query(Organization).filter(Organization.name == name)
        if not include_deleted:
            query = query.filter(Organization.deleted_at.is_(None))
        return query.first()

    def get_by_bin(self, db: Session, *, bin_val: str, include_deleted: bool = False) -> Optional[Organization]:
        query = db.query(Organization).filter(Organization.bin == bin_val)
        if not include_deleted:
            query = query.filter(Organization.deleted_at.is_(None))
        return query.first()

    def get_multi_organizations(
        self, db: Session, *, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> List[Organization]:
        query = db.query(self.model)
        if not include_deleted:
            query = query.filter(self.model.deleted_at.is_(None))
        return query.order_by(self.model.id).offset(skip).limit(limit).all()

    # create method is inherited from CRUDBase.
    # For organization creation with admin, a service layer function is better
    # as it's a transactional operation involving two models.

organization = CRUDOrganization(Organization)