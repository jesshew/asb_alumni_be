from typing import Optional, Dict, Any
from datetime import datetime
from app.database import get_db_cursor
from app.models.user import UserCreate, UserUpdate, UserResponse
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service class for user-related business logic."""

    @staticmethod
    def create_user(user_data: UserCreate) -> UserResponse:
        """Create a new user record."""
        with get_db_cursor() as cursor:
            # Convert pydantic model to dict and filter None values
            data = user_data.model_dump(exclude_none=True)
            
            # Build dynamic INSERT query
            columns = list(data.keys())
            placeholders = [f"%({col})s" for col in columns]
            
            query = f"""
                INSERT INTO asb_user ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                RETURNING *
            """
            
            cursor.execute(query, data)
            result = cursor.fetchone()
            
            return UserResponse(**dict(result))

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[UserResponse]:
        """Get user by ID."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM asb_user WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                return None
            
            return UserResponse(**dict(result))

    @staticmethod
    def get_user_by_email(email: str) -> Optional[UserResponse]:
        """Get user by email."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM asb_user WHERE user_email = %s", (email,))
            result = cursor.fetchone()
            
            if not result:
                return None
            
            return UserResponse(**dict(result))

    @staticmethod
    def get_user_list(
        page: int = 1, 
        page_size: int = 50,
        is_admin: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated list of users with optional filters."""
        with get_db_cursor() as cursor:
            # Build WHERE clause dynamically
            where_conditions = []
            params = {}
            
            if is_admin is not None:
                where_conditions.append("user_is_admin = %(is_admin)s")
                params['is_admin'] = is_admin
            
            if search:
                where_conditions.append("""
                    (user_name ILIKE %(search)s OR 
                     user_email ILIKE %(search)s)
                """)
                params['search'] = f"%{search}%"
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Get total count
            count_query = f"SELECT COUNT(*) FROM asb_user {where_clause}"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]
            
            # Calculate pagination
            offset = (page - 1) * page_size
            total_pages = (total_count + page_size - 1) // page_size
            
            # Get paginated results
            query = f"""
                SELECT * FROM asb_user 
                {where_clause}
                ORDER BY user_created_at DESC
                LIMIT %(limit)s OFFSET %(offset)s
            """
            params.update({'limit': page_size, 'offset': offset})
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Convert results to response models
            users = [UserResponse(**dict(result)) for result in results]
            
            return {
                "users": users,
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }

    @staticmethod
    def update_user(user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update a user record."""
        with get_db_cursor() as cursor:
            # Convert pydantic model to dict and filter None values
            data = user_data.model_dump(exclude_none=True)
            
            if not data:
                # No data to update
                return UserService.get_user_by_id(user_id)
            
            # Build dynamic UPDATE query
            set_clauses = [f"{col} = %({col})s" for col in data.keys()]
            data['user_id'] = user_id
            
            query = f"""
                UPDATE asb_user 
                SET {', '.join(set_clauses)}
                WHERE user_id = %(user_id)s
                RETURNING *
            """
            
            cursor.execute(query, data)
            result = cursor.fetchone()
            
            if not result:
                return None
            
            return UserResponse(**dict(result))

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Delete a user record."""
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM asb_user WHERE user_id = %s", (user_id,))
            return cursor.rowcount > 0

    @staticmethod
    def get_admin_users() -> list[UserResponse]:
        """Get all admin users."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM asb_user WHERE user_is_admin = true")
            results = cursor.fetchall()
            
            return [UserResponse(**dict(result)) for result in results]