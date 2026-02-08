import hashlib
import json

MODEL_NAME = "gpt-4.1-mini"
PROMPT_VERSION = "v1"  

def make_reco_cache_key(user_id: int, limit: int, viewed_ids: list[int], fav_ids: list[int]) -> str:
    payload = {
        "u": user_id,
        "limit": limit,
        "viewed": viewed_ids[:10],
        "fav": fav_ids,
        "model": MODEL_NAME,
        "v": PROMPT_VERSION,
    }
    s = json.dumps(payload, sort_keys=True)
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()[:24]
    return f"reco:{h}"
