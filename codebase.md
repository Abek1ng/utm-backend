# .gitignore

```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds Пthe exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot
*.po

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# PEP 582; __pypackages__
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak
venv.bak

# Spyder project settings
.spyderproject
.spyderworkspace

# Rope project settings
.ropeproject

# PyDev project settings
.pydevproject

# PyCharm
.idea/
*.iml
workspace.xml
tasks.xml

# VSCode
.vscode/

# alembic versions if not committed (though usually they are)
# alembic/versions/*

# Docker
docker-compose.override.yml
```

# alembic.ini

```ini
[alembic]
# path to migration scripts
script_location = alembic

# template for migration file names
# file_template = %%(rev)s_%%(slug)s

# timezone for timestamps within migration files
# timezone = UTC

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S

# Alembic environment variables can be configured here
# For example, to use a different database URL for migrations:
# sqlalchemy.url = driver://user:pass@localhost/dbname
# This is often set dynamically in env.py using os.environ
```

# alembic/env.py

```py
from logging.config import fileConfig
import os
from dotenv import load_dotenv

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base and models for autogenerate support
from app.db.base_class import Base

# Import all models individually to avoid circular imports
from app.models.user import User
from app.models.organization import Organization
from app.models.drone import Drone
from app.models.user_drone_assignment import UserDroneAssignment
from app.models.flight_plan import FlightPlan
from app.models.waypoint import Waypoint
from app.models.telemetry_log import TelemetryLog
from app.models.restricted_zone import RestrictedZone

target_metadata = Base.metadata

def get_url():
    return os.getenv("DATABASE_URL")

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

# alembic/script.py.mako

```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}

```

# alembic/versions/001_initial_migration.py

```py
"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create organizations table FIRST (no dependencies)
    op.create_table('organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('bin', sa.String(length=12), nullable=False),
        sa.Column('company_address', sa.String(length=500), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('bin')
    )
    op.create_index(op.f('ix_organizations_deleted_at'), 'organizations', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=True)

    # Create users table SECOND (references organizations)
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('iin', sa.String(length=12), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('AUTHORITY_ADMIN', 'ORGANIZATION_ADMIN', 'ORGANIZATION_PILOT', 'SOLO_PILOT', name='userrole'), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_user_organization_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('phone_number'),
        sa.UniqueConstraint('iin')
    )
    op.create_index(op.f('ix_users_deleted_at'), 'users', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_iin'), 'users', ['iin'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)

    # Now add the admin_id foreign key to organizations (circular reference)
    op.create_foreign_key('fk_organization_admin_id', 'organizations', 'users', ['admin_id'], ['id'])

    # Create drones table
    op.create_table('drones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('serial_number', sa.String(length=100), nullable=False),
        sa.Column('owner_type', sa.Enum('ORGANIZATION', 'SOLO_PILOT', name='droneownertype'), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('solo_owner_user_id', sa.Integer(), nullable=True),
        sa.Column('current_status', sa.Enum('IDLE', 'ACTIVE', 'MAINTENANCE', 'UNKNOWN', name='dronestatus'), nullable=False, server_default='IDLE'),
        sa.Column('last_telemetry_id', sa.BigInteger(), nullable=True),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_drone_organization_id'),
        sa.ForeignKeyConstraint(['solo_owner_user_id'], ['users.id'], name='fk_drone_solo_owner_user_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('serial_number')
    )
    op.create_index(op.f('ix_drones_deleted_at'), 'drones', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_drones_id'), 'drones', ['id'], unique=False)
    op.create_index(op.f('ix_drones_serial_number'), 'drones', ['serial_number'], unique=True)


def downgrade() -> None:
    op.drop_table('drones')
    op.drop_table('users')
    op.drop_table('organizations')

```

# alembic/versions/b621379b2521_add_remaining_tables.py

```py
"""Add remaining tables

Revision ID: b621379b2521
Revises: 001
Create Date: 2025-05-25 01:38:47.317934

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b621379b2521'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_drone_assignments table
    op.create_table('user_drone_assignments',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('drone_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['drone_id'], ['drones.id'], name='fk_user_drone_assignment_drone_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_drone_assignment_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'drone_id', name='pk_user_drone_assignment')
    )

    # Create flight_plans table
    op.create_table('flight_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('drone_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('planned_departure_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('planned_arrival_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('actual_departure_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_arrival_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.Enum('PENDING_ORG_APPROVAL', 'PENDING_AUTHORITY_APPROVAL', 'APPROVED', 'REJECTED_BY_ORG', 'REJECTED_BY_AUTHORITY', 'ACTIVE', 'COMPLETED', 'CANCELLED_BY_PILOT', 'CANCELLED_BY_ADMIN', name='flightplanstatus'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.String(length=500), nullable=True),
        sa.Column('approved_by_organization_admin_id', sa.Integer(), nullable=True),
        sa.Column('approved_by_authority_admin_id', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['approved_by_authority_admin_id'], ['users.id'], name='fk_flight_plan_auth_admin_id'),
        sa.ForeignKeyConstraint(['approved_by_organization_admin_id'], ['users.id'], name='fk_flight_plan_org_admin_id'),
        sa.ForeignKeyConstraint(['drone_id'], ['drones.id'], name='fk_flight_plan_drone_id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_flight_plan_organization_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_flight_plan_user_id'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_flight_plans_deleted_at'), 'flight_plans', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_flight_plans_id'), 'flight_plans', ['id'], unique=False)
    op.create_index(op.f('ix_flight_plans_status'), 'flight_plans', ['status'], unique=False)

    # Create waypoints table
    op.create_table('waypoints',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('flight_plan_id', sa.Integer(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('altitude_m', sa.Float(), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['flight_plan_id'], ['flight_plans.id'], name='fk_waypoint_flight_plan_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_waypoint_flight_plan_id_sequence_order', 'waypoints', ['flight_plan_id', 'sequence_order'], unique=True)
    op.create_index(op.f('ix_waypoints_flight_plan_id'), 'waypoints', ['flight_plan_id'], unique=False)
    op.create_index(op.f('ix_waypoints_id'), 'waypoints', ['id'], unique=False)

    # Create telemetry_logs table
    op.create_table('telemetry_logs',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('flight_plan_id', sa.Integer(), nullable=True),
    sa.Column('drone_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('altitude_m', sa.Float(), nullable=False),
    sa.Column('speed_mps', sa.Float(), nullable=True),
    sa.Column('heading_degrees', sa.Float(), nullable=True),
    sa.Column('status_message', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),  # ADD THIS LINE
    sa.ForeignKeyConstraint(['drone_id'], ['drones.id'], name='fk_telemetry_log_drone_id', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['flight_plan_id'], ['flight_plans.id'], name='fk_telemetry_log_flight_plan_id', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
)
    op.create_index(op.f('ix_telemetry_logs_drone_id'), 'telemetry_logs', ['drone_id'], unique=False)
    op.create_index(op.f('ix_telemetry_logs_flight_plan_id'), 'telemetry_logs', ['flight_plan_id'], unique=False)
    op.create_index(op.f('ix_telemetry_logs_id'), 'telemetry_logs', ['id'], unique=False)
    op.create_index(op.f('ix_telemetry_logs_timestamp'), 'telemetry_logs', ['timestamp'], unique=False)

    # Create restricted_zones table
    op.create_table('restricted_zones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('geometry_type', sa.Enum('CIRCLE', 'POLYGON', name='nfzgeometrytype'), nullable=False),
        sa.Column('definition_json', sa.JSON(), nullable=False),
        sa.Column('min_altitude_m', sa.Float(), nullable=True),
        sa.Column('max_altitude_m', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by_authority_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by_authority_id'], ['users.id'], name='fk_restricted_zone_creator_id'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_restricted_zones_deleted_at'), 'restricted_zones', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_restricted_zones_id'), 'restricted_zones', ['id'], unique=False)
    op.create_index(op.f('ix_restricted_zones_name'), 'restricted_zones', ['name'], unique=False)

    # Add the foreign key for drones.last_telemetry_id (circular reference)
    op.create_foreign_key('fk_drone_last_telemetry_id', 'drones', 'telemetry_logs', ['last_telemetry_id'], ['id'])


def downgrade() -> None:
    op.drop_table('restricted_zones')
    op.drop_table('telemetry_logs')
    op.drop_table('waypoints')
    op.drop_table('flight_plans')
    op.drop_table('user_drone_assignments')
```

# alembic/versions/d93e49272d92_add_deleted_at_to_telemetry_logs.py

```py

"""Add deleted_at to telemetry_logs

Revision ID: [new_revision_id]
Revises: b621379b2521
Create Date: [current_date]

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd93e49272d92'
down_revision = 'b621379b2521'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add deleted_at column to telemetry_logs if it doesn't exist
    op.add_column('telemetry_logs', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_telemetry_logs_deleted_at'), 'telemetry_logs', ['deleted_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_telemetry_logs_deleted_at'), table_name='telemetry_logs')
    op.drop_column('telemetry_logs', 'deleted_at')
```

# app/__init__.py

```py

```

# app/api/__init__.py

```py

```

# app/api/deps.py

```py
from typing import Generator, Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.token import TokenPayload
from app.crud import user as crud_user  # This imports the 'user' instance

reusable_http_bearer = HTTPBearer(auto_error=True)


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(reusable_http_bearer),
) -> User:
    token = credentials.credentials
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("sub") is None:
            raise credentials_exception
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    user_id = token_data.sub
    if user_id is None:
        raise credentials_exception
    
    # Fix: Use crud_user.get() instead of crud_user.user.get()
    user = crud_user.get(db, id=int(user_id))
    if not user:
        raise credentials_exception
    if not crud_user.is_active(user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    return user

# Role-specific dependencies
def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user

def get_current_authority_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.AUTHORITY_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges (Authority Admin required).",
        )
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

def get_current_organization_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ORGANIZATION_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges (Organization Admin required).",
        )
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization Admin not associated with an organization.")
    return current_user

def get_current_organization_member(current_user: User = Depends(get_current_user)) -> User:
    """For either Org Admin or Org Pilot"""
    if current_user.role not in [UserRole.ORGANIZATION_ADMIN, UserRole.ORGANIZATION_PILOT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user must be an Organization Admin or Organization Pilot.",
        )
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not associated with an organization.")
    return current_user

def get_current_pilot(current_user: User = Depends(get_current_user)) -> User:
    """For Solo Pilot or Organization Pilot"""
    if current_user.role not in [UserRole.SOLO_PILOT, UserRole.ORGANIZATION_PILOT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user must be a Pilot (Solo or Organization).",
        )
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

def verify_organization_access(
    organization_id_in_path: int,
    current_user: User = Depends(get_current_organization_admin)
) -> None:
    if current_user.organization_id != organization_id_in_path:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this organization's resources."
        )

def verify_user_in_organization(
    user_to_check_id: int,
    current_org_admin: User = Depends(get_current_organization_admin),
    db: Session = Depends(get_db)
) -> User:
    user = crud_user.get(db, id=user_to_check_id)  # Fix: Use crud_user.get()
    if not user or user.organization_id != current_org_admin.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or does not belong to this organization."
        )
    return user
```

# app/api/routers/__init__.py

```py

```

# app/api/routers/auth.py

```py
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User, UserRole # For setting roles
from app.schemas.user import UserRead 

router = APIRouter()

@router.post("/register/solo-pilot", response_model=schemas.UserRead)
def register_solo_pilot(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreateSolo,
) -> Any:
    """
    Registers a new independent (solo) pilot.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    if user_in.iin and crud.user.get_by_iin(db, iin=user_in.iin):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this IIN already exists in the system.",
        )
    
    user_create_internal = schemas.UserCreate(
        **user_in.model_dump(),
        role=UserRole.SOLO_PILOT, # Set role
        # password field is already in UserCreateSolo and thus in user_in
    )
    user = crud.user.create(db, obj_in=user_create_internal)
    return user

@router.post("/register/organization-admin", response_model=schemas.OrganizationAdminRegisterResponse)
def register_organization_admin(
    *,
    db: Session = Depends(deps.get_db),
    org_admin_in: schemas.OrganizationAdminRegister,
) -> Any:
    """
    Registers a new organization AND its primary admin user. Transactional.
    """
    # Check if admin email or IIN already exists
    admin_user = crud.user.get_by_email(db, email=org_admin_in.admin_email)
    if admin_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An admin with this email already exists.",
        )
    if org_admin_in.admin_iin and crud.user.get_by_iin(db, iin=org_admin_in.admin_iin):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An admin with this IIN already exists.",
        )

    # Check if organization name or BIN already exists
    if crud.organization.get_by_name(db, name=org_admin_in.org_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An organization with this name already exists.",
        )
    if crud.organization.get_by_bin(db, bin_val=org_admin_in.bin): # Use bin_val to avoid conflict
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An organization with this BIN already exists.",
        )

    try:
        # Create Admin User first
        admin_user_data = schemas.UserCreate(
            email=org_admin_in.admin_email,
            password=org_admin_in.admin_password,
            full_name=org_admin_in.admin_full_name,
            phone_number=org_admin_in.admin_phone_number,
            iin=org_admin_in.admin_iin,
            role=UserRole.ORGANIZATION_ADMIN,
            # organization_id will be set after org is created and admin is linked
        )
        created_admin_user = crud.user.create(db, obj_in=admin_user_data)

        # Create Organization
        org_data = schemas.OrganizationCreate( # Assuming OrganizationCreate schema exists
            name=org_admin_in.org_name,
            bin=org_admin_in.bin,
            company_address=org_admin_in.company_address,
            city=org_admin_in.city,
            admin_id=created_admin_user.id # Link admin to organization
        )
        created_org = crud.organization.create(db, obj_in=org_data)

        # Link admin user to the organization
        created_admin_user.organization_id = created_org.id
        db.add(created_admin_user)
        db.commit()
        db.refresh(created_admin_user)
        db.refresh(created_org) # Refresh org to get admin_user relationship if defined

        return {"organization": created_org, "admin_user": created_admin_user}

    except Exception as e:
        db.rollback() # Rollback in case of any error during the transaction
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register organization admin: {str(e)}"
        )


@router.post("/register/organization-pilot", response_model=schemas.UserRead)
def register_organization_pilot(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreateOrganizationPilot,
) -> Any:
    """
    Registers a new pilot who will be a member of an existing organization.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists.",
        )
    if user_in.iin and crud.user.get_by_iin(db, iin=user_in.iin):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this IIN already exists.",
        )
    
    organization = crud.organization.get(db, id=user_in.organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )
    if not organization.is_active:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot register pilot for an inactive organization.",
        )

    user_create_internal = schemas.UserCreate(
        **user_in.model_dump(exclude={"organization_id"}), # Exclude org_id as it's passed separately
        role=UserRole.ORGANIZATION_PILOT,
        organization_id=user_in.organization_id, # Set organization_id
    )
    user = crud.user.create(db, obj_in=user_create_internal)
    return user


@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Username is the email.
    """
    user = crud.user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
async def read_current_user(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get current user information."""
    return current_user
```

# app/api/routers/drones.py

```py
from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.models.user import UserRole
from app.models.drone import DroneOwnerType, DroneStatus

router = APIRouter()

@router.post("/", response_model=schemas.DroneRead, status_code=status.HTTP_201_CREATED)
def create_drone(
    *,
    db: Session = Depends(deps.get_db),
    drone_in: schemas.DroneCreate,
    current_user: models.User = Depends(deps.get_current_active_user), # SOLO_PILOT or ORGANIZATION_ADMIN
) -> Any:
    """
    Register a new drone. Ownership is determined by the authenticated user's role and input.
    """
    if current_user.role not in [UserRole.SOLO_PILOT, UserRole.ORGANIZATION_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Solo Pilots or Organization Admins can register drones.",
        )

    if crud.drone.get_by_serial_number(db, serial_number=drone_in.serial_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Drone with this serial number already exists.",
        )

    owner_type: DroneOwnerType
    solo_owner_user_id: Optional[int] = None
    organization_id_for_drone: Optional[int] = None # Renamed to avoid conflict

    if current_user.role == UserRole.SOLO_PILOT:
        if drone_in.organization_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo pilots cannot assign drones to an organization during creation.",
            )
        owner_type = DroneOwnerType.SOLO_PILOT
        solo_owner_user_id = current_user.id
    
    elif current_user.role == UserRole.ORGANIZATION_ADMIN:
        if drone_in.organization_id is not None and drone_in.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization admin can only register drones for their own organization.",
            )
        owner_type = DroneOwnerType.ORGANIZATION
        organization_id_for_drone = current_user.organization_id
        if not organization_id_for_drone: # Should not happen if role is ORG_ADMIN
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Org Admin has no organization ID.")
    else: # Should be caught by initial role check
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid role for drone creation.")

    db_drone = models.Drone(
        **drone_in.model_dump(exclude={"organization_id"}), # Exclude if it was just for validation
        owner_type=owner_type,
        solo_owner_user_id=solo_owner_user_id,
        organization_id=organization_id_for_drone,
        current_status=DroneStatus.IDLE # Default status
    )
    db.add(db_drone)
    db.commit()
    db.refresh(db_drone)
    return db_drone


@router.get("/my", response_model=List[schemas.DroneRead])
def list_my_drones(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: models.User = Depends(deps.get_current_active_user), # Any authenticated role
) -> Any:
    """
    List drones relevant to the authenticated user:
    - Solo Pilot: Lists drones where solo_owner_user_id matches.
    - Org Pilot: Lists drones assigned to them within their org.
    - Org Admin: Lists all drones within their organization.
    """
    is_org_admin = current_user.role == UserRole.ORGANIZATION_ADMIN
    
    drones = crud.drone.get_multi_drones_for_user(
        db, 
        user_id=current_user.id, 
        organization_id=current_user.organization_id, # Pass org_id for org users
        is_org_admin=is_org_admin,
        skip=skip, 
        limit=limit
    )
    return drones


