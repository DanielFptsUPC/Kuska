import os
import time

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "incident-media")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_media(path: str, data: bytes, content_type: str, attempts: int = 3) -> str:
    last_error = None
    for attempt in range(attempts):
        try:
            supabase.storage.from_(SUPABASE_BUCKET).upload(
                path, data, {"content-type": content_type, "upsert": "true"}
            )
            return supabase.storage.from_(SUPABASE_BUCKET).get_public_url(path)
        except Exception as e:
            last_error = e
            if attempt < attempts - 1:
                time.sleep(1)
    raise last_error
