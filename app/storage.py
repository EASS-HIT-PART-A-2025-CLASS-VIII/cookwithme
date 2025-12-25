from supabase import create_client
import os
import uuid

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

BUCKET = os.getenv("SUPABASE_BUCKET", "videos")

def upload_video(file):
    filename = f"{uuid.uuid4()}.mp4"

    supabase.storage.from_(BUCKET).upload(
        filename,
        file,
        {"content-type": "video/mp4"}
    )

    public_url = supabase.storage.from_(BUCKET).get_public_url(filename)
    return public_url