@router.get("/admin/all", response_model=List[schemas.DroneRead])
def list_all_drones_admin(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    organization_id: Optional[int] = Query(None),
    status: Optional[DroneStatus] = Query(None),
    current_user: models.User = Depends(deps.get_current_authority_admin), # Authority Admin Only
) -> Any:
    """
    List ALL drones in the system (Authority Admin only).
    """
    drones = crud.drone.get_all_drones_admin(
        db, 
        skip=skip, 
        limit=limit, 
        organization_id=organization_id, 
        status=status
    )
    return drones


@router.get("/{drone_id}", response_model=schemas.DroneRead)
def read_drone_by_id(
    drone_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get details for a specific drone.
    Authorization: Authority Admin, or owner/assignee.
    """
    db_drone = crud.drone.get(db, id=drone_id)
    if not db_drone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drone not found")

    # Authorization check
    can_view = False
    if current_user.role == UserRole.AUTHORITY_ADMIN:
        can_view = True
    elif current_user.role == UserRole.SOLO_PILOT:
        if db_drone.owner_type == DroneOwnerType.SOLO_PILOT and db_drone.solo_owner_user_id == current_user.id:
            can_view = True
    elif current_user.role == UserRole.ORGANIZATION_ADMIN:
        if db_drone.owner_type == DroneOwnerType.ORGANIZATION and db_drone.organization_id == current_user.organization_id:
            can_view = True
    elif current_user.role == UserRole.ORGANIZATION_PILOT:
        if db_drone.owner_type == DroneOwnerType.ORGANIZATION and db_drone.organization_id == current_user.organization_id:
            # Check if pilot is assigned to this drone
            assignment = crud.user_drone_assignment.get_assignment(db, user_id=current_user.id, drone_id=drone_id)
            if assignment:
                can_view = True
    
    if not can_view:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this drone")
        
    return db_drone


@router.put("/{drone_id}", response_model=schemas.DroneRead)
def update_drone(
    drone_id: int,
    drone_in: schemas.DroneUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update drone details. Serial number typically not updatable.
    Authorization: Authority Admin, or owner (Solo Pilot or Org Admin for their org's drones).
    """
    db_drone = crud.drone.get(db, id=drone_id)
    if not db_drone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drone not found")

    can_update = False
    if current_user.role == UserRole.AUTHORITY_ADMIN:
        can_update = True
    elif current_user.role == UserRole.SOLO_PILOT:
        if db_drone.owner_type == DroneOwnerType.SOLO_PILOT and db_drone.solo_owner_user_id == current_user.id:
            can_update = True
    elif current_user.role == UserRole.ORGANIZATION_ADMIN:
        if db_drone.owner_type == DroneOwnerType.ORGANIZATION and db_drone.organization_id == current_user.organization_id:
            can_update = True
            
    if not can_update:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this drone")

    # Prevent serial number update if drone_in contains it and it's different
    update_data = drone_in.model_dump(exclude_unset=True)
    if "serial_number" in update_data and update_data["serial_number"] != db_drone.serial_number:
        # Typically, serial number is immutable after creation or only changeable by Authority Admin.
        if current_user.role != UserRole.AUTHORITY_ADMIN:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Serial number cannot be changed by this user.")
        # If Authority Admin is changing it, ensure it's not taken by another drone
        existing_drone_sn = crud.drone.get_by_serial_number(db, serial_number=update_data["serial_number"])
        if existing_drone_sn and existing_drone_sn.id != drone_id:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New serial number already exists.")
    elif "serial_number" in update_data: # If SN is same or not provided for update
        del update_data["serial_number"]


    updated_drone = crud.drone.update(db, db_obj=db_drone, obj_in=update_data)
    return updated_drone


@router.delete("/{drone_id}", response_model=schemas.DroneRead, status_code=status.HTTP_200_OK)
def delete_drone(
    drone_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Soft delete a drone.
    Authorization: Authority Admin, or owner.
    """
    db_drone = crud.drone.get(db, id=drone_id)
    if not db_drone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drone not found")

    can_delete = False
    if current_user.role == UserRole.AUTHORITY_ADMIN:
        can_delete = True
    elif current_user.role == UserRole.SOLO_PILOT:
        if db_drone.owner_type == DroneOwnerType.SOLO_PILOT and db_drone.solo_owner_user_id == current_user.id:
            can_delete = True
    elif current_user.role == UserRole.ORGANIZATION_ADMIN:
        if db_drone.owner_type == DroneOwnerType.ORGANIZATION and db_drone.organization_id == current_user.organization_id:
            can_delete = True
            
    if not can_delete:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this drone")

    # TODO: Consider implications: active flights, assignments?
    # For MVP, just soft delete.
    if db_drone.current_status == DroneStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete an active drone. Complete or cancel its flights first.")

    deleted_drone = crud.drone.soft_remove(db, id=drone_id)
    if not deleted_drone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drone not found during delete.")
    return deleted_drone


@router.post("/{drone_id}/assign-user", response_model=schemas.UserDroneAssignmentRead)
def assign_user_to_drone(
    drone_id: int,
    assignment_in: schemas.UserAssignToDrone,
    db: Session = Depends(deps.get_db),
    current_org_admin: models.User = Depends(deps.get_current_organization_admin),
) -> Any:
    """
    Assign an organization pilot to a drone within the same organization (Org Admin Only).
    """
    db_drone = crud.drone.get(db, id=drone_id)
    if not db_drone or db_drone.organization_id != current_org_admin.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drone not found or does not belong to your organization.")

    user_to_assign = crud.user.get(db, id=assignment_in.user_id_to_assign)
    if not user_to_assign or \
       user_to_assign.organization_id != current_org_admin.organization_id or \
       user_to_assign.role != UserRole.ORGANIZATION_PILOT: # Ensure assigning an Org Pilot
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User to assign not found, not an Organization Pilot, or does not belong to your organization."
        )
    if not user_to_assign.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot assign an inactive user.")

    existing_assignment = crud.user_drone_assignment.get_assignment(db, user_id=user_to_assign.id, drone_id=drone_id)
    if existing_assignment:
        # Return existing assignment or raise error if re-assignment is not desired
        # For now, return existing.
        return existing_assignment
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already assigned to this drone.")

    assignment = crud.user_drone_assignment.assign_user_to_drone(
        db, user_id=user_to_assign.id, drone_id=drone_id
    )
    return assignment


@router.delete("/{drone_id}/unassign-user", status_code=status.HTTP_204_NO_CONTENT)
def unassign_user_from_drone(
    drone_id: int,
    unassignment_in: schemas.UserUnassignFromDrone, # Body for consistency, though user_id could be path param
    db: Session = Depends(deps.get_db),
    current_org_admin: models.User = Depends(deps.get_current_organization_admin),
) -> None:
    """
    Unassign an organization pilot from a drone (Org Admin Only).
    """
    db_drone = crud.drone.get(db, id=drone_id)
    if not db_drone or db_drone.organization_id != current_org_admin.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drone not found or does not belong to your organization.")

    user_to_unassign_id = unassignment_in.user_id_to_unassign
    user_to_unassign = crud.user.get(db, id=user_to_unassign_id)
    if not user_to_unassign or user_to_unassign.organization_id != current_org_admin.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User to unassign not found or does not belong to your organization."
        )

    assignment = crud.user_drone_assignment.get_assignment(db, user_id=user_to_unassign_id, drone_id=drone_id)
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not assigned to this drone.")

    crud.user_drone_assignment.unassign_user_from_drone(db, user_id=user_to_unassign_id, drone_id=drone_id)
    return None # FastAPI will return 204 No Content
```

# app/api/routers/flights.py

```py
from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.models.user import UserRole
from app.models.flight_plan import FlightPlanStatus
from app.services import flight_service # Use the service instance

router = APIRouter()

@router.post("/", response_model=schemas.FlightPlanRead, status_code=status.HTTP_201_CREATED)
def submit_new_flight_plan(
    *,
    db: Session = Depends(deps.get_db),
    flight_plan_in: schemas.FlightPlanCreate,
    current_user: models.User = Depends(deps.get_current_pilot), # SOLO_PILOT or ORGANIZATION_PILOT
) -> Any:
    """
    Submit a new flight plan.
    Backend sets initial status based on submitter's role. NFZ pre-check performed.
    """
    try:
        created_flight_plan = flight_service.submit_flight_plan(
            db, flight_plan_in=flight_plan_in, submitter=current_user
        )
        # Eager load waypoints for the response
        db.refresh(created_flight_plan, attribute_names=['waypoints'])
        return created_flight_plan
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e: # Catch other unexpected errors
        print(f"Error processing flight plan: {e}")  # Log the error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing flight plan.")


@router.get("/my", response_model=List[schemas.FlightPlanReadWithWaypoints])  # Change the response model
def list_my_flight_plans(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    status_filter: Optional[FlightPlanStatus] = Query(None, alias="status"),
    current_user: models.User = Depends(deps.get_current_pilot),
) -> Any:
    """
    List flight plans submitted by the currently authenticated user (Pilot).
    Includes drone details and waypoints.
    """
    flight_plans = crud.flight_plan.get_multi_for_user_with_drone(
        db, user_id=current_user.id, skip=skip, limit=limit, status=status_filter
    )
    return flight_plans


@router.get("/organization", response_model=List[schemas.FlightPlanRead])
def list_organization_flight_plans(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    status_filter: Optional[FlightPlanStatus] = Query(None, alias="status"),
    user_id_filter: Optional[int] = Query(None, alias="user_id"),
    current_org_admin: models.User = Depends(deps.get_current_organization_admin),
) -> Any:
    """
    List all flight plans associated with the Organization Admin's organization.
    """
    if not current_org_admin.organization_id: # Should be guaranteed by dependency
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Admin not linked to an organization.")
        
    flight_plans = crud.flight_plan.get_multi_for_organization(
        db, 
        organization_id=current_org_admin.organization_id, 
        skip=skip, 
        limit=limit, 
        status=status_filter,
        user_id=user_id_filter
    )
    return flight_plans


@router.get("/admin/all", response_model=List[schemas.FlightPlanRead])
def list_all_flight_plans_admin(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    status_filter: Optional[FlightPlanStatus] = Query(None, alias="status"),
    organization_id_filter: Optional[int] = Query(None, alias="organization_id"),
    user_id_filter: Optional[int] = Query(None, alias="user_id"),
    current_authority_admin: models.User = Depends(deps.get_current_authority_admin),
) -> Any:
    """
    List ALL flight plans in the system (Authority Admin Only).
    """
    flight_plans = crud.flight_plan.get_all_flight_plans_admin(
        db,
        skip=skip,
        limit=limit,
        status=status_filter,
        organization_id=organization_id_filter,
        user_id=user_id_filter
    )
    return flight_plans


@router.get("/{flight_plan_id}", response_model=schemas.FlightPlanReadWithWaypoints)
def read_flight_plan_by_id(
    flight_plan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get details of a specific flight plan, including waypoints.
    Authorization: Authority Admin, submitter, or relevant Org Admin.
    """
    db_flight_plan = crud.flight_plan.get_flight_plan_with_details(db, id=flight_plan_id)
    if not db_flight_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flight plan not found")

    can_view = False
    if current_user.role == UserRole.AUTHORITY_ADMIN:
        can_view = True
    elif current_user.id == db_flight_plan.user_id: # Submitter
        can_view = True
    elif current_user.role == UserRole.ORGANIZATION_ADMIN and \
         db_flight_plan.organization_id == current_user.organization_id:
        can_view = True
    
    if not can_view:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this flight plan")
        
    return db_flight_plan


@router.put("/{flight_plan_id}/status", response_model=schemas.FlightPlanRead)
def update_flight_plan_status_endpoint( # Renamed to avoid conflict with service method
    flight_plan_id: int,
    status_update_in: schemas.FlightPlanStatusUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user), # Org Admin or Authority Admin
) -> Any:
    """
    Update the status of a flight plan.
    - Org Admin: Can change PENDING_ORG_APPROVAL to PENDING_AUTHORITY_APPROVAL or REJECTED_BY_ORG.
    - Authority Admin: Can change PENDING_AUTHORITY_APPROVAL to APPROVED or REJECTED_BY_AUTHORITY.
    """
    if current_user.role not in [UserRole.ORGANIZATION_ADMIN, UserRole.AUTHORITY_ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authorized to update flight plan status.")

    try:
        updated_flight_plan = flight_service.update_flight_plan_status(
            db,
            flight_plan_id=flight_plan_id,
            new_status=status_update_in.status,
            actor=current_user,
            rejection_reason=status_update_in.rejection_reason
        )
        db.refresh(updated_flight_plan, attribute_names=['waypoints']) # Ensure waypoints are loaded if schema needs them
        return updated_flight_plan
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log error e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating flight plan status.")


@router.put("/{flight_plan_id}/start", response_model=schemas.FlightPlanRead)
def start_flight_endpoint( # Renamed
    flight_plan_id: int,
    db: Session = Depends(deps.get_db),
    current_pilot: models.User = Depends(deps.get_current_pilot), # Submitting Pilot
) -> Any:
    """
    Pilot starts an APPROVED flight. Sets status to ACTIVE, triggers telemetry simulation.
    """
    try:
        started_flight_plan = flight_service.start_flight(
            db, flight_plan_id=flight_plan_id, pilot=current_pilot
        )
        db.refresh(started_flight_plan, attribute_names=['waypoints'])
        return started_flight_plan
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log error e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error starting flight.")


@router.put("/{flight_plan_id}/cancel", response_model=schemas.FlightPlanRead)
def cancel_flight_endpoint( # Renamed
    flight_plan_id: int,
    cancel_in: schemas.FlightPlanCancel,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user), # Pilot, Org Admin, or Auth Admin
) -> Any:
    """
    Pilot or Admin cancels a flight.
    """
    if current_user.role not in [UserRole.SOLO_PILOT, UserRole.ORGANIZATION_PILOT, UserRole.ORGANIZATION_ADMIN, UserRole.AUTHORITY_ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authorized to cancel flight plans.")
    
    try:
        cancelled_flight_plan = flight_service.cancel_flight(
            db,
            flight_plan_id=flight_plan_id,
            actor=current_user,
            reason=cancel_in.reason
        )
        db.refresh(cancelled_flight_plan, attribute_names=['waypoints'])
        return cancelled_flight_plan
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log error e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error cancelling flight.")


@router.get("/{flight_plan_id}/history", response_model=schemas.FlightPlanHistory)
def get_flight_plan_history(
    flight_plan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user), # Auth Admin, submitter, relevant Org Admin
) -> Any:
    """
    Get the planned waypoints and all recorded telemetry logs for a completed or active flight.
    """
    db_flight_plan = crud.flight_plan.get_flight_history(db, flight_plan_id=flight_plan_id) # This method loads waypoints and telemetry
    
    if not db_flight_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flight plan not found")

    can_view = False
    if current_user.role == UserRole.AUTHORITY_ADMIN:
        can_view = True
    elif current_user.id == db_flight_plan.user_id: # Submitter
        can_view = True
    elif current_user.role == UserRole.ORGANIZATION_ADMIN and \
         db_flight_plan.organization_id == current_user.organization_id:
        can_view = True
    
    if not can_view:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this flight plan history")

    # Ensure all necessary data is loaded for FlightPlanReadWithWaypoints
    # The get_flight_history CRUD method should handle this with selectinload
    
    # Convert to FlightPlanReadWithWaypoints
    flight_plan_details_schema = schemas.FlightPlanReadWithWaypoints.model_validate(db_flight_plan)
    
    # Telemetry logs are already loaded by crud.flight_plan.get_flight_history
    actual_telemetry_schema = [schemas.TelemetryLogRead.model_validate(log) for log in db_flight_plan.telemetry_logs]

    return schemas.FlightPlanHistory(
        flight_plan_details=flight_plan_details_schema,
        actual_telemetry=actual_telemetry_schema
    )
```

# app/api/routers/nfz.py

```py
from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.models.user import UserRole

router = APIRouter()

# --- Endpoints under /admin/nfz (Authority Admin Only) ---

@router.post("/admin/nfz/", response_model=schemas.RestrictedZoneRead, status_code=status.HTTP_201_CREATED)
def create_nfz(
    *,
    db: Session = Depends(deps.get_db),
    nfz_in: schemas.RestrictedZoneCreate,
    current_admin: models.User = Depends(deps.get_current_authority_admin),
) -> Any:
    """
    Create a new No-Fly Zone (Authority Admin only).
    """
    # Check for duplicate name if names should be unique
    existing_nfz = crud.restricted_zone.get_by_name(db, name=nfz_in.name)
    if existing_nfz:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A No-Fly Zone with the name '{nfz_in.name}' already exists.",
        )
    
    # TODO: Add validation for nfz_in.definition_json based on nfz_in.geometry_type
    # e.g., circle needs center_lat, center_lon, radius_m
    # polygon needs coordinates: List[List[List[float]]]

    db_nfz = models.RestrictedZone(
        **nfz_in.model_dump(),
        created_by_authority_id=current_admin.id,
        is_active=True # Default to active on creation
    )
    db.add(db_nfz)
    db.commit()
    db.refresh(db_nfz)
    return db_nfz


@router.get("/admin/nfz/", response_model=List[schemas.RestrictedZoneRead])
def list_nfzs_admin(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    is_active: Optional[bool] = Query(None),
    current_admin: models.User = Depends(deps.get_current_authority_admin),
) -> Any:
    """
    List all No-Fly Zones (Authority Admin view, can see inactive/deleted).
    """
    # include_deleted=True could be an option if admin needs to see soft-deleted ones
    nfzs = crud.restricted_zone.get_multi_zones_admin(
        db, skip=skip, limit=limit, is_active=is_active, include_deleted=False # Set to True to see soft-deleted
    )
    return nfzs


@router.get("/admin/nfz/{zone_id}", response_model=schemas.RestrictedZoneRead)
def get_nfz_by_id_admin(
    zone_id: int,
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_authority_admin),
) -> Any:
    """
    Get details of a specific NFZ (Authority Admin only).
    """
    # include_deleted=True if admin should be able to fetch soft-deleted NFZ by ID
    nfz = crud.restricted_zone.get(db, id=zone_id, include_deleted=False) 
    if not nfz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No-Fly Zone not found")
    return nfz


