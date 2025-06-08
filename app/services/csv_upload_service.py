from typing import Optional, Dict, Any
from datetime import datetime
from app.database import get_db_cursor
from app.models.csv_upload import CsvUploadCreate, CsvUploadUpdate, CsvUploadResponse
import logging

logger = logging.getLogger(__name__)

class CsvUploadService:
    """Service class for CSV upload-related business logic."""

    @staticmethod
    def create_csv_upload(csv_data: CsvUploadCreate) -> CsvUploadResponse:
        """Create a new CSV upload record."""
        with get_db_cursor() as cursor:
            # Convert pydantic model to dict and filter None values
            data = csv_data.model_dump(exclude_none=True)
            
            # Build dynamic INSERT query
            columns = list(data.keys())
            placeholders = [f"%({col})s" for col in columns]
            
            query = f"""
                INSERT INTO csv_upload ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                RETURNING *
            """
            
            cursor.execute(query, data)
            result = cursor.fetchone()
            
            return CsvUploadResponse(**dict(result))

    @staticmethod
    def get_csv_upload_by_id(csv_upload_id: int) -> Optional[CsvUploadResponse]:
        """Get CSV upload by ID."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM csv_upload WHERE csv_upload_id = %s", 
                (csv_upload_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                return None
            
            return CsvUploadResponse(**dict(result))

    @staticmethod
    def get_csv_upload_list(
        page: int = 1, 
        page_size: int = 50,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated list of CSV uploads with optional filters."""
        with get_db_cursor() as cursor:
            # Build WHERE clause dynamically
            where_conditions = []
            params = {}
            
            if search:
                where_conditions.append("""
                    (csv_upload_file_name ILIKE %(search)s OR 
                     csv_upload_description ILIKE %(search)s)
                """)
                params['search'] = f"%{search}%"
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Get total count
            count_query = f"SELECT COUNT(*) FROM csv_upload {where_clause}"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]
            
            # Calculate pagination
            offset = (page - 1) * page_size
            total_pages = (total_count + page_size - 1) // page_size
            
            # Get paginated results
            query = f"""
                SELECT * FROM csv_upload 
                {where_clause}
                ORDER BY csv_upload_uploaded_at DESC
                LIMIT %(limit)s OFFSET %(offset)s
            """
            params.update({'limit': page_size, 'offset': offset})
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Convert results to response models
            csv_uploads = [CsvUploadResponse(**dict(result)) for result in results]
            
            return {
                "csv_uploads": csv_uploads,
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }

    @staticmethod
    def update_csv_upload(
        csv_upload_id: int, 
        csv_data: CsvUploadUpdate
    ) -> Optional[CsvUploadResponse]:
        """Update a CSV upload record."""
        with get_db_cursor() as cursor:
            # Convert pydantic model to dict and filter None values
            data = csv_data.model_dump(exclude_none=True)
            
            if not data:
                # No data to update
                return CsvUploadService.get_csv_upload_by_id(csv_upload_id)
            
            # Build dynamic UPDATE query
            set_clauses = [f"{col} = %({col})s" for col in data.keys()]
            data['csv_upload_id'] = csv_upload_id
            
            query = f"""
                UPDATE csv_upload 
                SET {', '.join(set_clauses)}
                WHERE csv_upload_id = %(csv_upload_id)s
                RETURNING *
            """
            
            cursor.execute(query, data)
            result = cursor.fetchone()
            
            if not result:
                return None
            
            return CsvUploadResponse(**dict(result))

    @staticmethod
    def delete_csv_upload(csv_upload_id: int) -> bool:
        """Delete a CSV upload record."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "DELETE FROM csv_upload WHERE csv_upload_id = %s", 
                (csv_upload_id,)
            )
            return cursor.rowcount > 0

    @staticmethod
    def get_recent_csv_uploads(limit: int = 10) -> list[CsvUploadResponse]:
        """Get the most recent CSV upload records."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM csv_upload 
                ORDER BY csv_upload_uploaded_at DESC 
                LIMIT %s
            """, (limit,))
            results = cursor.fetchall()
            
            return [CsvUploadResponse(**dict(result)) for result in results] 