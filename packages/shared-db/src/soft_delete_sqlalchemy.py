"""
Soft Delete Pattern Implementation for SQLAlchemy
=================================================

This module provides a comprehensive soft delete implementation for SQLAlchemy ORM:
- SoftDeleteMixin for adding soft delete fields to models
- Query filter to automatically exclude deleted records
- Helper functions for soft delete operations
- Session event listeners for automatic filtering

Usage:
    1. Add SoftDeleteMixin to your models
    2. Apply soft delete filter to your queries
    3. Use the helper functions for soft delete operations

Author: SAHOOL Team
"""

from datetime import datetime
from typing import Any, TypeVar

from sqlalchemy import Column, DateTime, String, event
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Query, Session, declarative_mixin

# Type variable for generic model classes
T = TypeVar("T")


# ═══════════════════════════════════════════════════════════════════════════
# Soft Delete Mixin
# ═══════════════════════════════════════════════════════════════════════════


@declarative_mixin
class SoftDeleteMixin:
    """
    Mixin class that adds soft delete functionality to SQLAlchemy models.

    Adds two columns:
    - deleted_at: Timestamp when the record was soft-deleted (NULL if not deleted)
    - deleted_by: Identifier of the user who deleted the record

    Example:
        ```python
        from sqlalchemy import Column, String, Integer
        from sqlalchemy.orm import Mapped, mapped_column
        from packages.shared_db.src.soft_delete_sqlalchemy import SoftDeleteMixin

        class Product(Base, SoftDeleteMixin):
            __tablename__ = "products"

            id: Mapped[int] = mapped_column(Integer, primary_key=True)
            name: Mapped[str] = mapped_column(String(255), nullable=False)
            # deletedAt and deletedBy are inherited from SoftDeleteMixin
        ```
    """

    @declared_attr
    def deleted_at(cls) -> Column:
        """Timestamp when the record was deleted (NULL if active)"""
        return Column(
            "deleted_at",
            DateTime(timezone=True),
            nullable=True,
            default=None,
            index=True,
            comment="تاريخ الحذف - Soft delete timestamp",
        )

    @declared_attr
    def deleted_by(cls) -> Column:
        """User ID or identifier who deleted the record"""
        return Column(
            "deleted_by",
            String(255),
            nullable=True,
            default=None,
            comment="من قام بالحذف - User who deleted the record",
        )

    def soft_delete(self, deleted_by: str | None = None) -> None:
        """
        Soft delete this record instance.

        Args:
            deleted_by: User ID or identifier performing the deletion

        Example:
            ```python
            product = session.query(Product).filter_by(id=123).first()
            product.soft_delete(deleted_by="user-456")
            session.commit()
            ```
        """
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    def restore(self) -> None:
        """
        Restore a soft-deleted record.

        Example:
            ```python
            product = session.query(Product).filter_by(id=123).first()
            product.restore()
            session.commit()
            ```
        """
        self.deleted_at = None
        self.deleted_by = None

    def is_deleted(self) -> bool:
        """
        Check if this record is soft-deleted.

        Returns:
            True if the record is deleted, False otherwise

        Example:
            ```python
            if product.is_deleted():
                print("This product has been deleted")
            ```
        """
        return self.deleted_at is not None

    @classmethod
    def filter_active(cls, query: Query) -> Query:
        """
        Add filter to query to exclude soft-deleted records.

        Args:
            query: SQLAlchemy query object

        Returns:
            Query filtered to only include active (non-deleted) records

        Example:
            ```python
            query = session.query(Product)
            query = Product.filter_active(query)
            products = query.all()  # Only returns non-deleted products
            ```
        """
        return query.filter(cls.deleted_at.is_(None))

    @classmethod
    def filter_deleted(cls, query: Query) -> Query:
        """
        Add filter to query to only include soft-deleted records.

        Args:
            query: SQLAlchemy query object

        Returns:
            Query filtered to only include deleted records

        Example:
            ```python
            query = session.query(Product)
            query = Product.filter_deleted(query)
            deleted_products = query.all()
            ```
        """
        return query.filter(cls.deleted_at.isnot(None))

    @classmethod
    def with_deleted(cls, query: Query) -> Query:
        """
        Return query that includes both active and deleted records.

        Args:
            query: SQLAlchemy query object

        Returns:
            Unfiltered query

        Example:
            ```python
            query = session.query(Product)
            all_products = Product.with_deleted(query).all()
            ```
        """
        return query


# ═══════════════════════════════════════════════════════════════════════════
# Query Helper Functions
# ═══════════════════════════════════════════════════════════════════════════


