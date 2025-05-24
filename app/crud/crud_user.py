from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.crud.base import CRUDBase
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.db.utils import apply_soft_delete_filter_to_query_condition


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str, include_deleted: bool = False) -> Optional[User]:
        query = db.query(User).filter(User.email == email)
        if not include_deleted and hasattr(User, "deleted_at"):
            query = query.filter(User.deleted_at.is_(None))
        return query.first()

    def get_by_iin(self, db: Session, *, iin: str, include_deleted: bool = False) -> Optional[User]:
        query = db.query(User).filter(User.iin == iin)
        if not include_deleted and hasattr(User, "deleted_at"):
            query = query.filter(User.deleted_at.is_(None))
        return query.first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            phone_number=obj_in.phone_number,
            iin=obj_in.iin,
            role=obj_in.role, # Role is now part of UserCreate
            is_active=True, # Default, can be overridden if UserCreate has is_active
            organization_id=getattr(obj_in, 'organization_id', None) # If present in schema
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "new_password" in update_data and update_data["new_password"]:
            hashed_password = get_password_hash(update_data["new_password"])
            del update_data["new_password"] # Don't store plain new_password
            if "current_password" in update_data: # current_password might not be in dict if obj_in is dict
                 del update_data["current_password"]
            db_obj.hashed_password = hashed_password # Set hashed password directly

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(
        self, db: Session, *, email: str, password: str
    ) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not user.is_active: # Do not authenticate inactive users
            return None
        from app.core.security import verify_password # Local import to avoid circularity if security needs User
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_authority_admin(self, user: User) -> bool:
        return user.role == UserRole.AUTHORITY_ADMIN
    
    def is_organization_admin(self, user: User) -> bool:
        return user.role == UserRole.ORGANIZATION_ADMIN

    def get_multi_users(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100, 
        role: Optional[UserRole] = None, 
        organization_id: Optional[int] = None,
        include_deleted: bool = False
    ) -> List[User]:
        query = db.query(self.model)
        if not include_deleted:
            query = query.filter(self.model.deleted_at.is_(None))
        
        if role:
            query = query.filter(self.model.role == role)
        if organization_id is not None: # Check for None explicitly for 0
            query = query.filter(self.model.organization_id == organization_id)
            
        return query.order_by(self.model.id).offset(skip).limit(limit).all()

    def set_user_status(self, db: Session, *, user_id: int, is_active: bool) -> Optional[User]:
        db_user = self.get(db, id=user_id)
        if not db_user:
            return None
        db_user.is_active = is_active
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

user = CRUDUser(User)