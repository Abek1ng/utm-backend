from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.models.user import UserRole # Ensure UserRole is imported

def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you are not using Alembic, you can use:
    # from app.db.base_class import Base
    # from app.db.session import engine
    # Base.metadata.create_all(bind=engine)

    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name=settings.FIRST_SUPERUSER_FULL_NAME,
            iin=settings.FIRST_SUPERUSER_IIN, # Ensure IIN is in settings
            role=UserRole.AUTHORITY_ADMIN, # Set the role
            is_active=True, # Superuser should be active
        )
        user = crud.user.create(db, obj_in=user_in)
        print(f"Superuser '{settings.FIRST_SUPERUSER_EMAIL}' created.")
    else:
        print(f"Superuser '{settings.FIRST_SUPERUSER_EMAIL}' already exists.")