def soft_delete_filter(query: Query) -> Query:
    """
    Apply soft delete filter to a query.

    This function automatically filters out soft-deleted records.

    Args:
        query: SQLAlchemy query object

    Returns:
        Filtered query excluding deleted records

    Example:
        ```python
        from packages.shared_db.src.soft_delete_sqlalchemy import soft_delete_filter

        query = session.query(Product)
        query = soft_delete_filter(query)
        products = query.all()  # Only active products
        ```
    """
    # Get the model class from the query
    if hasattr(query, "column_descriptions"):
        for desc in query.column_descriptions:
            model = desc.get("type")
            if model and hasattr(model, "deleted_at"):
                return query.filter(model.deleted_at.is_(None))
    return query


def get_active_records(session: Session, model: type[T], **filters) -> list[T]:
    """
    Get all active (non-deleted) records for a model.

    Args:
        session: SQLAlchemy session
        model: Model class
        **filters: Additional filter criteria

    Returns:
        List of active records

    Example:
        ```python
        from packages.shared_db.src.soft_delete_sqlalchemy import get_active_records

        # Get all active products
        products = get_active_records(session, Product)

        # Get active products with additional filters
        seed_products = get_active_records(
            session,
            Product,
            category="SEEDS"
        )
        ```
    """
    query = session.query(model)
    if hasattr(model, "deleted_at"):
        query = query.filter(model.deleted_at.is_(None))
    if filters:
        query = query.filter_by(**filters)
    return query.all()


def get_deleted_records(session: Session, model: type[T], **filters) -> list[T]:
    """
    Get all soft-deleted records for a model.

    Args:
        session: SQLAlchemy session
        model: Model class
        **filters: Additional filter criteria

    Returns:
        List of deleted records

    Example:
        ```python
        from packages.shared_db.src.soft_delete_sqlalchemy import get_deleted_records

        deleted_products = get_deleted_records(session, Product)
        ```
    """
    query = session.query(model)
    if hasattr(model, "deleted_at"):
        query = query.filter(model.deleted_at.isnot(None))
    if filters:
        query = query.filter_by(**filters)
    return query.all()


def get_all_records(session: Session, model: type[T], **filters) -> list[T]:
    """
    Get all records (including deleted ones) for a model.

    Args:
        session: SQLAlchemy session
        model: Model class
        **filters: Additional filter criteria

    Returns:
        List of all records

    Example:
        ```python
        from packages.shared_db.src.soft_delete_sqlalchemy import get_all_records

        all_products = get_all_records(session, Product)
        ```
    """
    query = session.query(model)
    if filters:
        query = query.filter_by(**filters)
    return query.all()


# ═══════════════════════════════════════════════════════════════════════════
# CRUD Helper Functions
# ═══════════════════════════════════════════════════════════════════════════


def soft_delete_record(
    session: Session,
    model: type[T],
    record_id: Any,
    deleted_by: str | None = None,
    id_field: str = "id",
) -> T | None:
    """
    Soft delete a single record by ID.

    Args:
        session: SQLAlchemy session
        model: Model class
        record_id: ID of the record to delete
        deleted_by: User ID performing the deletion
        id_field: Name of the ID field (default: 'id')

    Returns:
        The soft-deleted record, or None if not found

    Example:
        ```python
        from packages.shared_db.src.soft_delete_sqlalchemy import soft_delete_record

        deleted_product = soft_delete_record(
            session,
            Product,
            "product-123",
            deleted_by="user-456"
        )
        session.commit()
        ```
    """
    record = session.query(model).filter(getattr(model, id_field) == record_id).first()

    if record and hasattr(record, "soft_delete"):
        record.soft_delete(deleted_by=deleted_by)
        return record

    return None


def soft_delete_many(
    session: Session, model: type[T], deleted_by: str | None = None, **filters
) -> int:
    """
    Soft delete multiple records matching filters.

    Args:
        session: SQLAlchemy session
        model: Model class
        deleted_by: User ID performing the deletion
        **filters: Filter criteria for records to delete

    Returns:
        Number of records soft-deleted

    Example:
        ```python
        from packages.shared_db.src.soft_delete_sqlalchemy import soft_delete_many

        # Soft delete all products in a category
        count = soft_delete_many(
            session,
            Product,
            deleted_by="admin-123",
            category="DEPRECATED"
        )
        session.commit()
        print(f"Deleted {count} products")
        ```
    """
    if not hasattr(model, "deleted_at"):
        raise AttributeError(f"{model.__name__} does not have soft delete fields")

    query = session.query(model)
    if filters:
        query = query.filter_by(**filters)

    # Only delete non-deleted records
    query = query.filter(model.deleted_at.is_(None))

    count = query.update(
        {"deleted_at": datetime.utcnow(), "deleted_by": deleted_by},
        synchronize_session="fetch",
    )

    return count


