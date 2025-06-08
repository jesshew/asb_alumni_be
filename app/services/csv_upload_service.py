from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from app.database import get_db_cursor
from app.models.csv_upload import CsvUploadCreate, CsvUploadUpdate, CsvUploadResponse
from app.utils.supabase import get_supabase_client
from app.config import settings
import logging
from supabase.lib.client_options import ClientOptions

logger = logging.getLogger(__name__)


class CsvUploadService:
    """Service class for CSV upload-related business logic."""

    @staticmethod
    async def create_csv_upload(csv_data: CsvUploadCreate) -> CsvUploadResponse:
        """Create a new CSV upload record and upload file to Supabase storage."""
        unique_filename = None
        try:
            # Log initial file info
            logger.info(
                f"Starting CSV upload process for file: {csv_data.file.filename}"
            )

            # Generate a unique filename
            file_extension = csv_data.file.filename.split(".")[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            logger.info(f"Generated unique filename: {unique_filename}")

            # Read file content
            file_content = await csv_data.file.read()
            file_size = len(file_content)
            logger.info(f"Read file content, size: {file_size} bytes")

            # Get Supabase client and verify bucket
            supabase = get_supabase_client()

            try:
                # Check if bucket exists
                bucket_list = supabase.storage.list_buckets()
                logger.info(f"Available buckets: {[b['name'] for b in bucket_list]}")

                bucket_exists = any(
                    bucket["name"] == settings.SUPABASE_BUCKET_NAME
                    for bucket in bucket_list
                )
                if not bucket_exists:
                    logger.error(f"Bucket '{settings.SUPABASE_BUCKET_NAME}' not found")
                    raise Exception(
                        f"Storage bucket '{settings.SUPABASE_BUCKET_NAME}' not found"
                    )

                logger.info(f"Found bucket: {settings.SUPABASE_BUCKET_NAME}")
            except Exception as bucket_error:
                logger.error(f"Error checking bucket: {bucket_error}")
                raise

            # Upload to Supabase storage
            try:
                logger.info("Attempting to upload file to Supabase storage")
                result = supabase.storage.from_(settings.SUPABASE_BUCKET_NAME).upload(
                    unique_filename, file_content
                )
                logger.info(f"Upload successful: {result}")
            except Exception as upload_error:
                logger.error(f"Error during file upload: {upload_error}")
                raise

            # Get the public URL
            try:
                file_url = supabase.storage.from_(
                    settings.SUPABASE_BUCKET_NAME
                ).get_public_url(unique_filename)
                logger.info(f"Generated public URL: {file_url}")
            except Exception as url_error:
                logger.error(f"Error getting public URL: {url_error}")
                raise

            # Create database record
            try:
                with get_db_cursor() as cursor:
                    query = """
                        INSERT INTO csv_upload (
                            csv_upload_file_name,
                            csv_upload_file_url,
                            csv_upload_description,
                            csv_upload_uploaded_at
                        ) VALUES (%s, %s, %s, %s)
                        RETURNING *
                    """
                    cursor.execute(
                        query,
                        (
                            csv_data.file.filename,
                            file_url,
                            csv_data.description,
                            datetime.now(),
                        ),
                    )
                    result = cursor.fetchone()
                    logger.info("Successfully created database record")

                    return CsvUploadResponse(**dict(result))
            except Exception as db_error:
                logger.error(f"Database error: {db_error}")
                raise

        except Exception as e:
            logger.error(f"Error in create_csv_upload: {str(e)}")
            # Delete uploaded file if it exists
            if unique_filename:
                try:
                    supabase = get_supabase_client()
                    supabase.storage.from_(settings.SUPABASE_BUCKET_NAME).remove(
                        [unique_filename]
                    )
                    logger.info(f"Cleaned up file {unique_filename} after error")
                except Exception as delete_error:
                    logger.error(
                        f"Error deleting file after failed upload: {delete_error}"
                    )
            raise Exception(f"Failed to process CSV upload: {str(e)}")

    @staticmethod
    def get_csv_upload_by_id(csv_upload_id: int) -> Optional[CsvUploadResponse]:
        """Get CSV upload by ID."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM csv_upload WHERE csv_upload_id = %s", (csv_upload_id,)
            )
            result = cursor.fetchone()

            if not result:
                return None

            return CsvUploadResponse(**dict(result))

    @staticmethod
    def get_csv_upload_list(
        page: int = 1, page_size: int = 50, search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated list of CSV uploads with optional filters."""
        with get_db_cursor() as cursor:
            # Build WHERE clause dynamically
            where_conditions = []
            params = {}

            if search:
                where_conditions.append(
                    """
                    (csv_upload_file_name ILIKE %(search)s OR 
                     csv_upload_description ILIKE %(search)s)
                """
                )
                params["search"] = f"%{search}%"

            where_clause = (
                "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            )

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
            params.update({"limit": page_size, "offset": offset})

            cursor.execute(query, params)
            results = cursor.fetchall()

            # Convert results to response models
            csv_uploads = [CsvUploadResponse(**dict(result)) for result in results]

            return {
                "csv_uploads": csv_uploads,
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
            }

    @staticmethod
    def update_csv_upload(
        csv_upload_id: int, csv_data: CsvUploadUpdate
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
            data["csv_upload_id"] = csv_upload_id

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
    async def delete_csv_upload(csv_upload_id: int) -> bool:
        """Delete a CSV upload record and the associated file from storage."""
        try:
            with get_db_cursor() as cursor:
                # First get the file URL to extract the filename
                cursor.execute(
                    "SELECT csv_upload_file_url FROM csv_upload WHERE csv_upload_id = %s",
                    (csv_upload_id,),
                )
                result = cursor.fetchone()

                if not result:
                    return False

                # Extract filename from URL
                file_url = result["csv_upload_file_url"]
                filename = file_url.split("/")[-1]

                # Delete from Supabase storage
                supabase = get_supabase_client()
                supabase.storage.from_(settings.SUPABASE_BUCKET_NAME).remove([filename])

                # Delete database record
                cursor.execute(
                    "DELETE FROM csv_upload WHERE csv_upload_id = %s", (csv_upload_id,)
                )
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error in delete_csv_upload: {e}")
            raise

    @staticmethod
    def get_recent_csv_uploads(limit: int = 10) -> list[CsvUploadResponse]:
        """Get the most recent CSV upload records."""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM csv_upload 
                ORDER BY csv_upload_uploaded_at DESC 
                LIMIT %s
            """,
                (limit,),
            )
            results = cursor.fetchall()

            return [CsvUploadResponse(**dict(result)) for result in results]