@router.put("/admin/nfz/{zone_id}", response_model=schemas.RestrictedZoneRead)
def update_nfz(
    zone_id: int,
    nfz_in: schemas.RestrictedZoneUpdate,
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_authority_admin),
) -> Any:
    """
    Update an existing NFZ (Authority Admin only).
    """
    db_nfz = crud.restricted_zone.get(db, id=zone_id)
    if not db_nfz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No-Fly Zone not found")

    update_data = nfz_in.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] != db_nfz.name:
        existing_nfz_name = crud.restricted_zone.get_by_name(db, name=update_data["name"])
        if existing_nfz_name and existing_nfz_name.id != zone_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NFZ name already taken.")

    # TODO: Add validation for definition_json if geometry_type is also changing or if definition_json is updated.

    updated_nfz = crud.restricted_zone.update(db, db_obj=db_nfz, obj_in=update_data)
    return updated_nfz


@router.delete("/admin/nfz/{zone_id}", response_model=schemas.RestrictedZoneRead, status_code=status.HTTP_200_OK)
def delete_nfz(
    zone_id: int,
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_authority_admin),
) -> Any:
    """
    Soft delete an NFZ (Authority Admin only).
    """
    db_nfz = crud.restricted_zone.get(db, id=zone_id)
    if not db_nfz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No-Fly Zone not found")

    # Soft delete also marks it as inactive
    deleted_nfz = crud.restricted_zone.soft_remove(db, id=zone_id)
    if not deleted_nfz: # Should not happen if get() found it
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NFZ not found during delete.")
    
    if deleted_nfz.is_active: # Ensure it's marked inactive
        deleted_nfz.is_active = False
        db.add(deleted_nfz)
        db.commit()
        db.refresh(deleted_nfz)
        
    return deleted_nfz


# --- Public/Authenticated Read Endpoint for NFZ map display ---
@router.get("/nfz/", response_model=List[schemas.RestrictedZoneRead])
def list_active_nfzs_for_map(
    db: Session = Depends(deps.get_db),
    # No specific authentication for this, public or any authenticated user
    # current_user: models.User = Depends(deps.get_current_active_user), # If auth required
) -> Any:
    """
    List active No-Fly Zones for map display (Public or Authenticated).
    """
    active_nfzs = crud.restricted_zone.get_all_active_zones(db)
    return active_nfzs
```

# app/api/routers/organizations.py

```py
from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.models.user import UserRole

router = APIRouter()

@router.get("/", response_model=List[schemas.OrganizationRead])
def read_organizations(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    # Authorization: Primarily for Authority Admin.
    # Org Admins might see their own if they forgot ID, but /users/me is better.
    # If this endpoint is for pilot registration selection, it might need broader access.
    # For now, restrict to Authority Admin as per endpoint spec.
    current_user: models.User = Depends(deps.get_current_authority_admin),
) -> Any:
    """
    List all organizations (Authority Admin only). Supports pagination.
    """
    organizations = crud.organization.get_multi_organizations(db, skip=skip, limit=limit)
    return organizations

@router.get("/{organization_id}", response_model=schemas.OrganizationReadWithDetails)
def read_organization_by_id(
    organization_id: int = Path(..., title="The ID of the organization to get"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get details for a specific organization.
    Authorization: Authority Admin, or Organization Admin (if organization_id matches their org).
    """
    org = crud.organization.get(db, id=organization_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    if current_user.role == UserRole.AUTHORITY_ADMIN:
        pass # Authority admin can see any organization
    elif current_user.role == UserRole.ORGANIZATION_ADMIN:
        if current_user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this organization's details.",
            )
    else: # Other roles (e.g., pilots) generally shouldn't access this directly unless specified
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access organization details.",
        )
    
    # Populate OrganizationReadWithDetails if needed
    # For example, load admin_user details
    admin_user_details = None
    if org.admin_id:
        admin_user_details = crud.user.get(db, id=org.admin_id)

    # This is a basic example; you might want to load lists of users, drones etc.
    # into OrganizationReadWithDetails based on further requirements.
    return schemas.OrganizationReadWithDetails(
        **schemas.OrganizationRead.model_validate(org).model_dump(),
        admin_user=admin_user_details if admin_user_details else None
        # users=[], drones=[] # Populate these if your schema expects them
    )


@router.put("/{organization_id}", response_model=schemas.OrganizationRead)
def update_organization(
    organization_id: int,
    org_in: schemas.OrganizationUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update organization details (Org Admin for their own org, or Authority Admin).
    """
    org = crud.organization.get(db, id=organization_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    can_update_all_fields = False
    if current_user.role == UserRole.AUTHORITY_ADMIN:
        can_update_all_fields = True
    elif current_user.role == UserRole.ORGANIZATION_ADMIN:
        if current_user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this organization.",
            )
        # Org Admin can update limited fields. `new_admin_id` might be restricted or require special handling.
        if org_in.new_admin_id and org_in.new_admin_id != org.admin_id:
             # Check if the new admin belongs to this organization and has ORG_ADMIN role
            new_admin_user = crud.user.get(db, id=org_in.new_admin_id)
            if not new_admin_user or \
               new_admin_user.organization_id != organization_id or \
               new_admin_user.role != UserRole.ORGANIZATION_ADMIN:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid new admin ID or new admin not suitable.")
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update organization details.",
        )

    update_data = org_in.model_dump(exclude_unset=True)
    
    # If Org Admin is updating and not all fields are allowed, filter update_data
    if not can_update_all_fields and current_user.role == UserRole.ORGANIZATION_ADMIN:
        allowed_fields_for_org_admin = {"name", "company_address", "city"} # Example
        # BIN is usually immutable or changed by Authority. `new_admin_id` handled above.
        update_data = {k: v for k, v in update_data.items() if k in allowed_fields_for_org_admin or k == "new_admin_id"}


    # Check for uniqueness if name or BIN is being changed
    if "name" in update_data and update_data["name"] != org.name:
        existing_org_name = crud.organization.get_by_name(db, name=update_data["name"])
        if existing_org_name and existing_org_name.id != organization_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization name already taken.")
    
    if "bin" in update_data and update_data["bin"] != org.bin:
        if not can_update_all_fields: # Org admins typically cannot change BIN
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization Admin cannot change BIN.")
        existing_org_bin = crud.organization.get_by_bin(db, bin_val=update_data["bin"])
        if existing_org_bin and existing_org_bin.id != organization_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization BIN already in use.")

    if "new_admin_id" in update_data:
        org.admin_id = update_data.pop("new_admin_id") # Update admin_id directly on model

    updated_org = crud.organization.update(db, db_obj=org, obj_in=update_data)
    return updated_org


@router.delete("/{organization_id}", response_model=schemas.OrganizationRead, status_code=status.HTTP_200_OK)
def delete_organization(
    organization_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_authority_admin), # Authority Admin Only
) -> Any:
    """
    Soft delete an organization (Authority Admin only).
    Cascading implications (users, drones, flights) need careful consideration for a full implementation.
    MVP: Mark org as deleted, prevent new activity.
    """
    org_to_delete = crud.organization.get(db, id=organization_id)
    if not org_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # TODO: Implement cascading logic if required (e.g., deactivate users, drones of this org)
    # For MVP, just soft delete the organization.
    # It might also be good to disassociate the admin_id or mark users as inactive.
    # For now, simple soft delete.
    
    # Example: Deactivate all users of this organization
    # users_in_org = crud.user.get_multi_users(db, organization_id=organization_id, limit=1000) # Get all
    # for user_in_org in users_in_org:
    #     crud.user.set_user_status(db, user_id=user_in_org.id, is_active=False)

    deleted_org = crud.organization.soft_remove(db, id=organization_id)
    if not deleted_org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found during delete.")
    
    # Mark organization as inactive as well upon soft delete
    deleted_org.is_active = False
    db.add(deleted_org)
    db.commit()
    db.refresh(deleted_org)

    return deleted_org


@router.get("/{organization_id}/users", response_model=List[schemas.UserRead])
def list_organization_users(
    organization_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all users belonging to a specific organization.
    Authorization: Authority Admin, or Organization Admin (if organization_id matches their org).
    """
    org = crud.organization.get(db, id=organization_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    if current_user.role == UserRole.AUTHORITY_ADMIN:
        pass
    elif current_user.role == UserRole.ORGANIZATION_ADMIN:
        if current_user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to list users for this organization.",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to list organization users.",
        )

    users = crud.user.get_multi_users(db, organization_id=organization_id, skip=skip, limit=limit)
    return users


@router.get("/{organization_id}/drones", response_model=List[schemas.DroneRead])
def list_organization_drones(
    organization_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all drones belonging to a specific organization.
    Authorization: Authority Admin, or Organization Admin (if organization_id matches their org).
    """
    org = crud.organization.get(db, id=organization_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    if current_user.role == UserRole.AUTHORITY_ADMIN:
        pass
    elif current_user.role == UserRole.ORGANIZATION_ADMIN:
        if current_user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to list drones for this organization.",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to list organization drones.",
        )

    drones = crud.drone.get_multi_drones_for_organization(
        db, organization_id=organization_id, skip=skip, limit=limit
    )
    return drones
```

# app/api/routers/telemetry.py

```py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException, status
from typing import Optional

from app.services.telemetry_service import connection_manager
from app.core.security import decode_token
from app.crud import user as crud_user # Renamed to avoid conflict
from app.db.session import get_db # For token validation if needed
from sqlalchemy.orm import Session
from app.core.config import settings


router = APIRouter()

# Path for WebSocket defined in settings.WS_TELEMETRY_PATH
@router.websocket(settings.WS_TELEMETRY_PATH)
async def websocket_telemetry_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None) # Token for authentication
    # db: Session = Depends(get_db) # Cannot use Depends directly in WebSocket route like this
):
    """
    WebSocket endpoint for clients to connect and receive real-time telemetry.
    Authentication via token in query parameter.
    """
    # Authentication (simplified for WebSocket)
    # In a real app, you might want to create a short-lived WebSocket ticket
    # or handle token validation more robustly.
    user_id_from_token: Optional[int] = None
    if token:
        user_id_str = decode_token(token)
        if user_id_str:
            try:
                user_id_from_token = int(user_id_str)
                # Optional: Fetch user from DB to ensure they are active, etc.
                # This requires a synchronous DB call from an async context,
                # which can be tricky. For now, just validating token existence.
                # with SessionLocal() as db_session: # Example if you need DB access
                #     user = crud_user.user.get(db_session, id=user_id_from_token)
                #     if not user or not user.is_active:
                #         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                #         return
            except ValueError:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token format")
                return
        else: # Token invalid or expired
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired token")
            return
    else: # No token provided, could be public or require token
        # For MVP, let's assume if no token, it's a public (unauthenticated) connection
        # or close if auth is strictly required.
        # For now, let's allow connection even without token for simplicity of broadcast.
        # If strict auth needed:
        # await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token required")
        # return
        pass


    await connection_manager.connect(websocket)
    client_host = websocket.client.host if websocket.client else "unknown"
    client_port = websocket.client.port if websocket.client else "unknown"
    print(f"WebSocket client {client_host}:{client_port} connected (User ID: {user_id_from_token or 'Anonymous'}).")
    
    try:
        while True:
            # This loop keeps the connection alive.
            # The server broadcasts messages; clients primarily listen.
            # Client can send messages too (e.g., for filtering preferences),
            # but not implemented in this MVP.
            data = await websocket.receive_text() 
            # For MVP, we don't expect clients to send much data.
            # If they do, process it here.
            # Example: await websocket.send_text(f"Message text was: {data}")
            print(f"Received from {client_host}:{client_port} (User ID: {user_id_from_token or 'Anonymous'}): {data}")
            # Echo back or process client messages if needed
            # await connection_manager.send_personal_message(f"You wrote: {data}", websocket)

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        print(f"WebSocket client {client_host}:{client_port} (User ID: {user_id_from_token or 'Anonymous'}) disconnected.")
    except Exception as e:
        connection_manager.disconnect(websocket)
        print(f"WebSocket error for client {client_host}:{client_port} (User ID: {user_id_from_token or 'Anonymous'}): {e}")
        # Optionally try to close with an error code if not already disconnected
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except RuntimeError: # Already closed
            pass
```

# app/api/routers/users.py

```py
from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.security import get_password_hash, verify_password
from app.models.user import UserRole

router = APIRouter()

@router.get("/me", response_model=schemas.UserRead)
def read_users_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=schemas.UserRead)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    if user_in.new_password:
        if not user_in.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is required to set a new password.",
            )
        if not verify_password(user_in.current_password, current_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")
    
    # Prevent users from changing their role or is_active status via this endpoint
    update_data = user_in.model_dump(exclude_unset=True)
    if "role" in update_data:
        del update_data["role"]
    if "is_active" in update_data:
        del update_data["is_active"]
    if "organization_id" in update_data: # Users cannot change their org this way
        del update_data["organization_id"]

    user = crud.user.update(db, db_obj=current_user, obj_in=update_data)
    return user

@router.get("/", response_model=List[schemas.UserRead])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    role: Optional[UserRole] = Query(None),
    organization_id: Optional[int] = Query(None),
    current_user: models.User = Depends(deps.get_current_authority_admin), # Admin Only
) -> Any:
    """
    Retrieve users (Admin only). Supports pagination and filtering.
    """
    users = crud.user.get_multi_users(
        db, skip=skip, limit=limit, role=role, organization_id=organization_id
    )
    return users

@router.get("/{user_id}", response_model=schemas.UserRead)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_authority_admin), # Admin Only
) -> Any:
    """
    Get a specific user by ID (Admin only).
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/{user_id}/status", response_model=schemas.UserRead)
def update_user_status(
    user_id: int,
    user_status_in: schemas.UserStatusUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_authority_admin), # Admin Only
) -> Any:
    """
    Activate or deactivate a user account (Admin only).
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Prevent deactivating the last authority admin if needed (more complex logic)
    # For now, allow deactivation.

    updated_user = crud.user.set_user_status(db, user_id=user_id, is_active=user_status_in.is_active)
    return updated_user

@router.delete("/{user_id}", response_model=schemas.UserRead, status_code=status.HTTP_200_OK) # Or 204 No Content
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_authority_admin), # Admin Only
) -> Any:
    """
    Soft delete a user (Admin only).
    """
    user_to_delete = crud.user.get(db, id=user_id)
    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user_to_delete.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admins cannot delete themselves.")

    # Consider implications: what happens to their drones, flights, etc.?
    # For MVP, soft delete marks them. Further logic might be needed to handle associated resources.
    
    # Soft delete the user
    deleted_user = crud.user.soft_remove(db, id=user_id)
    if not deleted_user: # Should not happen if get() found the user
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found during delete.")

    # To return 204 No Content, change response_model to None and return Response(status_code=204)
    return deleted_user
```

# app/api/routers/utility.py

```py
from typing import List, Any, Optional
import asyncio
from app.crud import telemetry_log as crud_telemetry_log
from app.models.drone import DroneOwnerType # For Remote ID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.models.user import UserRole
from app.models.flight_plan import FlightPlanStatus
from app.crud import flight_plan as crud_flight_plan
from app.crud import drone as crud_drone # For Remote ID

router = APIRouter()

@router.get("/weather", response_model=schemas.WeatherInfo)
async def get_weather_info(
    lat: float = Query(..., description="Latitude for weather forecast"),
    lon: float = Query(..., description="Longitude for weather forecast"),
    current_user: models.User = Depends(deps.get_current_active_user), # Authenticated users
) -> Any:
    """
    Get weather information for a given location. (Placeholder - requires external API integration)
    """
    # This is a placeholder. You would integrate with a real weather API here.
    # Example: OpenWeatherMap, WeatherAPI.com, etc.
    # For now, returning dummy data.
    from datetime import datetime, timezone
    import random

    # Simulate API call
    await asyncio.sleep(0.1) # Simulate network latency

    return schemas.WeatherInfo(
        lat=lat,
        lon=lon,
        temp=random.uniform(10, 30), # Celsius
        wind_speed=random.uniform(1, 10), # m/s
        wind_direction=random.uniform(0, 359), # degrees
        conditions_summary=random.choice(["Clear", "Cloudy", "Light Rain", "Sunny"]),
        timestamp=datetime.now(timezone.utc)
    )

@router.get("/remoteid/active-flights", response_model=List[schemas.RemoteIdBroadcast])
async def get_active_flights_remote_id(
    db: Session = Depends(deps.get_db),
    # Authorization: Public or AUTHORITY_ADMIN as per spec
    # For now, let's make it require Authority Admin to align with potential sensitivity
    # If public, remove current_user dependency or use an optional one.
    current_user: Optional[models.User] = Depends(deps.get_current_active_user), # Make it optional for public access
) -> Any:
    """
    Get a list of currently active flights with their emulated Remote ID data.
    (Placeholder - requires fetching live telemetry and formatting)
    """
    # If strict Authority Admin access:
    # current_admin: models.User = Depends(deps.get_current_authority_admin)

    # If public, but want to log if an admin accesses:
    if current_user and current_user.role == UserRole.AUTHORITY_ADMIN:
        print("Authority Admin accessed Remote ID endpoint.")
    # If public access is not desired without any auth, make current_user non-optional.


    # 1. Get all active flight plans
    active_flight_plans = crud_flight_plan.get_all_flight_plans_admin(
        db, status=FlightPlanStatus.ACTIVE, limit=1000 # Get all active
    )

    remote_id_broadcasts: List[schemas.RemoteIdBroadcast] = []

    for fp in active_flight_plans:
        # 2. For each active flight, get its latest telemetry
        latest_telemetry = crud_telemetry_log.get_latest_log_for_drone(db, drone_id=fp.drone_id)
        db_drone = crud_drone.get(db, id=fp.drone_id) # Get drone for serial number

        if latest_telemetry and db_drone:
            operator_id = None
            if db_drone.owner_type == DroneOwnerType.SOLO_PILOT and db_drone.solo_owner_user_id:
                operator_id = f"SOLO-{db_drone.solo_owner_user_id}" # Example proxy
            elif db_drone.owner_type == DroneOwnerType.ORGANIZATION and db_drone.organization_id:
                operator_id = f"ORG-{db_drone.organization_id}" # Example proxy

            broadcast = schemas.RemoteIdBroadcast(
                drone_serial_number=db_drone.serial_number,
                current_lat=latest_telemetry.latitude,
                current_lon=latest_telemetry.longitude,
                current_alt=latest_telemetry.altitude_m,
                timestamp=latest_telemetry.timestamp,
                operator_id_proxy=operator_id,
                # control_station_location_proxy: Placeholder, would need pilot's location if available
            )
            remote_id_broadcasts.append(broadcast)
            
    return remote_id_broadcasts