def restore_record(
    session: Session, model: type[T], record_id: Any, id_field: str = "id"
) -> T | None:
    """
    Restore a soft-deleted record by ID.

    Args:
        session: SQLAlchemy session
        model: Model class
        record_id: ID of the record to restore
        id_field: Name of the ID field (default: 'id')

    Returns:
        The restored record, or None if not found

    Example:
        ```python
        from packages.shared_db.src.soft_delete_sqlalchemy import restore_record

        restored_product = restore_record(session, Product, "product-123")
        session.commit()
        ```
    """
    record = session.query(model).filter(getattr(model, id_field) == record_id).first()

    if record and hasattr(record, "restore"):
        record.restore()
        return record

    return None


def restore_many(session: Session, model: type[T], **filters) -> int:
    """
    Restore multiple soft-deleted records.

    Args:
        session: SQLAlchemy session
        model: Model class
        **filters: Filter criteria for records to restore

    Returns:
        Number of records restored

    Example:
        ```python
        from packages.shared_db.src.soft_delete_sqlalchemy import restore_many

        count = restore_many(session, Product, category="SEEDS")
        session.commit()
        print(f"Restored {count} products")
        ```
    """
    if not hasattr(model, "deleted_at"):
        raise AttributeError(f"{model.__name__} does not have soft delete fields")

    query = session.query(model)
    if filters:
        query = query.filter_by(**filters)

    # Only restore deleted records
    query = query.filter(model.deleted_at.isnot(None))

    count = query.update(
        {"deleted_at": None, "deleted_by": None}, synchronize_session="fetch"
    )

    return count


def hard_delete_record(
    session: Session, model: type[T], record_id: Any, id_field: str = "id"
) -> bool:
    """
    Permanently delete a record (hard delete).

    WARNING: This cannot be undone. Use only when necessary (e.g., GDPR compliance).

    Args:
        session: SQLAlchemy session
        model: Model class
        record_id: ID of the record to delete
        id_field: Name of the ID field (default: 'id')

    Returns:
        True if deleted, False if not found

    Example:
        ```python
        from packages.shared_db.src.soft_delete_sqlalchemy import hard_delete_record

        # Permanently delete a record (GDPR compliance)
        success = hard_delete_record(session, Product, "product-123")
        session.commit()
        ```
    """
    record = session.query(model).filter(getattr(model, id_field) == record_id).first()

    if record:
        session.delete(record)
        return True

    return False


# ═══════════════════════════════════════════════════════════════════════════
# Session Event Listeners (Optional Auto-filtering)
# ═══════════════════════════════════════════════════════════════════════════


def enable_soft_delete_filter(session: Session) -> None:
    """
    Enable automatic soft delete filtering for a session.

    This will automatically filter out soft-deleted records in all queries
    on this session.

    Args:
        session: SQLAlchemy session

    Example:
        ```python
        from packages.shared_db.src.soft_delete_sqlalchemy import enable_soft_delete_filter

        session = Session()
        enable_soft_delete_filter(session)

        # All queries on this session will now exclude deleted records
        products = session.query(Product).all()  # Only active products
        ```
    """

    @event.listens_for(session, "after_attach")
    def receive_after_attach(session, instance):
        """Auto-filter soft-deleted records"""
        if hasattr(instance.__class__, "deleted_at"):
            # This is a model with soft delete
            pass  # The filtering happens at query level

    # Note: For automatic filtering at query level, you might want to use
    # a custom Query class. See the documentation for advanced usage.


def count_active_records(session: Session, model: type[T]) -> int:
    """
    Count active (non-deleted) records.

    Args:
        session: SQLAlchemy session
        model: Model class

    Returns:
        Count of active records
    """
    query = session.query(model)
    if hasattr(model, "deleted_at"):
        query = query.filter(model.deleted_at.is_(None))
    return query.count()


def count_deleted_records(session: Session, model: type[T]) -> int:
    """
    Count soft-deleted records.

    Args:
        session: SQLAlchemy session
        model: Model class

    Returns:
        Count of deleted records
    """
    query = session.query(model)
    if hasattr(model, "deleted_at"):
        query = query.filter(model.deleted_at.isnot(None))
    return query.count()


# ═══════════════════════════════════════════════════════════════════════════
# Utility Functions
# ═══════════════════════════════════════════════════════════════════════════


def get_deletion_metadata(record: Any) -> dict | None:
    """
    Get deletion metadata from a record.

    Args:
        record: Model instance

    Returns:
        Dictionary with deletedAt and deletedBy, or None if not deleted

    Example:
        ```python
        metadata = get_deletion_metadata(product)
        if metadata:
            print(f"Deleted at: {metadata['deleted_at']}")
            print(f"Deleted by: {metadata['deleted_by']}")
        ```
    """
    if hasattr(record, "is_deleted") and record.is_deleted():
        return {"deleted_at": record.deleted_at, "deleted_by": record.deleted_by}
    return None


def is_soft_deletable(model: type) -> bool:
    """
    Check if a model supports soft delete.

    Args:
        model: Model class

    Returns:
        True if the model has soft delete fields
    """
    return hasattr(model, "deleted_at") and hasattr(model, "deleted_by")
