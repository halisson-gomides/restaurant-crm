"""Base service class for all business logic services."""

from typing import TypeVar, Generic, Optional, List, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

T = TypeVar("T")


class BaseService(Generic[T]):
    """Generic base service for CRUD operations."""

    def __init__(self, model: type[T]):
        """
        Initialize base service.

        Args:
            model: SQLAlchemy model class.
        """
        self.model = model

    async def create(self, db: AsyncSession, obj_in: dict) -> T:
        """
        Create a new object.

        Args:
            db: Database session.
            obj_in: Object data dictionary.

        Returns:
            Created object.
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    

    async def get_by_id(self, db: AsyncSession, obj_id: str) -> Optional[T]:
        """
        Get object by ID.

        Args:
            db: Database session.
            obj_id: Object ID.

        Returns:
            Object or None if not found.
        """
        result = await db.execute(select(self.model).where(self.model.id == obj_id))
        return result.scalar_one_or_none()

    async def get_by_field(self, db: AsyncSession, field_name: str, value: Any) -> Optional[T]:
        """
        Get object by field value.

        Args:
            db: Database session.
            field_name: Field name.
            value: Field value.

        Returns:
            Object or None if not found.
        """
        field = getattr(self.model, field_name)
        result = await db.execute(select(self.model).where(field == value))
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
    ) -> List[T]:
        """
        List objects with optional filtering.

        Args:
            db: Database session.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            filters: Optional dictionary of filters.

        Returns:
            List of objects.
        """
        query = select(self.model)

        if filters:
            for field_name, value in filters.items():
                field = getattr(self.model, field_name)
                query = query.where(field == value)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def update(self, db: AsyncSession, obj_id: str, obj_in: dict) -> Optional[T]:
        """
        Update an object.

        Args:
            db: Database session.
            obj_id: Object ID.
            obj_in: Updated object data dictionary.

        Returns:
            Updated object or None if not found.
        """
        db_obj = await self.get_by_id(db, obj_id)
        if not db_obj:
            return None

        for field, value in obj_in.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, obj_id: str) -> bool:
        """
        Delete an object.

        Args:
            db: Database session.
            obj_id: Object ID.

        Returns:
            True if deleted, False if not found.
        """
        db_obj = await self.get_by_id(db, obj_id)
        if not db_obj:
            return False

        await db.delete(db_obj)
        await db.commit()
        return True