# Need to import asyncio for the weather endpoint

```

# app/api/v1.py

```py
from fastapi import APIRouter

from app.api.routers import auth, users, organizations, drones, flights, nfz, utility
# Telemetry router (for WebSocket) is usually added in main.py directly to the app.
# If telemetry.py also had HTTP routes, it would be included here.

api_router = APIRouter()

# Include each router with its prefix
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(drones.router, prefix="/drones", tags=["Drones"])
api_router.include_router(flights.router, prefix="/flights", tags=["Flight Plans"])

# The nfz.py router contains routes starting with /admin/nfz and /nfz, so no prefix needed here.
api_router.include_router(nfz.router, tags=["No-Fly Zones (NFZ)"])

# The utility.py router contains routes like /weather and /remoteid/active-flights, so no prefix needed here.
api_router.include_router(utility.router, tags=["Utilities"])
```

# app/core/__init__.py

```py

```

# app/core/config.py

```py
from pydantic_settings import BaseSettings
from typing import List, Optional, Union
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    PROJECT_NAME: str = "UTM API"
    API_V1_STR: str = "/api/v1"

    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str  # This should come directly from .env

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # First Superuser
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_FULL_NAME: str
    FIRST_SUPERUSER_IIN: str

    BACKEND_CORS_ORIGINS: List[Union[AnyHttpUrl, str]] = [
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://localhost:8080"
    ]
    
    # WebSocket
    WS_TELEMETRY_PATH: str = "/ws/telemetry"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
```

# app/core/security.py

```py
from datetime import datetime, timedelta, timezone
from typing import Optional, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM
JWT_SECRET_KEY = settings.SECRET_KEY


def create_access_token(subject: Any, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
```

# app/crud/__init__.py

```py
from .crud_user import user
from .crud_organization import organization
from .crud_drone import drone, user_drone_assignment
from .crud_flight_plan import flight_plan
from .crud_telemetry_log import telemetry_log
from .crud_restricted_zone import restricted_zone

# Only import waypoint if the file is properly implemented
try:
    from .crud_waypoint import waypoint
except ImportError:
    # waypoint CRUD is handled through flight_plan CRUD
    pass
```

# app/crud/base.py

```py
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.sql import func # For count

from app.db.base_class import Base
from app.db.utils import get_active_query, apply_soft_delete_filter_to_query_condition

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any, include_deleted: bool = False) -> Optional[ModelType]:
        query = db.query(self.model)
        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))
        return query.filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> List[ModelType]:
        query = db.query(self.model)
        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))
        return query.offset(skip).limit(limit).all()
    
    def get_multi_with_filter(
        self, db: Session, *, filter_conditions: Optional[List] = None, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> List[ModelType]:
        query = db.query(self.model)
        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))
        if filter_conditions:
            for condition in filter_conditions:
                query = query.filter(condition)
        return query.offset(skip).limit(limit).all()

    def get_count(self, db: Session, include_deleted: bool = False) -> int:
        query = db.query(func.count(self.model.id))
        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))
        return query.scalar_one()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> Optional[ModelType]:
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj # Return the deleted object or None

    def soft_remove(self, db: Session, *, id: Any) -> Optional[ModelType]:
        obj = db.query(self.model).get(id)
        if obj and hasattr(self.model, "deleted_at"):
            setattr(obj, "deleted_at", func.now())
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj
        elif obj: # If no deleted_at, perform hard delete
            return self.remove(db, id=id)
        return None
```

# app/crud/crud_drone.py

```py
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
```

# app/crud/crud_flight_plan.py

```py
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
```

# app/crud/crud_organization.py

```py
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
```

# app/crud/crud_restricted_zone.py

```py
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
```

# app/crud/crud_telemetry_log.py

```py
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
```

# app/crud/crud_user.py

```py
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
```

# app/crud/crud_waypoint.py

```py
from typing import List
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.waypoint import Waypoint
from app.schemas.waypoint import WaypointCreate, WaypointUpdate

class CRUDWaypoint(CRUDBase[Waypoint, WaypointCreate, WaypointUpdate]):
    def get_by_flight_plan_id(self, db: Session, *, flight_plan_id: int) -> List[Waypoint]:
        return db.query(Waypoint).filter(Waypoint.flight_plan_id == flight_plan_id).order_by(Waypoint.sequence_order).all()

waypoint = CRUDWaypoint(Waypoint)
```

# app/db/__init__.py

```py
from .base_class import Base
from .session import SessionLocal, engine, get_db
from . import utils # If utils contains functions to be exported

# REMOVE: from app import crud, schemas
```

# app/db/base_class.py

```py
from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, DateTime, func

@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s" # e.g. User -> users

    # Default audit columns - can be overridden in specific models if needed
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

```

# app/db/init_db.py

```py
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
```

# app/db/session.py

```py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

# app/db/utils.py

```py
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql import ColumnElement
from typing import Type, TypeVar
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)

def with_soft_delete_filter(query: Query, model: Type[ModelType], include_deleted: bool = False) -> Query:
    """Applies a filter to exclude soft-deleted records unless include_deleted is True."""
    if not include_deleted and hasattr(model, 'deleted_at'):
        return query.filter(model.deleted_at.is_(None))
    return query

def get_active_query(db: Session, model: Type[ModelType]) -> Query:
    """Returns a query for the model that filters out soft-deleted records."""
    if hasattr(model, 'deleted_at'):
        return db.query(model).filter(model.deleted_at.is_(None))
    return db.query(model) # If model doesn't have deleted_at, return normal query

def apply_soft_delete_filter_to_query_condition(model: Type[ModelType], condition: ColumnElement) -> ColumnElement:
    """Combines a given condition with the soft delete filter."""
    if hasattr(model, 'deleted_at'):
        return (condition) & (model.deleted_at.is_(None))
    return condition
```

# app/main.py

```py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router as api_v1_router
from app.api.routers import telemetry
from app.core.config import settings
from app.db.session import SessionLocal

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS setup
if hasattr(settings, 'BACKEND_CORS_ORIGINS') and settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_v1_router, prefix=settings.API_V1_STR)
app.include_router(telemetry.router)

@app.on_event("startup")
async def startup_event():
    print("Application startup...")
    # Import here to avoid circular imports
    from app.db.init_db import init_db
    
    db = SessionLocal()
    try:
        init_db(db)
        print("Initial database setup complete.")
    except Exception as e:
        print(f"Error during initial DB setup: {e}")
    finally:
        db.close()
    print("UTM API started successfully.")

@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "message": f"Welcome to {settings.PROJECT_NAME}!"}
```

# app/models/__init__.py

```py
from .user import User, UserRole  # UserRole enum needs to be accessible
from .organization import Organization
from .drone import Drone, DroneOwnerType, DroneStatus # Enums
from .user_drone_assignment import UserDroneAssignment
from .flight_plan import FlightPlan, FlightPlanStatus # Enum
from .waypoint import Waypoint
from .telemetry_log import TelemetryLog
from .restricted_zone import RestrictedZone, NFZGeometryType # Enum

# This helps Alembic find all models
from app.db.base_class import Base
```

# app/models/drone.py

```py
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum, BigInteger
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class DroneOwnerType(str, enum.Enum):
    ORGANIZATION = "ORGANIZATION"
    SOLO_PILOT = "SOLO_PILOT"

class DroneStatus(str, enum.Enum):
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    MAINTENANCE = "MAINTENANCE"
    UNKNOWN = "UNKNOWN"

class Drone(Base):
    __tablename__ = "drones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    serial_number = Column(String(100), unique=True, index=True, nullable=False)
    owner_type = Column(SAEnum(DroneOwnerType), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id", name="fk_drone_organization_id"), nullable=True)
    solo_owner_user_id = Column(Integer, ForeignKey("users.id", name="fk_drone_solo_owner_user_id"), nullable=True)
    current_status = Column(SAEnum(DroneStatus), nullable=False, default=DroneStatus.IDLE)
    # last_telemetry_id: Foreign key to telemetry_logs. Needs careful handling with Alembic if telemetry_logs table is defined later.
    # Alembic use_alter=True helps here.
    last_telemetry_id = Column(BigInteger, ForeignKey("telemetry_logs.id", name="fk_drone_last_telemetry_id", use_alter=True), nullable=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    # created_at, updated_at, deleted_at from Base

    # Relationships
    organization_owner = relationship("Organization", back_populates="owned_drones", foreign_keys=[organization_id])
    solo_owner_user = relationship("User", back_populates="owned_drones_solo", foreign_keys=[solo_owner_user_id])
    
    # Users assigned to this drone (M2M)
    assigned_users_through_link = relationship("UserDroneAssignment", back_populates="drone", lazy="selectin")

    flight_plans = relationship("FlightPlan", back_populates="drone", lazy="selectin")
    telemetry_logs = relationship("TelemetryLog", back_populates="drone", foreign_keys="[TelemetryLog.drone_id]", lazy="selectin") # All logs for this drone

    # Relationship for last_telemetry_id if you want to load the object
    # last_telemetry_point = relationship("TelemetryLog", foreign_keys=[last_telemetry_id])
```

# app/models/flight_plan.py

```py
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class FlightPlanStatus(str, enum.Enum):
    PENDING_ORG_APPROVAL = "PENDING_ORG_APPROVAL"
    PENDING_AUTHORITY_APPROVAL = "PENDING_AUTHORITY_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED_BY_ORG = "REJECTED_BY_ORG"
    REJECTED_BY_AUTHORITY = "REJECTED_BY_AUTHORITY"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED_BY_PILOT = "CANCELLED_BY_PILOT"
    CANCELLED_BY_ADMIN = "CANCELLED_BY_ADMIN"

class FlightPlan(Base):
    __tablename__ = "flight_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", name="fk_flight_plan_user_id"), nullable=False) # Submitter
    drone_id = Column(Integer, ForeignKey("drones.id", name="fk_flight_plan_drone_id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id", name="fk_flight_plan_organization_id"), nullable=True)
    
    planned_departure_time = Column(DateTime(timezone=True), nullable=False)
    planned_arrival_time = Column(DateTime(timezone=True), nullable=False)
    actual_departure_time = Column(DateTime(timezone=True), nullable=True)
    actual_arrival_time = Column(DateTime(timezone=True), nullable=True)
    
    status = Column(SAEnum(FlightPlanStatus), nullable=False, index=True)
    notes = Column(Text, nullable=True) # VARCHAR(1000) in schema, Text is more flexible
    rejection_reason = Column(String(500), nullable=True)
    
    approved_by_organization_admin_id = Column(Integer, ForeignKey("users.id", name="fk_flight_plan_org_admin_id"), nullable=True)
    approved_by_authority_admin_id = Column(Integer, ForeignKey("users.id", name="fk_flight_plan_auth_admin_id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True) # Final approval time
    # created_at, updated_at, deleted_at from Base

    # Relationships
    submitter_user = relationship("User", foreign_keys=[user_id], back_populates="submitted_flight_plans")
    drone = relationship("Drone", back_populates="flight_plans")
    organization = relationship("Organization", back_populates="flight_plans", foreign_keys=[organization_id])
    
    organization_approver = relationship("User", foreign_keys=[approved_by_organization_admin_id], back_populates="organization_approved_flight_plans")
    authority_approver = relationship("User", foreign_keys=[approved_by_authority_admin_id], back_populates="authority_approved_flight_plans")
    
    waypoints = relationship("Waypoint", back_populates="flight_plan", cascade="all, delete-orphan", lazy="selectin")
    telemetry_logs = relationship("TelemetryLog", back_populates="flight_plan", cascade="all, delete-orphan", lazy="selectin") # Or set null on delete
```

# app/models/organization.py

```py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    bin = Column(String(12), unique=True, index=True, nullable=False) # Business ID Number
    company_address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id", name="fk_organization_admin_id"), unique=True, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    # created_at, updated_at, deleted_at from Base

    # Relationships
    users = relationship("User", back_populates="organization", foreign_keys="[User.organization_id]")
    admin_user = relationship("User", foreign_keys=[admin_id]) # , back_populates="admin_of_organization"
    
    # Drones owned by this organization
    owned_drones = relationship(
        "Drone",
        foreign_keys="[Drone.organization_id]",
        back_populates="organization_owner",
        lazy="selectin"
    )

    # Flight plans related to this organization (indirectly via users or drones)
    # This can be complex to model directly if not explicitly linked.
    # We can query flight plans where flight_plan.organization_id is set.
    flight_plans = relationship("FlightPlan", back_populates="organization", foreign_keys="[FlightPlan.organization_id]")
```

# app/models/restricted_zone.py

```py
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum, Float, JSON, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class NFZGeometryType(str, enum.Enum):
    CIRCLE = "CIRCLE"
    POLYGON = "POLYGON"

class RestrictedZone(Base):
    __tablename__ = "restricted_zones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True) # VARCHAR(1000) in schema
    geometry_type = Column(SAEnum(NFZGeometryType), nullable=False)
    definition_json = Column(JSON, nullable=False) # Stores center/radius for circle, or coordinates for polygon
    min_altitude_m = Column(Float, nullable=True)
    max_altitude_m = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_by_authority_id = Column(Integer, ForeignKey("users.id", name="fk_restricted_zone_creator_id"), nullable=False)
    # created_at, updated_at, deleted_at from Base

    # Relationships
    creator_authority = relationship("User", back_populates="created_restricted_zones", foreign_keys=[created_by_authority_id])
```

# app/models/telemetry_log.py

```py
from sqlalchemy import Column, BigInteger, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    # flight_plan_id can be nullable if live telemetry w/o plan, but for this project, assume it's linked.
    # Or, as per schema, ondelete SET NULL if a flight plan is deleted but logs are kept.
    flight_plan_id = Column(Integer, ForeignKey("flight_plans.id", name="fk_telemetry_log_flight_plan_id", ondelete="SET NULL"), nullable=True, index=True)
    drone_id = Column(Integer, ForeignKey("drones.id", name="fk_telemetry_log_drone_id", ondelete="CASCADE"), nullable=False, index=True)
    
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude_m = Column(Float, nullable=False)
    speed_mps = Column(Float, nullable=True)
    heading_degrees = Column(Float, nullable=True) # 0-359.9
    status_message = Column(String(255), nullable=True) # e.g., "ON_SCHEDULE", "NFZ_ALERT"
    # created_at, updated_at from Base. deleted_at might not be relevant for telemetry.

    # Relationships
    flight_plan = relationship("FlightPlan", back_populates="telemetry_logs")
    drone = relationship("Drone", back_populates="telemetry_logs", foreign_keys=[drone_id])
```

# app/models/user_drone_assignment.py

```py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class UserDroneAssignment(Base):
    __tablename__ = "user_drone_assignments"

    # Override the 'id' from Base as it's not the PK here.
    # We'll use a composite primary key.
    # The 'id' column from Base will still exist but won't be the PK.
    # This is a common pattern if you want audit columns on an association table.
    # Alternatively, don't inherit Base if you strictly want only the M2M columns.
    # For now, let's keep Base inheritance for potential audit consistency.

    user_id = Column(Integer, ForeignKey("users.id", name="fk_user_drone_assignment_user_id", ondelete="CASCADE"), primary_key=True)
    drone_id = Column(Integer, ForeignKey("drones.id", name="fk_user_drone_assignment_drone_id", ondelete="CASCADE"), primary_key=True)
    
    # 'created_at' from Base can serve as 'assigned_at' if default=func.now() is acceptable.
    # If a distinct 'assigned_at' is needed separate from 'created_at', define it:
    # assigned_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    # For simplicity, let's assume Base.created_at IS assigned_at for this table.
    # The db_scheme.md explicitly lists `assigned_at`. So let's add it and make Base.created_at distinct or unused.

    # To match db_scheme.md which has `assigned_at` and no other audit columns for this table:
    # We should NOT inherit Base.
    # Let's go with the previous correction: Not inheriting Base for this specific table.
    # This means it won't have `created_at`, `updated_at`, `deleted_at` from the common Base.
    # This is the cleanest way to match the provided db_scheme.md for this specific table.
    # So, the "Corrected app/models/user_drone_assignment.py" (the one NOT inheriting Base) is better.
    # I will proceed with that version.

    # Reverting to the non-Base inheriting version for UserDroneAssignment for strict schema adherence.
    # This means UserDroneAssignment will NOT be in Base.metadata automatically unless explicitly added.
    # This is a slight complication for Alembic if `target_metadata = Base.metadata` is used.
    # A common practice is to have all tables inherit from the same Base.
    # Let's make a pragmatic choice: inherit Base, and `assigned_at` is the primary timestamp.
    # The `id` from Base will be there but not the primary key.
    
    # Final decision for UserDroneAssignment: Inherit Base, `created_at` from Base IS `assigned_at`.
    # This keeps all tables under one Base.metadata for Alembic.
    # The `db_scheme.md` `assigned_at` will map to `Base.created_at`.
    # The `id` column from `Base` will exist but `user_id, drone_id` will be the composite PK.

    # Override 'id' from Base as it's not the PK here.
    # The 'id' column from Base will still exist.
    # This is a bit of a compromise to keep all models under one Base.
    # The primary key constraint will ensure uniqueness.
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'drone_id', name='pk_user_drone_assignment'),
        {}, # Ensure this is a tuple for other args like schema
    )
    # `created_at` from Base will serve as `assigned_at`.
    # `updated_at` and `deleted_at` from Base are available if needed.
    # `id` from Base is also available, though not the PK.

    # Relationships
    user = relationship("User", back_populates="assigned_drones_through_link")
    drone = relationship("Drone", back_populates="assigned_users_through_link")
```

