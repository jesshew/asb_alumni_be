from typing import List, Optional, Dict, Any
import json
from datetime import datetime
from app.database import get_db_cursor
from app.models.alumni import AlumniCreate, AlumniUpdate, AlumniResponse
import logging

logger = logging.getLogger(__name__)

class AlumniService:
    """Service class for alumni-related business logic."""

    @staticmethod
    def create_alumni(alumni_data: AlumniCreate) -> AlumniResponse:
        """Create a new alumni record."""
        with get_db_cursor() as cursor:
            # Convert pydantic model to dict and filter None values
            data = alumni_data.model_dump(exclude_none=True)
            
            # Handle JSONB fields
            if 'alumni_tags' in data and data['alumni_tags']:
                data['alumni_tags'] = json.dumps(data['alumni_tags'])
            if 'alumni_raw_data' in data and data['alumni_raw_data']:
                data['alumni_raw_data'] = json.dumps(data['alumni_raw_data'])
            
            # Build dynamic INSERT query
            columns = list(data.keys())
            placeholders = [f"%({col})s" for col in columns]
            
            query = f"""
                INSERT INTO alumni ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                RETURNING *
            """
            
            cursor.execute(query, data)
            result = cursor.fetchone()
            
            # Convert JSONB fields back to dict
            if result['alumni_tags']:
                result['alumni_tags'] = json.loads(result['alumni_tags'])
            if result['alumni_raw_data']:
                result['alumni_raw_data'] = json.loads(result['alumni_raw_data'])
            
            return AlumniResponse(**dict(result))

    @staticmethod
    def get_alumni_by_id(alumni_id: int) -> Optional[AlumniResponse]:
        """Get alumni by ID."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM alumni WHERE alumni_id = %s", (alumni_id,))
            result = cursor.fetchone()
            
            if not result:
                return None
            
            # Convert JSONB fields back to dict
            result_dict = dict(result)
            if result_dict['alumni_tags']:
                result_dict['alumni_tags'] = json.loads(result_dict['alumni_tags'])
            if result_dict['alumni_raw_data']:
                result_dict['alumni_raw_data'] = json.loads(result_dict['alumni_raw_data'])
            
            return AlumniResponse(**result_dict)

    @staticmethod
    def get_alumni_list(
        page: int = 1, 
        page_size: int = 50,
        is_latest: Optional[bool] = None,
        graduation_year: Optional[int] = None,
        program: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated list of alumni with optional filters."""
        with get_db_cursor() as cursor:
            # Build WHERE clause dynamically
            where_conditions = []
            params = {}
            
            if is_latest is not None:
                where_conditions.append("alumni_is_latest = %(is_latest)s")
                params['is_latest'] = is_latest
            
            if graduation_year:
                where_conditions.append("alumni_graduation_year = %(graduation_year)s")
                params['graduation_year'] = graduation_year
            
            if program:
                where_conditions.append("alumni_program ILIKE %(program)s")
                params['program'] = f"%{program}%"
            
            if search:
                where_conditions.append("""
                    (alumni_first_name ILIKE %(search)s OR 
                     alumni_last_name ILIKE %(search)s OR 
                     alumni_preferred_name ILIKE %(search)s OR
                     alumni_current_company_name ILIKE %(search)s)
                """)
                params['search'] = f"%{search}%"
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Get total count
            count_query = f"SELECT COUNT(*) FROM alumni {where_clause}"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]
            
            # Calculate pagination
            offset = (page - 1) * page_size
            total_pages = (total_count + page_size - 1) // page_size
            
            # Get paginated results
            query = f"""
                SELECT * FROM alumni 
                {where_clause}
                ORDER BY alumni_created_at DESC
                LIMIT %(limit)s OFFSET %(offset)s
            """
            params.update({'limit': page_size, 'offset': offset})
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Convert results to response models
            alumni_list = []
            for result in results:
                result_dict = dict(result)
                if result_dict['alumni_tags']:
                    result_dict['alumni_tags'] = json.loads(result_dict['alumni_tags'])
                if result_dict['alumni_raw_data']:
                    result_dict['alumni_raw_data'] = json.loads(result_dict['alumni_raw_data'])
                alumni_list.append(AlumniResponse(**result_dict))
            
            return {
                "alumni": alumni_list,
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }

    @staticmethod
    def update_alumni(alumni_id: int, alumni_data: AlumniUpdate) -> Optional[AlumniResponse]:
        """Update an alumni record."""
        with get_db_cursor() as cursor:
            # Convert pydantic model to dict and filter None values
            data = alumni_data.model_dump(exclude_none=True)
            
            if not data:
                # No data to update
                return AlumniService.get_alumni_by_id(alumni_id)
            
            # Handle JSONB fields
            if 'alumni_tags' in data and data['alumni_tags']:
                data['alumni_tags'] = json.dumps(data['alumni_tags'])
            if 'alumni_raw_data' in data and data['alumni_raw_data']:
                data['alumni_raw_data'] = json.dumps(data['alumni_raw_data'])
            
            # Add updated timestamp
            data['alumni_updated_at'] = datetime.now()
            
            # Build dynamic UPDATE query
            set_clauses = [f"{col} = %({col})s" for col in data.keys()]
            data['alumni_id'] = alumni_id
            
            query = f"""
                UPDATE alumni 
                SET {', '.join(set_clauses)}
                WHERE alumni_id = %(alumni_id)s
                RETURNING *
            """
            
            cursor.execute(query, data)
            result = cursor.fetchone()
            
            if not result:
                return None
            
            # Convert JSONB fields back to dict
            result_dict = dict(result)
            if result_dict['alumni_tags']:
                result_dict['alumni_tags'] = json.loads(result_dict['alumni_tags'])
            if result_dict['alumni_raw_data']:
                result_dict['alumni_raw_data'] = json.loads(result_dict['alumni_raw_data'])
            
            return AlumniResponse(**result_dict)

    @staticmethod
    def delete_alumni(alumni_id: int) -> bool:
        """Delete an alumni record."""
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM alumni WHERE alumni_id = %s", (alumni_id,))
            return cursor.rowcount > 0

    @staticmethod
    def get_alumni_by_linkedin_url(linkedin_url: str) -> Optional[AlumniResponse]:
        """Get alumni by LinkedIn URL."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM alumni WHERE alumni_linkedin_url = %s", 
                (linkedin_url,)
            )
            result = cursor.fetchone()
            
            if not result:
                return None
            
            # Convert JSONB fields back to dict
            result_dict = dict(result)
            if result_dict['alumni_tags']:
                result_dict['alumni_tags'] = json.loads(result_dict['alumni_tags'])
            if result_dict['alumni_raw_data']:
                result_dict['alumni_raw_data'] = json.loads(result_dict['alumni_raw_data'])
            
            return AlumniResponse(**result_dict) 