import asyncio
import os
import sys
from datetime import datetime, timezone

import redis
from sqlalchemy import func
from sqlmodel import Session, select

from app.database import engine         
from app.models import Recipe, RecipeView


# -----------------------
# Config
# -----------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

LOCK_KEY = "refresh:ai_recommendations"
LOCK_TTL_SECONDS = int(os.getenv("REFRESH_LOCK_TTL", "120"))

LAST_RUN_KEY = "refresh:last_run"
LAST_RUN_TTL_SECONDS = int(os.getenv("REFRESH_LAST_RUN_TTL", "3600"))

DEFAULT_INTERVAL_SECONDS = int(os.getenv("REFRESH_INTERVAL", "180"))


# -----------------------
# Redis client
# -----------------------
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(*args):
    print(*args, flush=True)


def count_rows(session: Session, model) -> int:
    return int(
        session.exec(
            select(func.count()).select_from(model)
        ).one()
    )


# -----------------------
# Core refresh logic
# -----------------------
def refresh_recommendations_sync():
    """
    MVP background refresh job:
    - reads DB stats
    - stores last_run timestamp in Redis
    """
    with Session(engine) as session:
        views_count = count_rows(session, RecipeView)
        recipes_count = count_rows(session, Recipe)

    ts = now_iso()
    log(f"[{ts}] 🔄 Refresh ran | views={views_count} recipes={recipes_count}")

    redis_client.set(
        LAST_RUN_KEY,
        ts,
        ex=LAST_RUN_TTL_SECONDS,
    )


# -----------------------
# Lock helpers
# -----------------------
async def acquire_lock() -> bool:
    return bool(
        redis_client.set(
            LOCK_KEY,
            "1",
            nx=True,
            ex=LOCK_TTL_SECONDS,
        )
    )


async def release_lock():
    try:
        redis_client.delete(LOCK_KEY)
    except Exception:
        pass


# -----------------------
# Run once (idempotent)
# -----------------------
async def run_once(retries: int = 3):
    if not await acquire_lock():
        log("⏭️ Refresh already running – skipping")
        return

    try:
        log("🚀 Running refresh job")

        last_err = None
        for attempt in range(1, retries + 1):
            try:
                await asyncio.to_thread(refresh_recommendations_sync)
                log("✅ Refresh finished")
                return
            except Exception as e:
                last_err = e
                log(f"⚠️ Attempt {attempt}/{retries} failed: {repr(e)}")
                await asyncio.sleep(1.5 * attempt)

        log(f"❌ Refresh failed after {retries} retries: {repr(last_err)}")
        raise last_err

    finally:
        await release_lock()


# -----------------------
# Loop mode (worker)
# -----------------------
async def loop_forever(interval_seconds: int = DEFAULT_INTERVAL_SECONDS):
    log(f"🟢 Worker alive | interval={interval_seconds}s | redis={REDIS_URL}")
    while True:
        try:
            await run_once()
        except Exception as e:
            log(f"⚠️ run_once crashed but loop continues: {repr(e)}")
        await asyncio.sleep(interval_seconds)


# -----------------------
# CLI entrypoint
# -----------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CookWithMe refresh worker")
    parser.add_argument("--loop", action="store_true", help="run forever")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SECONDS)
    args = parser.parse_args()

    try:
        if args.loop:
            asyncio.run(loop_forever(args.interval))
        else:
            asyncio.run(run_once())
    except KeyboardInterrupt:
        log("👋 Worker stopped")
        sys.exit(0)