# app/models/user.py

```py
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class UserRole(str, enum.Enum):
    AUTHORITY_ADMIN = "AUTHORITY_ADMIN"
    ORGANIZATION_ADMIN = "ORGANIZATION_ADMIN"
    ORGANIZATION_PILOT = "ORGANIZATION_PILOT"
    SOLO_PILOT = "SOLO_PILOT"

class User(Base):
    __tablename__ = "users" # Explicitly set as per db_scheme.md

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), unique=True, index=True, nullable=True)
    iin = Column(String(12), unique=True, index=True, nullable=True) # Kazakhstani ID
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id", name="fk_user_organization_id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    # created_at, updated_at, deleted_at from Base

    # Relationships
    organization = relationship("Organization", back_populates="users", foreign_keys=[organization_id])
    
    # Drones owned by solo pilot
    owned_drones_solo = relationship(
        "Drone",
        foreign_keys="[Drone.solo_owner_user_id]",
        back_populates="solo_owner_user",
        lazy="selectin" # Or "joined" if frequently accessed
    )
    
    # Drones assigned to this user (M2M)
    assigned_drones_through_link = relationship("UserDroneAssignment", back_populates="user", lazy="selectin")

    submitted_flight_plans = relationship("FlightPlan", foreign_keys="[FlightPlan.user_id]", back_populates="submitter_user", lazy="selectin")
    
    # For flight plan approvals
    organization_approved_flight_plans = relationship(
        "FlightPlan",
        foreign_keys="[FlightPlan.approved_by_organization_admin_id]",
        back_populates="organization_approver",
        lazy="selectin"
    )
    authority_approved_flight_plans = relationship(
        "FlightPlan",
        foreign_keys="[FlightPlan.approved_by_authority_admin_id]",
        back_populates="authority_approver",
        lazy="selectin"
    )
    
    created_restricted_zones = relationship(
        "RestrictedZone",
        foreign_keys="[RestrictedZone.created_by_authority_id]",
        back_populates="creator_authority",
        lazy="selectin"
    )

    # For organization admin link
    # If an organization has one admin, this relationship is on the Organization model
    # admin_of_organization = relationship("Organization", back_populates="admin_user", uselist=False)
```

# app/models/waypoint.py

```py
from sqlalchemy import Column, Integer, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Waypoint(Base):
    __tablename__ = "waypoints"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    flight_plan_id = Column(Integer, ForeignKey("flight_plans.id", name="fk_waypoint_flight_plan_id", ondelete="CASCADE"), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude_m = Column(Float, nullable=False) # AGL
    sequence_order = Column(Integer, nullable=False)
    # created_at, updated_at from Base. deleted_at might not be relevant if waypoints are immutable once plan is set.

    # Relationships
    flight_plan = relationship("FlightPlan", back_populates="waypoints")

    __table_args__ = (
        Index("ix_waypoint_flight_plan_id_sequence_order", "flight_plan_id", "sequence_order", unique=True),
    )
```

# app/schemas/__init__.py

```py
from .token import Token, TokenPayload
from .msg import Msg

from .user import (
    UserBase,
    UserCreateSolo,
    UserCreateOrganizationPilot,
    UserCreate, # Generic internal create
    UserUpdate,
    UserRead,
    UserRole, # Re-export enum for API use
    UserStatusUpdate,
    OrganizationAdminRegister,
    OrganizationAdminRegisterResponse,
)
from .organization import (
    OrganizationBase,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationRead,
    OrganizationReadWithDetails, # Placeholder, can extend OrganizationRead
)
from .drone import (
    DroneBase,
    DroneCreate,
    DroneUpdate,
    DroneRead,
    DroneOwnerType, # Re-export
    DroneStatus,    # Re-export
    UserAssignToDrone,
    UserUnassignFromDrone,
    UserDroneAssignmentRead, # For response of assignment
)
from .waypoint import (
    WaypointBase,
    WaypointCreate,
    WaypointRead,
    WaypointUpdate, # If needed
)
from .flight_plan import (
    FlightPlanBase,
    FlightPlanCreate,
    FlightPlanUpdate, # If needed for general updates by pilot
    FlightPlanRead,
    FlightPlanReadWithWaypoints,
    FlightPlanStatus, # Re-export
    FlightPlanStatusUpdate,
    FlightPlanCancel,
    FlightPlanHistory,
)
from .telemetry import (
    TelemetryLogBase,
    TelemetryLogCreate,
    TelemetryLogRead,
    LiveTelemetryMessage, # For WebSocket
)
from .restricted_zone import (
    RestrictedZoneBase,
    RestrictedZoneCreate,
    RestrictedZoneUpdate,
    RestrictedZoneRead,
    NFZGeometryType, # Re-export
)
from .utility import (
    WeatherInfo,
    RemoteIdBroadcast,
)
```

# app/schemas/drone.py

```py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.drone import DroneOwnerType, DroneStatus # Import enums

# Shared properties
class DroneBase(BaseModel):
    brand: str
    model: str
    serial_number: str

# Properties to receive via API on creation
class DroneCreate(DroneBase):
    # Ownership is determined by authenticated user's role and this optional field
    organization_id: Optional[int] = None # If Org Admin registers for their org

# Properties to receive via API on update
class DroneUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    # serial_number: Optional[str] = None # Typically not updatable
    current_status: Optional[DroneStatus] = None

# Properties to return to client
class DroneRead(DroneBase):
    id: int
    owner_type: DroneOwnerType
    organization_id: Optional[int] = None
    solo_owner_user_id: Optional[int] = None
    current_status: DroneStatus
    last_seen_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserAssignToDrone(BaseModel):
    user_id_to_assign: int

class UserUnassignFromDrone(BaseModel):
    user_id_to_unassign: int

class UserDroneAssignmentRead(BaseModel):
    user_id: int
    drone_id: int
    assigned_at: datetime # This comes from Base.created_at in our model compromise

    class Config:
        from_attributes = True
```

# app/schemas/flight_plan.py

```py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.flight_plan import FlightPlanStatus # Import enum
from app.schemas.waypoint import WaypointCreate, WaypointRead
from app.schemas.drone import DroneRead
from app.schemas.user import UserRead
from app.schemas.telemetry import TelemetryLogRead # Forward reference

# Shared properties
class FlightPlanBase(BaseModel):
    drone_id: int
    planned_departure_time: datetime
    planned_arrival_time: datetime
    notes: Optional[str] = None

# Properties to receive via API on creation
class FlightPlanCreate(FlightPlanBase):
    waypoints: List[WaypointCreate]

# Properties to receive via API on update (e.g., by pilot before approval)
# This is not explicitly in endpoints.md but could be useful
class FlightPlanUpdate(BaseModel):
    planned_departure_time: Optional[datetime] = None
    planned_arrival_time: Optional[datetime] = None
    notes: Optional[str] = None
    waypoints: Optional[List[WaypointCreate]] = None # Allow updating waypoints before approval

# Properties to return to client
class FlightPlanRead(FlightPlanBase):
    id: int
    user_id: int # Submitter
    organization_id: Optional[int] = None
    status: FlightPlanStatus
    actual_departure_time: Optional[datetime] = None
    actual_arrival_time: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    approved_by_organization_admin_id: Optional[int] = None
    approved_by_authority_admin_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    drone: Optional[DroneRead] = None  # Uncomment this line
    # submitter_user: Optional[UserRead] = None # Can be added

    class Config:
        from_attributes = True

class FlightPlanReadWithWaypoints(FlightPlanRead):
    waypoints: List[WaypointRead] = []
    drone: Optional[DroneRead] = None # Example of richer data
    submitter_user: Optional[UserRead] = None # Example

class FlightPlanStatusUpdate(BaseModel):
    status: FlightPlanStatus
    rejection_reason: Optional[str] = None

class FlightPlanCancel(BaseModel):
    reason: Optional[str] = None

class FlightPlanHistory(BaseModel):
    flight_plan_details: FlightPlanReadWithWaypoints
    # planned_waypoints: List[WaypointRead] # Already in FlightPlanReadWithWaypoints
    actual_telemetry: List["TelemetryLogRead"] # Forward reference

# Resolve forward reference
FlightPlanHistory.model_rebuild()
```

# app/schemas/msg.py

```py
from pydantic import BaseModel

class Msg(BaseModel):
    message: str
```

# app/schemas/organization.py

```py
from pydantic import BaseModel, Field
from typing import Optional, List, Annotated
from datetime import datetime
from app.schemas.user import UserRead # For admin_user and users list
# Shared properties
class OrganizationBase(BaseModel):
    name: str
    bin: Annotated[str, Field(min_length=12, max_length=12)]
    company_address: str
    city: str

# Properties to receive via API on creation (handled by /auth/register/organization-admin)
# class OrganizationCreate(OrganizationBase):
#     admin_id: Optional[int] = None # Set after admin user is created

# Properties to receive via API on update
class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    bin: Optional[str] = None
    company_address: Optional[str] = None
    city: Optional[str] = None
    new_admin_id: Optional[int] = None # To change the organization admin

# Properties to return to client
class OrganizationRead(OrganizationBase):
    id: int
    admin_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # admin_user: Optional[UserRead] = None # Can be added if needed

    class Config:
        from_attributes = True

class OrganizationReadWithDetails(OrganizationRead):
    # users: List[UserRead] = [] # Example: list of pilots
    # drones: List["DroneRead"] = [] # Example: list of drones
    admin_user: Optional[UserRead] = None
    # Add more details as needed based on endpoint III.2
    pass

# For OrganizationAdminRegisterResponse to resolve forward reference
from app.schemas.user import UserRead

class OrganizationCreate(OrganizationBase): # Ensure this schema is properly defined
    admin_id: Optional[int] = None


```

# app/schemas/restricted_zone.py

```py
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from app.models.restricted_zone import NFZGeometryType # Import enum

# Shared properties
class RestrictedZoneBase(BaseModel):
    name: str
    description: Optional[str] = None
    geometry_type: NFZGeometryType
    definition_json: Dict[str, Any] # e.g., {"center_lat": ..., "radius_m": ...} or {"coordinates": ...}
    min_altitude_m: Optional[float] = Field(default=None, ge=0)
    max_altitude_m: Optional[float] = Field(default=None, ge=0) # Could be validated against min_alt

# Properties to receive via API on creation
class RestrictedZoneCreate(RestrictedZoneBase):
    pass

# Properties to receive via API on update
class RestrictedZoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    geometry_type: Optional[NFZGeometryType] = None
    definition_json: Optional[Dict[str, Any]] = None
    min_altitude_m: Optional[float] = None
    max_altitude_m: Optional[float] = None
    is_active: Optional[bool] = None

# Properties to return to client
class RestrictedZoneRead(RestrictedZoneBase):
    id: int
    is_active: bool
    created_by_authority_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

# app/schemas/telemetry.py

```py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Shared properties for DB log
class TelemetryLogBase(BaseModel):
    timestamp: datetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude_m: float
    speed_mps: Optional[float] = Field(default=None, ge=0)
    heading_degrees: Optional[float] = Field(default=None, ge=0, le=360)
    status_message: Optional[str] = None

# Properties to receive for creating a log entry (usually internal)
class TelemetryLogCreate(TelemetryLogBase):
    flight_plan_id: Optional[int] = None # Can be null if not tied to a plan initially
    drone_id: int

# Properties to return to client for a log entry
class TelemetryLogRead(TelemetryLogBase):
    id: int # BigInt in DB, int here is fine for Pydantic
    flight_plan_id: Optional[int] = None
    drone_id: int
    created_at: datetime # from Base

    class Config:
        from_attributes = True

# Message format for WebSocket broadcast
class LiveTelemetryMessage(BaseModel):
    flight_id: int # flight_plan_id
    drone_id: int
    lat: float
    lon: float
    alt: float # altitude_m
    timestamp: datetime
    speed: Optional[float] = None # speed_mps
    heading: Optional[float] = None # heading_degrees
    # status: str # e.g., "ON_SCHEDULE/ALERT_NFZ/SIGNAL_LOST" -> from TelemetryLog.status_message
    status_message: Optional[str] = None
```

# app/schemas/token.py

```py
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
```

# app/schemas/user.py

```py
import app
from pydantic import BaseModel, EmailStr, constr, Field
from typing import Optional, List, Annotated, TYPE_CHECKING
from datetime import datetime
from app.models.user import UserRole # Import the enum from models
if TYPE_CHECKING:
    from app.schemas.organization import OrganizationRead
# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[Annotated[str, constr(max_length=20)]] = None
    iin: Optional[Annotated[str, constr(min_length=12, max_length=12)]] = None # Kazakhstani IIN

# Properties to receive via API on creation (generic)
class UserCreate(UserBase):
    password: str
    role: UserRole
    organization_id: Optional[int] = None
    
# Properties for Solo Pilot Registration
class UserCreateSolo(UserBase):
    password: str

# Properties for Organization Pilot Registration
class UserCreateOrganizationPilot(UserBase):
    password: str
    organization_id: int

# Properties for Organization Admin Registration (part of OrganizationAdminRegister)
class AdminUserCreateForOrg(UserBase):
    password: str # Renamed from admin_password for consistency

# Properties to receive via API on update
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[Annotated[str, constr(max_length=20)]] = None
    current_password: Optional[str] = None # Required if changing password
    new_password: Optional[str] = None

# Properties to return to client
class UserRead(UserBase):
    id: int
    role: UserRole
    is_active: bool
    organization_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# For registering an organization and its admin
class OrganizationAdminRegister(BaseModel):
    org_name: str
    bin: Annotated[str, constr(min_length=12, max_length=12)]
    company_address: str
    city: str
    admin_full_name: str
    admin_email: EmailStr
    admin_password: str
    admin_phone_number: Optional[Annotated[str, constr(max_length=20)]] = None
    admin_iin: Optional[Annotated[str, constr(min_length=12, max_length=12)]] = None

class OrganizationAdminRegisterResponse(BaseModel):
    organization: "OrganizationRead" # Use fully qualified forward ref for clarity
    admin_user: UserRead

class UserStatusUpdate(BaseModel):
    is_active: bool
    
from app.schemas.organization import OrganizationRead # Import the actual class for Pydantic to resolve
OrganizationAdminRegisterResponse.model_rebuild()
```

# app/schemas/utility.py

```py
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class WeatherInfo(BaseModel):
    # Example fields, adjust based on actual weather API response
    lat: float
    lon: float
    temp: float # Celsius
    wind_speed: float # m/s
    wind_direction: float # degrees
    conditions_summary: str
    timestamp: datetime

class RemoteIdBroadcast(BaseModel):
    drone_serial_number: str
    current_lat: float
    current_lon: float # Corrected from lon
    current_alt: float # Corrected from alt
    timestamp: datetime
    operator_id_proxy: Optional[str] = None # e.g., masked user ID or org ID
    control_station_location_proxy: Optional[Dict[str, float]] = None # e.g., {"lat": ..., "lon": ...}
