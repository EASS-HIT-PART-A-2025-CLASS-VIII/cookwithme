from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from openai import OpenAI
import json
import os
import time
import hashlib
import redis

from app.database import get_session
from app.security import get_current_user
from app.models import Recipe, RecipeView, Favorite

# -----------------------
# Redis + cache key config
# -----------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

MODEL_NAME = "gpt-4.1-mini"
PROMPT_VERSION = "v1"  # bump this when you change prompt/schema behavior

CACHE_TTL_SECONDS = int(os.getenv("RECO_CACHE_TTL", str(60 * 30)))  # default: 30 min
LOCK_TTL_SECONDS = int(os.getenv("RECO_LOCK_TTL", "20"))            # default: 20 sec


def make_reco_cache_key(
    user_id: int,
    limit: int,
    viewed_ids: list[int],
    fav_ids: list[int],
    candidate_ids: list[int],
) -> str:
    """
    Cache key includes:
    - user + signals (views/favs)
    - limit
    - candidate ids snapshot (so cache updates when catalog changes)
    - model + version
    """
    payload = {
        "u": user_id,
        "limit": limit,
        "viewed": viewed_ids[:10],
        "fav": fav_ids,
        "cands": candidate_ids[:60],
        "model": MODEL_NAME,
        "v": PROMPT_VERSION,
    }
    s = json.dumps(payload, sort_keys=True)
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()[:24]
    return f"reco:{h}"


# -----------------------
# Router + OpenAI client
# -----------------------
router = APIRouter()
client = OpenAI()


def extract_json_from_response(resp):
    if hasattr(resp, "output_text") and resp.output_text:
        return resp.output_text
    try:
        return resp.output[0].content[0].text
    except Exception:
        raise ValueError("Could not extract text from OpenAI response")


@router.get("/recommendations")
def get_recommendations(
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
    limit: int = 6,
):
    limit = max(1, min(limit, 3))

    # ---- signals: last viewed ----
    viewed_ids_raw = session.exec(
        select(RecipeView.recipe_id)
        .where(RecipeView.user_id == user.id)
        .order_by(RecipeView.created_at.desc())
        .limit(10)
    ).all()
    viewed_ids = [v for v in viewed_ids_raw if v is not None]
    viewed_set = set(viewed_ids)

    viewed_recipes = (
        session.exec(select(Recipe).where(Recipe.id.in_(viewed_set))).all()
        if viewed_set
        else []
    )

    viewed_compact = [
        {"id": r.id, "title": r.title, "ingredients": r.ingredients or []}
        for r in viewed_recipes
        if r.id is not None
    ]

    # ---- favorites (optional signal) ----
    fav_ids_raw = session.exec(
        select(Favorite.recipe_id).where(Favorite.user_id == user.id)
    ).all()
    fav_ids = [f for f in fav_ids_raw if f is not None]
    fav_set = set(fav_ids)

    # ---- candidates ----
    candidates = session.exec(
        select(Recipe).order_by(Recipe.id.desc()).limit(60)
    ).all()

    candidate_ids = [r.id for r in candidates if r.id is not None]

    candidates_compact = [
        {
            "id": r.id,
            "title": r.title,
            "ingredients": r.ingredients or [],
            "time": r.time_minutes,
            "difficulty": str(r.difficulty),
        }
        for r in candidates
        if r.id is not None
    ]

    if not candidates_compact:
        return {"recommendations": []}

    # -----------------------
    # Redis cache + lock (save OpenAI cost)
    # -----------------------
    cache_key = make_reco_cache_key(user.id, limit, viewed_ids, fav_ids, candidate_ids)

    # 1) Cache-first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    lock_key = f"{cache_key}:lock"

    # 2) Single-flight lock (avoid parallel duplicate OpenAI calls)
    got_lock = redis_client.set(lock_key, "1", nx=True, ex=LOCK_TTL_SECONDS)
    if not got_lock:
        # someone else is computing -> wait briefly for cache
        for _ in range(10):  # ~2 seconds
            time.sleep(0.2)
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

        # do NOT call OpenAI (avoid extra cost)
        return {"recommendations": [], "status": "busy_try_again"}

    try:
        prompt = {
            "recent_views": viewed_compact,
            "candidates": candidates_compact,
            "rules": {
                "max_results": limit,
                "avoid_recipe_ids": list(viewed_set | fav_set),
                "short_reason": True,
            },
        }

        resp = client.responses.create(
            model=MODEL_NAME,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a recommendation engine for a cooking app. "
                        "Recommend ONLY from the provided candidates. "
                        "Return valid JSON exactly in this format:\n"
                        '{ "recommendations": [{ "recipe_id": number, "reason": string }] }'
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(prompt, ensure_ascii=False),
                },
            ],
            temperature=0.3,
        )

        raw = extract_json_from_response(resp)
        data = json.loads(raw)
        recs = data.get("recommendations", [])

        # Map rec IDs -> recipe fields for frontend
        ids = [r.get("recipe_id") for r in recs if isinstance(r, dict) and "recipe_id" in r]
        ids = [i for i in ids if isinstance(i, int)]

        if not ids:
            result = {"recommendations": []}
            redis_client.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(result))
            return result

        recipes = session.exec(select(Recipe).where(Recipe.id.in_(ids))).all()
        by_id = {r.id: r for r in recipes if r.id is not None}

        out = []
        for r in recs:
            rid = r.get("recipe_id") if isinstance(r, dict) else None
            recipe = by_id.get(rid)
            if recipe:
                out.append(
                    {
                        "id": recipe.id,
                        "title": recipe.title,
                        "time_minutes": recipe.time_minutes,
                        "difficulty": str(recipe.difficulty),
                        "image_url": recipe.image_url,
                    }
                )

        result = {"recommendations": out}
        redis_client.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(result))
        return result

    except Exception as e:
        print("⚠️ OpenAI error:", e)
        return {"recommendations": [], "status": "ai_unavailable"}

    finally:
        # Always release the lock so we don't get stuck in "busy"
        try:
            redis_client.delete(lock_key)
        except Exception:
            pass