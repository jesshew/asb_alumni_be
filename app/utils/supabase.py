from supabase import create_client, Client
from app.config import settings


def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    return create_client(
        supabase_url=settings.SUPABASE_URL, supabase_key=settings.SUPABASE_KEY
    )