```

# app/schemas/waypoint.py

```py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Shared properties
class WaypointBase(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude_m: float = Field(..., gt=0) # Altitude above ground level
    sequence_order: int = Field(..., ge=0)

# Properties to receive via API on creation
class WaypointCreate(WaypointBase):
    pass

# Properties to receive via API on update (if waypoints are updatable post-creation)
class WaypointUpdate(WaypointBase):
    pass

# Properties to return to client
class WaypointRead(WaypointBase):
    id: int
    flight_plan_id: int
    # created_at: datetime # from Base, if needed
    # updated_at: datetime # from Base, if needed

    class Config:
        from_attributes = True
```

# app/services/__init__.py

```py
# This file can be empty or used to import services for easier access
from .flight_service import FlightService
from .nfz_service import NFZService
from .telemetry_service import TelemetryService, ConnectionManager

flight_service = FlightService()
nfz_service = NFZService()
telemetry_service = TelemetryService() # The instance for simulation
connection_manager = ConnectionManager() # The instance for WebSocket connections
```

# app/services/flight_service.py

```py
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.flight_plan import FlightPlan, FlightPlanStatus
from app.models.drone import Drone, DroneStatus
from app.schemas.flight_plan import FlightPlanCreate
from app.crud import flight_plan as crud_flight_plan
from app.crud import drone as crud_drone
from app.services.nfz_service import NFZService # For NFZ checks
from app.services.telemetry_service import telemetry_service # To start simulation
from app.models.drone import DroneStatus

class FlightService:
    def __init__(self, nfz_service: NFZService = NFZService()): # Allow injecting for tests
        self.nfz_service = nfz_service

    def submit_flight_plan(
        self, 
        db: Session, 
        *, 
        flight_plan_in: FlightPlanCreate, 
        submitter: User
    ) -> FlightPlan:
        # 1. Validate Drone
        db_drone = crud_drone.get(db, id=flight_plan_in.drone_id)
        if not db_drone:
            raise ValueError("Drone not found.")
        
        # Check drone ownership/assignment based on submitter's role
        if submitter.role == UserRole.SOLO_PILOT:
            if db_drone.solo_owner_user_id != submitter.id:
                raise ValueError("Solo pilot can only submit flights for their own drones.")
            organization_id = None
        elif submitter.role == UserRole.ORGANIZATION_PILOT:
            if not submitter.organization_id or db_drone.organization_id != submitter.organization_id:
                raise ValueError("Organization pilot can only submit flights for drones in their organization.")
            # Check if pilot is assigned to this drone
            assignment = crud_drone.user_drone_assignment.get_assignment(db, user_id=submitter.id, drone_id=db_drone.id)
            if not assignment:
                # Or if org allows any pilot to use any org drone without explicit assignment
                # This rule needs clarification from requirements. Assuming explicit assignment for now.
                raise ValueError("Organization pilot is not assigned to this drone.")
            organization_id = submitter.organization_id
        else:
            raise ValueError("Invalid user role for submitting flight plans.")

        # 2. Perform NFZ Pre-check (Simplified)
        # This would involve checking waypoints against RestrictedZone geometries
        # For now, a placeholder
        nfz_violations = self.nfz_service.check_flight_plan_against_nfzs(db, flight_plan_in.waypoints)
        if nfz_violations:
            # For MVP, we might just raise an error or log it.
            # A real system might allow submission with warnings or require modification.
            raise ValueError(f"Flight plan intersects with No-Fly Zones: {', '.join(nfz_violations)}")

        # 3. Determine initial status
        initial_status: FlightPlanStatus
        if submitter.role == UserRole.SOLO_PILOT:
            initial_status = FlightPlanStatus.PENDING_AUTHORITY_APPROVAL
        elif submitter.role == UserRole.ORGANIZATION_PILOT:
            # Assuming two-step approval for organizations
            initial_status = FlightPlanStatus.PENDING_ORG_APPROVAL 
        else: # Should not happen due to earlier check
            raise ValueError("Cannot determine initial flight plan status for user role.")

        # 4. Create Flight Plan
        created_flight_plan = crud_flight_plan.create_with_waypoints(
            db, 
            obj_in=flight_plan_in, 
            user_id=submitter.id,
            organization_id=organization_id,
            initial_status=initial_status
        )
        return created_flight_plan

    def update_flight_plan_status(
        self,
        db: Session,
        *,
        flight_plan_id: int,
        new_status: FlightPlanStatus,
        actor: User, # User performing the action
        rejection_reason: str | None = None,
    ) -> FlightPlan:
        db_flight_plan = crud_flight_plan.get(db, id=flight_plan_id)
        if not db_flight_plan:
            raise ValueError("Flight plan not found.")

        current_status = db_flight_plan.status
        is_org_approval_step = False

        # State transition logic based on actor's role and current status
        if actor.role == UserRole.ORGANIZATION_ADMIN:
            if db_flight_plan.organization_id != actor.organization_id:
                raise ValueError("Organization Admin cannot modify flight plans outside their organization.")
            
            if current_status == FlightPlanStatus.PENDING_ORG_APPROVAL:
                if new_status == FlightPlanStatus.PENDING_AUTHORITY_APPROVAL: # Org Admin approves, sends to Authority
                    is_org_approval_step = True
                elif new_status == FlightPlanStatus.REJECTED_BY_ORG:
                    if not rejection_reason:
                        raise ValueError("Rejection reason required when rejecting by organization.")
                # Org admin might also directly approve if no authority step is needed (e.g. for certain flights)
                # elif new_status == FlightPlanStatus.APPROVED: # Org Admin self-approves
                #     is_org_approval_step = True 
                else:
                    raise ValueError(f"Invalid status transition from {current_status} to {new_status} by Organization Admin.")
            else:
                raise ValueError(f"Organization Admin cannot change status from {current_status}.")

        elif actor.role == UserRole.AUTHORITY_ADMIN:
            valid_previous_statuses_for_authority = [
                FlightPlanStatus.PENDING_AUTHORITY_APPROVAL,
                FlightPlanStatus.PENDING_ORG_APPROVAL # If solo pilot or orgs submit directly to authority
            ]
            if current_status in valid_previous_statuses_for_authority:
                if new_status == FlightPlanStatus.APPROVED:
                    pass # Authority approves
                elif new_status == FlightPlanStatus.REJECTED_BY_AUTHORITY:
                    if not rejection_reason:
                        raise ValueError("Rejection reason required when rejecting by authority.")
                else:
                    raise ValueError(f"Invalid status transition from {current_status} to {new_status} by Authority Admin.")
            else:
                raise ValueError(f"Authority Admin cannot change status from {current_status}.")
        else:
            raise ValueError("User role not authorized to update flight plan status.")

        return crud_flight_plan.update_status(
            db, 
            db_obj=db_flight_plan, 
            new_status=new_status, 
            rejection_reason=rejection_reason,
            approver_id=actor.id,
            is_org_approval=is_org_approval_step
        )

    def start_flight(self, db: Session, *, flight_plan_id: int, pilot: User) -> FlightPlan:
        db_flight_plan = crud_flight_plan.get(db, id=flight_plan_id)
        if not db_flight_plan:
            raise ValueError("Flight plan not found.")
        if db_flight_plan.user_id != pilot.id:
            raise ValueError("Only the submitting pilot can start the flight.")
        if db_flight_plan.status != FlightPlanStatus.APPROVED:
            raise ValueError(f"Flight plan must be APPROVED to start. Current status: {db_flight_plan.status}")

        started_flight = crud_flight_plan.start_flight(db, db_obj=db_flight_plan)
        
        # Start telemetry simulation for this flight
        telemetry_service.start_flight_simulation(db, flight_plan=started_flight)
        
        return started_flight

    def cancel_flight(
        self, 
        db: Session, 
        *, 
        flight_plan_id: int, 
        actor: User, 
        reason: str | None = None
    ) -> FlightPlan:
        db_flight_plan = crud_flight_plan.get(db, id=flight_plan_id)
        if not db_flight_plan:
            raise ValueError("Flight plan not found.")

        cancelled_by_role_type = "UNKNOWN" # For status CANCELLED_BY_ADMIN or CANCELLED_BY_PILOT

        if actor.role in [UserRole.SOLO_PILOT, UserRole.ORGANIZATION_PILOT]:
            if db_flight_plan.user_id != actor.id:
                raise ValueError("Pilot can only cancel their own flight plans.")
            if db_flight_plan.status not in [FlightPlanStatus.PENDING_ORG_APPROVAL, FlightPlanStatus.PENDING_AUTHORITY_APPROVAL, FlightPlanStatus.APPROVED]:
                raise ValueError(f"Pilot cannot cancel flight in status {db_flight_plan.status}.")
            cancelled_by_role_type = "PILOT"
        
        elif actor.role == UserRole.ORGANIZATION_ADMIN:
            if db_flight_plan.organization_id != actor.organization_id:
                raise ValueError("Organization Admin cannot cancel flights outside their organization.")
            # Org Admin can cancel flights in more states, e.g., PENDING_*, APPROVED, maybe even ACTIVE (emergency)
            # Add specific state checks if needed.
            cancelled_by_role_type = "ADMIN"

        elif actor.role == UserRole.AUTHORITY_ADMIN:
            # Authority Admin can cancel flights in most states
            cancelled_by_role_type = "ADMIN"
        else:
            raise ValueError("User role not authorized to cancel this flight plan.")

        # If flight was active, stop simulation
        if db_flight_plan.status == FlightPlanStatus.ACTIVE:
            telemetry_service.stop_flight_simulation(flight_plan_id)
            # Also update drone status if it was active
            db_drone = crud_drone.get(db, id=db_flight_plan.drone_id)
            if db_drone and db_drone.current_status == DroneStatus.ACTIVE:
                crud_drone.update(db, db_obj=db_drone, obj_in={"current_status": DroneStatus.IDLE})


        return crud_flight_plan.cancel_flight(db, db_obj=db_flight_plan, cancelled_by_role=cancelled_by_role_type, reason=reason)

flight_service = FlightService() # Singleton instance
```

# app/services/nfz_service.py

```py
# app/services/nfz_service.py
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.crud import restricted_zone as crud_restricted_zone
from app.schemas.waypoint import WaypointCreate

class NFZService:
    def check_flight_plan_against_nfzs(self, db: Session, waypoints: List[WaypointCreate]) -> List[str]:
        """
        Check if flight plan waypoints intersect with No-Fly Zones.
        Returns list of NFZ names that are violated.
        """
        # For MVP, this is a placeholder implementation
        # In a real system, you'd check waypoint coordinates against NFZ geometries
        
        # Get all active NFZs
        active_nfzs = crud_restricted_zone.get_all_active_zones(db)
        
        violations = []
        
        # Placeholder logic - you'd implement proper geometric intersection here
        for waypoint in waypoints:
            for nfz in active_nfzs:
                # Simple placeholder check - in reality you'd use proper geometry libraries
                # like Shapely to check if point is inside polygon/circle
                if self._simple_point_in_nfz_check(waypoint, nfz):
                    violations.append(nfz.name)
        
        return list(set(violations))  # Remove duplicates
    
    def check_point_against_nfzs(self, db: Session, lat: float, lon: float, alt: float) -> List[Dict[str, Any]]:
        """
        Check if a single point intersects with No-Fly Zones.
        Returns list of NFZ details that are breached.
        """
        active_nfzs = crud_restricted_zone.get_all_active_zones(db)
        
        breaches = []
        for nfz in active_nfzs:
            if self._point_in_nfz(lat, lon, alt, nfz):
                breaches.append({
                    'name': nfz.name,
                    'id': nfz.id,
                    'description': nfz.description
                })
        
        return breaches
    
    def _simple_point_in_nfz_check(self, waypoint: WaypointCreate, nfz) -> bool:
        """
        Placeholder for geometric intersection check.
        In a real implementation, you'd use proper geometric calculations.
        """
        # This is a very basic placeholder - always returns False for now
        # Real implementation would:
        # 1. Parse nfz.definition_json based on nfz.geometry_type
        # 2. Use geometric libraries to check intersection
        # 3. Consider altitude constraints (min_altitude_m, max_altitude_m)
        return False
    
    def _point_in_nfz(self, lat: float, lon: float, alt: float, nfz) -> bool:
        """
        Check if a point is inside an NFZ.
        Placeholder implementation.
        """
        # Check altitude constraints first
        if nfz.min_altitude_m is not None and alt < nfz.min_altitude_m:
            return False
        if nfz.max_altitude_m is not None and alt > nfz.max_altitude_m:
            return False
        
        # Placeholder for geometric check
        # Real implementation would check if lat/lon is inside the NFZ geometry
        return False

nfz_service = NFZService()
```

# app/services/telemetry_service.py

```py
import asyncio
import random
import time
from datetime import datetime, timezone
from typing import List, Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.models.flight_plan import FlightPlan, FlightPlanStatus
from app.models.drone import Drone, DroneStatus
from app.models.telemetry_log import TelemetryLog
from app.schemas.telemetry import TelemetryLogCreate, LiveTelemetryMessage
from app.crud import telemetry_log as crud_telemetry_log
from app.crud import drone as crud_drone
from app.crud import flight_plan as crud_flight_plan # For completing flight
from app.db.session import SessionLocal # To create new sessions in async tasks
from app.services.nfz_service import nfz_service # For in-flight NFZ checks


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        # For targeted messages if needed in future (e.g., per organization_id)
        # self.scoped_connections: Dict[Any, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            self.disconnect(websocket)
        except RuntimeError: # Handle cases where connection might be closing
            self.disconnect(websocket)


    async def broadcast(self, message_data: dict): # Changed to accept dict for JSON
        # message_json = json.dumps(message_data) # Pydantic model will be converted by FastAPI
        disconnected_sockets = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message_data)
            except (WebSocketDisconnect, RuntimeError):
                disconnected_sockets.append(connection)
        
        for ws in disconnected_sockets:
            self.disconnect(ws)


class TelemetryService:
    def __init__(self):
        self.active_simulations: Dict[int, asyncio.Task] = {} # flight_plan_id -> Task
        self.simulation_stop_events: Dict[int, asyncio.Event] = {} # flight_plan_id -> Event

    async def _simulate_flight_telemetry(self, flight_plan_id: int, stop_event: asyncio.Event):
        """Simulates telemetry for a given flight plan."""
        # Create a new DB session for this long-running task
        # This is important because the original request's session will be closed.
        db: Session = SessionLocal()
        try:
            fp = crud_flight_plan.get_flight_plan_with_details(db, id=flight_plan_id)
            if not fp or not fp.waypoints:
                print(f"Flight plan {flight_plan_id} not found or no waypoints for simulation.")
                return

            # Update drone status to ACTIVE
            db_drone = crud_drone.get(db, id=fp.drone_id)
            if db_drone:
                db_drone.current_status = DroneStatus.ACTIVE
                db.add(db_drone)
                db.commit()
                db.refresh(db_drone)

            current_waypoint_index = 0
            num_waypoints = len(fp.waypoints)
            
            # Simplified: Assume linear interpolation between waypoints
            # A real simulation would be much more complex (speed, turns, ascent/descent rates)
            
            # Simulation loop
            while current_waypoint_index < num_waypoints and not stop_event.is_set():
                if current_waypoint_index >= len(fp.waypoints): # Should not happen if loop condition is correct
                    break
                
                target_waypoint = fp.waypoints[current_waypoint_index]
                
                # Simulate movement towards target_waypoint (very basic)
                # For now, let's just "jump" to waypoints every few seconds
                # In a real sim, you'd calculate intermediate points.
                
                lat = target_waypoint.latitude
                lon = target_waypoint.longitude
                alt = target_waypoint.altitude_m
                timestamp = datetime.now(timezone.utc)
                speed_mps = random.uniform(5, 15) # m/s
                heading_degrees = random.uniform(0, 359.9)
                status_message = "ON_SCHEDULE"

                # In-flight NFZ check (using the new DB session)
                nfz_breaches = nfz_service.check_point_against_nfzs(db, lat, lon, alt)
                if nfz_breaches:
                    status_message = f"ALERT_NFZ: Breached {', '.join([b['name'] for b in nfz_breaches])}"
                    # Potentially trigger other alert mechanisms

                # Create and store telemetry log
                log_entry = TelemetryLogCreate(
                    flight_plan_id=fp.id,
                    drone_id=fp.drone_id,
                    timestamp=timestamp,
                    latitude=lat,
                    longitude=lon,
                    altitude_m=alt,
                    speed_mps=speed_mps,
                    heading_degrees=heading_degrees,
                    status_message=status_message,
                )
                db_log_entry = crud_telemetry_log.create(db, obj_in=log_entry)

                # Update drone's last seen and last telemetry
                if db_drone:
                    db_drone.last_seen_at = timestamp
                    db_drone.last_telemetry_id = db_log_entry.id # type: ignore
                    db.add(db_drone)
                    db.commit() # Commit frequently for updates to be visible

                # Broadcast telemetry via WebSocket
                live_message = LiveTelemetryMessage(
                    flight_id=fp.id,
                    drone_id=fp.drone_id,
                    lat=lat,
                    lon=lon,
                    alt=alt,
                    timestamp=timestamp,
                    speed=speed_mps,
                    heading=heading_degrees,
                    status_message=status_message,
                )
                await connection_manager.broadcast(live_message.model_dump())
                
                # Move to next waypoint after a delay
                await asyncio.sleep(5) # Telemetry update interval
                current_waypoint_index += 1

                if stop_event.is_set():
                    print(f"Simulation for flight {flight_plan_id} stopped by event.")
                    status_message = "FLIGHT_INTERRUPTED" # Or similar
                    # Log one final telemetry point indicating interruption if needed
                    break
            
            # Simulation finished (either completed waypoints or stopped)
            final_status_message = "FLIGHT_COMPLETED"
            if stop_event.is_set() and current_waypoint_index < num_waypoints:
                final_status_message = "FLIGHT_CANCELLED_OR_STOPPED"

            # Update flight plan status to COMPLETED if all waypoints were reached
            # and it wasn't externally stopped (e.g., by cancellation)
            # Re-fetch flight plan to get its current status from DB
            db.refresh(fp) # Refresh fp object
            if not stop_event.is_set() and fp.status == FlightPlanStatus.ACTIVE:
                crud_flight_plan.complete_flight(db, db_obj=fp)
                final_status_message = "FLIGHT_COMPLETED"
            
            # Update drone status to IDLE
            if db_drone:
                db_drone.current_status = DroneStatus.IDLE
                db.add(db_drone)
                db.commit()
            
            print(f"Simulation for flight {flight_plan_id} ended with status: {final_status_message}.")

        except Exception as e:
            print(f"Error during flight simulation for {flight_plan_id}: {e}")
            # Attempt to set drone to UNKNOWN or IDLE on error
            if 'db_drone' in locals() and db_drone:
                db_drone.current_status = DroneStatus.UNKNOWN
                db.add(db_drone)
                db.commit()
        finally:
            db.close() # Ensure the session is closed for this task
            if flight_plan_id in self.active_simulations:
                del self.active_simulations[flight_plan_id]
            if flight_plan_id in self.simulation_stop_events:
                del self.simulation_stop_events[flight_plan_id]


    def start_flight_simulation(self, db: Session, flight_plan: FlightPlan):
        if flight_plan.id in self.active_simulations:
            print(f"Simulation for flight {flight_plan.id} is already active.")
            return

        stop_event = asyncio.Event()
        self.simulation_stop_events[flight_plan.id] = stop_event
        
        # We pass flight_plan.id instead of the whole object
        # because the object might become stale if the DB session that loaded it closes.
        # The async task will create its own DB session.
        task = asyncio.create_task(self._simulate_flight_telemetry(flight_plan.id, stop_event))
        self.active_simulations[flight_plan.id] = task
        print(f"Started simulation for flight {flight_plan.id}")

    def stop_flight_simulation(self, flight_plan_id: int):
        if flight_plan_id in self.simulation_stop_events:
            self.simulation_stop_events[flight_plan_id].set() # Signal the task to stop
            print(f"Stop signal sent for flight simulation {flight_plan_id}")
        else:
            print(f"No active simulation found to stop for flight {flight_plan_id}")
        
        # Task cancellation is an option too, but graceful stop via event is preferred.
        # if flight_plan_id in self.active_simulations:
        #     self.active_simulations[flight_plan_id].cancel()

