"""
Shared Base Repository providing generic, reusable CRUD logic with transaction safety,
proper logging, type hinting, and robust error handling.
"""

import logging
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Generic Base Repository implementing standard CRUD database access patterns.
    Ensures rollback on exceptions and logs operations.
    """

    def __init__(self, model: Type[ModelType], db: Session) -> None:
        """
        Initializes the repository with a specific model and db session.

        Args:
            model: The SQLAlchemy model class.
            db: The SQLAlchemy Session database transaction wrapper.
        """
        self.model = model
        self.db = db
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

    def create(self, obj: ModelType) -> ModelType:
        """
        Persists a new database model instance. Handles transaction commit/rollback.

        Args:
            obj: The instantiated SQLAlchemy model to persist.

        Returns:
            The saved and refreshed model instance.
        """
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            self.logger.info(f"Successfully created {self.model.__name__} record.")
            return obj
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to create {self.model.__name__}: {e}", exc_info=True)
            raise e

    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Retrieves a record by its primary key ID.

        Args:
            id: The primary key of the model (usually UUID or int).

        Returns:
            The model instance if found, otherwise None.
        """
        try:
            return self.db.get(self.model, id)
        except Exception as e:
            self.logger.error(f"Error retrieving {self.model.__name__} by ID {id}: {e}", exc_info=True)
            raise e

    def get_all(self, limit: int = 100) -> List[ModelType]:
        """
        Retrieves all records, up to a specified limit.

        Args:
            limit: Maximum number of records to return.

        Returns:
            A list of model instances.
        """
        try:
            stmt = select(self.model).limit(limit)
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            self.logger.error(f"Error retrieving all {self.model.__name__} records: {e}", exc_info=True)
            raise e

    def update(self, db_obj: ModelType, obj_in: Dict[str, Any] | ModelType) -> ModelType:
        """
        Updates an existing model instance with new attributes.

        Args:
            db_obj: The existing database model instance.
            obj_in: A dictionary of new field values or a model instance with updated attributes.

        Returns:
            The updated and refreshed model instance.
        """
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = {
                    c.key: getattr(obj_in, c.key)
                    for c in self.model.__table__.columns
                    if hasattr(obj_in, c.key)
                }

            for field in update_data:
                # Retain primary key
                if field != "id":
                    setattr(db_obj, field, update_data[field])

            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            self.logger.info(f"Successfully updated {self.model.__name__} with ID {getattr(db_obj, 'id', None)}")
            return db_obj
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to update {self.model.__name__}: {e}", exc_info=True)
            raise e

    def delete(self, id: Any) -> bool:
        """
        Deletes a record by its primary key ID.

        Args:
            id: The primary key of the record to delete.

        Returns:
            True if the record was found and deleted, False otherwise.
        """
        try:
            db_obj = self.get_by_id(id)
            if db_obj is None:
                self.logger.warning(f"Attempted to delete non-existent {self.model.__name__} with ID {id}")
                return False
            self.db.delete(db_obj)
            self.db.commit()
            self.logger.info(f"Successfully deleted {self.model.__name__} with ID {id}")
            return True
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to delete {self.model.__name__} with ID {id}: {e}", exc_info=True)
            raise e

    def exists(self, **filters: Any) -> bool:
        """
        Checks if any records exist matching the specified filter criteria.

        Args:
            **filters: Field-value pairs to filter by.

        Returns:
            True if at least one matching record exists, False otherwise.
        """
        try:
            stmt = select(func.count()).select_from(self.model)
            for attr_name, value in filters.items():
                if hasattr(self.model, attr_name):
                    stmt = stmt.where(getattr(self.model, attr_name) == value)
            count_val = self.db.scalar(stmt) or 0
            return count_val > 0
        except Exception as e:
            self.logger.error(f"Error checking existence in {self.model.__name__}: {e}", exc_info=True)
            raise e

    def count(self, **filters: Any) -> int:
        """
        Counts the total number of records matching the filter criteria.

        Args:
            **filters: Field-value pairs to filter by.

        Returns:
            Total count of matching records.
        """
        try:
            stmt = select(func.count()).select_from(self.model)
            for attr_name, value in filters.items():
                if hasattr(self.model, attr_name):
                    stmt = stmt.where(getattr(self.model, attr_name) == value)
            return self.db.scalar(stmt) or 0
        except Exception as e:
            self.logger.error(f"Error counting records in {self.model.__name__}: {e}", exc_info=True)
            raise e

    def paginate(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_desc: bool = False,
    ) -> Tuple[List[ModelType], int]:
        """
        Paginates DB queries and supports filtering and sorting.

        Args:
            page: Current page number (1-indexed).
            per_page: Number of items per page.
            filters: Key-value filters to apply to the search selection.
            sort_by: Column name to sort the result query set.
            sort_desc: Set to True for descending sort order, otherwise False.

        Returns:
            A tuple containing (items_list, total_matching_count).
        """
        try:
            if page < 1:
                page = 1
            if per_page < 1:
                per_page = 20

            offset = (page - 1) * per_page

            stmt = select(self.model)
            count_stmt = select(func.count()).select_from(self.model)

            if filters:
                for attr_name, value in filters.items():
                    if hasattr(self.model, attr_name):
                        stmt = stmt.where(getattr(self.model, attr_name) == value)
                        count_stmt = count_stmt.where(getattr(self.model, attr_name) == value)

            total_count = self.db.scalar(count_stmt) or 0

            if sort_by and hasattr(self.model, sort_by):
                sort_attr = getattr(self.model, sort_by)
                if sort_desc:
                    stmt = stmt.order_by(sort_attr.desc())
                else:
                    stmt = stmt.order_by(sort_attr.asc())
            elif hasattr(self.model, "created_at"):
                stmt = stmt.order_by(getattr(self.model, "created_at").desc())

            stmt = stmt.offset(offset).limit(per_page)
            items = list(self.db.scalars(stmt).all())

            return items, total_count
        except Exception as e:
            self.logger.error(f"Error paginating {self.model.__name__}: {e}", exc_info=True)
            raise e

    def search(self, query_str: str, search_fields: List[str], limit: int = 100) -> List[ModelType]:
        """
        Performs an ILIKE string match query across multiple specified fields.

        Args:
            query_str: Substring search query.
            search_fields: List of model column names to search.
            limit: Maximum rows to return.

        Returns:
            Filtered list of model instances.
        """
        try:
            if not query_str or not search_fields:
                return []

            conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    attr = getattr(self.model, field)
                    # Check compatibility. In SQLite, ILIKE isn't fully native but SQLAlchemy handles it.
                    conditions.append(attr.ilike(f"%{query_str}%"))

            if not conditions:
                return []

            stmt = select(self.model).where(or_(*conditions)).limit(limit)
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            self.logger.error(
                f"Error searching {self.model.__name__} fields {search_fields} with target '{query_str}': {e}",
                exc_info=True
            )
            raise e

    def bulk_insert(self, objs: List[ModelType]) -> List[ModelType]:
        """
        Inserts multiple model records efficiently in a single transactional block.

        Args:
            objs: List of instantiated models to insert.

        Returns:
            The saved models list populated with primary keys.
        """
        try:
            if not objs:
                return []
            self.db.add_all(objs)
            self.db.commit()
            for obj in objs:
                self.db.refresh(obj)
            self.logger.info(f"Successfully bulk inserted {len(objs)} {self.model.__name__} records.")
            return objs
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to bulk insert {self.model.__name__}: {e}", exc_info=True)
            raise e
