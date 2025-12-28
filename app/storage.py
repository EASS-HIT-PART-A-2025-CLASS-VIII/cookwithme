from supabase import create_client
import os
import uuid

supabase = None

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET = os.getenv("SUPABASE_BUCKET", "videos")

def upload_video(file: bytes) -> str:
    if supabase is None:
        raise RuntimeError("Supabase is not configured")
    filename = f"{uuid.uuid4()}.mp4"

    supabase.storage.from_(BUCKET).upload(
        filename,
        file,
        {"content-type": "video/mp4"}
    )

    public_url = supabase.storage.from_(BUCKET).get_public_url(filename)
    return public_url