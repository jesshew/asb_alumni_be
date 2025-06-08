from typing import Optional, Dict, Any
from datetime import datetime
from app.database import get_db_cursor
from app.models.scrape_history import ScrapeHistoryCreate, ScrapeHistoryUpdate, ScrapeHistoryResponse
import logging

logger = logging.getLogger(__name__)

class ScrapeHistoryService:
    """Service class for scrape history-related business logic."""

    @staticmethod
    def create_scrape_history(scrape_data: ScrapeHistoryCreate) -> ScrapeHistoryResponse:
        """Create a new scrape history record."""
        with get_db_cursor() as cursor:
            # Convert pydantic model to dict and filter None values
            data = scrape_data.model_dump(exclude_none=True)
            
            # Build dynamic INSERT query
            columns = list(data.keys())
            placeholders = [f"%({col})s" for col in columns]
            
            query = f"""
                INSERT INTO scrape_history ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                RETURNING *
            """
            
            cursor.execute(query, data)
            result = cursor.fetchone()
            
            return ScrapeHistoryResponse(**dict(result))

    @staticmethod
    def get_scrape_history_by_id(scrape_history_id: int) -> Optional[ScrapeHistoryResponse]:
        """Get scrape history by ID."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM scrape_history WHERE scrape_history_id = %s", 
                (scrape_history_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                return None
            
            return ScrapeHistoryResponse(**dict(result))

    @staticmethod
    def get_scrape_history_list(
        page: int = 1, 
        page_size: int = 50,
        status: Optional[str] = None,
        mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated list of scrape history with optional filters."""
        with get_db_cursor() as cursor:
            # Build WHERE clause dynamically
            where_conditions = []
            params = {}
            
            if status:
                where_conditions.append("scrape_history_status = %(status)s")
                params['status'] = status
            
            if mode:
                where_conditions.append("scrape_history_mode = %(mode)s")
                params['mode'] = mode
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Get total count
            count_query = f"SELECT COUNT(*) FROM scrape_history {where_clause}"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]
            
            # Calculate pagination
            offset = (page - 1) * page_size
            total_pages = (total_count + page_size - 1) // page_size
            
            # Get paginated results
            query = f"""
                SELECT * FROM scrape_history 
                {where_clause}
                ORDER BY scrape_history_started_at DESC
                LIMIT %(limit)s OFFSET %(offset)s
            """
            params.update({'limit': page_size, 'offset': offset})
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Convert results to response models
            scrape_histories = [ScrapeHistoryResponse(**dict(result)) for result in results]
            
            return {
                "scrape_histories": scrape_histories,
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }

    @staticmethod
    def update_scrape_history(
        scrape_history_id: int, 
        scrape_data: ScrapeHistoryUpdate
    ) -> Optional[ScrapeHistoryResponse]:
        """Update a scrape history record."""
        with get_db_cursor() as cursor:
            # Convert pydantic model to dict and filter None values
            data = scrape_data.model_dump(exclude_none=True)
            
            if not data:
                # No data to update
                return ScrapeHistoryService.get_scrape_history_by_id(scrape_history_id)
            
            # Build dynamic UPDATE query
            set_clauses = [f"{col} = %({col})s" for col in data.keys()]
            data['scrape_history_id'] = scrape_history_id
            
            query = f"""
                UPDATE scrape_history 
                SET {', '.join(set_clauses)}
                WHERE scrape_history_id = %(scrape_history_id)s
                RETURNING *
            """
            
            cursor.execute(query, data)
            result = cursor.fetchone()
            
            if not result:
                return None
            
            return ScrapeHistoryResponse(**dict(result))

    @staticmethod
    def delete_scrape_history(scrape_history_id: int) -> bool:
        """Delete a scrape history record."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "DELETE FROM scrape_history WHERE scrape_history_id = %s", 
                (scrape_history_id,)
            )
            return cursor.rowcount > 0

    @staticmethod
    def get_latest_scrape_histories(limit: int = 10) -> list[ScrapeHistoryResponse]:
        """Get the latest scrape history records."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM scrape_history 
                ORDER BY scrape_history_started_at DESC 
                LIMIT %s
            """, (limit,))
            results = cursor.fetchall()
            
            return [ScrapeHistoryResponse(**dict(result)) for result in results] 