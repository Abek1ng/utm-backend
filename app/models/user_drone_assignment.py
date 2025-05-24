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