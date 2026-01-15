from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Response ,Request
from sqlmodel import Session, select
from app.seed.seed_data import run_seed
from app.database import init_db, get_session
from app.storage import upload_video
from app.models import Recipe, RecipeCreate, RecipeUpdate, Review, ReviewCreate, ReviewRead, Highlight, User, Favorite, UserRole, RecipeReadWithStats
from app.crud import create_recipe,get_all_recipes,get_recipe_by_id,update_recipe,delete_recipe,create_user, authenticate_user, get_user_by_email,create_highlight, get_all_highlights
from pydantic import BaseModel, EmailStr
from fastapi.staticfiles import StaticFiles
from app.auth_jwt import create_access_token
from .security import require_admin, get_current_user
from sqlalchemy import func
import traceback

app = FastAPI()
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@app.on_event("startup")
def startup():
    init_db()     
    run_seed()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# --------------------------
# LOGIN/REGISTER
# --------------------------
@app.post("/auth/register", status_code=201)
def register(payload: RegisterRequest, session: Session = Depends(get_session)):
    existing = get_user_by_email(session, payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = create_user(session, payload.email, payload.password, role="user")
    return {"id": user.id, "email": user.email, "role": user.role}

@app.post("/auth/login")
def login(payload: LoginRequest, session: Session = Depends(get_session)):
    user = authenticate_user(session, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(subject=str(user.id), role=user.role)
    return {"access_token": token, "token_type": "bearer"}
# --------------------------
# RECIPES CRUD
# --------------------------

@app.post("/recipes", response_model=Recipe, status_code=201)
def create_recipe_endpoint(
    recipe: RecipeCreate,
    admin: User = Depends(require_admin),
):
    return create_recipe(recipe)

@app.get("/recipes/{recipe_id}", response_model=Recipe)
def read_one(recipe_id: int):
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(404, "Recipe not found")
    return recipe


@app.put("/recipes/{recipe_id}", response_model=Recipe)
def update_recipe_endpoint(recipe_id: int, data: RecipeUpdate, admin: User = Depends(require_admin)):
    updated = update_recipe(recipe_id, data)
    if not updated:
        raise HTTPException(404, "Recipe not found")
    return updated

@app.delete("/recipes/{recipe_id}")
def delete_recipe_endpoint(recipe_id: int, admin: User = Depends(require_admin)):
    deleted = delete_recipe(recipe_id)
    if not deleted:
        raise HTTPException(404, "Recipe not found")
    return {"message": "Recipe deleted"}


# --------------------------
# HIGHLIGHTS
# --------------------------
@app.post("/upload-video")
async def upload_video_endpoint(file: UploadFile = File(...)):
    video_url = upload_video(await file.read())
    return {"video_url": video_url}

@app.post("/highlights", response_model=Highlight)
def create_highlight_endpoint(
    highlight: Highlight,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    return create_highlight(session, highlight)

@app.get("/highlights", response_model=list[Highlight])
def get_highlights(session: Session = Depends(get_session)):
    return get_all_highlights(session)

@app.delete("/highlights/{highlight_id}")
def delete_highlight(
    highlight_id: int,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    highlight = session.get(Highlight, highlight_id)
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")

    session.delete(highlight)
    session.commit()
    return {"message": "Highlight deleted"}

# --------------------------
# REVIEWS
# --------------------------

@app.post("/recipes/{recipe_id}/reviews", response_model=ReviewRead, status_code=201)
def add_review(
    recipe_id: int,
    payload: ReviewCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(404, "Recipe not found")

    review = Review(
        recipe_id=recipe_id,
        user_id=user.id,
        author_email=user.email,
        rating=payload.rating,
        comment=payload.comment,
    )

    session.add(review)
    session.commit()
    session.refresh(review)
    return review

@app.get("/recipes/{recipe_id}/reviews", response_model=list[ReviewRead])
def get_reviews(
    recipe_id: int,
    session: Session = Depends(get_session),
):
    stmt = (
        select(Review)
        .where(Review.recipe_id == recipe_id)
        .order_by(Review.created_at.desc())
    )
    return session.exec(stmt).all()

@app.delete("/reviews/{review_id}", status_code=204)
def delete_review(
    review_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    is_owner = (review.user_id == user.id)
    is_admin = (getattr(user.role, "value", user.role) == "admin")

    if not (is_owner or is_admin):
        raise HTTPException(status_code=403, detail="Not allowed to delete this review")

    session.delete(review)
    session.commit()
    return Response(status_code=204)

@app.get("/recipes", response_model=list[RecipeReadWithStats])
def read_all(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    recipes = session.exec(select(Recipe)).all()

    stats = session.exec(
        select(
            Review.recipe_id,
            func.coalesce(func.avg(Review.rating), 0).label("avg_rating"),
            func.count(Review.id).label("reviews_count"),
        )
        .group_by(Review.recipe_id)
    ).all()

    stats_map = {
        rid: (float(avg), int(cnt)) for (rid, avg, cnt) in stats
    }

    out = []
    for r in recipes:
        avg, cnt = stats_map.get(r.id, (0.0, 0))
        out.append(RecipeReadWithStats(
            id=r.id,
            title=r.title,
            ingredients=r.ingredients,
            instructions_md=r.instructions_md,
            time_minutes=r.time_minutes,
            difficulty=r.difficulty,
            image_url=r.image_url or "",
            avg_rating=round(avg, 1),
            reviews_count=cnt,
        ))
    return out

# --------------------------
# FAVORITES
# --------------------------

@app.get("/favorites", response_model=list[Recipe])
def get_favorites(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    fav_ids = session.exec(
        select(Favorite.recipe_id).where(Favorite.user_id == user.id)
    ).all()

    if not fav_ids:
        return []

    recipes = session.exec(select(Recipe).where(Recipe.id.in_(fav_ids))).all()
    return recipes


@app.post("/favorites/{recipe_id}", status_code=201)
def add_favorite(
    recipe_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    exists = session.get(Favorite, (user.id, recipe_id))
    if exists:
        return {"ok": True}

    session.add(Favorite(user_id=user.id, recipe_id=recipe_id))
    session.commit()
    return {"ok": True}


@app.delete("/favorites/{recipe_id}", status_code=204)
def remove_favorite(
    recipe_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    fav = session.get(Favorite, (user.id, recipe_id))
    if not fav:
        return Response(status_code=204)

    session.delete(fav)
    session.commit()
    return Response(status_code=204)