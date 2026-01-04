"""
Base Repository Pattern
نمط المستودع الأساسي
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from .base import Base

# Generic type for models
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations
    المستودع الأساسي مع عمليات CRUD الشائعة

    Usage:
        class UserRepository(BaseRepository[User]):
            pass

        repo = UserRepository(db, User)
        users = repo.get_all()
    """

    def __init__(self, db: Session, model: type[ModelType]):
        self.db = db
        self.model = model

    # =============================================================================
    # Read Operations
    # =============================================================================

    def get_by_id(self, id: UUID | str) -> ModelType | None:
        """Get a single record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order_desc: bool = False,
    ) -> list[ModelType]:
        """Get all records with pagination"""
        query = self.db.query(self.model)

        if order_by and hasattr(self.model, order_by):
            order_column = getattr(self.model, order_by)
            query = query.order_by(order_column.desc() if order_desc else order_column)

        return query.offset(skip).limit(limit).all()

    def get_by_tenant(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Get all records for a specific tenant"""
        return (
            self.db.query(self.model)
            .filter(self.model.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_field(
        self,
        field_name: str,
        value: Any,
        limit: int = 100,
    ) -> list[ModelType]:
        """Get records by a specific field value"""
        if not hasattr(self.model, field_name):
            raise ValueError(f"Model {self.model.__name__} has no field '{field_name}'")

        field = getattr(self.model, field_name)
        return self.db.query(self.model).filter(field == value).limit(limit).all()

    def get_one_by_field(
        self,
        field_name: str,
        value: Any,
    ) -> ModelType | None:
        """Get a single record by a specific field value"""
        if not hasattr(self.model, field_name):
            raise ValueError(f"Model {self.model.__name__} has no field '{field_name}'")

        field = getattr(self.model, field_name)
        return self.db.query(self.model).filter(field == value).first()

    def count(self, tenant_id: str | None = None) -> int:
        """Count all records"""
        query = self.db.query(func.count(self.model.id))
        if tenant_id and hasattr(self.model, "tenant_id"):
            query = query.filter(self.model.tenant_id == tenant_id)
        return query.scalar() or 0

    def exists(self, id: UUID | str) -> bool:
        """Check if a record exists"""
        return self.db.query(
            self.db.query(self.model).filter(self.model.id == id).exists()
        ).scalar()

    # =============================================================================
    # Write Operations
    # =============================================================================

    def create(self, obj_in: dict[str, Any]) -> ModelType:
        """Create a new record"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def create_many(self, objects: list[dict[str, Any]]) -> list[ModelType]:
        """Create multiple records"""
        db_objects = [self.model(**obj) for obj in objects]
        self.db.add_all(db_objects)
        self.db.commit()
        for obj in db_objects:
            self.db.refresh(obj)
        return db_objects

    def update(self, id: UUID | str, obj_in: dict[str, Any]) -> ModelType | None:
        """Update an existing record"""
        db_obj = self.get_by_id(id)
        if db_obj is None:
            return None

        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update_many(
        self,
        filters: dict[str, Any],
        values: dict[str, Any],
    ) -> int:
        """Update multiple records matching filters"""
        query = self.db.query(self.model)

        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)

        result = query.update(values, synchronize_session=False)
        self.db.commit()
        return result

    def delete(self, id: UUID | str) -> bool:
        """Delete a record by ID"""
        db_obj = self.get_by_id(id)
        if db_obj is None:
            return False

        self.db.delete(db_obj)
        self.db.commit()
        return True

    def delete_many(self, filters: dict[str, Any]) -> int:
        """Delete multiple records matching filters"""
        query = self.db.query(self.model)

        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)

        result = query.delete(synchronize_session=False)
        self.db.commit()
        return result

    # =============================================================================
    # Soft Delete Operations (if model has is_deleted field)
    # =============================================================================

    def soft_delete(self, id: UUID | str) -> bool:
        """Soft delete a record (mark as deleted)"""
        if not hasattr(self.model, "is_deleted"):
            raise ValueError(f"Model {self.model.__name__} doesn't support soft delete")

        from datetime import datetime

        return (
            self.update(id, {"is_deleted": True, "deleted_at": datetime.utcnow()})
            is not None
        )

    def get_active(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: str | None = None,
    ) -> list[ModelType]:
        """Get all active (non-deleted) records"""
        if not hasattr(self.model, "is_deleted"):
            return self.get_all(skip, limit)

        query = self.db.query(self.model).filter(self.model.is_deleted == False)

        if tenant_id and hasattr(self.model, "tenant_id"):
            query = query.filter(self.model.tenant_id == tenant_id)

        return query.offset(skip).limit(limit).all()

    def restore(self, id: UUID | str) -> bool:
        """Restore a soft-deleted record"""
        if not hasattr(self.model, "is_deleted"):
            raise ValueError(f"Model {self.model.__name__} doesn't support soft delete")

        return self.update(id, {"is_deleted": False, "deleted_at": None}) is not None


class TenantRepository(BaseRepository[ModelType]):
    """
    Repository with built-in tenant filtering
    مستودع مع تصفية المستأجر المدمجة
    """

    def __init__(self, db: Session, model: type[ModelType], tenant_id: str):
        super().__init__(db, model)
        self.tenant_id = tenant_id

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order_desc: bool = False,
    ) -> list[ModelType]:
        """Get all records for current tenant"""
        query = self.db.query(self.model).filter(self.model.tenant_id == self.tenant_id)

        if order_by and hasattr(self.model, order_by):
            order_column = getattr(self.model, order_by)
            query = query.order_by(order_column.desc() if order_desc else order_column)

        return query.offset(skip).limit(limit).all()

    def get_by_id(self, id: UUID | str) -> ModelType | None:
        """Get a single record by ID (tenant-scoped)"""
        return (
            self.db.query(self.model)
            .filter(self.model.id == id, self.model.tenant_id == self.tenant_id)
            .first()
        )

    def create(self, obj_in: dict[str, Any]) -> ModelType:
        """Create a new record with tenant_id"""
        obj_in["tenant_id"] = self.tenant_id
        return super().create(obj_in)

    def count(self, tenant_id: str | None = None) -> int:
        """Count records for current tenant"""
        return super().count(self.tenant_id)
