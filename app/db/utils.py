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