telemetry_service = TelemetryService() # Singleton instance
connection_manager = ConnectionManager() # Singleton instance
```

# db_test_report_20250525_015516.json

```json
{
  "test_suite": "UTM Database Comprehensive Test",
  "timestamp": "2025-05-24T20:55:16.145386+00:00",
  "database_url": "localhost:5432/utm_db",
  "test_data_created": {
    "users": [
      2,
      3,
      4,
      5,
      6,
      7,
      8,
      9,
      10,
      11,
      12,
      13,
      14,
      15,
      16
    ],
    "organizations": [
      1,
      2,
      3
    ],
    "drones": [
      1,
      2,
      3,
      4,
      5,
      6,
      7,
      8,
      9,
      10,
      11,
      12,
      13,
      14,
      15,
      16,
      17,
      18,
      19
    ],
    "flight_plans": [
      1,
      2,
      3,
      4,
      5,
      6,
      7,
      8,
      9,
      10,
      11,
      12,
      13,
      14,
      15,
      16
    ],
    "waypoints": [
      1,
      2,
      3,
      4,
      5,
      6,
      7,
      8,
      9,
      10,
      11,
      12,
      13,
      14,
      15,
      16,
      17,
      18,
      19,
      20,
      21,
      22,
      23,
      24,
      25,
      26,
      27,
      28,
      29,
      30,
      31,
      32,
      33,
      34,
      35,
      36,
      37,
      38,
      39,
      40,
      41,
      42
    ],
    "telemetry_logs": [],
    "restricted_zones": [
      1,
      2,
      3
    ],
    "user_drone_assignments": [
      [
        6,
        1
      ],
      [
        6,
        2
      ],
      [
        7,
        1
      ],
      [
        7,
        2
      ],
      [
        8,
        4
      ],
      [
        8,
        5
      ],
      [
        9,
        4
      ],
      [
        9,
        5
      ],
      [
        10,
        7
      ],
      [
        10,
        8
      ],
      [
        11,
        7
      ],
      [
        11,
        8
      ]
    ]
  },
  "database_schema_info": {
    "users": {
      "total_records": 1
    },
    "organizations": {
      "total_records": 0
    },
    "drones": {
      "total_records": 0
    },
    "flight_plans": {
      "total_records": 0
    },
    "waypoints": {
      "total_records": 0
    },
    "telemetry_logs": {
      "total_records": 0
    },
    "restricted_zones": {
      "total_records": 0
    },
    "user_drone_assignments": {
      "total_records": 0
    }
  }
}
```

# db_test_report_20250525_024019.json

```json
{
  "test_suite": "UTM Database Comprehensive Test",
  "timestamp": "2025-05-24T21:40:19.661556+00:00",
  "database_url": "localhost:5432/utm_db",
  "test_data_created": {
    "users": [],
    "organizations": [],
    "drones": [],
    "flight_plans": [],
    "waypoints": [],
    "telemetry_logs": [],
    "restricted_zones": [],
    "user_drone_assignments": []
  },
  "database_schema_info": {
    "users": {
      "total_records": 17
    },
    "organizations": {
      "total_records": 4
    },
    "drones": {
      "total_records": 20
    },
    "flight_plans": {
      "total_records": 16
    },
    "waypoints": {
      "total_records": 42
    },
    "telemetry_logs": {
      "total_records": 15
    },
    "restricted_zones": {
      "total_records": 3
    },
    "user_drone_assignments": {
      "total_records": 12
    }
  }
}
```

# docker-compose.yml

```yml
version: '3.8'

services:
  db:
    image: postgres:15
    container_name: utm_postgres_db
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-utm_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-utm_password}
      POSTGRES_DB: ${POSTGRES_DB:-utm_db}
    ports:
      - "5432:5432" # Expose PostgreSQL port to host (optional, for direct access)
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-utm_user} -d ${POSTGRES_DB:-utm_db}"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: utm_fastapi_app
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/app # Mount current directory to /app in container for live reload
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER:-utm_user}:${POSTGRES_PASSWORD:-utm_password}@db/${POSTGRES_DB:-utm_db}
      - SECRET_KEY=${SECRET_KEY:-your_super_secret_key_please_change_this_in_production}
      - ALGORITHM=${ALGORITHM:-HS256}
      - ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES:-60}
      - API_V1_STR=${API_V1_STR:-/api/v1}
      - PROJECT_NAME=${PROJECT_NAME:-UTM API}
      - FIRST_SUPERUSER_EMAIL=${FIRST_SUPERUSER_EMAIL:-admin@example.com}
      - FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD:-changethis}
      - FIRST_SUPERUSER_FULL_NAME=${FIRST_SUPERUSER_FULL_NAME:-Authority Admin}
      - FIRST_SUPERUSER_IIN=${FIRST_SUPERUSER_IIN:-000000000000}
      - WS_TELEMETRY_PATH=${WS_TELEMETRY_PATH:-/ws/telemetry}
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

# Dockerfile

```
FROM python:3.10-slim

WORKDIR /app

# Set environment variables to prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies (if any, e.g., for psycopg2 if not using -binary)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./alembic.ini /app/alembic.ini
COPY ./alembic /app/alembic
COPY ./app /app/app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Uvicorn
# The --host 0.0.0.0 is important to make it accessible from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

# requirements.txt

```txt
alembic==1.16.1
annotated-types==0.7.0
anyio==4.9.0
bcrypt==4.3.0
certifi==2025.4.26
cffi==1.17.1
click==8.1.8
cryptography==45.0.2
dnspython==2.7.0
ecdsa==0.19.1
email_validator==2.2.0
fastapi==0.115.12
fastapi-cli==0.0.7
greenlet==3.2.2
h11==0.16.0
httpcore==1.0.9
httptools==0.6.4
httpx==0.28.1
idna==3.10
itsdangerous==2.2.0
Jinja2==3.1.6
Mako==1.3.10
markdown-it-py==3.0.0
MarkupSafe==3.0.2
mdurl==0.1.2
orjson==3.10.18
passlib==1.7.4
psycopg2-binary==2.9.10
pyasn1==0.4.8
pycparser==2.22
pydantic==2.11.5
pydantic-extra-types==2.10.4
pydantic-settings==2.9.1
pydantic_core==2.33.2
Pygments==2.19.1
python-dotenv==1.1.0
python-jose==3.4.0
python-multipart==0.0.20
PyYAML==6.0.2
rich==14.0.0
rich-toolkit==0.14.6
rsa==4.9.1
shellingham==1.5.4
six==1.17.0
sniffio==1.3.1
SQLAlchemy==2.0.41
starlette==0.46.2
typer==0.15.4
typing-inspection==0.4.1
typing_extensions==4.13.2
ujson==5.10.0
uvicorn==0.34.2
uvloop==0.21.0
watchfiles==1.0.5
websockets==15.0.1

```

# test_database_full.py

```py
#!/usr/bin/env python3
"""
Comprehensive Database Test Suite for UTM Backend

This script tests all database operations, relationships, and business logic
at full scale, then cleans up all test data.

Run with: python test_database_full.py
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import SessionLocal
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.models.drone import Drone, DroneOwnerType, DroneStatus
from app.models.flight_plan import FlightPlan, FlightPlanStatus
from app.models.waypoint import Waypoint
from app.models.telemetry_log import TelemetryLog
from app.models.restricted_zone import RestrictedZone, NFZGeometryType
from app.models.user_drone_assignment import UserDroneAssignment
from app.crud import user as crud_user
from app.crud import organization as crud_organization
from app.crud import drone as crud_drone
from app.crud import flight_plan as crud_flight_plan
from app.schemas.user import UserCreate
from app.schemas.organization import OrganizationCreate
from app.schemas.drone import DroneCreate
from app.schemas.flight_plan import FlightPlanCreate
from app.schemas.waypoint import WaypointCreate
from app.schemas.telemetry import TelemetryLogCreate
from app.schemas.restricted_zone import RestrictedZoneCreate
from app.core.security import get_password_hash


class DatabaseTestSuite:
    def __init__(self):
        self.db = SessionLocal()
        self.test_data_ids = {
            'users': [],
            'organizations': [],
            'drones': [],
            'flight_plans': [],
            'waypoints': [],
            'telemetry_logs': [],
            'restricted_zones': [],
            'user_drone_assignments': []
        }
        print(f"🔗 Connected to database: {settings.DATABASE_URL}")

    def log_test(self, test_name: str, status: str = "RUNNING"):
        """Log test progress"""
        symbols = {"RUNNING": "⏳", "PASS": "✅", "FAIL": "❌", "INFO": "ℹ️"}
        print(f"{symbols.get(status, '📝')} {test_name}")

    def create_test_data(self):
        """Create comprehensive test data"""
        self.log_test("Creating comprehensive test data", "RUNNING")
        
        try:
            # 1. Create Authority Admin
            authority_admin = User(
                full_name="Test Authority Admin",
                email="authority@test.com",
                phone_number="+77012345001",
                iin="123456789001",
                hashed_password=get_password_hash("testpass123"),
                role=UserRole.AUTHORITY_ADMIN,
                is_active=True
            )
            self.db.add(authority_admin)
            self.db.flush()
            self.test_data_ids['users'].append(authority_admin.id)

            # 2. Create Organizations
            organizations = []
            for i in range(3):
                org = Organization(
                    name=f"Test Organization {i+1}",
                    bin=f"12345678901{i}",
                    company_address=f"Test Address {i+1}",
                    city=f"Test City {i+1}",
                    is_active=True
                )
                self.db.add(org)
                self.db.flush()
                organizations.append(org)
                self.test_data_ids['organizations'].append(org.id)

            # 3. Create Organization Admins
            org_admins = []
            for i, org in enumerate(organizations):
                admin = User(
                    full_name=f"Org Admin {i+1}",
                    email=f"org_admin_{i+1}@test.com",
                    phone_number=f"+7701234500{i+2}",
                    iin=f"12345678900{i+2}",
                    hashed_password=get_password_hash("testpass123"),
                    role=UserRole.ORGANIZATION_ADMIN,
                    organization_id=org.id,
                    is_active=True
                )
                self.db.add(admin)
                self.db.flush()
                org_admins.append(admin)
                self.test_data_ids['users'].append(admin.id)
                
                # Link admin to organization
                org.admin_id = admin.id
                self.db.add(org)

            # 4. Create Organization Pilots
            org_pilots = []
            for i, org in enumerate(organizations):
                for j in range(2):  # 2 pilots per organization
                    pilot = User(
                        full_name=f"Org Pilot {i+1}-{j+1}",
                        email=f"org_pilot_{i+1}_{j+1}@test.com",
                        phone_number=f"+770123451{i}{j}",
                        iin=f"1234567891{i}{j}",
                        hashed_password=get_password_hash("testpass123"),
                        role=UserRole.ORGANIZATION_PILOT,
                        organization_id=org.id,
                        is_active=True
                    )
                    self.db.add(pilot)
                    self.db.flush()
                    org_pilots.append(pilot)
                    self.test_data_ids['users'].append(pilot.id)

            # 5. Create Solo Pilots
            solo_pilots = []
            for i in range(5):
                pilot = User(
                    full_name=f"Solo Pilot {i+1}",
                    email=f"solo_pilot_{i+1}@test.com",
                    phone_number=f"+7701234520{i}",
                    iin=f"12345678920{i}",
                    hashed_password=get_password_hash("testpass123"),
                    role=UserRole.SOLO_PILOT,
                    is_active=True
                )
                self.db.add(pilot)
                self.db.flush()
                solo_pilots.append(pilot)
                self.test_data_ids['users'].append(pilot.id)

            # 6. Create Drones
            drones = []
            
            # Organization drones
            for i, org in enumerate(organizations):
                for j in range(3):  # 3 drones per organization
                    drone = Drone(
                        brand=f"DJI",
                        model=f"Phantom {i+1}{j+1}",
                        serial_number=f"ORG{i+1}_DRONE_{j+1}_SN{i:03d}{j:03d}",
                        owner_type=DroneOwnerType.ORGANIZATION,
                        organization_id=org.id,
                        current_status=DroneStatus.IDLE
                    )
                    self.db.add(drone)
                    self.db.flush()
                    drones.append(drone)
                    self.test_data_ids['drones'].append(drone.id)

            # Solo pilot drones
            for i, pilot in enumerate(solo_pilots):
                for j in range(2):  # 2 drones per solo pilot
                    drone = Drone(
                        brand="Autel",
                        model=f"EVO {i+1}{j+1}",
                        serial_number=f"SOLO{i+1}_DRONE_{j+1}_SN{i:03d}{j:03d}",
                        owner_type=DroneOwnerType.SOLO_PILOT,
                        solo_owner_user_id=pilot.id,
                        current_status=DroneStatus.IDLE
                    )
                    self.db.add(drone)
                    self.db.flush()
                    drones.append(drone)
                    self.test_data_ids['drones'].append(drone.id)

            # 7. Create User-Drone Assignments
            org_drones = [d for d in drones if d.owner_type == DroneOwnerType.ORGANIZATION]
            for i, pilot in enumerate(org_pilots):
                # Assign 2 drones to each org pilot
                org_id = pilot.organization_id
                available_drones = [d for d in org_drones if d.organization_id == org_id]
                for j in range(min(2, len(available_drones))):
                    assignment = UserDroneAssignment(
                        user_id=pilot.id,
                        drone_id=available_drones[j].id
                    )
                    self.db.add(assignment)
                    self.db.flush()
                    self.test_data_ids['user_drone_assignments'].append((pilot.id, available_drones[j].id))

            # 8. Create Restricted Zones
            nfz_data = [
                {
                    "name": "Airport NFZ",
                    "description": "Major airport restricted area",
                    "geometry_type": NFZGeometryType.CIRCLE,
                    "definition": {"center_lat": 43.23, "center_lon": 76.95, "radius_m": 5000},
                    "min_alt": 0, "max_alt": 500
                },
                {
                    "name": "Military Base NFZ",
                    "description": "Military installation restricted area",
                    "geometry_type": NFZGeometryType.POLYGON,
                    "definition": {"coordinates": [[[76.90, 43.20], [76.92, 43.20], [76.92, 43.22], [76.90, 43.22], [76.90, 43.20]]]},
                    "min_alt": 0, "max_alt": 1000
                },
                {
                    "name": "City Center NFZ",
                    "description": "Downtown restricted flying area",
                    "geometry_type": NFZGeometryType.CIRCLE,
                    "definition": {"center_lat": 43.24, "center_lon": 76.93, "radius_m": 2000},
                    "min_alt": 0, "max_alt": 150
                }
            ]

            for nfz in nfz_data:
                zone = RestrictedZone(
                    name=nfz["name"],
                    description=nfz["description"],
                    geometry_type=nfz["geometry_type"],
                    definition_json=nfz["definition"],
                    min_altitude_m=nfz["min_alt"],
                    max_altitude_m=nfz["max_alt"],
                    is_active=True,
                    created_by_authority_id=authority_admin.id
                )
                self.db.add(zone)
                self.db.flush()
                self.test_data_ids['restricted_zones'].append(zone.id)

            # 9. Create Flight Plans
            flight_plans = []
            base_time = datetime.now(timezone.utc)
            
            # Solo pilot flight plans
            for i, pilot in enumerate(solo_pilots):
                pilot_drones = [d for d in drones if d.solo_owner_user_id == pilot.id]
                if pilot_drones:
                    for j in range(2):  # 2 flight plans per solo pilot
                        waypoints_data = [
                            {"lat": 43.20 + (j*0.01), "lon": 76.90 + (j*0.01), "alt": 50 + (j*10), "order": 0},
                            {"lat": 43.21 + (j*0.01), "lon": 76.91 + (j*0.01), "alt": 60 + (j*10), "order": 1},
                            {"lat": 43.22 + (j*0.01), "lon": 76.92 + (j*0.01), "alt": 70 + (j*10), "order": 2},
                        ]
                        
                        flight_plan = FlightPlan(
                            user_id=pilot.id,
                            drone_id=pilot_drones[0].id,
                            planned_departure_time=base_time + timedelta(hours=i*2 + j),
                            planned_arrival_time=base_time + timedelta(hours=i*2 + j + 1),
                            status=FlightPlanStatus.PENDING_AUTHORITY_APPROVAL,
                            notes=f"Solo pilot test flight {i+1}-{j+1}"
                        )
                        self.db.add(flight_plan)
                        self.db.flush()
                        flight_plans.append(flight_plan)
                        self.test_data_ids['flight_plans'].append(flight_plan.id)
                        
                        # Add waypoints
                        for wp_data in waypoints_data:
                            waypoint = Waypoint(
                                flight_plan_id=flight_plan.id,
                                latitude=wp_data["lat"],
                                longitude=wp_data["lon"],
                                altitude_m=wp_data["alt"],
                                sequence_order=wp_data["order"]
                            )
                            self.db.add(waypoint)
                            self.db.flush()
                            self.test_data_ids['waypoints'].append(waypoint.id)

            # Organization pilot flight plans
            for i, pilot in enumerate(org_pilots):
                assigned_drones = [a for a in self.test_data_ids['user_drone_assignments'] if a[0] == pilot.id]
                if assigned_drones:
                    drone_id = assigned_drones[0][1]  # Use first assigned drone
                    waypoints_data = [
                        {"lat": 43.25 + (i*0.01), "lon": 76.95 + (i*0.01), "alt": 80 + (i*5), "order": 0},
                        {"lat": 43.26 + (i*0.01), "lon": 76.96 + (i*0.01), "alt": 90 + (i*5), "order": 1},
                    ]
                    
                    flight_plan = FlightPlan(
                        user_id=pilot.id,
                        drone_id=drone_id,
                        organization_id=pilot.organization_id,
                        planned_departure_time=base_time + timedelta(hours=24 + i),
                        planned_arrival_time=base_time + timedelta(hours=25 + i),
                        status=FlightPlanStatus.PENDING_ORG_APPROVAL,
                        notes=f"Organization pilot test flight {i+1}"
                    )
                    self.db.add(flight_plan)
                    self.db.flush()
                    flight_plans.append(flight_plan)
                    self.test_data_ids['flight_plans'].append(flight_plan.id)
                    
                    # Add waypoints
                    for wp_data in waypoints_data:
                        waypoint = Waypoint(
                            flight_plan_id=flight_plan.id,
                            latitude=wp_data["lat"],
                            longitude=wp_data["lon"],
                            altitude_m=wp_data["alt"],
                            sequence_order=wp_data["order"]
                        )
                        self.db.add(waypoint)
                        self.db.flush()
                        self.test_data_ids['waypoints'].append(waypoint.id)

            # 10. Create Telemetry Data
            for flight_plan in flight_plans[:5]:  # Add telemetry for first 5 flights
                drone = next(d for d in drones if d.id == flight_plan.drone_id)
                waypoints = [w for w in self.db.query(Waypoint).filter_by(flight_plan_id=flight_plan.id).all()]
                
                for i, waypoint in enumerate(waypoints):
                    telemetry = TelemetryLog(
                        flight_plan_id=flight_plan.id,
                        drone_id=drone.id,
                        timestamp=flight_plan.planned_departure_time + timedelta(minutes=i*10),
                        latitude=waypoint.latitude,
                        longitude=waypoint.longitude,
                        altitude_m=waypoint.altitude_m,
                        speed_mps=15.0 + (i * 2),
                        heading_degrees=90.0 + (i * 45),
                        status_message="ON_SCHEDULE"
                    )
                    self.db.add(telemetry)
                    self.db.flush()
                    self.test_data_ids['telemetry_logs'].append(telemetry.id)
                    
                    # Update drone's last telemetry
                    drone.last_telemetry_id = telemetry.id
                    drone.last_seen_at = telemetry.timestamp

            self.db.commit()
            self.log_test("Test data creation completed", "PASS")
            
        except Exception as e:
            self.db.rollback()
            self.log_test(f"Test data creation failed: {str(e)}", "FAIL")
            raise

    def test_crud_operations(self):
        """Test all CRUD operations"""
        self.log_test("Testing CRUD operations", "RUNNING")
        
        try:
            # Test user CRUD
            users = crud_user.user.get_multi(self.db, limit=100)
            assert len(users) >= 11, f"Expected at least 11 users, got {len(users)}"
            
            # Test organization CRUD
            orgs = crud_organization.organization.get_multi(self.db, limit=100)
            assert len(orgs) >= 3, f"Expected at least 3 organizations, got {len(orgs)}"
            
            # Test drone CRUD
            drones = crud_drone.drone.get_multi(self.db, limit=100)
            assert len(drones) >= 19, f"Expected at least 19 drones, got {len(drones)}"  # 9 org + 10 solo
            
            # Test flight plan CRUD
            flight_plans = crud_flight_plan.flight_plan.get_multi(self.db, limit=100)
            assert len(flight_plans) >= 16, f"Expected at least 16 flight plans, got {len(flight_plans)}"
            
            self.log_test("CRUD operations test", "PASS")
            
        except Exception as e:
            self.log_test(f"CRUD operations test failed: {str(e)}", "FAIL")
            raise

    def test_relationships(self):
        """Test database relationships"""
        self.log_test("Testing database relationships", "RUNNING")
        
        try:
            # Test User-Organization relationship
            org_admin = self.db.query(User).filter_by(role=UserRole.ORGANIZATION_ADMIN).first()
            assert org_admin.organization is not None, "Organization admin should have an organization"
            assert org_admin.organization.admin_id == org_admin.id, "Organization should reference admin"
            
            # Test Drone ownership relationships
            org_drone = self.db.query(Drone).filter_by(owner_type=DroneOwnerType.ORGANIZATION).first()
            assert org_drone.organization_owner is not None, "Org drone should have organization owner"
            
            solo_drone = self.db.query(Drone).filter_by(owner_type=DroneOwnerType.SOLO_PILOT).first()
            assert solo_drone.solo_owner_user is not None, "Solo drone should have user owner"
            
            # Test Flight Plan relationships
            flight_plan = self.db.query(FlightPlan).first()
            assert flight_plan.submitter_user is not None, "Flight plan should have submitter"
            assert flight_plan.drone is not None, "Flight plan should have drone"
            assert len(flight_plan.waypoints) > 0, "Flight plan should have waypoints"
            
            # Test User-Drone assignments
            assignment = self.db.query(UserDroneAssignment).first()
            assert assignment.user is not None, "Assignment should have user"
            assert assignment.drone is not None, "Assignment should have drone"
            
            # Test Telemetry relationships
            telemetry = self.db.query(TelemetryLog).first()
            if telemetry:
                assert telemetry.drone is not None, "Telemetry should have drone"
                assert telemetry.flight_plan is not None, "Telemetry should have flight plan"
            
            self.log_test("Database relationships test", "PASS")
            
        except Exception as e:
            self.log_test(f"Database relationships test failed: {str(e)}", "FAIL")
            raise

    def test_business_logic(self):
        """Test business logic constraints"""
        self.log_test("Testing business logic constraints", "RUNNING")
        
        try:
            # Test user roles and permissions
            authority_admins = self.db.query(User).filter_by(role=UserRole.AUTHORITY_ADMIN).all()
            assert len(authority_admins) >= 1, "Should have at least one authority admin"
            
            # Test organization constraints
            org_admins = self.db.query(User).filter_by(role=UserRole.ORGANIZATION_ADMIN).all()
            for admin in org_admins:
                assert admin.organization_id is not None, "Org admin must have organization"
                assert admin.organization.admin_id == admin.id, "Organization must reference admin"
            
            # Test drone ownership constraints
            org_drones = self.db.query(Drone).filter_by(owner_type=DroneOwnerType.ORGANIZATION).all()
            for drone in org_drones:
                assert drone.organization_id is not None, "Org drone must have organization"
                assert drone.solo_owner_user_id is None, "Org drone cannot have solo owner"
            
            solo_drones = self.db.query(Drone).filter_by(owner_type=DroneOwnerType.SOLO_PILOT).all()
            for drone in solo_drones:
                assert drone.solo_owner_user_id is not None, "Solo drone must have user owner"
                assert drone.organization_id is None, "Solo drone cannot have organization"
            
            # Test flight plan status workflow
            pending_org = self.db.query(FlightPlan).filter_by(status=FlightPlanStatus.PENDING_ORG_APPROVAL).all()
            pending_auth = self.db.query(FlightPlan).filter_by(status=FlightPlanStatus.PENDING_AUTHORITY_APPROVAL).all()
            
            for fp in pending_org:
                assert fp.organization_id is not None, "Org approval flight must have organization"
            
            # Test waypoint ordering
            flight_plans_with_waypoints = self.db.query(FlightPlan).join(Waypoint).all()
            for fp in flight_plans_with_waypoints:
                waypoints = sorted(fp.waypoints, key=lambda w: w.sequence_order)
                for i, wp in enumerate(waypoints):
                    assert wp.sequence_order == i, f"Waypoint order should be sequential, expected {i}, got {wp.sequence_order}"
            
            self.log_test("Business logic constraints test", "PASS")
            
        except Exception as e:
            self.log_test(f"Business logic constraints test failed: {str(e)}", "FAIL")
            raise

    def test_data_integrity(self):
        """Test data integrity and constraints"""
        self.log_test("Testing data integrity", "RUNNING")
        
        try:
            # Test unique constraints
            emails = [user.email for user in self.db.query(User).all()]
            assert len(emails) == len(set(emails)), "User emails should be unique"
            
            serial_numbers = [drone.serial_number for drone in self.db.query(Drone).all()]
            assert len(serial_numbers) == len(set(serial_numbers)), "Drone serial numbers should be unique"
            
            org_names = [org.name for org in self.db.query(Organization).all()]
            assert len(org_names) == len(set(org_names)), "Organization names should be unique"
            
            org_bins = [org.bin for org in self.db.query(Organization).all()]
            assert len(org_bins) == len(set(org_bins)), "Organization BINs should be unique"
            
            # Test foreign key integrity
            flight_plans = self.db.query(FlightPlan).all()
            for fp in flight_plans:
                assert self.db.query(User).filter_by(id=fp.user_id).first() is not None, "Flight plan user must exist"
                assert self.db.query(Drone).filter_by(id=fp.drone_id).first() is not None, "Flight plan drone must exist"
            
            # Test cascade constraints
            waypoints = self.db.query(Waypoint).all()
            for wp in waypoints:
                assert self.db.query(FlightPlan).filter_by(id=wp.flight_plan_id).first() is not None, "Waypoint flight plan must exist"
            
            self.log_test("Data integrity test", "PASS")
            
        except Exception as e:
            self.log_test(f"Data integrity test failed: {str(e)}", "FAIL")
            raise

    def test_performance(self):
        """Test database performance with complex queries"""
        self.log_test("Testing database performance", "RUNNING")
        
        try:
            import time
            
            # Test complex join query performance
            start_time = time.time()
            complex_query = self.db.query(FlightPlan)\
                .join(User)\
                .join(Drone)\
                .outerjoin(Organization)\
                .outerjoin(Waypoint)\
                .outerjoin(TelemetryLog)\
                .limit(100).all()
            query_time = time.time() - start_time
            
            assert query_time < 5.0, f"Complex query took too long: {query_time:.2f}s"
            
            # Test pagination performance
            start_time = time.time()
            paginated_users = crud_user.user.get_multi(self.db, skip=0, limit=50)
            pagination_time = time.time() - start_time
            
            assert pagination_time < 1.0, f"Pagination query took too long: {pagination_time:.2f}s"
            
            # Test aggregation performance
            start_time = time.time()
            user_count = self.db.query(User).count()
            drone_count = self.db.query(Drone).count()
            flight_count = self.db.query(FlightPlan).count()
            aggregation_time = time.time() - start_time
            
            assert aggregation_time < 1.0, f"Aggregation queries took too long: {aggregation_time:.2f}s"
            
            self.log_test(f"Performance test (Query: {query_time:.2f}s, Pagination: {pagination_time:.2f}s, Aggregation: {aggregation_time:.2f}s)", "PASS")
            
        except Exception as e:
            self.log_test(f"Performance test failed: {str(e)}", "FAIL")
            raise

    def print_test_summary(self):
        """Print summary of created test data"""
        self.log_test("Test Data Summary", "INFO")
        
        summary = {
            'Users': len(self.test_data_ids['users']),
            'Organizations': len(self.test_data_ids['organizations']),
            'Drones': len(self.test_data_ids['drones']),
            'Flight Plans': len(self.test_data_ids['flight_plans']),
            'Waypoints': len(self.test_data_ids['waypoints']),
            'Telemetry Logs': len(self.test_data_ids['telemetry_logs']),
            'Restricted Zones': len(self.test_data_ids['restricted_zones']),
            'User-Drone Assignments': len(self.test_data_ids['user_drone_assignments'])
        }
        
        for entity, count in summary.items():
            print(f"  📊 {entity}: {count} records")
        
        # Print some sample data
        print("\n📋 Sample Data:")
        
        # Sample users by role
        users_by_role = {}
        for user in self.db.query(User).all():
            role = user.role.value
            if role not in users_by_role:
                users_by_role[role] = []
            users_by_role[role].append(user.email)
        
        for role, emails in users_by_role.items():
            print(f"  👤 {role}: {len(emails)} users")
            if emails:
                print(f"      Example: {emails[0]}")
        
        # Sample flight plans by status
        fp_by_status = {}
        for fp in self.db.query(FlightPlan).all():
            status = fp.status.value
            if status not in fp_by_status:
                fp_by_status[status] = 0
            fp_by_status[status] += 1
        
        print(f"\n  ✈️  Flight Plans by Status:")
        for status, count in fp_by_status.items():
            print(f"      {status}: {count}")

    def cleanup_test_data(self):
        """Clean up all test data"""
        self.log_test("Cleaning up test data", "RUNNING")
        
        try:
            # Order matters due to foreign key constraints
            cleanup_order = [
                ('telemetry_logs', TelemetryLog),
                ('waypoints', Waypoint),
                ('flight_plans', FlightPlan),
                ('user_drone_assignments', UserDroneAssignment),
                ('drones', Drone),
                ('restricted_zones', RestrictedZone),
                ('users', User),
                ('organizations', Organization)
            ]
            
            for table_name, model_class in cleanup_order:
                if table_name == 'user_drone_assignments':
                    # Special handling for composite key
                    for user_id, drone_id in self.test_data_ids[table_name]:
                        assignment = self.db.query(UserDroneAssignment).filter_by(
                            user_id=user_id, drone_id=drone_id
                        ).first()
                        if assignment:
                            self.db.delete(assignment)
                else:
                    ids_to_delete = self.test_data_ids[table_name]
                    if ids_to_delete:
                        # Delete in batches for better performance
                        for i in range(0, len(ids_to_delete), 100):
                            batch = ids_to_delete[i:i+100]
                            self.db.query(model_class).filter(model_class.id.in_(batch)).delete(synchronize_session=False)
                        
                print(f"  🗑️  Cleaned {len(self.test_data_ids[table_name])} {table_name}")
            
            self.db.commit()
            self.log_test("Test data cleanup completed", "PASS")
            
        except Exception as e:
            self.db.rollback()
            self.log_test(f"Test data cleanup failed: {str(e)}", "FAIL")
            raise

    def verify_cleanup(self):
        """Verify that all test data has been cleaned up"""
        self.log_test("Verifying cleanup", "RUNNING")
        
        try:
            # Check that test data is gone
            remaining_counts = {}
            
            # Count remaining test users (by email pattern)
            remaining_counts['test_users'] = self.db.query(User).filter(
                User.email.like('%@test.com')
            ).count()
            
            # Count remaining test organizations (by name pattern)
            remaining_counts['test_orgs'] = self.db.query(Organization).filter(
                Organization.name.like('Test Organization%')
            ).count()
            
            # Count remaining test drones (by serial number pattern)
            remaining_counts['test_drones'] = self.db.query(Drone).filter(
                Drone.serial_number.like('%_SN%')
            ).count()
            
            # Count remaining test flight plans (by notes pattern)
            remaining_counts['test_flights'] = self.db.query(FlightPlan).filter(
                FlightPlan.notes.like('%test flight%')
            ).count()
            
            # Count remaining test NFZs (by name pattern)
            remaining_counts['test_nfz'] = self.db.query(RestrictedZone).filter(
                RestrictedZone.name.like('%NFZ')
            ).count()
            
            total_remaining = sum(remaining_counts.values())
            
            if total_remaining == 0:
                self.log_test("Cleanup verification passed - no test data remaining", "PASS")
            else:
                self.log_test(f"Cleanup verification warning - {total_remaining} test records may remain", "INFO")
                for entity, count in remaining_counts.items():
                    if count > 0:
                        print(f"  ⚠️  {entity}: {count} remaining")
            
        except Exception as e:
            self.log_test(f"Cleanup verification failed: {str(e)}", "FAIL")

    def generate_test_report(self):
        """Generate a comprehensive test report"""
        self.log_test("Generating test report", "INFO")
        
        report = {
            "test_suite": "UTM Database Comprehensive Test",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database_url": settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else "hidden",
            "test_data_created": self.test_data_ids,
            "database_schema_info": {}
        }
        
        try:
            # Get table information
            tables_info = {}
            table_names = ['users', 'organizations', 'drones', 'flight_plans', 'waypoints', 
                          'telemetry_logs', 'restricted_zones', 'user_drone_assignments']
            
            for table_name in table_names:
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                count_result = self.db.execute(count_query).scalar()
                tables_info[table_name] = {"total_records": count_result}
            
            report["database_schema_info"] = tables_info
            
            # Save report to file
            report_filename = f"db_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"📄 Test report saved to: {report_filename}")
            
        except Exception as e:
            self.log_test(f"Report generation failed: {str(e)}", "FAIL")

    def run_stress_test(self):
        """Run stress tests with high volume data"""
        self.log_test("Running stress test", "RUNNING")
        
        try:
            import time
            stress_test_ids = []
            
            # Create many users quickly
            start_time = time.time()
            for i in range(100):
                user = User(
                    full_name=f"Stress Test User {i}",
                    email=f"stress_test_{i}@test.com",
                    phone_number=f"+77000000{i:03d}",
                    iin=f"99999999{i:03d}",
                    hashed_password=get_password_hash("stresstest"),
                    role=UserRole.SOLO_PILOT,
                    is_active=True
                )
                self.db.add(user)
                if i % 20 == 0:  # Commit in batches
                    self.db.flush()
                    
            self.db.commit()
            creation_time = time.time() - start_time
            
            # Test bulk query performance
            start_time = time.time()
            stress_users = self.db.query(User).filter(User.email.like('stress_test_%')).all()
            query_time = time.time() - start_time
            
            # Cleanup stress test data
            start_time = time.time()
            self.db.query(User).filter(User.email.like('stress_test_%')).delete()
            self.db.commit()
            cleanup_time = time.time() - start_time
            
            self.log_test(f"Stress test (Create: {creation_time:.2f}s, Query: {query_time:.2f}s, Cleanup: {cleanup_time:.2f}s)", "PASS")
            
        except Exception as e:
            self.db.rollback()
            self.log_test(f"Stress test failed: {str(e)}", "FAIL")
            raise

    def run_all_tests(self):
        """Run the complete test suite"""
        print("🚀 Starting Comprehensive Database Test Suite")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Create test data
            self.create_test_data()
            
            # Print summary of created data
            self.print_test_summary()
            
            print("\n" + "=" * 60)
            print("🧪 Running Database Tests")
            print("=" * 60)
            
            # Run all tests
            self.test_crud_operations()
            self.test_relationships()
            self.test_business_logic()
            self.test_data_integrity()
            self.test_performance()
            self.run_stress_test()
            
            print("\n" + "=" * 60)
            print("✅ All tests completed successfully!")
            
            end_time = datetime.now()
            duration = end_time - start_time
            print(f"⏱️  Total test duration: {duration.total_seconds():.2f} seconds")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Test suite failed: {str(e)}")
            raise
        
        finally:
            # Always clean up, even if tests fail
            print("\n" + "=" * 60)
            print("🧹 Cleaning Up Test Data")
            print("=" * 60)
            self.cleanup_test_data()
            self.verify_cleanup()
            self.generate_test_report()
            self.db.close()
            print("🎉 Database test suite completed!")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()


def main():
    """Main function to run the test suite"""
    try:
        with DatabaseTestSuite() as test_suite:
            test_suite.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️  Test suite interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
```

